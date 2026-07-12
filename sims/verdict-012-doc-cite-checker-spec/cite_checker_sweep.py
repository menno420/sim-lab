#!/usr/bin/env python3
"""verdict-012 -- doc-cite-checker spec sweep (idea-engine PROPOSAL 010).

Settles which spec `tools/check_doc_cites.py` (superbot-next) should ship with:
sweeps the cite-rule ladder (a: file-exists / b: +line-range<=EOF / c: +identifier
near cited lines) x cite-grammar variants x doc-tree-scope variants x path-
resolution policies over TWO evidence layers:

  1. a SYNTHETIC corpus with planted, labeled cites (exact precision/recall), and
  2. the two REAL pinned corpora:
       superbot-next @ 2c62a099973a2ee384af51e9a33074d9cd411002
       superbot      @ b2b7fe0ce02a2a68cc18eac5242ab160b7b4330f
     where every flagged cite of the audited variants carries a hand-audited
     classification (labels.json) -> true-catch vs false-positive counts.

Corpora are fetched ON RUN into ./corpora/<name> (gitignored) via shallow
`git fetch origin <sha>`; SHA-pinning keeps the content deterministic, so the
cache is a transport detail, not an input degree of freedom.

Run (the one command):

    python3 sims/verdict-012-doc-cite-checker-spec/cite_checker_sweep.py

Exit 0 iff all self-checks pass. Deterministic: NO RNG anywhere (the rule-c
audit sample is a fixed stride over the sorted flag list); byte-identical
re-runs (results.json is canonical JSON, no timestamps).

Stdlib-only. SelfCheck battery vendor-copied from harness/simharness.py
(sims never import harness at runtime).
"""

import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))

PINS = {
    "superbot-next": ("https://github.com/menno420/superbot-next.git",
                      "2c62a099973a2ee384af51e9a33074d9cd411002"),
    "superbot": ("https://github.com/menno420/superbot.git",
                 "b2b7fe0ce02a2a68cc18eac5242ab160b7b4330f"),
}

# Cite grammar: the canonical idea's source-extension set (superbot
# docs/ideas/rebuild-design-cite-checker-2026-07-04.md: "known source ext
# .py/.ts/.tsx/.yml" + .yaml).
EXTS = ("py", "ts", "tsx", "yml", "yaml")

# Token candidates (the LOOSE shape); grammar variants are predicates on top.
CITE_RX = re.compile(
    r"(?<![\w/.-])((?:[\w.-]+/)*[\w.-]+\.(?:%s)):(\d+)(?:-(\d+))?" % "|".join(EXTS)
)

# A path segment that is not line-number debris ('163-168/x.py' regex-glue
# artifact seen live in superbot runtime-logic-mechanics doc) or ellipsis
# ('..._supervisor.py' seen live in strand-1 05-ops-kernel-rails).
SEG_HAS_LETTER = re.compile(r"[A-Za-z_]")

GRAMMARS = ("g1-loose", "g2-strict-slash", "g3-strict-guard")
FENCES = ("keep", "skip")          # count cites inside ``` fenced blocks, or not
SCOPES = ("all-md", "docs-only")
POLICIES = ("exact", "suffix", "foreign-skip")  # path resolution
RUNGS = ("a", "b", "c")

# Known-foreign first segments (cross-repo / library roots), per corpus.
# superbot-next docs cite the LEGACY superbot tree (disbot/, views/, cogs/,
# utils/, scripts/) and discord.py internals (ext/). superbot docs cite the
# NEXT tree (sb/), the extracted kit (substrate-kit/), and discord.py (ext/).
# NOTE the measured blind spot: superbot-next test paths (tests/unit/...)
# cited from superbot COLLIDE with superbot's own tests/ root, so first-
# segment foreign-skip cannot remove those -- reported, not hidden.
FOREIGN = {
    "superbot-next": ("disbot/", "views/", "cogs/", "utils/", "scripts/", "ext/"),
    "superbot": ("sb/", "substrate-kit/", "ext/"),
}

