#!/usr/bin/env python3
"""verdict-015 — heartbeat intra-file contradiction linter: detector-cell sweep.

Answers idea-engine PROPOSAL 013 (control/outbox.md, 2026-07-12T22:04:42Z,
sim-ready; idea ideas/fleet/heartbeat-contradiction-linter-2026-07-12.md):
over the committed revisions of idea-engine control/status.md
(fc0bab6 -> 0cfe15e), which (fact-key extraction grammar x
disposition-vocabulary normalization x comparison scope) cell catches the
known live intra-file contradiction at c77563c (line 3 "STILL ENABLED and
LEFT ARMED deliberately" vs line 9 "being DISMANTLED with the chat archive",
same failsafe trigger) plus planted disposition-flip contradictions, at
near-zero false positives -- in particular NOT flagging e66c78a's
quotation-negation carry ("the stale Q-0265 'must re-arm both / being
dismantled' paragraph is DROPPED as superseded")?

HEADLINE CORPUS FINDING (source wins over the proposal's premise): the
"other 21 revisions" are NOT clean. The carried ⚑ paragraph "The archiving
coordinator's failsafe cron trigger AND its 15-minute send_later chain are
being DISMANTLED with the chat archive" is present in ALL 21 session-1-era
revisions (fc0bab6 -> c77563c), every one of which simultaneously declares
the same failsafe live/armed/standing in its phase line -- and 9 of which
also declare the pacemaker chain alive/armed. Ground truth (hand-audited,
committed in labels.json): 30 real (revision x entity) intra-file
contradictions, all instances of ONE carry+update seam. The proposal's
c77563c specimen is simply the instance its probe noticed. Scoring is
therefore label-based: every flagged pair is classified against a committed
archetype table (true-contradiction vs named false-positive archetypes);
unlabeled pairs fail the run.

CORPUS-COUNT RECONCILIATION: the proposal says "22 committed revisions,
fc0bab6 -> 0cfe15e". `git log fc0bab6..0cfe15e -- control/status.md` (git
range semantics, EXCLUSIVE of the lower endpoint) returns exactly 22;
endpoint-INCLUSIVE (fc0bab6^..0cfe15e) returns 23. This sim commits and
sweeps all 23 endpoint-inclusive revisions.

Deterministic, stdlib-only, no network, no RNG: fixtures are sha256-pinned,
plants are ENUMERATED (first eligible statement, fixed templates). Exit 0
iff all self-checks pass. One command:

    python3 sims/verdict-015-heartbeat-contradiction-linter/heartbeat_contradiction_sweep.py
"""

import hashlib
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
CORPUS_DIR = os.path.join(HERE, "corpus")
LABELS_PATH = os.path.join(HERE, "labels.json")
RESULTS_PATH = os.path.join(HERE, "results.json")

SPECIMEN_SHORT = "c77563c"        # the proposal's pinned specimen (line 3 vs line 9)
HARD_FP_SHORT = "e66c78a"         # the quotation-negation carry that must NOT flag
SPECIMEN_TRIG = "trig_01T83UuVthszGBcENYwrTrm7"
CARRY_MARK = "being DISMANTLED with the chat archive"

# ---------------------------------------------------------------- vocabulary
# Disposition classes, from the idea writeup ("armed/enabled/live vs
# dismantled/deleted/disabled/paused") plus this corpus's own surface forms
# for the same states (standing/stands for the failsafe, alive for the
# pacemaker chain). Deliberately EXCLUDED: "active" (keyless phase labels
# like ACTIVE-IDLE), "fired"/"expired"/"parked"/"dropped" (lifecycle words
# for non-routine objects; "DROPPED" at e66c78a governs a paragraph).
UP_WORDS = ["enabled", "re-enabled", "armed", "re-armed", "live", "alive",
            "standing", "stands"]
DOWN_WORDS = ["disabled", "dismantled", "deleted", "retired", "paused"]
UP_RE = re.compile(r"(?<![\w-])(" + "|".join(UP_WORDS) + r")(?![\w])", re.IGNORECASE)
DOWN_RE = re.compile(r"(?<![\w])(" + "|".join(DOWN_WORDS) + r")(?![\w])", re.IGNORECASE)

