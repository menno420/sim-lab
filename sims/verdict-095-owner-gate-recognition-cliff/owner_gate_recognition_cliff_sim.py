#!/usr/bin/env python3
"""VERDICT 095 sim — owner-gate parser recognition cliff (idea-engine PROPOSAL 082).

Three-arm, hermetic, stdlib-only, pre-registered (fixtures.json committed
BEFORE this runner):

  Arm A — regex-faithful replay of the five pinned source behaviors
          ((i) recognition: text.lstrip().startswith('⚑') and '**Owner:**'
          in text; (ii) row shape ^- \\[[ xX]\\]\\s+; (iii) the fold rule
          with its closure/invisibility clauses; (iv) case-sensitive
          checked-only DONE disposition with both-marks lint; (v) gate
          section + once-live checkpoint arming), plus the strict lint
          (every error class conditioned on recognition) and the
          conservation-lint repair arm. Seedless, DECISION-bearing.
  Arm B — INDEPENDENTLY-WRITTEN character-level twin: no row regexes —
          per-character line classification plus an explicit index fold
          walk over parallel state/text lists. Tied to Arm A through the
          typed must-equal contacts C1-C4.
  Arm R — seeded random cells, REPORTING-ONLY (no statistical gate): per
          trace EXACTLY 3 rng.randint draws in registered order (corpus in
          [0,2], grid cell in [1,26], salt in [1,1000] drawn-and-logged),
          one random.Random per seed. Seeds 20261722 (N = 20,000) /
          20261723 (N = 8,000) with registered preview censuses and
          class-stream digests; presentation shuffle 20261724
          (presentation leg only); aux 20261725 reserved and NEVER read.

Decision rule (registered order, twin independently-written evaluators over
an ENUMERATED boolean input set): REJECT -> INVALID -> APPROVE -> NULL,
REJECT evaluated FIRST.

Deterministic: no wall clock, no absolute paths, no network, no git at run
time; stdout and results.json are byte-identical across process runs.
CPython 3.11 pinned and asserted (Arms A/B are seedless exact parsing and
integer counting, platform-independent; only reporting-only Arm R and the
presentation shuffle touch the pinned minor's random module).
"""

import hashlib
import json
import os
import random
import re
import sys

sys.dont_write_bytecode = True

HERE = os.path.dirname(os.path.abspath(__file__))

with open(os.path.join(HERE, "fixtures.json"), "r", encoding="utf-8") as fh:
    FIX = json.load(fh)

FLAG = "⚑"    # ⚑
TIMER = "⏲"   # ⏲

C0 = list(FIX["corpus"]["C0"])
C1 = C0[:17] + C0[18:]                      # C0 minus line 18 (the DONE row)
C2 = list(C0)
C2[4] = ("1. " + FLAG + " Package the zip and stage the listing draft — "
         "**stage first** (default).")
CORPORA = (C0, C1, C2)
CORPUS_NAMES = ("C0", "C1", "C2")

CHECKS = []          # (name, ok, detail)
RESULTS = {}         # measured values -> results.json
SEEDS_CONSTRUCTED = []


def check(name, ok, detail):
    CHECKS.append((name, bool(ok), str(detail)))
    print("  [%s] %s: %s" % ("PASS" if ok else "FAIL", name, detail))


def make_rng(seed):
    SEEDS_CONSTRUCTED.append(seed)
    return random.Random(seed)


# ---------------------------------------------------------------------------
# Arm A — regex-faithful replay of the five pinned behaviors (DECISION-bearing)
# ---------------------------------------------------------------------------

ROW_RE = re.compile(r"^- \[([ xX])\]\s+(.*)$")
DONE_RE = re.compile(r"[—–-]\s*DONE\s+(\d{4})-(\d{2})-(\d{2})")
KILL_RE = re.compile(r"^KILL-CHECK:\s*(.*)$")
GATE_RE = re.compile(r"^##\s.*OWNER-GATE", re.IGNORECASE)
STEP_RE = re.compile(r"^(\d+)\.\s+(.*)$")
H1_RE = re.compile(r"^# \S")
H2_RE = re.compile(r"^##\s")