C_WINDOW = 20      # rule-c: identifier must appear within +/- this many lines
C_SAMPLE_N = 15    # rule-c real-corpus audit sample size (stated, not silent)

ID_RX = re.compile(r"`([A-Za-z_][A-Za-z0-9_]{3,})`")
ID_STOP = {"None", "True", "False", "self", "async", "await", "return",
           "import", "class", "print"}


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


# ---- corpus fetch / index ---------------------------------------------------

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


class Tree:
    """File index over a corpus (real dir or synthetic dict path->text)."""

    def __init__(self, files, get_text):
        self.files = sorted(files)
        self.fileset = set(files)
        self.by_base = {}
        for f in self.files:
            self.by_base.setdefault(f.rsplit("/", 1)[-1], []).append(f)
        self._get_text = get_text
        self._nlines = {}
        self._lines = {}

    @classmethod
    def from_dir(cls, root):
        files = []
        for dp, dns, fns in os.walk(root):
            dns[:] = [d for d in dns if d != ".git"]
            for fn in fns:
                files.append(os.path.relpath(os.path.join(dp, fn), root)
                             .replace(os.sep, "/"))
        def get_text(rel):
            with open(os.path.join(root, rel), encoding="utf-8",
                      errors="replace") as fh:
                return fh.read()
        return cls(files, get_text)

    @classmethod
    def from_dict(cls, d):
        return cls(list(d), lambda rel: d[rel])

    def text(self, rel):
        if rel not in self._lines:
            self._lines[rel] = self._get_text(rel).splitlines()
        return self._lines[rel]

    def nlines(self, rel):
        if rel not in self._nlines:
            self._nlines[rel] = len(self.text(rel))
        return self._nlines[rel]

    def mds(self):
        return [f for f in self.files if f.endswith(".md")]


# ---- extraction -------------------------------------------------------------

def extract_cites(tree):
    """All cite tokens from every .md, with fence state and same-line ids."""
    out = []
    for md in tree.mds():
        in_fence = False
        for lineno, line in enumerate(tree.text(md), 1):
            if line.lstrip().startswith("```"):
                in_fence = not in_fence
                continue
            for m in CITE_RX.finditer(line):
                path, s, e = m.group(1), int(m.group(2)), m.group(3)
                e = int(e) if e else s
                ids = [i for i in ID_RX.findall(line)
                       if i not in ID_STOP and "." not in i
                       and i != path.rsplit("/", 1)[-1].split(".")[0]]
                out.append({
                    "doc": md, "lineno": lineno, "path": path,
                    "start": s, "end": e, "fenced": in_fence,
                    "ids": ids, "line": line.strip(),
                })
    return out


def grammar_ok(cite, grammar):
    p = cite["path"]
    if grammar == "g1-loose":
        return True
    if "/" not in p:
        return False
    if grammar == "g2-strict-slash":
        return True
    # g3-strict-guard: every segment carries a letter/underscore; no ellipsis
    if "..." in p:
        return False
    return all(SEG_HAS_LETTER.search(seg) for seg in p.split("/"))


def resolve(tree, path, policy, corpus):
    """-> (status, candidates). status: skipped|exact|suffix|ambiguous|missing."""
    if policy == "foreign-skip" and any(
            path.startswith(pre) for pre in FOREIGN.get(corpus, ())):
        return "skipped", []
    if path in tree.fileset:
        return "exact", [path]
    if policy == "exact":
        return "missing", []
    base = path.rsplit("/", 1)[-1]
    if "/" in path:
        cands = [t for t in tree.by_base.get(base, []) if t.endswith("/" + path)]
    else:
        cands = list(tree.by_base.get(base, []))
    if len(cands) == 1:
        return "suffix", cands
    if len(cands) > 1:
        return "ambiguous", cands
    return "missing", []


