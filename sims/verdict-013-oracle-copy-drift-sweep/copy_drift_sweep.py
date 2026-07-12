#!/usr/bin/env python3
"""verdict-013 -- oracle user-copy punctuation-drift sweep (idea-engine PROPOSAL 011).

Settles which (user-copy enumeration grammar x match-normalization tier) cell a
`tools/check_copy_drift.py` checker (superbot-next) should ship with -- and
whether the winning cell's true-catch count on the REAL corpora justifies a
red-gating checker over a one-line fix. Sweeps:

  GRAMMARS (rebuild-side user-copy enumeration; probe axis i):
    g1-verbatim3   str literals within +/-3 lines of a `# ... verbatim` comment
    g2-verbatim10  same, +/-10 lines (window variant of the same grammar)
    g3-refusal     str literals inside tuple returns `return False, "..."` & kin
    g4-userreach   str literals inside calls named send/reply/embed-etc.
    g5-msg         g3 UNION g4 (the probe Q3 "refusal-tuple/message literals")
    g6-all         ALL non-docstring str literals (upper-bound / FP-flood control)
  TIERS (match normalization; probe axis iii):
    t0-byte        byte equality only (flags nothing by construction: a drift
                   detector needs normalized-equal AND byte-differ)
    t1-ws          collapse whitespace runs, strip
    t2-punct       t1 + unify curly quotes + strip punctuation
    t3-case        t2 + casefold
    t4-fuzzy       t3, OR difflib ratio >= 0.90 between t3 forms
  GATING/PAIRING RULES (probe axis iv, the mechanical half):
    r-any          flag every normalized-equal-but-byte-differ (N,O) pair
    r-noexact      + suppress when the rebuild literal ALSO byte-matches some
                   oracle literal (i.e. it is verbatim-conformant somewhere;
                   its normalized collisions with OTHER fragments are noise)
  (red-vs-warn + waiver/allowlist -- the judgment half of axis iv -- is decided
  FROM the audited FP numbers and stated machine-readably in REPORT.md.)

over TWO evidence layers:

  1. the REAL pinned corpora --
       superbot-next @ af985c17def5ff2478103cb363ebb150cb583a97 (scan sb/)
       superbot      @ 1ecc21138fe0a1eb672d03b66bd319164c29d55f (oracle disbot/)
     with hand-audited labels (labels.json) for every flagged pair of the
     full-audit domain -> true-drift / intentional-change / false-pair, and
  2. a SEEDED PLANTED-DRIFT layer: realistic punctuation / casing / whitespace /
     wording mutations injected into a copy of the rebuild corpus's literal
     table (seed 20260712) -> per-cell recall with hand-derived expectations.

Corpora are fetched ON RUN into ./corpora/<name> (gitignored) via shallow
`git fetch origin <sha>`; SHA-pinning keeps content deterministic, so the cache
is a transport detail, not an input degree of freedom.

Run (the one command):

    python3 sims/verdict-013-oracle-copy-drift-sweep/copy_drift_sweep.py

Exit 0 iff all self-checks pass. Deterministic: the ONLY RNG is the planted-
drift injector, seeded 20260712; audit samples are fixed strides over sorted
pair lists (no RNG); byte-identical re-runs (results.json is canonical JSON,
no timestamps).

Stdlib-only. SelfCheck battery vendor-copied from harness/simharness.py
(sims never import harness at runtime).
"""

import ast
import difflib
import io
import json
import os
import random
import re
import subprocess
import sys
import tokenize

HERE = os.path.dirname(os.path.abspath(__file__))

PINS = {
    "superbot-next": ("https://github.com/menno420/superbot-next.git",
                      "af985c17def5ff2478103cb363ebb150cb583a97"),
    "superbot": ("https://github.com/menno420/superbot.git",
                 "1ecc21138fe0a1eb672d03b66bd319164c29d55f"),
}
SCAN_ROOT = "sb"        # rebuild-side subtree (superbot-next)
ORACLE_ROOT = "disbot"  # oracle-side subtree (superbot)

GRAMMARS = ("g1-verbatim3", "g2-verbatim10", "g3-refusal", "g4-userreach",
            "g5-msg", "g6-all")
TIERS = ("t0-byte", "t1-ws", "t2-punct", "t3-case", "t4-fuzzy")
GATINGS = ("r-any", "r-noexact")

VERBATIM_WINDOWS = {"g1-verbatim3": 3, "g2-verbatim10": 10}

# g4-userreach: call names whose string args count as user-reaching copy
# (probe: "send/reply/embed args"). Logging names (error/warning/info/debug/
# exception) are deliberately EXCLUDED -- log strings are the probe's named
# FP-flood class, not user copy. Rebuild-side UI-component constructors
# (PanelSpec/TextBlock/...) are NOT enumerated -- a stated limit; the measured
# consequence is that g4 misses returned/panel copy (see tournament checks).
USER_CALL_NAMES = frozenset({
    "send", "reply", "respond", "send_message", "edit_message", "edit",
    "followup", "add_field", "insert_field_at", "set_field_at",
    "set_footer", "set_author", "Embed",
})

