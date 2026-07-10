# VERDICT 004 — explore-hub federated-world GLOBAL XP balance sweep

Numeric simulation (method ladder rung 1) settling how a shared GLOBAL XP pool can be a
cold-start accelerator in a NEW game without ever substituting for per-game mastery or
gating content, for the explore-hub plan in `menno420/superbot`.

- **Source idea:** idea-engine `control/outbox.md` PROPOSAL 004, pinned
  `cd7251ec30950d12d29e65c57d843864387d0aec`; canonical
  `menno420/superbot docs/ideas/explore-hub-federated-world-2026-06-19.md` @ `fd638e3`.
- **Run (one command, deterministic, stdlib-only, exit 0 iff all self-checks pass):**
  ```
  python3 sims/verdict-004-explore-hub-xp-balance/federated_xp_balance_sim.py
  ```
- **Files:** `federated_xp_balance_sim.py` (model + 300-cell sweep + 4469 self-checks) ·
  `README.md` · `REPORT.md` (the validity-gate answers + the verdict).
- **Verdict:** `needs-more-evidence` · evidence `simulation` · gate PASS on the STRUCTURAL
  claim (global skills as pure RATE multipliers, phi=0, cannot substitute or gate at any swept
  magnitude — 0 by construction); the recommended MAGNITUDE is a hypothesis pending live
  telemetry — see REPORT.md § "What it did NOT settle".
- **Recommended default:** global skills as RATE/efficiency multipliers (**phi=0** — the
  load-bearing invariant), effect budget **e ≈ 0.20**, trickle **t ≈ 0.10**, hard
  **BOOST_CAP ≈ 0.25**, content thresholds set **≤ pure-per-game max (never in a global-only
  band)**. Ship phi=0 as the invariant; keep the magnitude a tunable and confirm on the
  telemetry listed in REPORT.md.
