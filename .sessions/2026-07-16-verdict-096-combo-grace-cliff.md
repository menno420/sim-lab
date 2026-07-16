# Session — VERDICT 096 — the grace window that hides one shared budget: a forgiving-streak combo contract ("any action ≤ G=3 late is safe, and you only lose the streak on a REAL miss ℓ>G") priced where it exactly breaks — when the grace is funded by ONE shared budget rather than re-judged per action; every steady within-grace lateness breaks the streak at a finite history-determined step break_step = ⌊B0/ℓ⌋+1 (ℓ=1→11, ℓ=2→6, ℓ=3→4), the break is SILENT under the strict miss-contract (no single action exceeded G), and the FORGIVENESS INVERSION is the sharpest cut — the silently wiped multiplier = break_step−1 = ⌊B0/ℓ⌋ = {10,5,3} is strictly DECREASING in ℓ, so the player who leans LIGHTEST on grace each action (ℓ=1) rides the longest streak and loses the MOST (10 of M=25, >3× the ℓ=3 player); two repairs priced in-model — (a) a grace-low warning once per streak at break_step−1 with zero false positives on the ℓ=0 cohort, (b) replenish-on-within-grace R'=1 making ℓ=1 survive-forever and moving ℓ=2→10, ℓ=3→5 (idea-engine PROPOSAL 083, the round-17 GAME-MECHANICS rotation slot; P083 → V096 under the +13 offset, twentieth row)

> **Status:** `complete`
> 📊 Model: opus-class · high · simulation/verification

Objective: produce VERDICT 096 for idea-engine PROPOSAL 083 (the combo
grace-budget cliff, `ideas/superbot-games/combo-grace-budget-cliff-2026-07-16.md`,
outbox block `## PROPOSAL 083 · 2026-07-16T14:28:18Z · status: sim-ready`, read
at idea-engine main b97e97d). One slice, one branch
(`claude/v096-combo-grace-cliff`), one verdict. NUMBERING, verified at sim-lab
origin/main 35dc520 (the V095 merge #167 is the tip at session start): newest
`## VERDICT` header is 095; `## VERDICT 096` / `verdict-096` collision-grepped
with hit CLASSIFICATION per the V093 taxonomy — every hit PREDICTION-class (the
V095 refresh's own heartbeat/map next-expected pointers plus idea-engine
batons), zero claim-class hits — so idea-engine PROPOSAL 083 → **VERDICT 096**,
the +13 offset's twentieth row (map-row extension landed in
`docs/current-state.md` this same PR). Worker session; ledger appended to
`control/outbox.md` only — `control/inbox.md` untouched (manager-order file);
this slice also refreshes the coordinator heartbeat `control/status.md`
(next-expected roll to P084 → V097). No idea-engine claim file written by this
sim-lab slice (the V074–V095 precedent — the idea-engine claim rides the
idea-engine mirror PR). Seeds: the drafter's registered set **20261726–729** IS
the session seed set, quoted literally — Arm-R reporting-only 20261726
(N = 20,000) / 20261727 (N = 8,000) under the REGISTERED draw-order grammar (one
`random.Random` per seed; per trace EXACTLY 3 `rng.randint` draws in registered
order lateness ℓ ∈ [0,4], horizon cap ∈ [5,50], salt ∈ [1,1000]
drawn-and-logged; draw sentinels 3N: 60,000 / 24,000), presentation shuffle
20261728 (presentation leg only), aux 20261729 reserved and ASSERTED never read;
20261722–725 are P082/V095's set — untouched; the next free block starts at
**20261730**. This is a DETERMINISTIC-AUTOMATON exact-census head (nearest
method kin: P081/V094's deterministic-orbit replay against a comfort comment
with the true-sentence-survives move, and P082/V095's shipped-mechanism-vs-sold-
sentence disposition-TRUE / everywhere-INVERTED structure with a priced repair
fork) — the model pins a budget automaton (break-before-update, replenish-only-
on-clean, checked-first miss) and re-derives every census cell from scratch;
every decision leg is deterministic integer arithmetic, platform-independent;
zero repo/network reads at verdict time. This card holds the substrate gate red
deliberately until this flip (the born-red discipline — the designed hold is the
only red this branch produces itself).

## What happened

Built `sims/verdict-096-combo-grace-budget-cliff/` under the standing
discipline: fixtures.json committed BEFORE the runner (born-red card 36c5627 →
sim + fixtures + REPORT + map row f9dc96a → heartbeat 173e958 → this flip),
twin-arm: Arm A the pinned stepwise budget automaton (break-before-update,
replenish-only-on-clean ℓ≤0, checked-first miss ℓ>G, the strict `< 0` budget
boundary; seedless, DECISION-bearing); Arm B an INDEPENDENTLY-shaped twin (a
full-trajectory budget WALK over an explicit per-step trajectory, no
early-return closed form), tied through the typed contacts C1 (steady sim
break_step == ⌊B0/ℓ⌋+1) / C2 (repair-(b) sim == ⌊(B0−ℓ)/(ℓ−1)⌋+2) + the
twin-machine and twin-evaluator contacts; Arm R seeded reporting-only random
cells under the drafter's REGISTERED 3-draw grammar (ℓ∈[0,4], horizon∈[5,50],
salt∈[1,1000]). 35 self-checks, 35 passed, 0 failed; exit 0; < 1 s/run;
byte-identical double run (results 413f4d55…, run-stdout a0c9ed62…, sha256 in
REPORT.md); CPython 3.11 asserted. ZERO rehearsal fixes and zero fix-forwards
— the first complete in-repo run of the committed pipeline is the accepted run
and reproduced the drafter's disclosed 35/35 exactly. The independent
re-derivation had one live surprise, resolved cleanly and disclosed: the
registered class-stream digests did NOT reproduce under a full-label
concatenation (V095's digest procedure); they reproduce under a FIRST-CHARACTER
token stream (SURVIVE/SILENT-BREAK both → 'S', REAL-MISS → 'R'), matching BOTH
seeds' 12-hex digests exactly (96 bits of agreement — the encoding is
determined, not guessed), disclosed as a vacancy-derived fixture with the
census carrying the SURVIVE-vs-SILENT-BREAK split as the independent witness.
PR #168 opened READY at slice start.