MIN_NORM_LEN = 8        # eligibility: len(t3-normalized literal) >= this
FUZZY_THRESHOLD = 0.90  # difflib ratio on t3 forms
FUZZY_MAX_NORM_LEN = 300   # blocking: fuzzy comparisons only for norm forms <= this
FUZZY_BLOCK_TOKENS = 3     # blocking: index/query by the 3 rarest tokens
FUZZY_LEN_WINDOW = 0.2     # blocking: length difference <= 20% of the longer
MAX_SITES = 6           # per-pair site lists capped in results.json

SEED = 20260712
PLANT_PER_GRAMMAR = 24  # planted drifts per grammar (6 per mutation class)
MUTATION_CLASSES = ("punct", "case", "ws", "word")

# audit sampling (fixed stride, no RNG) for cells outside the full-audit domain
SAMPLE_N = {"g6-t2": 20, "g6-t3": 20, "g6-t4": 15, "gsmall-t4": 20}

# the winning cell (fixed by the audited numbers; asserted in frontier checks:
# it is the TC-maximal cell among all cells with zero audited FP, and t3-case
# dominates t2-punct on planted recall at identical real-corpus flags)
WINNING_CELL = ("g5-msg", "t3-case", "r-noexact")

# the motivating live instance (PROPOSAL 011 done-when citation)
TOURNAMENT_N = "You're already registered."
TOURNAMENT_O = "You're already registered!"
TOURNAMENT_N_SITE = ("sb/domain/rps/tournament.py", 153)
TOURNAMENT_O_SITES = (("disbot/utils/tournaments.py", 44),
                      ("disbot/views/rps/registration.py", 49))


# ---- SelfCheck battery (vendor-copied from harness/simharness.py) ----------

class SelfCheck:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.failures = []

    def check(self, cond, label):
        if cond:
            self.passed += 1
        else:
            self.failed += 1
            self.failures.append(label)
        return bool(cond)

    def report(self):
        for f in self.failures:
            print("SELF-CHECK FAILED: %s" % f)
        print("SELF-CHECKS: %d passed, %d failed" % (self.passed, self.failed))
        return self.failed == 0


# ---- corpus fetch -----------------------------------------------------------

def ensure_corpus(name):
    url, sha = PINS[name]
    root = os.path.join(HERE, "corpora", name)
    head = None
    if os.path.isdir(os.path.join(root, ".git")):
        try:
            head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=root,
                                  capture_output=True, text=True).stdout.strip()
        except OSError:
            head = None
    if head != sha:
        os.makedirs(root, exist_ok=True)
        def git(*args):
            r = subprocess.run(["git"] + list(args), cwd=root,
                               capture_output=True, text=True)
            if r.returncode != 0:
                sys.stderr.write("git %s failed:\n%s\n" % (" ".join(args), r.stderr))
                sys.exit(2)
        if not os.path.isdir(os.path.join(root, ".git")):
            git("init", "-q")
            git("remote", "add", "origin", url)
        git("fetch", "-q", "--depth", "1", "origin", sha)
        git("checkout", "-q", "--force", sha)
        head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=root,
                              capture_output=True, text=True).stdout.strip()
    return root, head


# ---- extraction -------------------------------------------------------------

def py_files(root, sub):
    out = []
    base = os.path.join(root, sub)
    for dp, dns, fns in os.walk(base):
        dns[:] = sorted(d for d in dns if d != ".git")
        for fn in sorted(fns):
            if fn.endswith(".py"):
                out.append(os.path.join(dp, fn))
    return sorted(out)


def parse_file(path):
    with open(path, encoding="utf-8", errors="replace") as fh:
        src = fh.read()
    try:
        return src, ast.parse(src)
    except SyntaxError:
        return src, None


def docstring_const_ids(tree):
    """id()s of Constant nodes that are module/class/function docstrings."""
    out = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.Module, ast.FunctionDef,
                             ast.AsyncFunctionDef, ast.ClassDef)):
            body = node.body
            if (body and isinstance(body[0], ast.Expr)
                    and isinstance(body[0].value, ast.Constant)
                    and isinstance(body[0].value.value, str)):
                out.add(id(body[0].value))
    return out


def str_constants(tree):
    """(lineno, value) for every plain-str Constant, docstrings excluded."""
    doc = docstring_const_ids(tree)
    return [(n.lineno, n.value) for n in ast.walk(tree)
            if isinstance(n, ast.Constant) and isinstance(n.value, str)
            and id(n) not in doc]


def verbatim_comment_lines(src):
    """Line numbers of `#` comments containing 'verbatim' (case-insensitive)."""
    out = set()
    try:
        for tok in tokenize.generate_tokens(io.StringIO(src).readline):
            if tok.type == tokenize.COMMENT and "verbatim" in tok.string.lower():
                out.add(tok.start[0])
    except (tokenize.TokenError, IndentationError):
        pass
    return out


def refusal_tuple_strings(tree):
    """str Constants inside `return <a>, <b>[, ...]` tuple returns (the shipped
    refusal-tuple convention: `return False, "copy"` and kin)."""
    out = []
    for node in ast.walk(tree):
        if (isinstance(node, ast.Return) and isinstance(node.value, ast.Tuple)
                and len(node.value.elts) >= 2):
            for elt in node.value.elts:
                if isinstance(elt, ast.Constant) and isinstance(elt.value, str):
                    out.append((elt.lineno, elt.value))
    return out