# ------------------------------------------------------------------ fact keys
TRIG_RE = re.compile(r"trig_[A-Za-z0-9]{8,}")
PR_RE = re.compile(r"(?<![\w/])#\d{1,5}\b")
# Entity aliases (the "+quoted routine names / noun-phrase" grammar variant):
# the two routine kinds every heartbeat in this corpus tracks. An alias hit
# maps to an entity CLASS key; explicit trig ids stay their own keys.
ALIAS_CLASSES = {
    "FAILSAFE": re.compile(r"failsafe", re.IGNORECASE),
    "PACEMAKER": re.compile(r"pacemaker|send_later\s+(?:chain|one-shots?)", re.IGNORECASE),
}

MAX_ATTR_DIST = 120  # max chars between a key occurrence and a disposition token
# conjunction spread: "X AND Y are being DISMANTLED" predicates one
# disposition of BOTH conjuncts -- a token attributed to its nearest key also
# attributes to any other key whose span to that key is a pure conjunction
# (no , ; . clause boundary).
CONJ_RE = re.compile(r"^[^,;.]*(?:\band\b|\+|&)[^,;.]*$", re.IGNORECASE)
# alias co-attribution: "failsafe cron \"NAME\" trig_X (...) live" names one
# entity by alias AND id; the token attributes to the nearest key (the id)
# AND to alias occurrences in the same statement whose span to the token
# crosses no , or ; (appositive naming, not a clause about something else).
COATTR_BLOCK_RE = re.compile(r"[,;]")

GRAMMARS = ["g1-trig-id", "g2-id+pr", "g3-id+alias"]
NORMS = ["n1-raw-cooccur", "n2-class+attrib", "n3-attrib+quote-excl"]
SCOPES = ["s1-same-line", "s2-whole-file", "s3-cross-block"]

# statement delimiters: sentence/semicolon/middot boundaries. The em-dash is
# deliberately NOT a delimiter: this corpus uses it inside parentheticals
# ("(0 */2 * * * — even hours :00) STILL ENABLED ...") where splitting would
# sever keys from their dispositions; MAX_ATTR_DIST bounds the blast radius.
STMT_SPLIT_RE = re.compile(r"(?:\.\s+|;\s+|\s·\s)")
QUOTE_RE = re.compile(r"\"[^\"\n]*\"|“[^”\n]*”")
SUPERSEDE_RE = re.compile(r"superseded|no longer", re.IGNORECASE)

CHECKS = {"passed": 0, "failed": 0}


def check(name, cond):
    if cond:
        CHECKS["passed"] += 1
    else:
        CHECKS["failed"] += 1
        print("SELF-CHECK FAIL: %s" % name)


