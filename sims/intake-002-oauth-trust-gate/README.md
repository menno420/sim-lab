# INTAKE 002 — Discord OAuth trust-gate adversarial verification (VERDICT 003)

Spike + JUDGMENT-ONLY (ladder rungs 2 and 3) settling whether the source idea's §5
Discord OAuth trust-gate for per-server personal stats — `identify`+`guilds` only, no
long-lived token storage, CSRF/state correctness, per-user isolation, rate limiting,
abuse-case walkthrough — plus the §4 superbot read-only API surface holds up under an
evidence-based adversarial verification. A runnable model of the authorization-code flow
with a reference implementation of all six §5 controls, then 13 executed attacks against
it (multi-seed, rate-limit swept). Every modelled attack is defeated; two attack classes
surface holes.

**Verdict:** `needs-more-evidence` — ruling **buildable-with-named-changes**. The gate can
be made trustworthy (the spike shows the concrete controls), but §5 as written is a
checklist not a spec, several threats are JUDGMENT-ONLY hypotheses for launch-time live
tests, and the §4 read-only API is **unbuilt AND unrouted** — phase 3 deadlocks regardless.
**Phases 1–2 (story page, data explorer) carry no auth surface and do NOT wait on this.**
Named changes + the holes are in `REPORT.md`.

Source idea: `menno420/idea-engine` `ideas/websites/superbot-site-stats-data-story-2026-07-10.md` @ `3e0131182acc89d9dcf708797e79cf3a7636c538` (§5 trust-gate, §4 read-only API); routed via idea-engine `control/outbox.md` PROPOSAL 002 @ `e77fa46022d7cd3ad0b0e57ddc2f7910b823df38`.

## One run command
```
python3 sims/intake-002-oauth-trust-gate/oauth_trust_gate_sim.py
```
Deterministic, stdlib-only, exit 0 iff all self-checks + all modelled attacks resolve as
designed (13 attacks defeated, 2 holes reproduced, 5-seed stable, 3×3 rate-limit sweep).
The seeded PRNG stands in for a CSPRNG for reproducibility — production MUST use a real
CSPRNG (disclosed abstraction; see REPORT.md § LIMITS).

## Files
- `REPORT.md` — the live verdict (7-section, all five validity-gate answers, per-§5-item checklist).
- `oauth_trust_gate_sim.py` — the model + reference impl + executed attack suite + self-checks.