def userreach_strings(tree):
    """str Constants anywhere inside a Call whose name is in USER_CALL_NAMES."""
    out = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            f = node.func
            name = (f.id if isinstance(f, ast.Name)
                    else f.attr if isinstance(f, ast.Attribute) else None)
            if name in USER_CALL_NAMES:
                for sub in ast.walk(node):
                    if (isinstance(sub, ast.Constant)
                            and isinstance(sub.value, str)):
                        out.append((sub.lineno, sub.value))
    return out


def extract_rebuild(root):
    """-> {grammar: {literal: sorted [(relpath, lineno), ...]}}"""
    gram = {g: {} for g in GRAMMARS}

    def add(g, rel, ln, v):
        gram[g].setdefault(v, set()).add((rel, ln))

    for path in py_files(root, SCAN_ROOT):
        rel = os.path.relpath(path, root).replace(os.sep, "/")
        src, tree = parse_file(path)
        if tree is None:
            continue
        consts = str_constants(tree)
        marks = verbatim_comment_lines(src)
        for ln, v in consts:
            add("g6-all", rel, ln, v)
            for g, win in VERBATIM_WINDOWS.items():
                if any(abs(ln - m) <= win for m in marks):
                    add(g, rel, ln, v)
        for ln, v in refusal_tuple_strings(tree):
            add("g3-refusal", rel, ln, v)
            add("g5-msg", rel, ln, v)
        for ln, v in userreach_strings(tree):
            add("g4-userreach", rel, ln, v)
            add("g5-msg", rel, ln, v)
    return {g: {v: sorted(sites) for v, sites in d.items()}
            for g, d in gram.items()}


def extract_oracle(root):
    """-> {literal: sorted [(relpath, lineno), ...]} over ORACLE_ROOT."""
    pool = {}
    for path in py_files(root, ORACLE_ROOT):
        rel = os.path.relpath(path, root).replace(os.sep, "/")
        _src, tree = parse_file(path)
        if tree is None:
            continue
        for ln, v in str_constants(tree):
            pool.setdefault(v, set()).add((rel, ln))
    return {v: sorted(sites) for v, sites in pool.items()}


# ---- normalization tiers ----------------------------------------------------

_PUNCT_RX = re.compile(r"[!?.,;:…*_`~\"']+")
_WS_RX = re.compile(r"\s+")


def n_ws(s):
    return _WS_RX.sub(" ", s).strip()


def n_punct(s):
    s = (s.replace("’", "'").replace("‘", "'")
          .replace("“", '"').replace("”", '"'))
    return n_ws(_PUNCT_RX.sub("", s))


def n_case(s):
    return n_punct(s).casefold()


NORM_FN = {"t1-ws": n_ws, "t2-punct": n_punct, "t3-case": n_case}


def eligible(lit):
    return len(n_case(lit)) >= MIN_NORM_LEN


# ---- matching engine --------------------------------------------------------

class Matcher:
    """Flag computation over a fixed oracle pool. flags(grammar_lits, tier,
    gating) -> sorted list of (n_lit, o_lit) pairs, normalized-equal at the
    tier (or fuzzy at t4) AND byte-different."""

    def __init__(self, oracle_lits):
        self.pool = sorted(oracle_lits)
        self.pool_set = set(self.pool)
        self.elig = [o for o in self.pool if eligible(o)]
        self.idx = {}  # tier -> norm -> sorted [o_lit, ...]
        for tier, fn in NORM_FN.items():
            d = {}
            for o in self.elig:
                d.setdefault(fn(o), []).append(o)
            self.idx[tier] = d
        # fuzzy blocking index over t3 forms (<= FUZZY_MAX_NORM_LEN)
        self.o_norm = {}
        df = {}
        for o in self.elig:
            no = n_case(o)
            if len(no) <= FUZZY_MAX_NORM_LEN:
                self.o_norm[o] = no
                for t in set(no.split()):
                    df[t] = df.get(t, 0) + 1
        self.df = df
        self.block = {}
        for o, no in self.o_norm.items():
            toks = sorted(set(no.split()), key=lambda t: (self.df[t], t))
            for t in toks[:FUZZY_BLOCK_TOKENS]:
                self.block.setdefault(t, []).append(o)

    def exact_pairs(self, lits, tier):
        fn = NORM_FN[tier]
        out = set()
        for v in lits:
            for o in self.idx[tier].get(fn(v), ()):
                if o != v:
                    out.add((v, o))
        return out

    def fuzzy_extras(self, lits):
        out = set()
        for v in lits:
            nv = n_case(v)
            if len(nv) > FUZZY_MAX_NORM_LEN:
                continue
            toks = sorted(set(nv.split()), key=lambda t: (self.df.get(t, 0), t))
            cands = set()
            for t in toks[:FUZZY_BLOCK_TOKENS]:
                cands.update(self.block.get(t, ()))
            for o in sorted(cands):
                if o == v:
                    continue
                no = self.o_norm[o]
                if no == nv:
                    continue  # already in t3 flags
                if abs(len(no) - len(nv)) > FUZZY_LEN_WINDOW * max(len(no), len(nv)):
                    continue
                sm = difflib.SequenceMatcher(None, nv, no)
                if sm.quick_ratio() < FUZZY_THRESHOLD:
                    continue
                if sm.ratio() >= FUZZY_THRESHOLD:
                    out.add((v, o))
        return out

    def flags(self, grammar_lits, tier, gating):
        lits = sorted(v for v in grammar_lits if eligible(v))
        if gating == "r-noexact":
            lits = [v for v in lits if v not in self.pool_set]
        if tier == "t0-byte":
            pairs = set()
        elif tier == "t4-fuzzy":
            pairs = self.exact_pairs(lits, "t3-case") | self.fuzzy_extras(lits)
        else:
            pairs = self.exact_pairs(lits, tier)
        return sorted(pairs)