def judge(tree, cite, policy, corpus):
    """-> (status, flag_rung_or_None, detail). Rung result for the FULL ladder:
    'a' = file missing; 'b' = resolved but range > EOF; 'c' = in-range but no
    same-line identifier within +/-C_WINDOW; None = passes all three."""
    status, cands = resolve(tree, cite["path"], policy, corpus)
    if status == "skipped":
        return status, None, ""
    if status == "missing":
        return status, "a", "file not found"
    if status == "ambiguous":
        # unverifiable-pass policy (favors no-false-positive)
        return status, None, "%d basename candidates" % len(cands)
    maxn = max(tree.nlines(c) for c in cands)
    if cite["end"] > maxn:
        return status, "b", "cited %d-%d > EOF %d" % (cite["start"], cite["end"], maxn)
    if len(cands) == 1 and cite["ids"]:
        src = tree.text(cands[0])
        lo = max(0, cite["start"] - 1 - C_WINDOW)
        hi = min(len(src), cite["end"] + C_WINDOW)
        window = "\n".join(src[lo:hi])
        if not any(i in window for i in cite["ids"]):
            return status, "c", "ids %s not within +/-%d lines" % (
                ",".join(cite["ids"][:3]), C_WINDOW)
    return status, None, ""


# ---- sweep ------------------------------------------------------------------

def in_scope(doc, scope):
    return scope == "all-md" or doc.startswith("docs/")


def sweep_corpus(tree, cites, corpus):
    """Full variant grid. Returns (table, flags) where flags maps
    (grammar,fence,scope,policy) -> list of per-cite flag records."""
    table = {}
    flags = {}
    # memo: judgement per (cite index, policy)
    memo = {}
    for gi, grammar in enumerate(GRAMMARS):
        gsel = [c for c in cites if grammar_ok(c, grammar)]
        for fence in FENCES:
            fsel = [c for c in gsel if fence == "keep" or not c["fenced"]]
            for scope in SCOPES:
                ssel = [c for c in fsel if in_scope(c["doc"], scope)]
                for policy in POLICIES:
                    key = (grammar, fence, scope, policy)
                    n = {"cites": len(ssel), "skipped": 0, "ambiguous": 0,
                         "a": 0, "b": 0, "c": 0}
                    fl = []
                    for c in ssel:
                        mkey = (id(c), policy)
                        if mkey not in memo:
                            memo[mkey] = judge(tree, c, policy, corpus)
                        status, rung, detail = memo[mkey]
                        if status == "skipped":
                            n["skipped"] += 1
                            continue
                        if status == "ambiguous":
                            n["ambiguous"] += 1
                        if rung:
                            n[rung] += 1
                            fl.append({
                                "doc": c["doc"], "lineno": c["lineno"],
                                "cite": "%s:%d%s" % (c["path"], c["start"],
                                        "-%d" % c["end"] if c["end"] != c["start"] else ""),
                                "path": c["path"], "rung": rung,
                                "detail": detail, "line": c["line"][:200],
                            })
                    table["|".join(key)] = n
                    flags[key] = fl
    return table, flags


# ---- synthetic corpus (evidence layer 1) ------------------------------------

