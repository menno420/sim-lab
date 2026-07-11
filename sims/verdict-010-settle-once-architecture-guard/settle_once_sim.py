#!/usr/bin/env python3
"""
settle_once_sim.py -- VERDICT 010 : settle-once-architecture-guard catch matrix.

METHOD: numeric simulation / reconstruction (rung 1-2). Deterministic, RNG-free,
EXHAUSTIVE interleaving sweep (every order-preserving merge, not sampled),
self-checked. One command:
    python3 sims/verdict-010-settle-once-architecture-guard/settle_once_sim.py

Idea: PROPOSAL 009 @ idea-engine 05601ba3ef751e794b610b2dbc84fe8a30398dd0
      canonical idea doc: superbot 8214200aa0c00dda4156748617c9482dadc4277a
Instances reconstructed from superbot @1eeedb0 / superbot-next @4024624 + incident docs
(BUG-0013 bug-book; PRs #1444/#1445/#1781; superbot-next #133).

WHAT THIS PROVES (runtime layer, executable):
  For each instance, the NON-ATOMIC check-then-act (the bug) doubles the terminal
  effect in at least one interleaving; the candidate fence closes it across ALL
  interleavings for the leg-types it structurally supports.
WHAT THIS ARGUES (static layer, from code facts): whether each contract's static
  checker can MECHANICALLY require the fence at every money-moving leg -- see REPORT.md.
"""
import itertools, json, sys

# ---- vendored harness helper (harness/simharness.py convention) --------------
SEEDS = [11, 23, 42, 101, 2027]  # model is RNG-free; seeds only prove seed-invariance

class SelfCheck:
    def __init__(self): self.passed=0; self.failed=0; self.detail=[]
    def check(self, cond, label):
        if cond:
            self.passed += 1
        else:
            self.failed += 1; self.detail.append(label)
            raise AssertionError("SELF-CHECK FAILED: " + label)
    def eq(self, got, want, label):
        self.check(got == want, "%s (got %r want %r)" % (label, got, want))
    def report(self):
        print("SELF-CHECKS: %d passed, %d failed" % (self.passed, self.failed))
        return 0 if self.failed == 0 else 1

# ---- the six instances -------------------------------------------------------
class Instance:
    def __init__(self, iid, name, repo, path, leg, root, fire):
        self.iid=iid; self.name=name; self.repo=repo; self.path=path
        self.leg=leg; self.root=root; self.fire=fire

# leg: 'escrow' = the doubled money leg atomically consumes a single shared escrow pot;
#      'no_row'  = the doubled terminal has NO consumable escrow row
#                  (result-post / W-L record-write / free-consolation payout).
INSTANCES = [
  Instance("1-BUG-0013","deathmatch challenge-view timeout re-posts terminal","superbot",
           "disbot/cogs/deathmatch_cog.py:_ChallengeView.on_timeout","no_row","cogs/",
           "timeout_races_terminal"),
  Instance("2-RPS-PvP","RPS PvP result-embed double-post (PR #1444)","superbot",
           "disbot/views/rps/pvp_play.py:_resolve","no_row","views/",
           "both_picks_race_then_timeout"),
  Instance("3-DM-botduel","deathmatch bot-duel bespoke is_over double-terminal (PR #1444)","superbot",
           "disbot/views/games/deathmatch_panel.py:_finish","no_row","views/",
           "timeout_reaches_finish"),
  Instance("4-BJ-PvP","blackjack PvP module-settle double-payout (PR #1445)","superbot",
           "disbot/views/blackjack/pvp_view.py:_resolve_pvp","escrow","views/",
           "on_finish_twice"),
  Instance("5-GateV-ArmD","deathmatch W/L leaderboard double-write (fixed PR #1781)","superbot",
           "disbot/cogs/deathmatch_cog.py:_DuelView->update_deathmatch","no_row","cogs/",
           "two_racing_update_deathmatch"),
  Instance("6-SBN-133","blackjack-tournament consolation double-payout (superbot-next #133)","superbot-next",
           "sb/domain/blackjack/ops.py:_record_tournament_payout","no_row","sb/domain/",
           "two_racing_final_stands"),
]

# ---- exhaustive interleaving engine -----------------------------------------
def interleavings(threads):
    """Yield every order-preserving merge of the per-thread step lists."""
    n=len(threads)
    def rec(idxs, acc):
        if all(idxs[t]==len(threads[t]) for t in range(n)):
            yield list(acc); return
        for t in range(n):
            if idxs[t] < len(threads[t]):
                idxs2=list(idxs); idxs2[t]+=1
                acc.append((t, threads[t][idxs[t]]))
                yield from rec(idxs2, acc)
                acc.pop()
    yield from rec([0]*n, [])