# ---- planted-drift layer ----------------------------------------------------

WORD_ALPHA_RX = re.compile(r"[A-Za-z]{4,}")


def mutate(lit, mclass, rng):
    """One realistic drift of the given class. Returns (mutated, applied_class)
    -- applied_class can differ when the requested class is inapplicable."""
    if mclass == "punct":
        if lit and lit[-1] in ".!?":
            swap = {".": "!", "!": ".", "?": "!"}
            return lit[:-1] + swap[lit[-1]], "punct"
        return lit + ".", "punct"
    if mclass == "case":
        for i, ch in enumerate(lit):
            if ch.isalpha() and ch.swapcase() != ch:
                return lit[:i] + ch.swapcase() + lit[i + 1:], "case"
        return " " + lit, "ws"  # no alpha: fall back to whitespace drift
    if mclass == "ws":
        i = lit.find(" ")
        if i >= 0:
            return lit[:i] + "  " + lit[i + 1:], "ws"
        return " " + lit, "ws"
    # word: morphological edit of the longest >=4-alpha token
    words = sorted(WORD_ALPHA_RX.findall(lit), key=lambda w: (-len(w), w))
    if words:
        w = words[0]
        repl = w[:-1] if w.endswith("s") else w + "s"
        return lit.replace(w, repl, 1), "word"
    return " " + lit, "ws"  # no word tokens: fall back


def fuzzy_ratio_ok(mut, orig):
    return (difflib.SequenceMatcher(None, n_case(mut), n_case(orig)).ratio()
            >= FUZZY_THRESHOLD)


def fuzzy_reachable(matcher, mut, orig):
    """Spec-level restatement of the t4 blocking rules (length window + shared
    rarest-token blocking key), written against the spec constants -- used to
    derive planted expectations AND to measure the blocking gap (word drifts
    whose ratio passes but whose mutated token escapes the blocking index)."""
    nv, no = n_case(mut), n_case(orig)
    if len(nv) > FUZZY_MAX_NORM_LEN or len(no) > FUZZY_MAX_NORM_LEN:
        return False
    if abs(len(no) - len(nv)) > FUZZY_LEN_WINDOW * max(len(no), len(nv)):
        return False
    qt = sorted(set(nv.split()),
                key=lambda t: (matcher.df.get(t, 0), t))[:FUZZY_BLOCK_TOKENS]
    ot = sorted(set(no.split()),
                key=lambda t: (matcher.df.get(t, 0), t))[:FUZZY_BLOCK_TOKENS]
    return bool(set(qt) & set(ot))


def expected_catch(applied_class, orig, mut, tier, matcher):
    """Hand-derived expectation: is the planted (mut, orig) pair flagged at the
    tier?  Semantics, not engine internals: t1 sees ws-only drift, t2 adds
    punctuation, t3 adds case, t4 adds fuzzy wording at ratio >= 0.90 subject
    to the stated blocking rules (fuzzy_reachable; the two helpers restate the
    spec's own formula and blocking constants -- disclosed)."""
    if tier == "t0-byte":
        return False
    caught_at = {"ws": 1, "punct": 2, "case": 3, "word": 5}[applied_class]
    rank = {"t1-ws": 1, "t2-punct": 2, "t3-case": 3, "t4-fuzzy": 4}[tier]
    if rank >= caught_at:
        return True
    if tier == "t4-fuzzy" and applied_class == "word":
        return fuzzy_ratio_ok(mut, orig) and fuzzy_reachable(matcher, mut, orig)
    return False


def plant_drifts(rebuild, matcher, sc):
    """Seeded injection into a COPY of the rebuild corpus's literal table:
    per grammar, take literals that byte-match the oracle (verbatim pairs),
    mutate up to PLANT_PER_GRAMMAR of them (classes cycled deterministically),
    and record hand-derived per-tier expectations."""
    rng = random.Random(SEED)
    plan = {}
    for g in GRAMMARS:
        verbatim = sorted(v for v in rebuild[g]
                          if eligible(v) and v in matcher.pool_set)
        n = min(PLANT_PER_GRAMMAR, len(verbatim))
        chosen = sorted(rng.sample(verbatim, n)) if n else []
        items = []
        for i, orig in enumerate(chosen):
            mclass = MUTATION_CLASSES[i % len(MUTATION_CLASSES)]
            mut, applied = mutate(orig, mclass, rng)
            if mut == orig or mut in matcher.pool_set or not eligible(mut):
                continue  # oracle byte-collision or vacuous mutation: skip
            items.append({"orig": orig, "mutated": mut, "class": applied})
        sc.check(len(items) >= min(4, n),
                 "planted %s: at least min(4,%d) usable plants (got %d)"
                 % (g, n, len(items)))
        plan[g] = items
    return plan