def parse_a(lines):
    """Faithful replay. Returns the full observable dict (plus explicit
    merged/vanished row accounting for the F1 conservation identity)."""
    obs = {"steps": 0, "decisions": 0, "decisions_no_default": 0,
           "pending": 0, "done": 0, "non_owner": 0, "parsed": 0, "armed": 0,
           "blocked": False, "manual": 0, "lint": 0,
           "pending_texts": [], "done_dates": [],
           "merged_rows": 0, "vanished_rows": 0, "row_heads": 0}
    lint = 0
    manual = 0
    if not any(H1_RE.match(ln) for ln in lines):
        lint += 1
        manual = 1
    start = None
    for i, ln in enumerate(lines):
        if GATE_RE.match(ln):
            start = i
            break
    if start is None:
        obs["lint"] = lint + 1          # no-gate-section
        obs["manual"] = 1
        return obs
    end = len(lines)
    for j in range(start + 1, len(lines)):
        if H2_RE.match(lines[j]):
            end = j
            break
    body = lines[start + 1:end]

    items = []                          # {"state","text"} dicts, fold-closed
    open_item = None
    kills = []
    steps = []
    for ln in body:
        m = ROW_RE.match(ln)
        if m:
            open_item = {"state": m.group(1), "text": m.group(2)}
            items.append(open_item)
            continue
        if ln[:1] in (" ", "\t") and ln.strip():
            # indented non-empty: folds into the OPEN item; else invisible
            if ROW_RE.match(ln.lstrip()):
                if open_item is not None:
                    obs["merged_rows"] += 1
                else:
                    obs["vanished_rows"] += 1
            if open_item is not None:
                open_item["text"] += " " + ln.strip()
            continue
        open_item = None                # flush-left non-matching: closes
        km = KILL_RE.match(ln)
        if km:
            kills.append(km.group(1))
            continue
        sm = STEP_RE.match(ln)
        if sm:
            steps.append(sm.group(2))
            continue

    obs["row_heads"] = len(items) + obs["merged_rows"] + obs["vanished_rows"]
    obs["steps"] = len(steps)
    for st in steps:
        if st.lstrip().startswith(FLAG):
            obs["decisions"] += 1
            if "(default" not in st:
                obs["decisions_no_default"] += 1
                lint += 1               # defaultless flagged decision
    for it in items:
        text = it["text"]
        owner = text.lstrip().startswith(FLAG) and "**Owner:**" in text
        if not owner:
            obs["non_owner"] += 1
            continue
        checked = it["state"] in "xX"
        dm = DONE_RE.search(text)
        if checked and dm:
            obs["done"] += 1
            obs["done_dates"].append("-".join(dm.groups()))
            _y, mo, dy = (int(g) for g in dm.groups())
            if not (1 <= mo <= 12 and 1 <= dy <= 31):
                lint += 1               # invalid DONE date
        else:
            obs["pending"] += 1
            obs["pending_texts"].append(text)
            if checked or dm:
                lint += 1               # half-flip (either direction)
    if not items:
        lint += 1                       # no-rows
        manual = 1
    for payload in kills:
        n = payload.count(TIMER)
        if n == 0:
            lint += 1                   # malformed KILL-CHECK payload
        obs["parsed"] += n
    obs["armed"] = obs["parsed"] if obs["done"] >= 1 else 0
    obs["blocked"] = any("(blocking)" in t for t in obs["pending_texts"])
    obs["lint"] = lint
    obs["manual"] = manual
    return obs


# ---------------------------------------------------------------------------
# Arm B — INDEPENDENTLY-WRITTEN character-level twin (no row regexes;
# explicit index fold walk over parallel lists)
# ---------------------------------------------------------------------------

_WS = " \t\n\r\f\v"


def _b_is_ws(ch):
    return ch in _WS


def _b_h1(ln):
    return len(ln) >= 3 and ln[0] == "#" and ln[1] == " " and not _b_is_ws(ln[2])


def _b_h2(ln):
    return len(ln) >= 3 and ln[0] == "#" and ln[1] == "#" and _b_is_ws(ln[2])


def _b_gate_heading(ln):
    return _b_h2(ln) and "OWNER-GATE" in ln.upper()


def _b_row(ln):
    """Character-level row-shape test. Returns (state, text) or None."""
    if len(ln) < 6:
        return None
    if ln[0] != "-" or ln[1] != " " or ln[2] != "[":
        return None
    if ln[3] not in (" ", "x", "X"):
        return None
    if ln[4] != "]":
        return None
    if not _b_is_ws(ln[5]):
        return None
    i = 5
    while i < len(ln) and _b_is_ws(ln[i]):
        i += 1
    return (ln[3], ln[i:])


def _b_step(ln):
    """Character-level numbered-step test. Returns step text or None."""
    i = 0
    while i < len(ln) and "0" <= ln[i] <= "9":
        i += 1
    if i == 0 or i >= len(ln) or ln[i] != ".":
        return None
    j = i + 1
    if j >= len(ln) or not _b_is_ws(ln[j]):
        return None
    while j < len(ln) and _b_is_ws(ln[j]):
        j += 1
    return ln[j:]


def _b_kill(ln):
    """Character-level KILL-CHECK head test. Returns payload or None."""
    head = "KILL-CHECK:"
    if len(ln) < len(head) or ln[:len(head)] != head:
        return None
    i = len(head)
    while i < len(ln) and _b_is_ws(ln[i]):
        i += 1
    return ln[i:]


def _b_indented_nonempty(ln):
    if not ln or not _b_is_ws(ln[0]):
        return False
    for ch in ln:
        if not _b_is_ws(ch):
            return True
    return False


def _b_strip(s):
    a = 0
    b = len(s)
    while a < b and _b_is_ws(s[a]):
        a += 1
    while b > a and _b_is_ws(s[b - 1]):
        b -= 1
    return s[a:b]


def _b_lstrip(s):
    a = 0
    while a < len(s) and _b_is_ws(s[a]):
        a += 1
    return s[a:]


def _b_done_scan(text):
    """Character-level DONE-disposition scan mirroring the pinned regex
    semantics: dash char, optional ws, literal DONE, >=1 ws, dddd-dd-dd.
    Returns (yyyy, mm, dd) strings or None. First match wins."""
    dashes = ("—", "–", "-")
    n = len(text)
    for i in range(n):
        if text[i] not in dashes:
            continue
        j = i + 1
        while j < n and _b_is_ws(text[j]):
            j += 1
        if text[j:j + 4] != "DONE":
            continue
        j += 4
        k = j
        while k < n and _b_is_ws(text[k]):
            k += 1
        if k == j:
            continue
        # dddd-dd-dd
        seg = text[k:k + 10]
        if len(seg) < 10:
            continue
        ok = all("0" <= seg[p] <= "9" for p in (0, 1, 2, 3, 5, 6, 8, 9))
        if ok and seg[4] == "-" and seg[7] == "-":
            return (seg[0:4], seg[5:7], seg[8:10])
    return None


