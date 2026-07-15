# verdict-087 — the bundle over a floorless PWYW (INTAKE 074)

Prices idea-engine PROPOSAL 074's harvested tension where it lives: the
venture-lab catalog commits a three-price lattice — kit **$49** fixed
(`candidates/membership-kit/LISTING.md:46` @ `520bdfc`), pack
**"Pay-what-you-want, $19 suggested"** (`candidates/template-packs/
LISTING.md:61`), Ship-It bundle **$59** fixed with the committed FAQ
claim **"it saves $9 and one checkout"** (`candidates/BUNDLE-LISTING.md
:73-74`) — while the ONE field the queued ⚑D publish click leaves open
is the PWYW floor f ("minimum owner's choice",
`docs/publishing/OWNER-QUEUE.md:162`; V040's own gap register G2 records
the absence verbatim). Three exact structure theorems carry the verdict:
**T1** advertised − achievable saving = s − f EXACTLY (independent of a
and p; at the floorless default the "+$9" copy and a "−$10" achievable
saving are true of the same triple simultaneously); **T2** a fixed
bundle over {fixed a, PWYW floor f} is lattice-coherent iff
p ∈ [a, a + f], mapping V040's anchor family {59, 64, 68} → floors
{10, 15, 19} with the banned $68 needing f = s = 19 EXACTLY (a
registered margin-0 contact — the banned anchor coheres only when the
PWYW knob is dead ink); **T3** under the committed affine fee schedule
(net(P) = (871/1000)·P − 4/5, V040's committed reading) the seller nets
exactly **+$9.51** per both-buyer routed to the bundle at f = 0 while
that buyer pays **$10** over the achievable path, and the only
f-independent genuine saving is the seller's **$0.80** saved second
fee. All decision arithmetic is seedless exact integers/Fractions
(REJECT checked first). The runner is hermetic — it reads ONLY
`fixtures.json` (committed before the runner); the venture-lab pins
were re-verified FIRSTHAND on a read-only public-HTTPS shallow clone at
exactly `520bdfc` and the five V040 external anchors verified in-tree
BEFORE the fixture was written (zero harvest anomalies).

## Run

```
python3 sims/verdict-087-bundle-pwyw-floor-lattice/bundle_pwyw_floor_lattice_sim.py
```

CPython 3.11 pinned and asserted. Deterministic: stdout and
`results.json` are byte-identical across process runs (verified by
external diff + sha256 — see REPORT.md). Stdlib-only, ~0.6 s. Every
decision number is an exact integer or Fraction; the seeded Arm R
carries no statistical gate.

## Files

- `fixtures.json` — every registered constant verbatim from the
  PROPOSAL 074 block / idea file (the committed triple with its
  file:line pins, the floor grid × anchor family with the decision cell
  f = 0, the buyer-path model, the F3 census anchors, the F4 pencil
  world, the F5 degeneracies, the T1 perturbed-constant controls, the
  Arm-R pmfs and seeds 20261660–663, the REJECT R1/R2/R3 clauses, the
  TYPED margin ledger — must-equal registered contacts vs must-clear
  strict rows, the V086 💡 applied — and the disclosed landing), plus
  fixture-level conventions C1–C13 — committed BEFORE the runner.
- `bundle_pwyw_floor_lattice_sim.py` — three-arm runner: Arm A seedless
  exact-Fraction closed forms over the full grid + perturbed controls
  (decision-bearing), Arm B INDEPENDENTLY-WRITTEN integer-cent twin
  (path costs by direct min() over enumerated w, w* by upward scan,
  window membership by scanning candidate bundle prices, the basis gap
  by direct subtraction, f* and the strict-discount law by upward floor
  scans, the fee layer in integer milli-dollars; powers the second
  decision evaluator), Arm R seeded buyer-type draws at the decision
  cell (FLOOR-HEAVY 20261660 at 50,000 episodes, SUGGESTED-ANCHORED
  20261661 at 20,000, presentation shuffle 20261662, aux 20261663 NEVER
  read; reporting-only, printed beside the exact expectations 2/5 & 53
  and 4/5 & 57).
- `results.json`, `run-stdout.txt` — the accepted run's outputs.
- `REPORT.md` — ruling, the full lattice surface (coherence, σ_ach, π,
  gap, Δ per floor × anchor), the typed margin ledger with the
  registered knife-edge, the F1–F6 gate results, the anomaly census
  (empty — every disclosed numeral reproduced exactly), the Arm-R
  traces beside the exact expectations, and the twin-arm /
  byte-identity notes.