def planted_recall(plan, rebuild, matcher, sc):
    """Per-cell recall over the planted set: rerun the matcher on the mutated
    literal table and check the (mutated, orig) pair is flagged."""
    out = {}
    for g in GRAMMARS:
        items = plan[g]
        if not items:
            out[g] = {}
            continue
        lits = set(rebuild[g])
        muts = {it["mutated"] for it in items}
        lits |= muts
        cell = {}
        for tier in TIERS:
            for gating in GATINGS:
                flags = matcher.flags(lits, tier, gating)
                flagged_pairs = set(flags)
                caught = 0
                for it in items:
                    hit = (it["mutated"], it["orig"]) in flagged_pairs
                    want = expected_catch(it["class"], it["orig"],
                                          it["mutated"], tier, matcher)
                    # gating never suppresses a plant: mutated literal is
                    # byte-absent from the oracle pool by construction
                    sc.check(hit == want,
                             "planted %s/%s/%s %r: want %s got %s"
                             % (g, tier, gating, it["mutated"][:40], want, hit))
                    caught += 1 if hit else 0
                cell["%s|%s" % (tier, gating)] = {
                    "caught": caught, "planted": len(items),
                    "recall": round(caught / len(items), 4)}
        # the measured t4 blocking gap: word plants an exhaustive fuzzy
        # comparison would catch (ratio >= threshold) but blocking misses
        gap = sum(1 for it in items if it["class"] == "word"
                  and fuzzy_ratio_ok(it["mutated"], it["orig"])
                  and not fuzzy_reachable(matcher, it["mutated"], it["orig"]))
        n_word = sum(1 for it in items if it["class"] == "word")
        cell["word_plants"] = n_word
        cell["word_ratio_ok_but_blocked"] = gap
        out[g] = cell
    return out


# ---- audit join --------------------------------------------------------------

# full-audit domain: every pair flagged by grammars g1..g5 at tiers t1..t3
# (r-any is the superset gating), PLUS the g6-all x t1-ws row (small enough to
# audit fully). g6 x t2/t3/t4 and the t4 rows of g1..g5 are covered by stated
# fixed-stride samples (no RNG).
FULL_GRAMS = ("g1-verbatim3", "g2-verbatim10", "g3-refusal", "g4-userreach",
              "g5-msg")
FULL_TIERS = ("t1-ws", "t2-punct", "t3-case")


