# Probe report — VERDICT 142 · the correlated-vote Condorcet jury ceiling (P129 → V142, +13)

**Verdict: APPROVE** (exact reproduction) — byte-identical verifier copy + exact digest reproduction + all three gates PASS in order G1→G2→G3. Born-red card flip is the deliberate LAST commit that releases the substrate-gate HOLD; landing is via merge-on-green (ORDER 003), zero agent merge calls.

Source: idea-engine `ideas/fleet/condorcet_jury_correlation_floor.py` at main `fa13e54` (PROPOSAL 129).

## Reproduction posture
- Verifier copied **byte-identical** from idea-engine `ideas/fleet/condorcet_jury_correlation_floor.py` — `diff` exit **0**, file sha256 `47035a4be9ee2cb49f8c77de6ec3fd6af362d699f02aba52b9690923254f5a32`, git blob `d66a4bb305fcb969909ea2dc9f5e98fd7af16e9a`, **281** lines / **11706** bytes. Permalink: https://github.com/menno420/idea-engine/blob/fa13e54eb8938c86cd2ad7d173272b401572bf3b/ideas/fleet/condorcet_jury_correlation_floor.py
- Pinned world: **SEED=20260717**, P_COMPETENCE=**0.60**, RHO=**0.30**, TRIALS=**120000**, N_GRID=**(1,3,5,9,15,25,51,101,201,501)**, N_LO=**1**, N_MID=**101**, N_HI=**501**, SIGMA_GATE=**3.0**. Stdlib-only (random, math, json, hashlib); no numpy/scipy. Paired common-random-numbers: each trial draws one common factor C~N(0,1) and N_MAX=501 idiosyncratic ε_i~N(0,1); the correlated votes √ρ·C+√(1−ρ)·ε_i>τ and the PAIRED independence control ε_i>τ (same ε, ρ=0) share every idiosyncratic draw and the marginal competence p — only ρ differs, so the ceiling EMERGES from the shared-factor draws. Gate z-scores for the paired-diff gates are on the estimated mean via its standard error (se=std/√TRIALS); the anchor gate on the Bernoulli se=√(Â(1−Â)/TRIALS). The correlated grid is anchored against the exact finite-N law A(N)=E_C[P(Bin(N,q(C))>N/2)] by deterministic trapezoidal integration over C.
- DIGEST POSTURE: **WHOLE-DICT / NO-SELF-FIELD / STDOUT-ONLY** — the results dict carries **NO** `results_sha256` field; `main()` computes `canonical=json.dumps(results, sort_keys=True, separators=(",",":"))`, `digest=sha256(canonical.encode()).hexdigest()`, then PRINTS the human-readable `json.dumps(results, indent=2, sort_keys=True)` dump followed by `Results-JSON sha256: <digest>`. It writes NO results file. **Twist:** the disclosed digest is the sha256 of the COMPACT-canonical serialization (sort_keys + `(",",":")` separators), NOT the pretty indent=2 dump printed on stdout — two serializations of the same dict; recompute over the compact form. Classified against `main()` lines 271–277 in the script text, not assumed. This verifier exposes a `simulate()` entry point returning the results dict — the in-process double-run calls `simulate()` twice and compact-hashes each return value.

## Digest — reproduced == disclosed
| run | digest |
|---|---|
| disclosed (P129 outbox / verifier `Results-JSON sha256:` line) | `35031fbde0abceef4eb8e2939d1609a5938709bd1b46ae8f03f9bc48dd3afc3c` |
| cross-invocation A (fresh `python3`, committed `run-stdout.txt`) | `35031fbde0abceef4eb8e2939d1609a5938709bd1b46ae8f03f9bc48dd3afc3c` |
| cross-invocation B (fresh `python3`) | `35031fbde0abceef4eb8e2939d1609a5938709bd1b46ae8f03f9bc48dd3afc3c` |
| in-process double-run #1 (`simulate()`, compact-hashed in-process) | `35031fbde0abceef4eb8e2939d1609a5938709bd1b46ae8f03f9bc48dd3afc3c` |
| in-process double-run #2 (`simulate()` again, compact-hashed in-process) | `35031fbde0abceef4eb8e2939d1609a5938709bd1b46ae8f03f9bc48dd3afc3c` |

**All canonical computations == the disclosed digest EXACTLY.** all_pass=**true**, exit **0**, byte-identical across runs (cross-invocation stdout diff exit **0**); the in-process double-run produced identical digests run-to-run.