def parse_b(lines):
    """Independently-written twin. Same observable dict, different shape:
    parallel lists + explicit index fold walk, zero row regexes."""
    obs = {"steps": 0, "decisions": 0, "decisions_no_default": 0,
           "pending": 0, "done": 0, "non_owner": 0, "parsed": 0, "armed": 0,
           "blocked": False, "manual": 0, "lint": 0,
           "pending_texts": [], "done_dates": [],
           "merged_rows": 0, "vanished_rows": 0, "row_heads": 0}
    lint = 0
    manual = 0
    h1_seen = False
    for ln in lines:
        if _b_h1(ln):
            h1_seen = True
            break
    if not h1_seen:
        lint += 1
        manual = 1
    gate_at = -1
    idx = 0
    while idx < len(lines):
        if _b_gate_heading(lines[idx]):
            gate_at = idx
            break
        idx += 1
    if gate_at < 0:
        obs["lint"] = lint + 1
        obs["manual"] = 1
        return obs
    stop = len(lines)
    idx = gate_at + 1
    while idx < len(lines):
        if _b_h2(lines[idx]):
            stop = idx
            break
        idx += 1

    states = []      # parallel lists — differently shaped from Arm A's dicts
    texts = []
    open_idx = -1
    kill_payloads = []
    step_texts = []
    i = gate_at + 1
    while i < stop:                      # explicit index fold walk
        ln = lines[i]
        row = _b_row(ln)
        if row is not None:
            states.append(row[0])
            texts.append(row[1])
            open_idx = len(texts) - 1
            i += 1
            continue
        if _b_indented_nonempty(ln):
            if _b_row(_b_lstrip(ln)) is not None:
                if open_idx >= 0:
                    obs["merged_rows"] += 1
                else:
                    obs["vanished_rows"] += 1
            if open_idx >= 0:
                texts[open_idx] = texts[open_idx] + " " + _b_strip(ln)
            i += 1
            continue
        open_idx = -1
        kp = _b_kill(ln)
        if kp is not None:
            kill_payloads.append(kp)
            i += 1
            continue
        st = _b_step(ln)
        if st is not None:
            step_texts.append(st)
        i += 1

    obs["row_heads"] = len(texts) + obs["merged_rows"] + obs["vanished_rows"]
    obs["steps"] = len(step_texts)
    for st in step_texts:
        stripped = _b_lstrip(st)
        if stripped[:1] == FLAG:
            obs["decisions"] += 1
            if "(default" not in st:
                obs["decisions_no_default"] += 1
                lint += 1
    for pos in range(len(texts)):
        text = texts[pos]
        owner = _b_lstrip(text)[:1] == FLAG and "**Owner:**" in text
        if not owner:
            obs["non_owner"] += 1
            continue
        checked = states[pos] in ("x", "X")
        dm = _b_done_scan(text)
        if checked and dm is not None:
            obs["done"] += 1
            obs["done_dates"].append(dm[0] + "-" + dm[1] + "-" + dm[2])
            mo = int(dm[1])
            dy = int(dm[2])
            if mo < 1 or mo > 12 or dy < 1 or dy > 31:
                lint += 1
        else:
            obs["pending"] += 1
            obs["pending_texts"].append(text)
            if checked or dm is not None:
                lint += 1
    if not texts:
        lint += 1
        manual = 1
    for kp in kill_payloads:
        cnt = 0
        for ch in kp:
            if ch == TIMER:
                cnt += 1
        if cnt == 0:
            lint += 1
        obs["parsed"] += cnt
    obs["armed"] = obs["parsed"] if obs["done"] >= 1 else 0
    blocked = False
    for t in obs["pending_texts"]:
        if "(blocking)" in t:
            blocked = True
    obs["blocked"] = blocked
    obs["lint"] = lint
    obs["manual"] = manual
    return obs


def obs_tuple(o):
    return (o["steps"], o["decisions"], o["decisions_no_default"],
            o["pending"], o["done"], o["non_owner"], o["parsed"], o["armed"],
            o["blocked"], o["manual"], o["lint"],
            tuple(o["pending_texts"]), tuple(o["done_dates"]))


def key_tuple(o):
    return [o["pending"], o["done"], o["armed"], o["lint"]]


# ---------------------------------------------------------------------------
# The registered 26-cell grid (operators x named targets, C0 line numbers)
# ---------------------------------------------------------------------------

def _sub1(old, new):
    def fn(line):
        return line.replace(old, new, 1)
    return fn


TARGETS = FIX["corpus"]["row_targets_C0_lines"]
OPS = {}
_cell = 1
for _rk in ("r1", "r2", "r3", "r4", "r5"):
    OPS[_cell] = ("OP1@" + _rk, TARGETS[_rk], _sub1("**Owner:**", "*Owner:**"))
    _cell += 1
for _rk in ("r1", "r2", "r3", "r4", "r5"):
    OPS[_cell] = ("OP2@" + _rk, TARGETS[_rk],
                  _sub1(FLAG + " **Owner:**", "**" + FLAG + " Owner:**"))
    _cell += 1
for _rk in ("r1", "r2", "r5"):
    OPS[_cell] = ("OP3@" + _rk, TARGETS[_rk], lambda ln: " " + ln)
    _cell += 1
for _rk in ("r1", "r3", "r5"):
    OPS[_cell] = ("OP4@" + _rk, TARGETS[_rk], _sub1("- [", "* ["))
    _cell += 1
OPS[17] = ("OP5@r1", TARGETS["r1"], _sub1("- [ ]", "- []"))
OPS[18] = ("OP6@step2", TARGETS["step2"], _sub1(FLAG + " ", ""))
OPS[19] = ("OP7@step2", TARGETS["step2"], _sub1(" (default)", ""))
OPS[20] = ("OP8@r1", TARGETS["r1"], _sub1("- [ ]", "- [x]"))
OPS[21] = ("OP9@r2", TARGETS["r2"], lambda ln: ln + " — DONE 2026-07-13")
OPS[22] = ("OP10@r5", TARGETS["r5"], _sub1("2026-07-13", "2026-13-13"))
OPS[23] = ("OP11@r5", TARGETS["r5"], _sub1("DONE", "done"))
OPS[24] = ("OP12@kill", TARGETS["kill"], _sub1("KILL-CHECK:", "KILL CHECK:"))
OPS[25] = ("OP13@heading", TARGETS["heading"], _sub1("##", "###"))
OPS[26] = ("OP14@cont4", TARGETS["cont4"], _sub1(" (blocking)", ""))