def stride_sample(pairs, n):
    pairs = sorted(pairs)
    if len(pairs) <= n:
        return pairs
    stride = max(1, len(pairs) // n)
    return pairs[::stride][:n]


def pair_key(n_lit, o_lit):
    return json.dumps([n_lit, o_lit], ensure_ascii=True, sort_keys=True)


def audit_domains(cell_flags):
    """-> (full_domain_pairs, samples) where samples maps a stated sample name
    -> sorted pair list."""
    full = set()
    for g in FULL_GRAMS:
        for t in FULL_TIERS:
            full |= set(cell_flags[(g, t, "r-any")])
    full |= set(cell_flags[("g6-all", "t1-ws", "r-any")])
    samples = {}
    samples["g6-t2"] = stride_sample(
        set(cell_flags[("g6-all", "t2-punct", "r-any")]) - full, SAMPLE_N["g6-t2"])
    samples["g6-t3"] = stride_sample(
        set(cell_flags[("g6-all", "t3-case", "r-any")]) - full
        - set(samples["g6-t2"]), SAMPLE_N["g6-t3"])
    small_t4 = set()
    for g in FULL_GRAMS:
        small_t4 |= set(cell_flags[(g, "t4-fuzzy", "r-any")])
    samples["gsmall-t4"] = stride_sample(small_t4 - full, SAMPLE_N["gsmall-t4"])
    covered = full | set(samples["g6-t2"]) | set(samples["g6-t3"]) \
        | set(samples["gsmall-t4"])
    samples["g6-t4"] = stride_sample(
        set(cell_flags[("g6-all", "t4-fuzzy", "r-any")]) - covered,
        SAMPLE_N["g6-t4"])
    return sorted(full), {k: sorted(v) for k, v in samples.items()}


AUTO_REASON = ("auto: rebuild literal is byte-verbatim elsewhere in the oracle "
               "pool -- this pair is a normalized collision with a DIFFERENT "
               "oracle fragment, exactly the class r-noexact suppresses")


def join_labels(cell_flags, full_domain, samples, labels, matcher, sc):
    """-> (label_map, per_cell audit counts). Classification precedence: a
    hand label from labels.json wins; a pair whose rebuild literal byte-matches
    the oracle pool somewhere is otherwise AUTO-classified false-pair (the only
    mechanically-derivable class -- verdict-012's auto-classification rule:
    auto-classify only what is mechanically derivable, never judgment calls).
    Every full-domain and sampled pair must then be classified (self-checked);
    pairs outside those domains count as unlabeled in their cells."""
    lmap = {}
    for rec in labels["pairs"]:
        lmap[pair_key(rec["n"], rec["o"])] = dict(rec, provenance="hand")
    auto = 0
    for pairs in [full_domain] + [samples[k] for k in sorted(samples)]:
        for n_lit, o_lit in pairs:
            k = pair_key(n_lit, o_lit)
            if k not in lmap and n_lit in matcher.pool_set:
                lmap[k] = {"n": n_lit, "o": o_lit, "verdict": "false-pair",
                           "class": "byte-verbatim-elsewhere",
                           "reason": AUTO_REASON, "provenance": "auto"}
                auto += 1
    for n_lit, o_lit in full_domain:
        sc.check(pair_key(n_lit, o_lit) in lmap,
                 "label coverage (full domain): %s" % pair_key(n_lit, o_lit)[:120])
    for name in sorted(samples):
        for n_lit, o_lit in samples[name]:
            sc.check(pair_key(n_lit, o_lit) in lmap,
                     "label coverage (sample %s): %s"
                     % (name, pair_key(n_lit, o_lit)[:120]))
    per_cell = {}
    for (g, t, r), flags in cell_flags.items():
        cnt = {"flagged": len(flags), "true-drift": 0, "intentional-change": 0,
               "false-pair": 0, "unlabeled": 0}
        for n_lit, o_lit in flags:
            rec = lmap.get(pair_key(n_lit, o_lit))
            if rec is None:
                cnt["unlabeled"] += 1
            else:
                cnt[rec["verdict"]] += 1
        cnt["tc"] = cnt["true-drift"]
        cnt["fp"] = cnt["intentional-change"] + cnt["false-pair"]
        per_cell["|".join((g, t, r))] = cnt
    return lmap, per_cell, auto


# ---- invariants ---------------------------------------------------------------

def invariant_checks(sc, cell_flags):
    tier_order = ("t0-byte", "t1-ws", "t2-punct", "t3-case", "t4-fuzzy")
    for g in GRAMMARS:
        for r in GATINGS:
            for a, b in zip(tier_order, tier_order[1:]):
                sc.check(set(cell_flags[(g, a, r)]) <= set(cell_flags[(g, b, r)]),
                         "tier monotonicity %s: %s <= %s (%s)" % (g, a, b, r))
    for t in TIERS:
        for r in GATINGS:
            f = {g: set(cell_flags[(g, t, r)]) for g in GRAMMARS}
            sc.check(f["g1-verbatim3"] <= f["g2-verbatim10"],
                     "grammar nesting g1<=g2 (%s,%s)" % (t, r))
            sc.check(f["g3-refusal"] <= f["g5-msg"],
                     "grammar nesting g3<=g5 (%s,%s)" % (t, r))
            sc.check(f["g4-userreach"] <= f["g5-msg"],
                     "grammar nesting g4<=g5 (%s,%s)" % (t, r))
            for g in GRAMMARS[:-1]:
                sc.check(f[g] <= f["g6-all"],
                         "grammar nesting %s<=g6 (%s,%s)" % (g, t, r))
    for g in GRAMMARS:
        for t in TIERS:
            sc.check(set(cell_flags[(g, t, "r-noexact")])
                     <= set(cell_flags[(g, t, "r-any")]),
                     "gating subset noexact<=any (%s,%s)" % (g, t))


def tournament_checks(sc, rebuild, oracle, cell_flags):
    pair = (TOURNAMENT_N, TOURNAMENT_O)
    sc.check(TOURNAMENT_N_SITE in rebuild["g3-refusal"].get(TOURNAMENT_N, []),
             "tournament: N literal at sb/domain/rps/tournament.py:153 in "
             "g3-refusal")
    o_sites = oracle.get(TOURNAMENT_O, [])
    for s in TOURNAMENT_O_SITES:
        sc.check(s in o_sites, "tournament: oracle site %s:%d present" % s)
    for g in ("g3-refusal", "g5-msg", "g6-all"):
        for t in ("t2-punct", "t3-case", "t4-fuzzy"):
            for r in GATINGS:
                sc.check(pair in set(cell_flags[(g, t, r)]),
                         "tournament: caught by %s/%s/%s" % (g, t, r))
    # measured discriminators (misses, asserted so drift = red run)
    sc.check(pair not in set(cell_flags[("g3-refusal", "t1-ws", "r-any")]),
             "tournament: t1-ws misses punctuation drift (by design)")
    sc.check(pair not in set(cell_flags[("g4-userreach", "t2-punct", "r-any")]),
             "tournament: g4-userreach misses returned copy (not at a send call)")
    sc.check(pair not in set(cell_flags[("g1-verbatim3", "t2-punct", "r-any")]),
             "tournament: g1-verbatim3 misses it (nearest verbatim marker is "
             "7 lines away, at line 160)")
    sc.check(pair in set(cell_flags[("g2-verbatim10", "t2-punct", "r-any")]),
             "tournament: g2-verbatim10 catches it (marker at line 160)")


# ---- main ---------------------------------------------------------------------

def compute_everything():
    sc = SelfCheck()
    results = {
        "pins": {k: v[1] for k, v in PINS.items()},
        "grid": {"grammars": list(GRAMMARS), "tiers": list(TIERS),
                 "gatings": list(GATINGS),
                 "scan_root": SCAN_ROOT, "oracle_root": ORACLE_ROOT,
                 "min_norm_len": MIN_NORM_LEN,
                 "fuzzy": {"threshold": FUZZY_THRESHOLD,
                           "max_norm_len": FUZZY_MAX_NORM_LEN,
                           "block_tokens": FUZZY_BLOCK_TOKENS,
                           "len_window": FUZZY_LEN_WINDOW},
                 "verbatim_windows": dict(VERBATIM_WINDOWS),
                 "user_call_names": sorted(USER_CALL_NAMES),
                 "seed": SEED, "plant_per_grammar": PLANT_PER_GRAMMAR},
        "determinism": "checked-by-byte-identical-rerun",
    }

    roots = {}
    for corpus in sorted(PINS):
        root, head = ensure_corpus(corpus)
        sc.check(head == PINS[corpus][1], "%s: corpus HEAD == pinned SHA" % corpus)
        roots[corpus] = root

    rebuild = extract_rebuild(roots["superbot-next"])
    oracle = extract_oracle(roots["superbot"])
    matcher = Matcher(oracle.keys())

    results["meta"] = {
        "rebuild_py_files": len(py_files(roots["superbot-next"], SCAN_ROOT)),
        "oracle_py_files": len(py_files(roots["superbot"], ORACLE_ROOT)),
        "oracle_distinct_literals": len(oracle),
        "oracle_eligible_literals": len(matcher.elig),
        "grammar_distinct_literals": {g: len(rebuild[g]) for g in GRAMMARS},
        "grammar_eligible_literals": {
            g: sum(1 for v in rebuild[g] if eligible(v)) for g in GRAMMARS},
    }
    sc.check(results["meta"]["rebuild_py_files"] == 528,
             "rebuild: 528 py files under sb/ (got %d)"
             % results["meta"]["rebuild_py_files"])

    # the sweep: every cell
    cell_flags = {}
    for g in GRAMMARS:
        for t in TIERS:
            for r in GATINGS:
                cell_flags[(g, t, r)] = matcher.flags(rebuild[g], t, r)
    for (g, t, r), fl in cell_flags.items():
        if t == "t0-byte":
            sc.check(len(fl) == 0, "t0-byte flags nothing (%s,%s)" % (g, r))

    invariant_checks(sc, cell_flags)
    tournament_checks(sc, rebuild, oracle, cell_flags)

    with open(os.path.join(HERE, "labels.json"), encoding="utf-8") as fh:
        labels = json.load(fh)

    full_domain, samples = audit_domains(cell_flags)
    lmap, per_cell, auto_n = join_labels(cell_flags, full_domain, samples,
                                         labels, matcher, sc)
    results["audit"] = {
        "full_domain_pairs": len(full_domain),
        "auto_classified_pairs": auto_n,
        "samples": {k: len(v) for k, v in samples.items()},
        "sample_populations": {
            "g6-t2": len(cell_flags[("g6-all", "t2-punct", "r-any")]),
            "g6-t3": len(cell_flags[("g6-all", "t3-case", "r-any")]),
            "g6-t4": len(cell_flags[("g6-all", "t4-fuzzy", "r-any")]),
            "gsmall-t4": len(set().union(*(
                set(cell_flags[(g, "t4-fuzzy", "r-any")]) for g in FULL_GRAMS))),
        },
        "labeled_pairs_total": len(labels["pairs"]),
    }
    results["sweep"] = per_cell

    # per-pair detail for the audited superset (sites + labels + attribution)
    detail = []
    for n_lit, o_lit in sorted(set(full_domain)
                               | set().union(*(set(v) for v in samples.values()))):
        rec = lmap.get(pair_key(n_lit, o_lit))
        min_tier = {}
        for g in GRAMMARS:
            for t in ("t1-ws", "t2-punct", "t3-case", "t4-fuzzy"):
                if (n_lit, o_lit) in set(cell_flags[(g, t, "r-any")]):
                    min_tier[g] = t
                    break
        detail.append({
            "n": n_lit, "o": o_lit,
            "n_sites": ["%s:%d" % s for s in
                        rebuild["g6-all"].get(n_lit, [])][:MAX_SITES],
            "o_sites": ["%s:%d" % s for s in oracle.get(o_lit, [])][:MAX_SITES],
            "has_exact_oracle_match": n_lit in matcher.pool_set,
            "min_tier_by_grammar": min_tier,
            "verdict": rec["verdict"] if rec else None,
            "class": rec.get("class") if rec else None,
            "reason": rec.get("reason") if rec else None,
            "provenance": rec.get("provenance") if rec else None,
        })
    results["pairs"] = detail

    # planted-drift layer
    plan = plant_drifts(rebuild, matcher, sc)
    results["planted"] = {
        "seed": SEED,
        "plan": {g: plan[g] for g in GRAMMARS},
        "recall": planted_recall(plan, rebuild, matcher, sc),
    }

    # frontier claims the ruling rests on (asserted so drift = red run)
    def cell(g, t, r):
        return per_cell["|".join((g, t, r))]
    win = cell(*WINNING_CELL)
    sc.check(win["tc"] == 1 and win["fp"] == 0 and win["unlabeled"] == 0,
             "frontier: winning cell %s = 1 TC / 0 FP, fully audited (got "
             "tc=%d fp=%d unl=%d)" % ("|".join(WINNING_CELL), win["tc"],
                                      win["fp"], win["unlabeled"]))
    g3w = cell("g3-refusal", "t3-case", "r-noexact")
    sc.check(g3w["tc"] == 1 and g3w["fp"] == 0,
             "frontier: g3-refusal|t3-case|r-noexact is also 1 TC / 0 FP "
             "(g5 == g3 on the real tree; g4-userreach contributes nothing)")
    sc.check(all(cell(g, t, r)["tc"] == 0
                 for g in ("g1-verbatim3", "g4-userreach")
                 for t in ("t1-ws", "t2-punct", "t3-case")
                 for r in GATINGS),
             "frontier: g1-verbatim3 (marker 7 lines away) and g4-userreach "
             "(returned copy) MISS every true drift at exact tiers")
    g6t1 = cell("g6-all", "t1-ws", "r-noexact")
    sc.check(g6t1["tc"] == 2 and g6t1["fp"] == 38,
             "frontier: widening to g6-all|t1-ws|r-noexact buys the 2 "
             "double-space hint drifts at 38 audited FPs (got tc=%d fp=%d)"
             % (g6t1["tc"], g6t1["fp"]))
    g6t2 = cell("g6-all", "t2-punct", "r-noexact")
    sc.check(g6t2["tc"] == 3,
             "frontier: g6-all|t2-punct|r-noexact reaches all 3 true drifts "
             "(at 68 labeled FPs + 138 unlabeled-sampled pairs)")
    n_td = sum(1 for rec in labels["pairs"] if rec["verdict"] == "true-drift")
    sc.check(n_td == 3,
             "audit total: exactly 3 hand-audited true-drift pairs exist on "
             "the real corpora (got %d)" % n_td)

    # tournament evidence block (the done-when citation, machine-checkable)
    results["tournament_instance"] = {
        "pair": {"n": TOURNAMENT_N, "o": TOURNAMENT_O},
        "n_site": "%s:%d" % TOURNAMENT_N_SITE,
        "o_sites": ["%s:%d" % s for s in TOURNAMENT_O_SITES],
        "caught_by_winning_cell": (TOURNAMENT_N, TOURNAMENT_O) in set(
            cell_flags[WINNING_CELL]),
        "winning_cell": "|".join(WINNING_CELL),
    }
    sc.check(results["tournament_instance"]["caught_by_winning_cell"],
             "tournament: caught by the winning cell %s"
             % "|".join(WINNING_CELL))
    results["winning_cell"] = {
        "grammar": WINNING_CELL[0], "tier": WINNING_CELL[1],
        "gating": WINNING_CELL[2],
        "tc": win["tc"], "fp": win["fp"],
        "planted_recall": results["planted"]["recall"]["g5-msg"][
            "t3-case|r-noexact"],
    }

    results["self_checks"] = {"passed": sc.passed, "failed": sc.failed}
    return sc, results


def summarize(results):
    lines = []
    lines.append("== verdict-013 oracle-copy drift sweep ==")
    m = results["meta"]
    lines.append("rebuild sb/: %d py files; oracle disbot/: %d py files, "
                 "%d distinct literals (%d eligible)"
                 % (m["rebuild_py_files"], m["oracle_py_files"],
                    m["oracle_distinct_literals"], m["oracle_eligible_literals"]))
    lines.append("grammar sizes (distinct/eligible literals): "
                 + "  ".join("%s %d/%d" % (g, m["grammar_distinct_literals"][g],
                                           m["grammar_eligible_literals"][g])
                             for g in GRAMMARS))
    lines.append("\ncell (grammar|tier|gating): flagged TC FP "
                 "[true-drift/intentional/false-pair/unlabeled]")
    for key in sorted(results["sweep"]):
        n = results["sweep"][key]
        lines.append("  %-38s %5d %3d %4d  [%d/%d/%d/%d]" % (
            key, n["flagged"], n["tc"], n["fp"], n["true-drift"],
            n["intentional-change"], n["false-pair"], n["unlabeled"]))
    lines.append("\nplanted recall (per grammar, tier|gating -> caught/planted):")
    for g in GRAMMARS:
        rec = results["planted"]["recall"][g]
        if not rec:
            lines.append("  %-14s (no verbatim byte-pairs to plant)" % g)
            continue
        parts = []
        for t in ("t1-ws", "t2-punct", "t3-case", "t4-fuzzy"):
            r = rec["%s|r-noexact" % t]
            parts.append("%s %d/%d" % (t, r["caught"], r["planted"]))
        lines.append("  %-14s %s" % (g, "  ".join(parts)))
    ti = results["tournament_instance"]
    lines.append("\ntournament.py:153 instance: pair (%r vs %r) at %s vs %s -> "
                 "caught by winning cell %s: %s"
                 % (ti["pair"]["n"], ti["pair"]["o"], ti["n_site"],
                    ", ".join(ti["o_sites"]), ti["winning_cell"],
                    ti["caught_by_winning_cell"]))
    a = results["audit"]
    lines.append("audit: %d full-domain pairs + samples %s (populations %s); "
                 "%d labeled pairs total"
                 % (a["full_domain_pairs"], a["samples"],
                    a["sample_populations"], a["labeled_pairs_total"]))
    return "\n".join(lines)


def main():
    sc, results = compute_everything()
    sc2, results2 = compute_everything()
    j1 = json.dumps(results, sort_keys=True)
    j2 = json.dumps(results2, sort_keys=True)
    sc.check(j1 == j2, "determinism: two in-process computations byte-identical")

    print(summarize(results))
    results["self_checks"] = {"passed": sc.passed, "failed": sc.failed}
    with open(os.path.join(HERE, "results.json"), "w", encoding="utf-8") as fh:
        json.dump(results, fh, sort_keys=True, indent=1, ensure_ascii=True)
        fh.write("\n")
    ok = sc.report()
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