## Gates (disclosed → reproduced), order G1→G2→G3
| gate | disclosed | reproduced | result |
|---|---|---|---|
| **G1** correlation-ceiling existence (mean(indep−corr)@N_HI>0, z≥3) | mean **0.321425**, z **238.4048** | mean **0.321425**, z **238.4048** | **PASS** |
| **G2** Condorcet-convergence control (mean(indep_hi−indep_lo)>0, z≥3, A_indep(501)>A_corr(501)) | mean **0.399042**, z **282.2685**, 0.999975>0.678550 | mean **0.399042**, z **282.2685**, 0.999975>0.678550 | **PASS** |
| **G3** closed-form ceiling anchor (max\|z\|<3, A_corr(1)≈p, monotone, \|A_theory(501)−A_∞\|<0.01) | max\|z\| **1.9267**, A_corr(1) **0.601933**, gap **0.000603** | max\|z\| **1.9267**, A_corr(1) **0.601933**, gap **0.000603** | **PASS** |

First-failing gate: **none**. all_pass=**true**, exit **0**.

## Sim & anchors (all match disclosed exactly)
- Ceiling: τ=Φ⁻¹(0.4)=**−0.253347**; A_∞=Φ(Φ⁻¹(0.6)/√0.3)=**0.678155**; residual 1−A_∞=**0.321845**; saturation scale 1/ρ=**3.3333**.
- Correlated accuracy A_corr climbs then plateaus at the ceiling: N=1→**0.601933**, 25→**0.668633**, 101→**0.676100**, 201→**0.677967**, 501→**0.678550**.
- Independent control A_indep follows the Condorcet climb to near-certainty: N=1→**0.600933**, 101→**0.979658**, 201→**0.998050**, 501→**0.999975**.
- G1 (correlation-ceiling existence): mean(correct_indep(501)−correct_corr(501))=**0.321425** > 0, z=**238.4048σ** — at the same large N and same competence, correlation leaves a persistent accuracy gap independence removes (A_corr(501)=0.678550 vs A_indep(501)=0.999975).
- G2 (Condorcet-convergence control): mean(correct_indep(501)−correct_indep(1))=**0.399042** > 0, z=**282.2685σ**, with A_indep(501)=**0.999975** > A_corr(501)=**0.678550** — the SAME voters made independent climb to certainty, so the ceiling is caused by ρ, not competence p.
- G3 (closed-form ceiling anchor): full-grid max|anchor z|=**1.9267** < 3, A_corr(1)=**0.601933** ≈ p=0.60 (marginal_ok), correlated grid monotone non-decreasing, A_theory(501)=**0.677552**, |A_theory(501)−A_∞|=**0.000603** < 0.01 — the plateau lands on Φ(Φ⁻¹(p)/√ρ).

## Reproduction commands (verbatim)
```
# byte-identical copy
diff idea-engine/ideas/fleet/condorcet_jury_correlation_floor.py \
     sims/verdict-142-condorcet-correlation-floor/condorcet_jury_correlation_floor.py   # exit 0
sha256sum <both>   # 47035a4be9ee2cb49f8c77de6ec3fd6af362d699f02aba52b9690923254f5a32 (both)

# cross-invocation A/B (fresh processes)
python3 condorcet_jury_correlation_floor.py > run-stdout.txt      # exit 0
python3 condorcet_jury_correlation_floor.py > B.txt ; diff run-stdout.txt B.txt   # exit 0
grep "Results-JSON sha256" run-stdout.txt
# -> 35031fbde0abceef4eb8e2939d1609a5938709bd1b46ae8f03f9bc48dd3afc3c

# in-process double-run + independent compact-digest recompute
python3 -c "call simulate() x2, sha256(json.dumps(r,sort_keys=True,separators=(',',':')))"
# -> both runs 35031fbd…afc3c == disclosed
```

**Ruling: APPROVE.** Byte-identical verifier copy (diff exit 0), the results-dict sha256 reproduces the disclosed digest `35031fbde0abceef4eb8e2939d1609a5938709bd1b46ae8f03f9bc48dd3afc3c` EXACTLY across cross-invocation A/B + a deterministic in-process double-run, and all three gates PASS in order G1→G2→G3. The card flip to `complete` is the deliberate LAST commit that releases the born-red HOLD; landing via merge-on-green (ORDER 003), zero agent merge calls.
