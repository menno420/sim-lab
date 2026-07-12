#!/usr/bin/env python3
"""verdict-016 -- INTAKE-TIME fact-snapshot builder (NOT part of the sim run).

Resolves every mechanical fact any grammar cell could query -- over the union
of all three grammars' extractions from all 27 fixtures AND all enumerated
planted mutants -- against pinned local FULL-HISTORY clones, and writes
repo_facts.json. After this build the sim is hermetic: the runner never
touches git or the network.

Committed for provenance. Re-running requires the two clones with
`refs/pull/*/head` fetched (git fetch origin '+refs/pull/*/head:refs/prheads/*')
so that squash-orphaned PR-head blobs (the blobs the recorded fabrications
cite) resolve -- the same "SHA in ANY ref after a full-ref fetch" semantics
the incident ledger used. PR-title existence facts were resolved via GitHub
MCP search at intake (api.github.com direct HTTP is walled for this seat):
zero PRs titled "Add cite resolution telemetry to verdict-012 follow-up"
owner-wide; the only sim-lab PRs with "verdict-014" in the title are #53-#56
(none matching the two claimed titles); the codex bot has authored ZERO PRs
in either repo. Those MCP-verified verdicts are pinned in TITLE_FACTS below.

Usage: python3 build_snapshot.py <sim-lab-clone> <idea-engine-clone>
"""

import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import review_authenticity_sweep as sweep  # noqa: E402

PINNED = {
    "menno420/sim-lab": "aa1a3cefbafd485e9981645d97e61ed6d30e8d58",
    "menno420/idea-engine": "390a89b5c292103236fe24a3e9f9f1f89cc5c22b",
}

# MCP-verified at intake 2026-07-12 (GitHub search_pull_requests; see module
# docstring). False = no PR/branch with this exact title exists in the repo.
TITLE_FACTS = {
    "menno420/sim-lab": {
        "Add cite resolution telemetry to verdict-012 follow-up": False,
        "verdict-014: finalize coordinator ledgers": False,
        "verdict-014: canonicalize cadence catch metric": False,
        sweep.PLANT_FAKE_TITLE: False,
    },
    "menno420/idea-engine": {
        sweep.PLANT_FAKE_TITLE: False,
    },
}
BOT_PR_COUNT = {"menno420/sim-lab": 0, "menno420/idea-engine": 0}


def git(repo_dir, *args):
    return subprocess.run(["git", "-C", repo_dir] + list(args),
                          capture_output=True)


class LiveFacts(sweep.Facts):
    """Facts that resolve misses live against the pinned clones and record
    every resolved fact into self.data (which becomes repo_facts.json)."""

    def __init__(self, dirs):
        self.dirs = dirs
        data = {"repos": {}, "sha_exists": {}, "blobs": {}}
        for repo, d in sorted(dirs.items()):
            prs = git(d, "for-each-ref", "refs/prheads", "--format=%(refname:strip=2)")
            pr_numbers = sorted(int(x) for x in prs.stdout.decode().split())
            assert pr_numbers, "no refs/prheads in %s -- fetch PR heads first" % d
            br = git(d, "for-each-ref", "refs/remotes/origin", "--format=%(refname:strip=3)")
            branches = sorted(x for x in br.stdout.decode().split() if x != "HEAD")
            data["repos"][repo] = {
                "pinned_head": PINNED[repo],
                "pr_numbers": pr_numbers,
                "branches": branches,
                "pr_titles_checked": dict(sorted(TITLE_FACTS[repo].items())),
                "bot_pr_count": BOT_PR_COUNT[repo],
                "provenance": "full-history clone @ %s + refs/pull/*/head fetched "
                              "(%d PR heads); title facts via GitHub MCP search at intake "
                              "2026-07-12" % (PINNED[repo][:7], len(pr_numbers)),
            }
        super(LiveFacts, self).__init__(data)

    def sha_exists(self, repo, token):
        key = "%s|%s" % (repo, token)
        if key not in self.data["sha_exists"]:
            r = git(self.dirs[repo], "rev-parse", "--verify", "--quiet", token + "^{object}")
            exists = r.returncode == 0
            if not exists and b"ambiguous" in r.stderr:
                exists = True
            self.data["sha_exists"][key] = exists
        return super(LiveFacts, self).sha_exists(repo, token)

    def blob(self, repo, anchor, path):
        key = "%s|%s|%s" % (repo, anchor, path)
        if key not in self.data["blobs"]:
            spec = "%s:%s" % (anchor, path)
            r = git(self.dirs[repo], "cat-file", "-e", spec)
            if r.returncode != 0:
                self.data["blobs"][key] = {"exists": False, "lines": None}
            else:
                blob = git(self.dirs[repo], "cat-file", "blob", spec).stdout
                n = blob.count(b"\n")
                if blob and not blob.endswith(b"\n"):
                    n += 1
                self.data["blobs"][key] = {"exists": True, "lines": n}
        return super(LiveFacts, self).blob(repo, anchor, path)

    def pr_title_exists(self, repo, title):
        checked = self.data["repos"][repo]["pr_titles_checked"]
        if title not in checked:
            raise SystemExit("UNRESOLVED TITLE FACT (add MCP verification): %s | %r"
                             % (repo, title))
        return super(LiveFacts, self).pr_title_exists(repo, title)