def mutate(lines, cellno):
    """Apply cell operator. Returns (mutated_lines_or_None, status) where
    status is 'ok' | 'INAPPLICABLE' | 'NO-EDIT'."""
    _label, lineno, fn = OPS[cellno]
    if lineno > len(lines):
        return None, "INAPPLICABLE"
    mut = list(lines)
    mut[lineno - 1] = fn(mut[lineno - 1])
    if mut == lines:
        return None, "NO-EDIT"
    return mut, "ok"


def classify(base_obs, mut_obs):
    # LOSSY: an owner row (pending+done), a decision, a DONE row, or an armed
    # checkpoint is LOST. A full valid flip that retires pending -> done is
    # disposition, not loss (the 2x2 RETIRE-LIVE cell).
    lossy = (mut_obs["pending"] + mut_obs["done"] < base_obs["pending"] + base_obs["done"]
             or mut_obs["decisions"] < base_obs["decisions"]
             or mut_obs["done"] < base_obs["done"]
             or mut_obs["armed"] < base_obs["armed"])
    alarmed = mut_obs["lint"] > 0 or mut_obs["manual"] > 0
    if lossy and not alarmed:
        return "SILENT-LOSSY"
    if lossy:
        return "ALARMED-LOSSY"
    if alarmed:
        return "ALARMED-SAFE"
    if obs_tuple(mut_obs) != obs_tuple(base_obs):
        return "SILENT-REGRADE"
    return "SILENT-IDENTICAL"           # must never occur (F5 taxonomy check)


# ---------------------------------------------------------------------------
# Repair arm — the conservation lint (a LOOSER net the deriver does not use)
# ---------------------------------------------------------------------------

def _strip_markup(s):
    out = []
    for ch in s:
        if ch not in "*_`":
            out.append(ch)
    return "".join(out).lower()


def net_counts(lines):
    owner = dec = kill = 0
    for ln in lines:
        ls = ln.lstrip()
        bulletish = (ls.startswith("- ") or ls.startswith("* ")
                     or ls.startswith("-[") or ls.startswith("*["))
        if (bulletish or FLAG in ln) and "owner:" in _strip_markup(ln):
            owner += 1
        if STEP_RE.match(ls) and "(default" in ln:
            dec += 1
        if TIMER in ln and "kill" in ln.lower():
            kill += 1
    return owner, dec, kill


def strict_counts(lines):
    o = parse_a(lines)
    start = None
    for i, ln in enumerate(lines):
        if GATE_RE.match(ln):
            start = i
            break
    kills = 0
    if start is not None:
        end = len(lines)
        for j in range(start + 1, len(lines)):
            if H2_RE.match(lines[j]):
                end = j
                break
        for ln in lines[start + 1:end]:
            if KILL_RE.match(ln):
                kills += 1
    return o["pending"] + o["done"], o["decisions"], kills


def repair_fires(lines):
    so, sd, sk = strict_counts(lines)
    no, nd, nk = net_counts(lines)
    return so < no or sd < nd or sk < nk


# ---------------------------------------------------------------------------
# Twin decision evaluators (registered order: REJECT -> INVALID -> APPROVE
# -> NULL, REJECT evaluated FIRST)
# ---------------------------------------------------------------------------

def evaluate_1(inp):
    """If-chain evaluator."""
    if inp["R1"] and inp["R2"] and inp["R3"] and inp["R4"]:
        return "REJECT"
    if not inp["gates_ok"]:
        return "INVALID"
    if inp["zero_silent"]:
        return "APPROVE"
    return "NULL"


def evaluate_2(inp):
    """Table-driven evaluator, independently written."""
    reject_score = (1 if inp["R1"] else 0) + (2 if inp["R2"] else 0) \
        + (4 if inp["R3"] else 0) + (8 if inp["R4"] else 0)
    rules = (
        ("REJECT", reject_score == 15),
        ("INVALID", inp["gates_ok"] is False),
        ("APPROVE", bool(inp["zero_silent"])),
        ("NULL", True),
    )
    for token, fires in rules:
        if fires:
            return token
    raise AssertionError("unreachable")


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------