def sha256_file(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


# --------------------------------------------------------------- corpus model
class Statement(object):
    __slots__ = ("block_idx", "block_label", "text", "start")

    def __init__(self, block_idx, block_label, text, start):
        self.block_idx = block_idx      # 1-based physical line number
        self.block_label = block_label  # field label of the line
        self.text = text
        self.start = start              # char offset within the block


def parse_blocks(content):
    """One physical line = one block (the status.md format is one field per
    line). Returns list of (line_no, label, text)."""
    blocks = []
    for i, line in enumerate(content.splitlines(), start=1):
        m = re.match(r"^([#\w⚑ .-]{1,24}?):\s", line)
        label = m.group(1) if m else ("header" if line.startswith("#") else "line")
        blocks.append((i, label, line))
    return blocks


def split_statements(blocks):
    out = []
    for line_no, label, text in blocks:
        pos = 0
        for part in STMT_SPLIT_RE.split(text):
            if part.strip():
                start = text.find(part, pos)
                if start < 0:
                    start = pos
                out.append(Statement(line_no, label, part, start))
                pos = start + len(part)
    return out


def keys_in(text, grammar):
    """Return list of (key, char_pos). Trig ids are always keys; g2 adds PR
    refs; g3 adds entity-alias classes."""
    found = []
    for m in TRIG_RE.finditer(text):
        found.append((m.group(0), m.start()))
    if grammar == "g2-id+pr":
        for m in PR_RE.finditer(text):
            found.append((m.group(0), m.start()))
    if grammar == "g3-id+alias":
        for cls, rx in ALIAS_CLASSES.items():
            for m in rx.finditer(text):
                found.append((cls, m.start()))
    return found


def dispositions_in(text):
    out = []
    for m in UP_RE.finditer(text):
        out.append(("UP", m.group(0), m.start()))
    for m in DOWN_RE.finditer(text):
        out.append(("DOWN", m.group(0), m.start()))
    return out


def mask_quotes(text):
    return QUOTE_RE.sub(lambda m: " " * len(m.group(0)), text)


# ------------------------------------------------------------------ extractor
def extract_facts(statements, grammar, norm):
    """n2/n3 machinery: per statement, attribute each disposition token to
    (a) the nearest key occurrence within MAX_ATTR_DIST, (b) keys conjoined
    to it (CONJ_RE), and (c) alias-class occurrences within MAX_ATTR_DIST
    whose span to the token crosses no comma/semicolon."""
    facts = []
    for st in statements:
        keys = keys_in(st.text, grammar)
        if not keys:
            continue
        disp_text = st.text
        if norm == "n3-attrib+quote-excl":
            disp_text = mask_quotes(st.text)
            if SUPERSEDE_RE.search(st.text):
                continue  # historical/superseded narration contributes nothing
        disps = dispositions_in(disp_text)
        if not disps:
            continue
        ids_here = set(k for k, _ in keys if k.startswith("trig_"))
        for cls, word, dpos in disps:
            best, bestd, bestpos = None, None, None
            for key, kpos in keys:
                d = abs(dpos - kpos)
                if bestd is None or d < bestd:
                    best, bestd, bestpos = key, d, kpos
            if bestd is None or bestd > MAX_ATTR_DIST:
                continue
            attributed = {best}
            for key, kpos in keys:
                if key in attributed:
                    continue
                lo, hi = sorted((kpos, bestpos))
                if CONJ_RE.match(st.text[lo:hi]):
                    attributed.add(key)
            for key, kpos in keys:
                if key in attributed or key not in ALIAS_CLASSES:
                    continue
                if abs(dpos - kpos) > MAX_ATTR_DIST:
                    continue
                lo, hi = sorted((kpos, dpos))
                if not COATTR_BLOCK_RE.search(st.text[lo:hi]):
                    attributed.add(key)
            for key in sorted(attributed):
                facts.append({
                    "key": key, "cls": cls, "block": st.block_idx,
                    "word": word, "ids": ids_here,
                    "snippet": st.text.strip()[:160],
                })
    return facts


def scope_ok(scope, block_a, block_b):
    if scope == "s1-same-line":
        return block_a == block_b
    if scope == "s3-cross-block":
        return block_a != block_b
    return True  # s2-whole-file


def conflicts_attrib(facts, scope):
    """Pairwise UP-vs-DOWN conflicts on the same key under the scope rule.
    Alias-class pairs where BOTH statements carry explicit, disjoint,
    non-empty trig-id sets are exempt (two different triggers legitimately in
    opposite states, disambiguated by their ids -- e66c78a line 3's NEW
    ENABLED / OLD DELETED pair)."""
    by_key = {}
    for f in facts:
        by_key.setdefault(f["key"], []).append(f)
    flags = []
    for key, fs in sorted(by_key.items()):
        ups = [f for f in fs if f["cls"] == "UP"]
        downs = [f for f in fs if f["cls"] == "DOWN"]
        pairs = []
        seen = set()
        for u in ups:
            for d in downs:
                if not scope_ok(scope, u["block"], d["block"]):
                    continue
                if key in ALIAS_CLASSES and u["ids"] and d["ids"] and not (u["ids"] & d["ids"]):
                    continue  # distinct-id exemption
                sig = (u["block"], u["snippet"], u["word"], d["block"], d["snippet"], d["word"])
                if sig in seen:
                    continue
                seen.add(sig)
                pairs.append((u, d))
        if pairs:
            flags.append({"key": key, "pairs": pairs})
    return flags


def conflicts_raw(blocks, grammar, scope):
    """n1 baseline: raw antonym co-occurrence, NO per-key attribution. A
    scope unit flags when it contains >=1 grammar key anywhere and an UP
    token and a DOWN token (same block for s1; opposite blocks -- at least
    one of the two key-bearing -- for s3; union for s2)."""
    per_block = {}
    for line_no, label, text in blocks:
        per_block[line_no] = {
            "keys": bool(keys_in(text, grammar)),
            "up": bool(UP_RE.search(text)),
            "down": bool(DOWN_RE.search(text)),
        }
    units = []
    if scope in ("s1-same-line", "s2-whole-file"):
        for b, info in sorted(per_block.items()):
            if info["keys"] and info["up"] and info["down"]:
                units.append((b, b))
    if scope in ("s3-cross-block", "s2-whole-file"):
        bs = sorted(per_block)
        for i, a in enumerate(bs):
            for b in bs[i + 1:]:
                ia, ib = per_block[a], per_block[b]
                if not (ia["keys"] or ib["keys"]):
                    continue
                if (ia["up"] and ib["down"]) or (ia["down"] and ib["up"]):
                    units.append((a, b))
    return units


# ------------------------------------------------------------- pair labeling
def label_pair(key, up, down, patterns):
    """Classify a flagged pair against the committed archetype table.
    FP archetypes take precedence: a pair whose UP (or DOWN) side is a named
    non-disposition artifact is not evidence, whatever the other side says."""
    for pat in patterns["fp_up_prefixes"]:
        if up["snippet"].startswith(pat):
            return "FP:" + pat[:32]
    for pat in patterns["fp_down_substrings"]:
        if pat in down["snippet"]:
            return "FP:" + pat[:32]
    if CARRY_MARK in down["snippet"]:
        return "TRUE:carry-vs-live"
    for pat in patterns["true_up_prefixes"]:
        if up["snippet"].startswith(pat):
            return "TRUE:" + pat[:32]
    return "UNLABELED"


# ------------------------------------------------------------------- planting
PLANT_UP_TEXT = "STILL ENABLED and LEFT ARMED as the dead-man bridge"
PLANT_DOWN_TEXT = "is being DISMANTLED with the archive handoff"
ALIAS_PHRASE = {"FAILSAFE": "the failsafe cron trigger",
                "PACEMAKER": "the send_later pacemaker chain"}


def build_plants(revs, base_shorts):
    """Enumerated (not random) plants, using the FIXED reference extraction
    config (grammar g3, norm n2): P1 flips the first trig-id-keyed
    disposition statement via an EXPLICIT-ID sentence appended to the last
    line; P2 does the same via an ALIAS-ONLY sentence (the real specimen's
    shape: no shared id token)."""
    plants = []
    for short in base_shorts:
        blocks, statements = revs[short]
        facts = extract_facts(statements, "g3-id+alias", "n2-class+attrib")
        p1 = next((f for f in facts if f["key"].startswith("trig_")), None)
        p2 = next((f for f in facts if f["key"] in ALIAS_CLASSES), None)
        if p1 is not None:
            flip = PLANT_DOWN_TEXT if p1["cls"] == "UP" else PLANT_UP_TEXT
            sentence = " PLANT-P1: %s %s." % (p1["key"], flip)
            plants.append(make_plant(short, "P1", p1["key"], blocks, sentence))
        if p2 is not None:
            flip = PLANT_DOWN_TEXT if p2["cls"] == "UP" else PLANT_UP_TEXT
            sentence = " PLANT-P2: %s %s." % (ALIAS_PHRASE[p2["key"]], flip)
            plants.append(make_plant(short, "P2", p2["key"], blocks, sentence))
    return plants


def make_plant(short, kind, key, blocks, sentence):
    new_blocks = [(n, l, t) for (n, l, t) in blocks]
    n, l, t = new_blocks[-1]
    new_blocks[-1] = (n, l, t + sentence)
    return {
        "id": "%s-%s" % (short, kind), "base": short, "kind": kind,
        "key": key, "plant_block": n,
        "blocks": new_blocks,
        "statements": split_statements(new_blocks),
    }


def plant_caught(plant, grammar, norm, scope):
    blocks, statements = plant["blocks"], plant["statements"]
    if norm == "n1-raw-cooccur":
        units = conflicts_raw(blocks, grammar, scope)
        return any(plant["plant_block"] in u for u in units)
    facts = extract_facts(statements, grammar, norm)
    flags = conflicts_attrib(facts, scope)
    for fl in flags:
        if fl["key"] != plant["key"]:
            continue
        for u, d in fl["pairs"]:
            if plant["plant_block"] in (u["block"], d["block"]):
                return True
    return False


# ----------------------------------------------------------------------- main
def main():
    with open(LABELS_PATH) as f:
        labels = json.load(f)
    manifest = labels["corpus_manifest"]
    patterns = labels["pair_label_patterns"]
    ground_truth = labels["ground_truth_contradictions"]

    # corpus integrity
    check("manifest lists 23 revisions", len(manifest) == 23)
    files = sorted(x for x in os.listdir(CORPUS_DIR) if x.endswith(".md"))
    check("corpus dir has 23 fixture files", len(files) == 23)
    revs, order = {}, []
    for entry in manifest:
        path = os.path.join(CORPUS_DIR, entry["fixture"])
        check("fixture exists: %s" % entry["fixture"], os.path.exists(path))
        check("fixture sha256 matches pin: %s" % entry["fixture"],
              sha256_file(path) == entry["sha256"])
        with open(path, encoding="utf-8") as f:
            content = f.read()
        blocks = parse_blocks(content)
        revs[entry["short"]] = (blocks, split_statements(blocks))
        order.append(entry["short"])
    check("specimen in corpus", SPECIMEN_SHORT in revs)
    check("hard-FP revision in corpus", HARD_FP_SHORT in revs)
    check("endpoints in corpus (inclusive count reconciliation)",
          order[0] == "fc0bab6" and order[-1] == "0cfe15e")

    # specimen ground truth (byte-pinned in the proposal)
    sp_blocks = revs[SPECIMEN_SHORT][0]
    l3, l9 = sp_blocks[2][2], sp_blocks[8][2]
    check("c77563c line 3 has the trig id", SPECIMEN_TRIG in l3)
    check("c77563c line 3 says STILL ENABLED and LEFT ARMED",
          "STILL ENABLED and LEFT ARMED" in l3)
    check("c77563c line 9 says being DISMANTLED", "being DISMANTLED" in l9)
    check("c77563c line 9 does NOT carry the trig id (grammar axis is load-bearing)",
          SPECIMEN_TRIG not in l9)
    check("c77563c line 9 names the failsafe by noun phrase", "failsafe cron trigger" in l9)

    # hard-FP ground truth
    fp_blocks = revs[HARD_FP_SHORT][0]
    f3, f9 = fp_blocks[2][2], fp_blocks[8][2]
    check("e66c78a line 9 quotes the negated carry",
          'must re-arm both / being dismantled' in f9)
    check("e66c78a line 9 marks it DROPPED as superseded", "DROPPED as superseded" in f9)
    ids_f3 = set(TRIG_RE.findall(f3))
    check("e66c78a line 3 carries >=2 distinct trig ids (NEW enabled / OLD deleted)",
          len(ids_f3) >= 2 and SPECIMEN_TRIG in ids_f3)
    check("e66c78a line 3 says DELETED about the old failsafe", "DELETED" in f3)

    # headline corpus finding, verified mechanically against ground truth
    carry_revs = [s for s in order if any(CARRY_MARK in b[2] for b in revs[s][0])]
    check("the carried DISMANTLED paragraph is present in exactly the 21 "
          "session-1-era revisions", carry_revs == order[:21])
    check("e66c78a and 0cfe15e do NOT carry the paragraph",
          HARD_FP_SHORT not in carry_revs and "0cfe15e" not in carry_revs)
    gt_instances = set()
    for g in ground_truth:
        gt_instances.add((g["rev"], g["entity"]))
        check("ground truth %s/%s: carry present" % (g["rev"], g["entity"]),
              g["rev"] in carry_revs)
        blocks_g = revs[g["rev"]][0]
        check("ground truth %s/%s: quoted up-evidence present verbatim" %
              (g["rev"], g["entity"]),
              any(g["up_evidence"] in b[2] for b in blocks_g))
    check("ground truth = 30 instances (21 FAILSAFE + 9 PACEMAKER)",
          len(gt_instances) == 30
          and sum(1 for r, e in gt_instances if e == "FAILSAFE") == 21
          and sum(1 for r, e in gt_instances if e == "PACEMAKER") == 9)

    # vocabulary sanity
    check("UP/DOWN vocab disjoint", not set(UP_WORDS) & set(DOWN_WORDS))
    check("'self-disabled' scans as DOWN not UP",
          dispositions_in("self-disabled")[0][0] == "DOWN"
          and not UP_RE.search("self-disabled"))
    check("'ACTIVE-IDLE' scans as no disposition", not dispositions_in("ACTIVE-IDLE"))

    plants = build_plants(revs, [s for s in order if s != SPECIMEN_SHORT])
    p1s = [p for p in plants if p["kind"] == "P1"]
    p2s = [p for p in plants if p["kind"] == "P2"]
    check("plants are deterministic and non-empty", len(p1s) > 0 and len(p2s) > 0)
    for p in plants:
        check("plant %s appended to last block" % p["id"],
              "PLANT-" in p["blocks"][-1][2])

    # ------------------------------------------------------------- the sweep
    cells = []
    for grammar in GRAMMARS:
        for norm in NORMS:
            for scope in SCOPES:
                if norm == "n1-raw-cooccur":
                    caught_specimen = False
                    unit_count = 0
                    e_flagged = False
                    rev_units = {}
                    for short in order:
                        units = conflicts_raw(revs[short][0], grammar, scope)
                        rev_units[short] = len(units)
                        unit_count += len(units)
                        if short == HARD_FP_SHORT and units:
                            e_flagged = True
                        if short == SPECIMEN_SHORT and (3, 9) in units:
                            caught_specimen = True
                    p1_caught = sum(1 for p in p1s if plant_caught(p, grammar, norm, scope))
                    p2_caught = sum(1 for p in p2s if plant_caught(p, grammar, norm, scope))
                    cells.append({
                        "grammar": grammar, "norm": norm, "scope": scope,
                        "specimen_caught": caught_specimen,
                        "tc_instances": None,  # n1 has no key attribution
                        "fp_flags": None,
                        "raw_units": unit_count,
                        "raw_unit_revisions": sum(1 for v in rev_units.values() if v),
                        "e66c78a_flagged": e_flagged,
                        "p1_recall": round(p1_caught / len(p1s), 4),
                        "p2_recall": round(p2_caught / len(p2s), 4),
                        "p1_caught": p1_caught, "p2_caught": p2_caught,
                        "misses": None, "fp_list": None,
                        "true_pairs": None, "fp_pairs": None, "unlabeled_pairs": 0,
                    })
                    continue

                caught = set()          # (rev, entity) true catches
                fp_flag_list = []       # flags with zero TRUE pairs
                true_pairs = fp_pairs = unlabeled = 0
                caught_specimen = False
                e_flagged = False
                for short in order:
                    facts = extract_facts(revs[short][1], grammar, norm)
                    flags = conflicts_attrib(facts, scope)
                    for fl in flags:
                        flag_true = False
                        for u, d in fl["pairs"]:
                            lab = label_pair(fl["key"], u, d, patterns)
                            if lab == "UNLABELED":
                                unlabeled += 1
                                print("UNLABELED PAIR: %s %s | UP L%d %r %s | DOWN L%d %r %s"
                                      % (short, fl["key"], u["block"], u["word"],
                                         u["snippet"][:80], d["block"], d["word"],
                                         d["snippet"][:80]))
                            elif lab.startswith("TRUE"):
                                true_pairs += 1
                                flag_true = True
                                if fl["key"] in ALIAS_CLASSES:
                                    caught.add((short, fl["key"]))
                                if (short == SPECIMEN_SHORT
                                        and fl["key"] in ("FAILSAFE", SPECIMEN_TRIG)
                                        and (u["block"], d["block"]) == (3, 9)):
                                    caught_specimen = True
                            else:
                                fp_pairs += 1
                        if not flag_true:
                            blocks_hit = sorted(set(
                                b for u, d in fl["pairs"] for b in (u["block"], d["block"])))
                            fp_flag_list.append({"rev": short, "key": fl["key"],
                                                 "lines": blocks_hit,
                                                 "n_pairs": len(fl["pairs"])})
                            if short == HARD_FP_SHORT:
                                e_flagged = True
                p1_caught = sum(1 for p in p1s if plant_caught(p, grammar, norm, scope))
                p2_caught = sum(1 for p in p2s if plant_caught(p, grammar, norm, scope))
                misses = sorted(gt_instances - caught)
                cells.append({
                    "grammar": grammar, "norm": norm, "scope": scope,
                    "specimen_caught": caught_specimen,
                    "tc_instances": len(caught & gt_instances),
                    "fp_flags": len(fp_flag_list),
                    "raw_units": None, "raw_unit_revisions": None,
                    "e66c78a_flagged": e_flagged,
                    "p1_recall": round(p1_caught / len(p1s), 4),
                    "p2_recall": round(p2_caught / len(p2s), 4),
                    "p1_caught": p1_caught, "p2_caught": p2_caught,
                    "misses": ["%s/%s" % m for m in misses],
                    "fp_list": fp_flag_list[:40],
                    "true_pairs": true_pairs, "fp_pairs": fp_pairs,
                    "unlabeled_pairs": unlabeled,
                })

    check("no unlabeled pairs anywhere in the sweep",
          all(c["unlabeled_pairs"] == 0 for c in cells))

    # ------------------------------------------------------- winner selection
    def cell(g, n, s):
        return next(c for c in cells
                    if c["grammar"] == g and c["norm"] == n and c["scope"] == s)

    attributed = [c for c in cells if c["norm"] != "n1-raw-cooccur"]
    eligible = [c for c in attributed
                if c["specimen_caught"] and not c["e66c78a_flagged"]]
    def sortkey(c):
        return (-c["tc_instances"], c["fp_flags"], c["fp_pairs"],
                -(c["p1_caught"] + c["p2_caught"]),
                GRAMMARS.index(c["grammar"]), NORMS.index(c["norm"]),
                SCOPES.index(c["scope"]))
    winner = sorted(eligible, key=sortkey)[0] if eligible else None
    co_winners = []
    if winner:
        co_winners = [c for c in eligible if
                      (c["tc_instances"], c["fp_flags"], c["fp_pairs"],
                       c["p1_caught"], c["p2_caught"]) ==
                      (winner["tc_instances"], winner["fp_flags"], winner["fp_pairs"],
                       winner["p1_caught"], winner["p2_caught"])]

    # ------------------------------------------------- hand-derived assertions
    # 1. id-only grammar can NEVER catch a real instance (the carry side of
    #    every real contradiction is keyless prose -- no shared id token):
    for n in NORMS[1:]:
        for s in SCOPES:
            c = cell("g1-trig-id", n, s)
            check("g1 %s %s catches nothing real (no shared id token)" % (n, s),
                  c["tc_instances"] == 0 and not c["specimen_caught"])
            check("g2 %s %s catches nothing real (PR keys add nothing)" % (n, s),
                  cell("g2-id+pr", n, s)["tc_instances"] == 0)
    # 2. same-line scope misses the cross-block disease in attributed cells:
    for g in GRAMMARS:
        for n in NORMS[1:]:
            check("%s %s s1 misses the cross-line specimen" % (g, n),
                  not cell(g, n, "s1-same-line")["specimen_caught"])
    # 3. the alias grammar with attribution catches the specimen cross-block:
    check("g3/n2/s3 catches the specimen",
          cell("g3-id+alias", "n2-class+attrib", "s3-cross-block")["specimen_caught"])
    check("g3/n3/s3 catches the specimen",
          cell("g3-id+alias", "n3-attrib+quote-excl", "s3-cross-block")["specimen_caught"])
    # 4. alias-only plants (P2) are invisible to id-only grammars:
    for n in NORMS[1:]:
        for s in SCOPES:
            check("g1 %s %s P2 recall is 0" % (n, s),
                  cell("g1-trig-id", n, s)["p2_caught"] == 0)
    # 5. whole-file dominates cross-block on catches per cell:
    for g in GRAMMARS:
        for n in NORMS[1:]:
            c2, c3 = cell(g, n, "s2-whole-file"), cell(g, n, "s3-cross-block")
            check("%s %s: s2 tc >= s3 tc" % (g, n),
                  c2["tc_instances"] >= c3["tc_instances"])
    # 6. the naive baseline flags the e66c78a fix itself (the writeup's
    #    "a naive co-occurrence check flags the fix itself"):
    check("naive n1 whole-file flags e66c78a (any grammar)",
          any(cell(g, "n1-raw-cooccur", "s2-whole-file")["e66c78a_flagged"]
              for g in GRAMMARS))
    # 7. plants never mutate base fixtures:
    for entry in manifest:
        path = os.path.join(CORPUS_DIR, entry["fixture"])
        check("fixture unchanged after sweep: %s" % entry["fixture"],
              sha256_file(path) == entry["sha256"])

    results = {
        "sim": "verdict-015-heartbeat-contradiction-linter",
        "corpus": {"revisions": 23, "carry_revisions": len(carry_revs),
                   "specimen": SPECIMEN_SHORT, "hard_fp": HARD_FP_SHORT,
                   "ground_truth_instances": len(gt_instances),
                   "count_reconciliation":
                       "proposal '22' = git-exclusive fc0bab6..0cfe15e; "
                       "endpoint-inclusive corpus committed here = 23"},
        "plants": {"p1_total": len(p1s), "p2_total": len(p2s),
                   "p1_bases": [p["base"] for p in p1s],
                   "p2_bases": [p["base"] for p in p2s]},
        "grid": {"grammars": GRAMMARS, "norms": NORMS, "scopes": SCOPES,
                 "cells": len(cells)},
        "cells": cells,
        "winner": ({k: winner[k] for k in
                    ("grammar", "norm", "scope", "specimen_caught",
                     "tc_instances", "fp_flags", "fp_pairs", "e66c78a_flagged",
                     "p1_recall", "p2_recall", "misses")} if winner else None),
        "co_winners": [{k: c[k] for k in ("grammar", "norm", "scope")}
                       for c in co_winners],
        "self_checks": None,
    }

    # ------------------------------------------------------------ determinism
    cells_recheck = []
    for grammar in GRAMMARS:
        for norm in NORMS[1:]:
            for scope in SCOPES:
                tot = 0
                for short in order:
                    facts = extract_facts(revs[short][1], grammar, norm)
                    tot += sum(len(fl["pairs"]) for fl in conflicts_attrib(facts, scope))
                cells_recheck.append((grammar, norm, scope, tot))
    firstpass = [(c["grammar"], c["norm"], c["scope"],
                  c["true_pairs"] + c["fp_pairs"])
                 for c in cells if c["norm"] != "n1-raw-cooccur"]
    check("in-process double computation agrees on every attributed cell",
          firstpass == cells_recheck)

    results["self_checks"] = dict(CHECKS)

    # ---------------------------------------------------------------- printout
    print("verdict-015 heartbeat-contradiction-linter sweep")
    print("corpus: 23 revisions fc0bab6->0cfe15e inclusive; carried DISMANTLED")
    print("paragraph in %d revisions; ground truth = %d real (rev x entity)"
          % (len(carry_revs), len(gt_instances)))
    print("intra-file contradictions (hand-audited, labels.json) -- the")
    print("proposal's 'one known live contradiction' premise is UNDERCOUNTED x30")
    print("plants: P1(id-keyed) n=%d, P2(alias-only, specimen-shaped) n=%d" %
          (len(p1s), len(p2s)))
    print()
    hdr = "%-14s %-22s %-15s %5s %6s %5s %7s %7s %7s %5s" % (
        "grammar", "norm", "scope", "spec", "TCin", "FPfl", "FPpair", "P1rec", "P2rec", "e66?")
    print(hdr)
    print("-" * len(hdr))
    for c in cells:
        tc = "-" if c["tc_instances"] is None else "%d/30" % c["tc_instances"]
        fpf = ("u%d" % c["raw_units"]) if c["fp_flags"] is None else str(c["fp_flags"])
        fpp = "-" if c["fp_pairs"] is None else str(c["fp_pairs"])
        print("%-14s %-22s %-15s %5s %6s %5s %7s %7.2f %7.2f %5s" % (
            c["grammar"], c["norm"], c["scope"],
            "Y" if c["specimen_caught"] else "n", tc, fpf, fpp,
            c["p1_recall"], c["p2_recall"],
            "YES" if c["e66c78a_flagged"] else "no"))
    print()
    if winner:
        print("WINNER: %s x %s x %s -- specimen CAUGHT, real-TC %d/30 instances,"
              % (winner["grammar"], winner["norm"], winner["scope"],
                 winner["tc_instances"]))
        print("  FP flags %d, FP pairs %d, e66c78a flagged: %s, planted recall "
              "P1 %.2f (%d/%d) P2 %.2f (%d/%d), misses: %s"
              % (winner["fp_flags"], winner["fp_pairs"],
                 "YES" if winner["e66c78a_flagged"] else "no",
                 winner["p1_recall"], winner["p1_caught"], len(p1s),
                 winner["p2_recall"], winner["p2_caught"], len(p2s),
                 winner["misses"] or "none"))
        if len(co_winners) > 1:
            print("  co-winners (identical scores): %s" %
                  "; ".join("%s x %s x %s" % (c["grammar"], c["norm"], c["scope"])
                            for c in co_winners))
    else:
        print("NO CELL catches the specimen without flagging e66c78a")

    with open(RESULTS_PATH, "w") as f:
        json.dump(results, f, indent=1, sort_keys=True, default=sorted)
        f.write("\n")

    print()
    print("SELF-CHECKS: %d passed, %d failed" % (CHECKS["passed"], CHECKS["failed"]))
    return 1 if CHECKS["failed"] else 0


if __name__ == "__main__":
    sys.exit(main())