def synthetic_tree():
    files = {}
    files["pkg/core/main.py"] = "\n".join(
        ["# main module"] + ["x%d = %d" % (i, i) for i in range(2, 48)]
        + ["class MainRunner:", "    '''runner'''", "    def run(self):",
           "        return 1", "    done = True"]
        + ["y%d = %d" % (i, i) for i in range(53, 101)]) + "\n"
    files["pkg/services/util/helpers.py"] = "\n".join(
        ["# helpers"] + ["h%d = %d" % (i, i) for i in range(2, 30)]
        + ["def compute_total(xs):", "    return sum(xs)"]
        + ["z%d = %d" % (i, i) for i in range(32, 61)]) + "\n"
    files["pkg/adapters/panel.py"] = "\n".join(
        ["# panel"] + ["p%d = %d" % (i, i) for i in range(2, 41)]) + "\n"
    files["pkg/a/dup.py"] = "a = 1\nb = 2\nc = 3\n"
    files["pkg/b/dup.py"] = "a = 1\nb = 2\nc = 3\n"
    files["parity/config.yml"] = "key: value\nother: 2\n"
    # the doc under test -- each planted cite is labeled P1..P10 in comments
    files["docs/design/spec.md"] = "\n".join([
        "# design spec (synthetic)",
        "",
        "P1 valid: the runner lives at `pkg/core/main.py:48-52` (`MainRunner`).",
        "P2 fabricated (the WorkflowResult twin): `pkg/core/contracts.py:48-52`",
        "   defines `WorkflowResult`.",
        "P3 out-of-range: see `pkg/core/main.py:400` for the epilogue.",
        "P4 wrong identifier: `pkg/adapters/panel.py:10-12` holds `NonexistentThing`.",
        "",
        "```",
        "P5 fenced: log cites phantom/thing.py:9 inside a code block",
        "```",
        "",
        "P6 cross-repo: `otherrepo/sb/domain/ops.py:5` (in the sibling repo).",
        "P7 bare noise: rename foo.py:12 style strings in prose.",
        "P8 relative (suffix-resolvable): `services/util/helpers.py:30`",
        "   (`compute_total`).",
        "P9 ambiguous bare: dup.py:3 could be either copy.",
        "P10 valid yml: `parity/config.yml:2`.",
    ]) + "\n"
    return Tree.from_dict(files)


# Expected flag outcome per planted cite, derived BY HAND from the spec
# semantics (not from the engine code): each entry gives a predicate over
# (grammar, fence, policy) -> expected rung flag or None.
def synthetic_expected(grammar, fence, policy):
    strict = grammar != "g1-loose"
    exp = {}
    exp["pkg/core/main.py:48-52"] = None                                   # P1
    exp["pkg/core/contracts.py:48-52"] = "a"                               # P2
    exp["pkg/core/main.py:400"] = "b"                                      # P3
    exp["pkg/adapters/panel.py:10-12"] = "c"                               # P4
    exp["phantom/thing.py:9"] = None if fence == "skip" else "a"           # P5
    exp["otherrepo/sb/domain/ops.py:5"] = (None if policy == "foreign-skip"
                                           else "a")                       # P6
    exp["foo.py:12"] = None if strict else "a"                             # P7 (bare)
    exp["services/util/helpers.py:30"] = ("a" if policy == "exact"
                                          else None)                       # P8
    # P9: ambiguous bare name -- unverifiable-pass under suffix resolution,
    # but the exact policy cannot resolve bare names at all, so it flags.
    exp["dup.py:3"] = "a" if policy == "exact" else None
    exp["parity/config.yml:2"] = None                                      # P10
    # bare cites never extracted under strict grammars: drop from expectation
    if strict:
        for k in ("foo.py:12", "dup.py:3"):
            exp[k] = None
    return exp


def run_synthetic(sc):
    tree = synthetic_tree()
    cites = extract_cites(tree)
    sc.check(len(cites) == 10, "synthetic: 10 planted cites extracted (got %d)"
             % len(cites))
    results = {}
    # foreign roots for the synthetic corpus
    FOREIGN["synthetic"] = ("otherrepo/",)
    truth_positive = {"pkg/core/contracts.py:48-52", "pkg/core/main.py:400",
                      "pkg/adapters/panel.py:10-12"}
    for grammar in GRAMMARS:
        for fence in FENCES:
            for policy in POLICIES:
                exp = synthetic_expected(grammar, fence, policy)
                got = {}
                for c in cites:
                    if not grammar_ok(c, grammar):
                        continue
                    if fence == "skip" and c["fenced"]:
                        continue
                    key = "%s:%d%s" % (c["path"], c["start"],
                          "-%d" % c["end"] if c["end"] != c["start"] else "")
                    status, rung, _ = judge(tree, c, policy, "synthetic")
                    got[key] = rung
                for key, want in exp.items():
                    have = got.get(key)
                    sc.check(have == want,
                             "synthetic %s/%s/%s %s: want %s got %s"
                             % (grammar, fence, policy, key, want, have))
                flagged = {k for k, v in got.items() if v}
                tp = len(flagged & truth_positive)
                fp = len(flagged - truth_positive)
                fn = len(truth_positive - flagged)
                prec = tp / (tp + fp) if (tp + fp) else 1.0
                rec = tp / (tp + fn) if (tp + fn) else 1.0
                results["|".join((grammar, fence, policy))] = {
                    "tp": tp, "fp": fp, "fn": fn,
                    "precision": round(prec, 4), "recall": round(rec, 4)}
    # headline synthetic checks
    best = results["g3-strict-guard|skip|foreign-skip"]
    sc.check(best["precision"] == 1.0 and best["recall"] == 1.0,
             "synthetic: frontier variant (g3/skip/foreign-skip) P=R=1.0")
    worst = results["g1-loose|keep|exact"]
    sc.check(worst["fp"] == 5,
             "synthetic: loosest variant has exactly 5 FPs (fenced, cross-repo,"
             " bare-noise, relative, ambiguous-bare) (got %d)" % worst["fp"])
    return results