def main():
    print("VERDICT 095 sim — owner-gate parser recognition cliff (P082)")
    print("=" * 74)

    # ---- F0: harness pins -------------------------------------------------
    pyminor = "%d.%d" % (sys.version_info[0], sys.version_info[1])
    check("F0.python-minor-pinned", pyminor == FIX["environment"]["cpython_minor_pinned"],
          "running CPython %s vs pinned %s" % (pyminor, FIX["environment"]["cpython_minor_pinned"]))
    check("F0.corpus-shape", len(C0) == 21 and len(C1) == 20 and len(C2) == 21,
          "C0 21 lines, C1 20 (line-18 deletion), C2 21")

    # ---- baselines (both arms) --------------------------------------------
    base_a = [parse_a(c) for c in CORPORA]
    base_b = [parse_b(c) for c in CORPORA]
    reg0 = FIX["anchors_F3"]["baseline_C0"]
    b0 = base_a[0]
    ok0 = (b0["steps"] == reg0["steps"] and b0["decisions"] == reg0["decisions"]
           and b0["pending"] == reg0["pending"] and b0["done"] == reg0["done"]
           and b0["non_owner"] == reg0["non_owner"]
           and b0["parsed"] == reg0["checkpoints_parsed"]
           and b0["armed"] == reg0["checkpoints_armed"]
           and b0["blocked"] is reg0["blocked"]
           and b0["lint"] == reg0["lint"] and b0["manual"] == reg0["manual"])
    check("F1.baseline-C0-echo", ok0,
          "steps %d decisions %d pending %d done %d non-owner %d parsed %d "
          "armed %d blocked %s lint %d manual %d" % (
              b0["steps"], b0["decisions"], b0["pending"], b0["done"],
              b0["non_owner"], b0["parsed"], b0["armed"], b0["blocked"],
              b0["lint"], b0["manual"]))
    b1 = base_a[1]
    check("F1.baseline-C1-echo",
          (b1["parsed"], b1["armed"], b1["pending"], b1["done"], b1["lint"]) == (2, 0, 4, 0, 0),
          "once-live pair (parsed %d, armed %d), pending %d done %d lint %d"
          % (b1["parsed"], b1["armed"], b1["pending"], b1["done"], b1["lint"]))
    b2 = base_a[2]
    check("F1.baseline-C2-echo",
          (b2["decisions"], b2["lint"], b2["pending"], b2["done"], b2["armed"]) == (2, 0, 4, 1, 2),
          "two decisions lint-clean (decisions %d lint %d), rest unchanged"
          % (b2["decisions"], b2["lint"]))
    check("F1.conservation-C0",
          b0["pending"] + b0["done"] + b0["non_owner"] == 6 and b0["row_heads"] == 6,
          "pending+done+non-owner = %d == 6 checkbox rows"
          % (b0["pending"] + b0["done"] + b0["non_owner"]))

    # ---- the 26-cell grid on C0 (twin-verified cell-by-cell) ---------------
    grid = {}            # label -> {"class","tuple","obs"}
    cls_counts = {}
    silent_list = []
    real_edit_all = True
    conservation_ok = True
    twin_cells_ok = True
    for k in range(1, 27):
        label = OPS[k][0]
        mut, status = mutate(C0, k)
        if status != "ok":
            real_edit_all = False
            continue
        ma = parse_a(mut)
        mb = parse_b(mut)
        if obs_tuple(ma) != obs_tuple(mb) or (ma["merged_rows"], ma["vanished_rows"]) \
                != (mb["merged_rows"], mb["vanished_rows"]):
            twin_cells_ok = False
        cls_a = classify(base_a[0], ma)
        cls_b = classify(base_b[0], mb)
        if cls_a != cls_b:
            twin_cells_ok = False
        grid[label] = {"class": cls_a, "tuple": key_tuple(ma), "obs": ma,
                       "repair_fires": repair_fires(mut)}
        cls_counts[cls_a] = cls_counts.get(cls_a, 0) + 1
        if cls_a == "SILENT-LOSSY":
            silent_list.append(label)
        # conservation: recognized + merged + vanished == checkbox-ish heads
        recognized = ma["pending"] + ma["done"] + ma["non_owner"]
        if recognized + ma["merged_rows"] + ma["vanished_rows"] != ma["row_heads"]:
            conservation_ok = False
        expected_heads = 6
        if k in (14, 15, 16, 17):
            expected_heads = 5           # OP4/OP5 destroy exactly one head
        elif k == 25:
            expected_heads = 0           # OP13 destroys the SECTION (no parse)
        if ma["row_heads"] != expected_heads:
            conservation_ok = False
    check("F1.real-edit-sentinel", real_edit_all and len(grid) == 26,
          "all 26 cells produce a real single edit on C0")
    check("F1.conservation-cells", conservation_ok,
          "recognized+merged+vanished == checkbox-ish heads on all 26 cells "
          "(6 heads except OP4/OP5 shape-destroying cells at 5)")
    check("F2a.census-twin-verified", twin_cells_ok,
          "Arm B == Arm A on the full observable tuple and class of every cell (C2 contact)")

    reg_totals = FIX["anchors_F3"]["class_totals"]
    check("F3.class-totals", cls_counts == reg_totals,
          "census %s == registered %s" % (json.dumps(cls_counts, sort_keys=True),
                                          json.dumps(reg_totals, sort_keys=True)))
    reg_silent = FIX["anchors_F3"]["silent_lossy_list_verbatim"]
    check("F3.silent-list-verbatim", silent_list == reg_silent,
          "18-cell SILENT-LOSSY membership list matches the registration verbatim, "
          "with cell coordinates (the V094 anchor-coordinates rule)")

    reg_key = FIX["anchors_F3"]["key_cell_tuples_pending_done_armed_lint"]
    key_ok = all(grid[lbl]["tuple"] == reg_key[lbl] for lbl in reg_key)
    check("F3.key-cell-tuples", key_ok,
          "; ".join("%s %s" % (lbl, grid[lbl]["tuple"]) for lbl in sorted(reg_key)))
    op12 = grid["OP12@kill"]["obs"]
    check("F3.OP12-tuple",
          [op12["parsed"], op12["armed"], op12["lint"]] == FIX["anchors_F3"]["OP12_tuple_parsed_armed_lint"],
          "OP12 parsed %d armed %d lint %d" % (op12["parsed"], op12["armed"], op12["lint"]))
    op13 = grid["OP13@heading"]["obs"]
    check("F3.OP13-tuple",
          [op13["pending"], op13["manual"], op13["lint"]] == FIX["anchors_F3"]["OP13_tuple_pending_manual_lint"],
          "OP13 pending %d manual %d lint %d" % (op13["pending"], op13["manual"], op13["lint"]))

    # ---- F2d: the position law (vanish vs merge, containment) -------------
    o11 = grid["OP3@r1"]["obs"]
    o12 = grid["OP3@r2"]["obs"]
    r1_txt = "click PUBLISH on the staged listing"
    r2_txt = "approve the $19 launch price"
    merged_contains = any(r1_txt in t and r2_txt in t for t in o12["pending_texts"])
    vanish_clean = not any(r1_txt in t and r2_txt in t for t in o11["pending_texts"])
    check("F2d.position-law",
          o11["pending"] == 3 and o12["pending"] == 3
          and o11["vanished_rows"] == 1 and o11["merged_rows"] == 0
          and o12["merged_rows"] == 1 and o12["vanished_rows"] == 0
          and merged_contains and vanish_clean,
          "OP3@r1 VANISH (pending 3, vanished 1) vs OP3@r2 MERGE (pending 3, "
          "merged 1, merged WHAT contains both clicks' text)")

    # ---- F2e: the lint-downstream law --------------------------------------
    lint_downstream = all(grid[lbl]["obs"]["lint"] == 0 and grid[lbl]["obs"]["manual"] == 0
                          for lbl in silent_list)
    check("F2e.lint-downstream-law", lint_downstream and len(silent_list) == 18,
          "every SILENT cell lands lint == 0 AND manual == 0 (18/18) — the "
          "guard and the hazard share one predicate")

    # ---- F2c/F3: the cascade + once-live -----------------------------------
    cascade_ok = all(grid[lbl]["tuple"] == [4, 0, 0, 0]
                     for lbl in ("OP1@r5", "OP2@r5", "OP4@r5"))
    check("F2c.cascade-triple", cascade_ok,
          "OP1@r5/OP2@r5/OP4@r5 each (pending 4, done 0, armed 0, lint 0) — one "
          "character disarms every kill-clock checkpoint")
    check("F3.once-live-pair",
          [b1["parsed"], b1["armed"]] == FIX["anchors_F3"]["once_live_pair_C1"],
          "C1 (no-DONE) parsed %d / armed %d" % (b1["parsed"], b1["armed"]))

    # ---- F2b/F3: the disposition 2x2 on r1 (the sentence's own grid) --------
    two = {}
    two["A_noop"] = parse_a(C0)
    mut = list(C0)
    mut[8] = mut[8].replace("- [ ]", "- [x]", 1)
    two["B_checked_nodone"] = parse_a(mut)
    mutB = mut
    mut = list(C0)
    mut[8] = mut[8] + " — DONE 2026-07-14"
    two["C_unchecked_done"] = parse_a(mut)
    mutC = mut
    mut = list(C0)
    mut[8] = mut[8].replace("- [ ]", "- [x]", 1) + " — DONE 2026-07-14"
    two["D_full_flip"] = parse_a(mut)
    mutD = mut
    twin_2x2 = all(obs_tuple(parse_b(m)) == obs_tuple(two[k2])
                   for m, k2 in ((C0, "A_noop"), (mutB, "B_checked_nodone"),
                                 (mutC, "C_unchecked_done"), (mutD, "D_full_flip")))
    r1_ok = (key_tuple(two["A_noop"]) == [4, 1, 2, 0]
             and key_tuple(two["B_checked_nodone"]) == [4, 1, 2, 1]
             and key_tuple(two["C_unchecked_done"]) == [4, 1, 2, 1]
             and key_tuple(two["D_full_flip"]) == [3, 2, 2, 0])
    silent_2x2 = 0
    for k2 in ("B_checked_nodone", "C_unchecked_done", "D_full_flip"):
        if classify(base_a[0], two[k2]) == "SILENT-LOSSY":
            silent_2x2 += 1
    check("F2b.disposition-2x2", r1_ok and silent_2x2 == 0 and twin_2x2,
          "NO-OP [4,1,2,0] · queue+lint [4,1,2,1] · queue+lint [4,1,2,1] · "
          "RETIRE-LIVE [3,2,2,0]; zero silent cells on the sentence's own grid; twin-verified")

    # ---- F2f: the granularity inversion ------------------------------------
    check("F2f.granularity-inversion",
          op13["manual"] >= 1 and op13["lint"] >= 1 and lint_downstream,
          "breaking the FILE (OP13) is guarded (manual %d, lint %d); breaking "
          "a ROW is silent (the 18 R2 cells)" % (op13["manual"], op13["lint"]))

    # ---- F3/F5: the repair census ------------------------------------------
    caught = [lbl for lbl in grid if grid[lbl]["repair_fires"]]
    caught_silent = [lbl for lbl in silent_list if grid[lbl]["repair_fires"]]
    extras = sorted(lbl for lbl in caught if lbl not in silent_list)
    missed_silentish = [lbl for lbl in grid
                        if grid[lbl]["class"] in ("SILENT-LOSSY", "SILENT-REGRADE")
                        and not grid[lbl]["repair_fires"]]
    fp = [CORPUS_NAMES[i] for i in range(3) if repair_fires(CORPORA[i])]
    reg_rep = FIX["anchors_F3"]["repair_census"]
    rep_ok = (len(caught_silent) == 18 and extras == sorted(reg_rep["extras"])
              and not fp and missed_silentish == reg_rep["missed"])
    check("F3.repair-census", rep_ok,
          "conservation lint catches %d/18 SILENT-LOSSY + extras %s; false "
          "positives %s; silent cells missed %s (the semantic-regrade cell, "
          "disclosed open)" % (len(caught_silent), extras, fp or "none",
                               missed_silentish))
    check("F5.repair-zero-false-positives", not fp,
          "repair arm fires on ZERO unmutated corpora (C0, C1, C2)")

    # ---- F4: the hand worlds (pencil, computed) -----------------------------
    check("F4a.substring-cell", "**Owner:**" not in "*Owner:**",
          "'**Owner:**' is not a substring of '*Owner:**' — one lost asterisk "
          "defeats the literal-token conjunct")
    bolded = "**" + FLAG + " Owner:**"
    check("F4b.bolded-flag-prefix",
          bolded.lstrip().startswith("*") and not bolded.lstrip().startswith(FLAG),
          "'**⚑ Owner:**'.lstrip() starts with '*', not ⚑ — bolding defeats the "
          "prefix conjunct")
    check("F4c.bracket-shape", ROW_RE.match("- [] " + FLAG + " **Owner:** x") is None
          and _b_row("- [] " + FLAG + " **Owner:** x") is None,
          "'- []' fails the single-char bracket shape (both arms)")
    check("F4d.lowercase-done-requeues",
          DONE_RE.search("— done 2026-07-13") is None
          and _b_done_scan("— done 2026-07-13") is None,
          "lowercase '— done 2026-07-13' unmatched by the case-sensitive DONE "
          "scan (both arms) — the row re-queues, the fail-safe direction")

    # ---- F5: degeneracy / convention controls ------------------------------
    check("F5.C1-once-live-control",
          b1["pending"] == 4 and tuple(b1["pending_texts"]) == tuple(b0["pending_texts"])
          and b1["done"] == 0 and b1["armed"] == 0 and b1["lint"] == 0,
          "C1 reproduces the once-live rule with everything else unchanged "
          "(same 4 pending texts, lint 0)")
    check("F5.C2-multi-decision-control",
          b2["decisions"] == 2 and b2["lint"] == 0 and b2["decisions_no_default"] == 0,
          "C2 (two decisions) parses lint-clean — decision cells are not an "
          "artifact of single-decision files")
    taxonomy_total = all(grid[lbl]["class"] in
                         ("SILENT-LOSSY", "ALARMED-LOSSY", "ALARMED-SAFE", "SILENT-REGRADE")
                         for lbl in grid)
    check("F5.taxonomy-total", taxonomy_total,
          "the classify taxonomy is total on all 26 C0 cells (no "
          "SILENT-IDENTICAL, no INAPPLICABLE/NO-EDIT on the registered grid)")

    # ---- Arm R — seeded random cells, REPORTING-ONLY ------------------------
    def run_arm_r(seed, N, twin_every_trace):
        rng = make_rng(seed)
        census = {}
        stream_parts = []
        draws = 0
        salt_sum = 0
        salt_first5 = []
        twin_ok = True
        pair_cache_a = {}
        base_by_arm = (base_a, base_b)
        for _t in range(N):
            ci = rng.randint(0, 2)
            cellno = rng.randint(1, 26)
            salt = rng.randint(1, 1000)
            draws += 3
            salt_sum += salt
            if len(salt_first5) < 5:
                salt_first5.append(salt)
            keyp = (ci, cellno)
            mut, status = mutate(CORPORA[ci], cellno)
            if status != "ok":
                cls_a = status
                if twin_every_trace:
                    mut_b, status_b = mutate(CORPORA[ci], cellno)
                    if status_b != status:
                        twin_ok = False
            else:
                cls_a = classify(base_a[ci], parse_a(mut))
                if twin_every_trace:
                    cls_b = classify(base_b[ci], parse_b(mut))
                    if cls_b != cls_a:
                        twin_ok = False
            prev = pair_cache_a.get(keyp)
            if prev is not None and prev != cls_a:
                twin_ok = False          # determinism guard per pair
            pair_cache_a[keyp] = cls_a
            census[cls_a] = census.get(cls_a, 0) + 1
            stream_parts.append(cls_a)
        digest = hashlib.sha256("".join(stream_parts).encode("utf-8")).hexdigest()[:12]
        return {"census": census, "digest": digest, "draws": draws,
                "salt_sum": salt_sum, "salt_first5": salt_first5,
                "twin_ok": twin_ok}

    reg_r = FIX["arm_r"]["seeds"]
    r22 = run_arm_r(20261722, 20000, twin_every_trace=True)
    r23 = run_arm_r(20261723, 8000, twin_every_trace=True)
    # in-process double run (reproducibility, Arm A stream)
    r22b = run_arm_r(20261722, 20000, twin_every_trace=False)
    r23b = run_arm_r(20261723, 8000, twin_every_trace=False)

    check("F6.armR-census-20261722", r22["census"] == reg_r["20261722"]["census"],
          json.dumps(r22["census"], sort_keys=True))
    check("F6.armR-census-20261723", r23["census"] == reg_r["20261723"]["census"],
          json.dumps(r23["census"], sort_keys=True))
    check("F6.armR-digest-20261722", r22["digest"] == reg_r["20261722"]["class_stream_digest"],
          "class-stream digest %s == registered %s"
          % (r22["digest"], reg_r["20261722"]["class_stream_digest"]))
    check("F6.armR-digest-20261723", r23["digest"] == reg_r["20261723"]["class_stream_digest"],
          "class-stream digest %s == registered %s"
          % (r23["digest"], reg_r["20261723"]["class_stream_digest"]))
    check("F1.armR-draw-sentinels",
          r22["draws"] == 60000 and r23["draws"] == 24000,
          "draw counters exactly 3N: %d / %d" % (r22["draws"], r23["draws"]))
    check("F6.armR-per-trace-twin", r22["twin_ok"] and r23["twin_ok"],
          "Arm B == Arm A on every trace of both seeds (C4 contact)")
    check("F6.armR-in-process-double-run",
          r22b["census"] == r22["census"] and r22b["digest"] == r22["digest"]
          and r23b["census"] == r23["census"] and r23b["digest"] == r23["digest"],
          "census + digest identical on a second in-process pass per seed")
    check("F5.armR-honest-classes",
          r22["census"].get("NO-EDIT", 0) > 0 and r22["census"].get("INAPPLICABLE", 0) > 0
          and sum(r22["census"].values()) == 20000 and sum(r23["census"].values()) == 8000,
          "INAPPLICABLE and NO-EDIT counted, never silently skipped; censuses "
          "sum to N")

    # ---- typed contacts C1/C2 (baselines + cells already; assert together) --
    c1_ok = all(obs_tuple(base_a[i]) == obs_tuple(base_b[i]) for i in range(3))
    check("F6.contact-C1-baselines", c1_ok,
          "Arm B == Arm A on the three baseline tuples")
    check("F6.contact-C2-cells", twin_cells_ok and twin_2x2,
          "Arm B == Arm A on all 26 grid cells and all four 2x2 cells")

    # ---- presentation shuffle (presentation leg ONLY) ------------------------
    prng = make_rng(FIX["arm_r"]["presentation_seed"])
    display = sorted(grid.keys())
    prng.shuffle(display)
    print("  census table (display order via presentation seed %d):"
          % FIX["arm_r"]["presentation_seed"])
    for lbl in display:
        g = grid[lbl]
        print("    %-13s %-14s pending/done/armed/lint = %s  repair:%s"
              % (lbl, g["class"], g["tuple"],
                 "CAUGHT" if g["repair_fires"] else "-"))

    check("F6.presentation-seed-scope",
          SEEDS_CONSTRUCTED == [20261722, 20261723, 20261722, 20261723, 20261724],
          "seed ledger %s — presentation seed read by the presentation leg "
          "only, after every decision leg finished" % (SEEDS_CONSTRUCTED,))
    check("F6.aux-seed-never-read",
          FIX["arm_r"]["aux_seed_never_read"] not in SEEDS_CONSTRUCTED,
          "aux seed 20261725 reserved and never read")

    # ---- decision ------------------------------------------------------------
    gates_ok_so_far = all(ok for _n, ok, _d in CHECKS)
    silent_count = len(silent_list)
    decision_inputs = {
        "R1": bool(r1_ok and silent_2x2 == 0 and twin_2x2),
        "R2": bool(cls_counts == reg_totals and silent_list == reg_silent
                   and lint_downstream and silent_count >= 15),
        "R3": bool(cascade_ok and [b1["parsed"], b1["armed"]] == [2, 0]),
        "R4": bool(op13["manual"] >= 1 and op13["lint"] >= 1 and rep_ok),
        "gates_ok": gates_ok_so_far,
        "zero_silent": silent_count == 0,
    }
    # enumerated boolean input set: both evaluators must agree everywhere
    agree_all = True
    for mask in range(64):
        probe = {"R1": bool(mask & 1), "R2": bool(mask & 2),
                 "R3": bool(mask & 4), "R4": bool(mask & 8),
                 "gates_ok": bool(mask & 16), "zero_silent": bool(mask & 32)}
        if evaluate_1(probe) != evaluate_2(probe):
            agree_all = False
    verdict_1 = evaluate_1(decision_inputs)
    verdict_2 = evaluate_2(decision_inputs)
    check("F6.contact-C3-evaluators",
          agree_all and verdict_1 == verdict_2,
          "twin evaluators agree on all 64 enumerated inputs and rule %s/%s"
          % (verdict_1, verdict_2))
    check("decision.approve-arithmetically-excluded",
          decision_inputs["zero_silent"] is False and silent_count == 18,
          "APPROVE requires zero SILENT-LOSSY cells; measured %d (the OP1@r1 "
          "pencil cell alone excludes it)" % silent_count)

    print("decision inputs: " + json.dumps(decision_inputs, sort_keys=True))
    print("VERDICT: %s (evaluator 1) / %s (evaluator 2)" % (verdict_1, verdict_2))

    passed = sum(1 for _n, ok, _d in CHECKS if ok)
    total = len(CHECKS)
    print("=" * 74)
    print("self-checks: %d/%d passed" % (passed, total))

    RESULTS.update({
        "verdict": verdict_1,
        "decision_inputs": decision_inputs,
        "baselines": {CORPUS_NAMES[i]: {kk: base_a[i][kk] for kk in
                                        ("steps", "decisions", "pending", "done",
                                         "non_owner", "parsed", "armed", "blocked",
                                         "lint", "manual")}
                      for i in range(3)},
        "grid": {lbl: {"class": grid[lbl]["class"],
                       "pending_done_armed_lint": grid[lbl]["tuple"],
                       "repair_fires": grid[lbl]["repair_fires"]}
                 for lbl in sorted(grid)},
        "class_totals": cls_counts,
        "silent_lossy_list": silent_list,
        "two_by_two": {k2: key_tuple(two[k2]) for k2 in sorted(two)},
        "cascade_triple": {lbl: grid[lbl]["tuple"]
                           for lbl in ("OP1@r5", "OP2@r5", "OP4@r5")},
        "once_live_pair_C1": [b1["parsed"], b1["armed"]],
        "position_law": {"OP3@r1": {"pending": o11["pending"], "vanished": o11["vanished_rows"]},
                         "OP3@r2": {"pending": o12["pending"], "merged": o12["merged_rows"],
                                    "containment": merged_contains}},
        "repair": {"caught": sorted(caught), "extras": extras,
                   "false_positives": fp, "missed_silent": missed_silentish},
        "arm_r": {
            "20261722": {"census": r22["census"], "digest": r22["digest"],
                         "draws": r22["draws"], "salt_sum": r22["salt_sum"],
                         "salt_first5": r22["salt_first5"]},
            "20261723": {"census": r23["census"], "digest": r23["digest"],
                         "draws": r23["draws"], "salt_sum": r23["salt_sum"],
                         "salt_first5": r23["salt_first5"]},
            "seed_ledger": SEEDS_CONSTRUCTED,
        },
        "checks": {"passed": passed, "total": total,
                   "failed": [n for n, ok, _d in CHECKS if not ok]},
        "environment": {"cpython_minor": pyminor,
                        "decision_arms": "seedless exact parsing and integer "
                                         "counting (platform-independent)"},
    })
    with open(os.path.join(HERE, "results.json"), "w", encoding="utf-8") as out:
        json.dump(RESULTS, out, indent=1, sort_keys=True)
        out.write("\n")

    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())