## Results

**VERDICT 096 — REJECT, all four registered clauses exact, 0 mismatched.**
(R1) the steady census over ℓ∈{0,1,2,3} lands {ℓ=0 survives; ℓ=1,2,3 break at
11, 6, 4} with the ℓ>G control (ℓ=4) breaking at step 1 — the folk belief made
precise, NOT "all within-grace survive"; (R2) steady sim break_step ==
⌊B0/ℓ⌋+1 exact [11,6,4] (C1), Arm B agreeing; (R3) the forgiveness inversion —
the silently wiped multiplier = break_step−1 = ⌊B0/ℓ⌋ = {10,5,3} strictly
DECREASING in ℓ, max at ℓ=1 (10 of M=25, cap never binds); (R4) repair (a)
fires once per streak at break_step−1 {10,5,3} with zero false positives on the
ℓ=0 cohort, and repair (b) at R'=1 makes ℓ=1 survive (net 0) and moves ℓ=2→10,
ℓ=3→5 == ⌊(B0−ℓ)/(ℓ−1)⌋+2 (C2). APPROVE did not fire and is arithmetically
excluded (the ℓ=1 cell breaks at 11 — B0=10 exhausted after 10 unit spends,
F4a pencil). Both Arm-R preview censuses reproduced EXACTLY (SURVIVE 4,595 ·
SILENT-BREAK 11,427 · REAL-MISS 3,978, draws 60,000, digest 3bfa073726f7 @
20261726; 1,844 / 4,534 / 1,622, draws 24,000, digest 6f857d0afcf4 @ 20261727);
taxonomy total (SURVIVE+SILENT-BREAK+REAL-MISS == N); twin evaluators
REJECT/REJECT over the enumerated 64-row boolean input set. The three
falsifiability worlds named in the registration (model-semantics, constant-
convention, design-transfer NULLs) were all reachable and none fired — every
census landed on the registered values.

## ⟲ Previous-session review

**Previous-session review** (⟲ previous session = VERDICT 095, sim-lab PR
#167 → 35dc520): a clean landing whose conventions this slice consumed
wholesale — born-red card / READY PR / no-sim-lab-claim-file (the idea-engine
claim rides the mirror PR) / registered-allocation-as-seed-set / typed margin
ledger / structured anomaly census / vacancy-derived disclosures carried
verbatim, the +13 offset extended to its twentieth row in the same grammar.
V095's 💡 (SHAPE-REGISTERED FIXTURES NEED A BEHAVIORAL DIGEST BESIDE THEM)
BOUND this slice and was honored AND stress-tested: P083 registered its Arm-R
class-stream digests exactly as V095's rule prescribes, and they were the
witness that pinned my reconstruction — but the reconstruction also EXPOSED the
rule's next edge (see 💡): the registered digest's token encoding is
non-injective (two classes collapse to one char), so the digest alone is only a
partial witness and the census had to carry the rest. V095's seed baton
(20261722–725; "next free block starts 20261726") made the P083 allocation land
exactly where the drafter registered it. Nothing was left pending for this
slice to resolve.

💡 **Session idea (genuine, this session):** A CLASS-STREAM DIGEST WITH A
NON-INJECTIVE TOKEN ENCODING IS ONLY A PARTIAL WITNESS — REGISTER THE ENCODING,
NOT JUST THE DIGEST. P083's Arm-R digest reproduced only under a
FIRST-CHARACTER token stream where SURVIVE and SILENT-BREAK both map to 'S' —
so the digest is blind to the exact split between the head's two most important
classes (the survivor vs the silent-break, which is the whole point of the
head) and witnesses only the position of REAL-MISS in the stream. It became a
full identity witness ONLY because the per-seed census counts were ALSO
registered and reproduced, fixing the S/S split the digest collapses. The
durable rule for drafters, one turn past V095's "register a digest beside shape
fixtures": register the digest's TOKEN ENCODING too, and prefer an INJECTIVE
one (one distinct char per class) so the digest alone is a complete witness; if
the encoding must collapse classes, say so and pair it explicitly with the full
census as the second, independent witness. A digest is only as faithful as its
alphabet. Dedup: V095's 💡 is about a digest EXISTING beside anchor-less shape
slots; V094's is anchor lists carrying COORDINATES; V078's is anchor values
self-evaluating; this is about a registered digest's ENCODING FIDELITY — a
non-injective token map silently narrows what the checksum can catch. Grepped
.sessions/ + sims/ at 35dc520 for "injective"/"encoding"/"first char" — no
prior card or REPORT states the digest-encoding-fidelity rule.

📊 Model: opus-class · high · simulation/verification