def load_fixtures():
    fixtures = []
    cdir = os.path.join(HERE, "corpus")
    for fn in sorted(os.listdir(cdir)):
        if not fn.endswith(".json"):
            continue
        d = json.load(open(os.path.join(cdir, fn)))
        name = fn[:-len(".json")]
        label = ("fabricated" if name.startswith("fabricated") else
                 "genuine-question-nocite" if name.startswith("genuine-question-nocite") else
                 "genuine-question" if name.startswith("genuine-question") else
                 "genuine-quota" if name.startswith("genuine-quota") else
                 "genuine-review")
        repo = ("menno420/sim-lab" if "sim-lab" in name else "menno420/idea-engine")
        fixtures.append({"name": name, "label": label, "repo": repo, "body": d["body"]})
    fixtures.sort(key=lambda fx: fx["name"])
    return fixtures


def touch_all_claims(body, repo, facts):
    full = ("sha", "ref", "path", "line")
    for _, fn in sweep.GRAMMARS:
        for c in fn(body, repo):
            sweep.validate_claim(c, full, facts)


def main():
    dirs = {"menno420/sim-lab": sys.argv[1], "menno420/idea-engine": sys.argv[2]}
    for repo, d in dirs.items():
        head = git(d, "rev-parse", "origin/main").stdout.decode().strip()
        assert head == PINNED[repo], "clone %s origin/main %s != pinned %s" % (d, head, PINNED[repo])
    facts = LiveFacts(dirs)

    fixtures = load_fixtures()
    assert len(fixtures) == 27, len(fixtures)
    for fx in fixtures:
        touch_all_claims(fx["body"], fx["repo"], facts)

    # ledger cross-check facts (queried explicitly so the runner's pinned
    # incident checks always hit the snapshot)
    facts.sha_exists("menno420/sim-lab", "188e97c")
    facts.sha_exists("menno420/sim-lab", "5d5caff")
    for p in ("control/inbox.md", "control/outbox.md", "control/status.md"):
        facts.blob("menno420/sim-lab", "a92f7dcf63aa5332f0043a27c30bb58e3d4a1963", p)
    facts.blob("menno420/sim-lab", "477b452c2e70b7e5a6c7e981eab8b2bb97bd497a",
               "sims/verdict-014-routine-cadence-economics/REPORT.md")

    mutants = sweep.enumerate_mutants(fixtures, facts)
    for mu in mutants:
        touch_all_claims(mu["body"], mu["repo"], facts)

    counts = {}
    for mu in mutants:
        counts[mu["class"]] = counts.get(mu["class"], 0) + 1
    print("mutant class counts: %s" % json.dumps(counts, sort_keys=True))
    print("self-checks during build: %s" % json.dumps(sweep.CHECKS, sort_keys=True))
    print("facts: %d sha_exists, %d blobs" % (len(facts.data["sha_exists"]),
                                              len(facts.data["blobs"])))
    assert not facts.misses, facts.misses

    with open(os.path.join(HERE, "repo_facts.json"), "w") as f:
        json.dump(facts.data, f, indent=1, sort_keys=True)
        f.write("\n")
    print("wrote repo_facts.json")


if __name__ == "__main__":
    main()