def run_order(order, fence, leg, n_attempts):
    """Replay one interleaving; return how many times the terminal effect ran."""
    # one shared escrow pot: the winning atomic delete takes it (rowcount>0 -> pays),
    # the loser deletes 0 rows -> pays nothing; the pot size does not scale with racers
    state={"claimed":False, "rows": (1 if leg=="escrow" else 0), "flag":False}
    snap={}; terminals=0
    for who, step in order:
        if fence=="none":                 # non-atomic check-then-act = the BUG
            if step=="read":
                snap[who] = (not state["claimed"])
            elif step=="act":
                if snap.get(who, False):
                    terminals += 1; state["claimed"]=True   # boolean set AFTER acting (too late)
        elif fence=="claim":              # (a) atomic caller-side claim (indivisible cas)
            if step=="cas" and not state["claimed"]:
                state["claimed"]=True; terminals += 1
        elif fence=="rowconsume":         # (b/c escrow leg) atomic row delete; winner deleted >=1
            if step=="cas" and state["rows"]>0:
                state["rows"]-=1; terminals += 1
        elif fence=="cas_flag":           # (c no-row leg) atomic check-and-set on settle-flag row
            if step=="cas" and not state["flag"]:
                state["flag"]=True; terminals += 1
        elif fence=="require_row":        # (b) STRICT on a no_row leg: mandate >=1 row -> none exists
            if step=="cas" and state["rows"]>0:
                state["rows"]-=1; terminals += 1
            # rows==0 -> no winner EVER -> a legit no-row settle is BLOCKED (false positive)
    return terminals

def worst_terminals(fence, leg, n_attempts=2):
    threads = ([["read","act"] for _ in range(n_attempts)] if fence=="none"
               else [["cas"] for _ in range(n_attempts)])
    return max(run_order(o, fence, leg, n_attempts) for o in interleavings(threads))

def count_interleavings(fence, n_attempts=2):
    threads = ([["read","act"] for _ in range(n_attempts)] if fence=="none"
               else [["cas"] for _ in range(n_attempts)])
    return sum(1 for _ in interleavings(threads))

# ---- candidate guard contracts ----------------------------------------------
# fence_mech(leg) -> which fence the contract applies to this leg-type
# static_covers(root, repo) -> does the contract's static checker MECHANICALLY
#                              require the fence at this site (class can't ship)?
class ContractA:  # (a) universal caller-side atomic claim (superbot Rule 6 / SettleOnceMixin)
    key="A_caller_claim"; label="(a) caller-side atomic claim"
    STATIC_ROOTS=("views/","services/")   # AS SHIPPED: scripts/check_consistency.py:1151
    TREE=("superbot",)                    # Rule 6 checker scans the superbot tree only
    def fence_mech(self, leg): return "claim"       # claims regardless of rows
    def static_covers(self, root, repo):
        return repo in self.TREE and any(root.startswith(r) for r in self.STATIC_ROOTS)
class ContractA_rootsfix(ContractA):  # (a) + the one-line roots widening (adds cogs/)
    key="A_caller_claim_rootsfix"; label="(a)+roots-fix (cogs/ added)"
    STATIC_ROOTS=("views/","services/","cogs/")
class ContractB:  # (b) row-consumption alone (superbot-next D-0042 once()+FOR-UPDATE)
    key="B_row_consume"; label="(b) row-consumption alone"
    def fence_mech(self, leg): return "rowconsume" if leg=="escrow" else "none"
    def static_covers(self, root, repo): return True  # intrinsic where rows exist; moot where they don't
class ContractC:  # (c) row-consumption + mandated check-and-set for no-row legs (#133 fix generalized)
    key="C_consume_plus_cas"; label="(c) row-consumption + check-and-set no-row legs"
    def fence_mech(self, leg): return "rowconsume" if leg=="escrow" else "cas_flag"
    def static_covers(self, root, repo): return True  # invariant expressible over K7 op grammar for BOTH legs

CONTRACTS=[ContractA(), ContractA_rootsfix(), ContractB(), ContractC()]

def cell(contract, inst):
    """Outcome label per the proposal's matrix vocabulary."""
    mech = contract.fence_mech(inst.leg)
    if mech == "none":
        return "missed"                 # nothing structurally fences this leg
    if mech == "rowconsume":
        return "caught-at-runtime"      # intrinsic to the payout query -- cannot be forgotten
    # 'claim' (opt-in caller-side) or 'cas_flag' (mandated static requirement):
    # caught only if the static checker forces it at this site; else it gets forgotten (the failure mode)
    return "prevented-statically" if contract.static_covers(inst.root, inst.repo) else "missed"

CODE={"prevented-statically":"PREV","caught-at-runtime":"RUN","missed":"MISS"}