# ---- real-corpus audit (labels) ----------------------------------------------

AUDIT_VARIANT = ("g1-loose", "keep", "all-md", "suffix")


def label_key(corpus, doc, path):
    return "%s|%s|%s" % (corpus, doc, path)


def classify_flags(corpus, flags, labels, sc, results):
    """Join the audited variant's flags against labels.json; assert coverage."""
    fl = flags[AUDIT_VARIANT]
    a_pairs = sorted({(f["doc"], f["path"]) for f in fl if f["rung"] == "a"})
    b_pairs = sorted({(f["doc"], f["path"]) for f in fl if f["rung"] == "b"})
    c_pairs = sorted({(f["doc"], f["path"]) for f in fl if f["rung"] == "c"})

    out = {"a": {"true-catch": 0, "false-positive": 0, "pairs": []},
           "b": {"true-catch": 0, "false-positive": 0, "pairs": []},
           "c_sampled": {"true-catch": 0, "false-positive": 0,
                         "sample": [], "population_pairs": len(c_pairs)}}
    for rung, pairs in (("a", a_pairs), ("b", b_pairs)):
        for doc, path in pairs:
            k = label_key(corpus, doc, path)
            lab = labels["rule_" + rung].get(k)
            if not sc.check(lab is not None,
                            "label coverage: rule-%s %s" % (rung, k)):
                continue
            out[rung][lab["verdict"]] += 1
            out[rung]["pairs"].append({"doc": doc, "path": path,
                                       "class": lab["class"],
                                       "verdict": lab["verdict"],
                                       "reason": lab["reason"]})
    # rule c: explicit deterministic sample (sorted pairs, fixed stride)
    if c_pairs:
        stride = max(1, len(c_pairs) // C_SAMPLE_N)
        sample = c_pairs[::stride][:C_SAMPLE_N]
        for doc, path in sample:
            k = label_key(corpus, doc, path)
            lab = labels["rule_c_sample"].get(k)
            if not sc.check(lab is not None,
                            "label coverage: rule-c sample %s" % k):
                continue
            out["c_sampled"][lab["verdict"]] += 1
            out["c_sampled"]["sample"].append({"doc": doc, "path": path,
                                               "class": lab["class"],
                                               "verdict": lab["verdict"],
                                               "reason": lab["reason"]})
    results["audit"][corpus] = out
    return out


def per_variant_audit(corpus, flags, labels, tree, sc, results):
    """Join EVERY variant's rule-a/rule-b flags against the audit labels ->
    per-variant true-catch / false-positive counts (unique doc,path pairs).
    Flags outside the audited superset are only possible under the exact
    policy (relative-or-ambiguous paths that suffix-resolution absorbs);
    those are auto-classified false-positive 'relative-path (suffix-
    resolvable)'. Anything else unlabeled is a self-check failure."""
    out = {}
    for key, fl in flags.items():
        cnt = {"a_tc": 0, "a_fp": 0, "b_tc": 0, "b_fp": 0, "c_pairs": 0}
        for rung in ("a", "b"):
            pairs = sorted({(f["doc"], f["path"]) for f in fl
                            if f["rung"] == rung})
            for doc, path in pairs:
                lab = labels["rule_" + rung].get(label_key(corpus, doc, path))
                if lab is not None:
                    verdict = lab["verdict"]
                else:
                    st, _ = resolve(tree, path, "suffix", corpus)
                    if rung == "a" and st in ("suffix", "ambiguous"):
                        verdict = "false-positive"  # auto: exact-only relative
                    else:
                        sc.check(False, "per-variant label gap: %s %s %s|%s"
                                 % (corpus, rung, doc, path))
                        continue
                cnt[rung + ("_tc" if verdict == "true-catch" else "_fp")] += 1
        cnt["c_pairs"] = len({(f["doc"], f["path"]) for f in fl
                              if f["rung"] == "c"})
        out["|".join(key)] = cnt
    results.setdefault("per_variant_audit", {})[corpus] = out


def fabrication_check(sc, trees, all_cites, results):
    """The known fabrication class: WorkflowResult @ disbot/core/contracts.py."""
    sb = trees["superbot"]
    absent = "disbot/core/contracts.py" not in sb.fileset
    real = "disbot/services/lifecycle/contracts.py" in sb.fileset
    sc.check(absent, "fabrication: disbot/core/contracts.py ABSENT from "
                     "superbot tree @ b2b7fe0")
    sc.check(real, "fabrication: real analogue disbot/services/lifecycle/"
                   "contracts.py EXISTS in superbot tree")
    hits = [c for c in all_cites["superbot"]
            if c["path"] in ("disbot/core/contracts.py", "core/contracts.py")]
    sc.check(len(hits) >= 5,
             "fabrication: >=5 cite instances of the fabricated path found in "
             "superbot *.md (got %d)" % len(hits))
    caught = {}
    for grammar in GRAMMARS:
        ok = all(judge(sb, c, "suffix", "superbot")[1] == "a"
                 for c in hits if grammar_ok(c, grammar))
        n = sum(1 for c in hits if grammar_ok(c, grammar))
        caught[grammar] = {"instances_in_grammar": n, "all_rung_a_flagged": ok}
        sc.check(ok and n == len(hits),
                 "fabrication: %s flags all %d instances at rung a" %
                 (grammar, len(hits)))
    results["fabrication_check"] = {
        "disbot_core_contracts_py_in_tree": not absent,
        "real_analogue_disbot_services_lifecycle_contracts_py": real,
        "cite_instances_found": sorted(
            {"%s:%d" % (c["doc"], c["lineno"]) for c in hits}),
        "caught_by": caught,
        "note": ("every surviving instance in the tree is a meta-mention that "
                 "DOCUMENTS the fabrication (correction notes / the canonical "
                 "idea file); rule (a) flags them all -- a live fabrication is "
                 "byte-identical to the checker, so the class IS caught, and a "
                 "red gate therefore needs a waiver mechanism for intentional "
                 "absent-path mentions"),
    }


# ---- invariants --------------------------------------------------------------

def invariant_checks(sc, flags_by_corpus):
    def fset(flags, key):
        return {(f["doc"], f["lineno"], f["cite"], f["rung"]) for f in flags[key]}
    for corpus, flags in flags_by_corpus.items():
        for fence in FENCES:
            for scope in SCOPES:
                for policy in POLICIES:
                    g1 = fset(flags, ("g1-loose", fence, scope, policy))
                    g2 = fset(flags, ("g2-strict-slash", fence, scope, policy))
                    g3 = fset(flags, ("g3-strict-guard", fence, scope, policy))
                    sc.check(g3 <= g2 <= g1,
                             "%s: grammar monotonicity %s/%s/%s"
                             % (corpus, fence, scope, policy))
        for grammar in GRAMMARS:
            for scope in SCOPES:
                for policy in POLICIES:
                    skip = fset(flags, (grammar, "skip", scope, policy))
                    keep = fset(flags, (grammar, "keep", scope, policy))
                    sc.check(skip <= keep,
                             "%s: fence-skip subset %s/%s/%s"
                             % (corpus, grammar, scope, policy))
        for grammar in GRAMMARS:
            for fence in FENCES:
                for policy in POLICIES:
                    docs = fset(flags, (grammar, fence, "docs-only", policy))
                    alls = fset(flags, (grammar, fence, "all-md", policy))
                    sc.check(docs <= alls,
                             "%s: docs-scope subset %s/%s/%s"
                             % (corpus, grammar, fence, policy))
        for grammar in GRAMMARS:
            for fence in FENCES:
                for scope in SCOPES:
                    fo = fset(flags, (grammar, fence, scope, "foreign-skip"))
                    su = fset(flags, (grammar, fence, scope, "suffix"))
                    sc.check(fo <= su,
                             "%s: foreign-skip subset %s/%s/%s"
                             % (corpus, grammar, fence, scope))


# ---- main --------------------------------------------------------------------

def compute_everything():
    sc = SelfCheck()
    results = {"pins": {k: v[1] for k, v in PINS.items()},
               "grid": {"grammars": list(GRAMMARS), "fences": list(FENCES),
                        "scopes": list(SCOPES), "policies": list(POLICIES),
                        "rungs": list(RUNGS), "exts": list(EXTS),
                        "c_window": C_WINDOW, "c_sample_n": C_SAMPLE_N,
                        "foreign_roots": {k: list(v) for k, v in FOREIGN.items()
                                          if k in PINS}},
               "audit": {}, "determinism": "checked-by-byte-identical-rerun"}

    results["synthetic"] = run_synthetic(sc)

    with open(os.path.join(HERE, "labels.json"), encoding="utf-8") as fh:
        labels = json.load(fh)

    trees, all_cites, flags_by_corpus = {}, {}, {}
    for corpus in sorted(PINS):
        root, head = ensure_corpus(corpus)
        sc.check(head == PINS[corpus][1],
                 "%s: corpus HEAD == pinned SHA" % corpus)
        tree = Tree.from_dir(root)
        trees[corpus] = tree
        cites = extract_cites(tree)
        all_cites[corpus] = cites
        table, flags = sweep_corpus(tree, cites, corpus)
        flags_by_corpus[corpus] = flags
        results.setdefault("sweep", {})[corpus] = table
        results.setdefault("meta", {})[corpus] = {
            "md_files": len(tree.mds()), "files": len(tree.files),
            "cites_loose_keep_all": len(cites)}
        classify_flags(corpus, flags, labels, sc, results)
        per_variant_audit(corpus, flags, labels, tree, sc, results)
        # store the audited variant's full flag list (the "flagged cite lines")
        results.setdefault("flagged", {})[corpus] = sorted(
            flags[AUDIT_VARIANT],
            key=lambda f: (f["doc"], f["lineno"], f["cite"], f["rung"]))

    fabrication_check(sc, trees, all_cites, results)
    invariant_checks(sc, flags_by_corpus)

    # frontier claims the ruling rests on (asserted so drift = red run)
    def cell(corpus, g, f, s, p):
        return results["sweep"][corpus]["|".join((g, f, s, p))]
    fr_next = cell("superbot-next", "g3-strict-guard", "skip", "all-md",
                   "foreign-skip")
    sc.check(fr_next["a"] == 0 and fr_next["b"] == 0,
             "frontier: superbot-next g3/skip/all-md/foreign-skip has 0 rule-a "
             "and 0 rule-b flags (got a=%d b=%d)" % (fr_next["a"], fr_next["b"]))
    fr_sb = cell("superbot", "g3-strict-guard", "skip", "all-md", "foreign-skip")
    sc.check(fr_sb["a"] > 0,
             "frontier: superbot residual rule-a flags REMAIN under the same "
             "variant (red-gate NOT clean there; got a=%d)" % fr_sb["a"])
    audit_sb = results["audit"]["superbot"]
    sc.check(audit_sb["c_sampled"]["population_pairs"] > 300,
             "rule-c population on superbot is noisy-large (>300 unique pairs; "
             "got %d)" % audit_sb["c_sampled"]["population_pairs"])
    results["self_checks"] = {"passed": sc.passed, "failed": sc.failed}
    return sc, results


def summarize(results):
    lines = []
    lines.append("== verdict-012 doc-cite-checker spec sweep ==")
    for corpus in sorted(PINS):
        m = results["meta"][corpus]
        lines.append("\n-- %s @ %s: %d files, %d md, %d cite tokens "
                     "(loose/keep/all-md)" % (corpus, results["pins"][corpus][:9],
                     m["files"], m["md_files"], m["cites_loose_keep_all"]))
        lines.append("   variant (grammar|fence|scope|policy): cites a b c "
                     "skipped ambiguous")
        for key, n in sorted(results["sweep"][corpus].items()):
            lines.append("   %-52s %5d %3d %3d %3d %4d %4d" % (
                key, n["cites"], n["a"], n["b"], n["c"], n["skipped"],
                n["ambiguous"]))
        lines.append("   per-variant audited counts (unique doc,path pairs) "
                     "a-TC a-FP b-TC b-FP c-pairs:")
        for key, n in sorted(results["per_variant_audit"][corpus].items()):
            lines.append("   %-52s %4d %4d %4d %4d %5d" % (
                key, n["a_tc"], n["a_fp"], n["b_tc"], n["b_fp"], n["c_pairs"]))
        a = results["audit"][corpus]
        lines.append("   AUDIT @ %s:" % "|".join(AUDIT_VARIANT))
        lines.append("     rule-a unique(doc,path): %d true-catch, %d "
                     "false-positive" % (a["a"]["true-catch"],
                                         a["a"]["false-positive"]))
        lines.append("     rule-b unique(doc,path): %d true-catch, %d "
                     "false-positive" % (a["b"]["true-catch"],
                                         a["b"]["false-positive"]))
        lines.append("     rule-c: %d unique pairs; sampled %d -> %d "
                     "true-catch, %d false-positive"
                     % (a["c_sampled"]["population_pairs"],
                        len(a["c_sampled"]["sample"]),
                        a["c_sampled"]["true-catch"],
                        a["c_sampled"]["false-positive"]))
    fc = results["fabrication_check"]
    lines.append("\n-- fabrication check (WorkflowResult / "
                 "disbot/core/contracts.py:48-52):")
    lines.append("   in superbot tree: %s; real analogue exists: %s; cite "
                 "instances found: %d; caught at rung a by: %s" % (
                     fc["disbot_core_contracts_py_in_tree"],
                     fc["real_analogue_disbot_services_lifecycle_contracts_py"],
                     len(fc["cite_instances_found"]),
                     ", ".join(g for g, v in sorted(fc["caught_by"].items())
                               if v["all_rung_a_flagged"])))
    lines.append("\n-- synthetic corpus (planted labels, exact):")
    for key, r in sorted(results["synthetic"].items()):
        lines.append("   %-38s P=%.2f R=%.2f (tp=%d fp=%d fn=%d)" % (
            key, r["precision"], r["recall"], r["tp"], r["fp"], r["fn"]))
    return "\n".join(lines)


def main():
    sc, results = compute_everything()
    # in-process determinism: recompute everything and compare canonical JSON
    sc2, results2 = compute_everything()
    j1 = json.dumps(results, sort_keys=True)
    j2 = json.dumps(results2, sort_keys=True)
    sc.check(j1 == j2, "determinism: two in-process computations byte-identical")

    print(summarize(results))
    results["self_checks"] = {"passed": sc.passed, "failed": sc.failed}
    with open(os.path.join(HERE, "results.json"), "w", encoding="utf-8") as fh:
        json.dump(results, fh, sort_keys=True, indent=1)
        fh.write("\n")
    ok = sc.report()
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