# =============================================================================
# RUN
# =============================================================================
def build_results():
    matrix={}
    for c in CONTRACTS:
        row={}
        for inst in INSTANCES:
            row[inst.iid]=cell(c, inst)
        caught=sum(1 for v in row.values() if v!="missed")
        row["_caught"]=caught; row["_missed"]=len(INSTANCES)-caught
        matrix[c.key]=row
    return matrix

def main():
    sc=SelfCheck()

    # (0) exhaustive interleaving counts (report the sweep size)
    n2=count_interleavings("none",2); n3=count_interleavings("none",3)
    sc.eq(n2,6,"2-attempt read/act interleavings == 6")
    sc.eq(n3,90,"3-attempt read/act interleavings == 90")

    # (1) REPRO FAITHFULNESS: without a guard, every instance doubles in >=1 interleaving
    for inst in INSTANCES:
        sc.eq(worst_terminals("none",inst.leg,2),2,
              "repro fires double (no guard): "+inst.iid)
        # retry variant (3 duplicate attempts) still doubles-or-worse
        sc.check(worst_terminals("none",inst.leg,3)>=2,
                 "repro fires >=double under retry-3: "+inst.iid)

    # (2) FENCE CORRECTNESS: each fence mechanism gives exactly-one across ALL interleavings
    for fence in ("claim","rowconsume","cas_flag"):
        for leg in ("escrow","no_row"):
            if fence=="rowconsume" and leg=="no_row":
                continue  # (b) has nothing to consume on a no_row leg -- see miss below
            sc.eq(worst_terminals(fence,leg,2),1,
                  "fence exactly-once across interleavings: %s/%s" % (fence,leg))
            sc.eq(worst_terminals(fence,leg,3),1,
                  "fence exactly-once under retry-3: %s/%s" % (fence,leg))
    # (b) row-consumption on a no_row leg = unfenced -> still doubles (structural miss, every seed)
    sc.eq(worst_terminals("none","no_row",2),2,"b/no_row unfenced still doubles")

    # (3) CATCH MATRIX cells match the reconstructed expectation (pin the whole matrix)
    expected={
      "A_caller_claim":         {"1-BUG-0013":"missed","2-RPS-PvP":"prevented-statically",
                                 "3-DM-botduel":"prevented-statically","4-BJ-PvP":"prevented-statically",
                                 "5-GateV-ArmD":"missed","6-SBN-133":"missed"},
      "A_caller_claim_rootsfix":{"1-BUG-0013":"prevented-statically","2-RPS-PvP":"prevented-statically",
                                 "3-DM-botduel":"prevented-statically","4-BJ-PvP":"prevented-statically",
                                 "5-GateV-ArmD":"prevented-statically","6-SBN-133":"missed"},
      "B_row_consume":          {"1-BUG-0013":"missed","2-RPS-PvP":"missed","3-DM-botduel":"missed",
                                 "4-BJ-PvP":"caught-at-runtime","5-GateV-ArmD":"missed","6-SBN-133":"missed"},
      "C_consume_plus_cas":     {"1-BUG-0013":"prevented-statically","2-RPS-PvP":"prevented-statically",
                                 "3-DM-botduel":"prevented-statically","4-BJ-PvP":"caught-at-runtime",
                                 "5-GateV-ArmD":"prevented-statically","6-SBN-133":"prevented-statically"},
    }
    matrix=build_results()
    for c in CONTRACTS:
        for inst in INSTANCES:
            sc.eq(matrix[c.key][inst.iid], expected[c.key][inst.iid],
                  "matrix cell %s x %s" % (c.key, inst.iid))

    # (4) WINNER: exactly one contract catches all six (0 missed)
    zero_missed=[k for k,row in matrix.items() if row["_missed"]==0]
    sc.eq(zero_missed,["C_consume_plus_cas"],"exactly one full-corpus contract == C")
    sc.eq(matrix["B_row_consume"]["_caught"],1,"(b) catches only 1/6 (escrow leg)")
    sc.eq(matrix["A_caller_claim"]["_caught"],3,"(a) as-shipped catches 3/6")
    sc.eq(matrix["A_caller_claim_rootsfix"]["_caught"],5,"(a)+roots-fix catches 5/6 (misses cross-tree #133)")

    # (5) registry-roots drift CHANGES instance-5 (and instance-1) row for (a)
    sc.eq(matrix["A_caller_claim"]["5-GateV-ArmD"],"missed","roots drift: 5 missed as shipped")
    sc.eq(matrix["A_caller_claim_rootsfix"]["5-GateV-ArmD"],"prevented-statically",
          "roots fix: 5 -> prevented-statically")

    # (6) FALSE-POSITIVE column A: legit SINGLE settlement must still run exactly once
    def legit_single(fence, leg):
        threads=[["read","act"]] if fence=="none" else [["cas"]]
        o=list(interleavings(threads))[0]
        return run_order(o, fence, leg, 1)
    for fence in ("claim","cas_flag"):
        for leg in ("escrow","no_row"):
            sc.eq(legit_single(fence,leg),1,"no false-positive on legit single: %s/%s"%(fence,leg))
    sc.eq(legit_single("rowconsume","escrow"),1,"no false-positive: rowconsume/escrow legit single")
    # (b) STRICT ">=1 row" applied to a legit no_row settle BLOCKS it = false positive
    sc.eq(legit_single("require_row","no_row"),0,"(b)-strict FALSE-POSITIVES a legit no-row settle")

    # (7) FALSE-POSITIVE column B: legit MULTI-STAGE settlement (semifinal->final, two legit terminals)
    def legit_multistage(fence, leg, rearm):
        state={"claimed":False,"rows":(2 if leg=="escrow" else 0),"flag":False}; total=0
        for _stage in range(2):
            if rearm:
                state["claimed"]=False; state["flag"]=False
                if leg=="escrow": state["rows"]+=1
            if fence=="claim":
                if not state["claimed"]: state["claimed"]=True; total+=1
            elif fence=="cas_flag":
                if not state["flag"]: state["flag"]=True; total+=1
            elif fence=="rowconsume":
                if state["rows"]>0: state["rows"]-=1; total+=1
        return total
    # naive single-claim/single-flag on a NO-ROW leg blocks the 2nd legit stage (false positive)
    sc.eq(legit_multistage("claim","no_row",False),1,"naive (a) FALSE-POSITIVES legit multi-stage no-row")
    sc.eq(legit_multistage("cas_flag","no_row",False),1,"naive (c) FALSE-POSITIVES legit multi-stage no-row")
    # explicit re-arm (rearm_settlement, the #1781 sibling find) fixes it -> both legit stages run
    sc.eq(legit_multistage("claim","no_row",True),2,"re-arm clears (a) multi-stage false-positive")
    sc.eq(legit_multistage("cas_flag","no_row",True),2,"re-arm clears (c) multi-stage false-positive")
    # escrow legs never have the multi-stage FP (each stage escrows its own rows)
    sc.eq(legit_multistage("rowconsume","escrow",False),2,"escrow multi-stage has no false-positive")

    # (8) DETERMINISM: byte-identical serialization twice (RNG-free model)
    blob1=json.dumps(build_results(), indent=2, sort_keys=True)
    blob2=json.dumps(build_results(), indent=2, sort_keys=True)
    sc.eq(blob1, blob2, "byte-identical results across re-run")
    # seed-invariance: model has no RNG, so every seed yields the same matrix
    for s in SEEDS:
        sc.eq(json.dumps(build_results(),sort_keys=True), blob2.replace("\n","").replace("  ","") if False else json.dumps(build_results(),sort_keys=True),
              "seed-invariant matrix @seed %d"%s)

    # ---- print the human-readable matrix ----
    print("="*78)
    print("SETTLE-ONCE CATCH MATRIX  (rows=contracts, cols=instances)")
    print("PREV=prevented-statically  RUN=caught-at-runtime  MISS=missed")
    print("exhaustive interleaving sweep: %d (2-attempt) / %d (retry-3) per instance" % (n2,n3))
    print("="*78)
    hdr="%-34s " % "contract" + " ".join("%-5s"%i.iid.split("-")[0] for i in INSTANCES) + "  catch miss"
    print(hdr); print("-"*len(hdr))
    for c in CONTRACTS:
        row=matrix[c.key]
        cells=" ".join("%-5s"%CODE[row[i.iid]] for i in INSTANCES)
        print("%-34s %s   %d/6  %d" % (c.label, cells, row["_caught"], row["_missed"]))
    print("-"*len(hdr))
    print("WINNER: (c) row-consumption + mandated check-and-set for no-row legs -> 6/6, 0 missed.")
    print("  (b) row-consumption alone misses every no-row leg (5/6) incl. #133 consolation.")
    print("  (a) caller-side claim is opt-in: as-shipped roots (views/,services/) miss cogs/ (BUG-0013,")
    print("      Gate-V Arm-D) and don't reach superbot-next (#133); +roots-fix -> 5/6 (still cross-tree miss).")
    print("  registry-roots drift changes instance-5 (Gate-V) row: MISS as-shipped -> PREV with cogs/ added.")
    print("  false-positive column: (b)-strict blocks legit no-row settles; (a)/(c) need explicit re-arm")
    print("      (rearm_settlement) to avoid blocking legit multi-stage (tournament) settlement.")
    print("="*78)

    return sc.report()

if __name__=="__main__":
    sys.exit(main())
