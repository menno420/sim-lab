# VERDICT 089 — REJECT — the check digit's exact blind spot (P076, check-digit transposition floor)

**Ruling: REJECT** — per the pre-registered rule applied in the registered
order REJECT → INVALID → APPROVE → NULL (REJECT evaluated FIRST and fires
on all three clauses; twin independently-written decision evaluators agree
REJECT/REJECT; every decision number an exact small integer).

179 self-checks, 179 passed, 0 failed; exit 0 on the accepted run;
~6 s/run (the 10! census is the only heavy leg, ~3 s); stdlib-only;
hermetic (reads only its own fixtures.json — and the head is fully
hermetic at the model level: every constant invented-but-pinned in the
idea file, no external repo re-verification owed); CPython 3.11 pinned
and asserted. stdout + results.json byte-identical across two full
in-repo process runs by external diff + sha256:

- `results.json` sha256 `4c781e403f2f402723e809169c80fda7abd084f717366b01fc3176727ceb3eaa`
- `run-stdout.txt` sha256 `703f865c20bfaeb7a337cd81b3c803322845db0db830b9e3f0e445314dd23255`

**Anomaly census (structured, the V087/V088 coverage convention): 19
compared-and-matched, 0 mismatched, 3 vacant.** Every disclosed numeral
in the P076 registration — decision AND reporting — reproduced exactly
from scratch: the complete histogram (total 3,628,800; min 2 at 46,400;
max 90 at exactly the 10 rotations; no zero bin; the even-only support
{2, 4, …, 36, 40, 42, 44, 56, 58, 90} with the disclosed gap structure
above 44), Luhn's census 2 with miss set {(0,9),(9,0)}, the 16-cell
linear partition {4 × 90, 12 × 10} with floor 10 and the ten ordered
|a−b| = 5 escape pairs, ISBN-10 0/0, EAN-13 10/90 + 90/90 with 120/990
full-code patterns, ALL-ONES 0/90, the Damm censuses 0/900 + 0/900 +
958/9000, all four word-level enumerations {1000,0,60} / {1000,0,300,
1800} / {1331,0,0} / {1000,0,0}, the four typed contacts, the pencil
worlds, the degeneracy controls — **and the seeded Arm-R preview
reproduced EXACTLY (412/17954, 1948/18026, 17966/17966, 600,000 draws
counted)**: the sim-chosen per-episode draw order (disclosed in
fixtures.json) evidently coincides with the drafter's stream order, so
even the reporting-only rows landed byte-for-byte. The drafter's
NO-DERIVED-LITERALS claim survived a zero-trust re-derivation intact.
The three VACANT rows, stated as themselves: (1) the 6-permutation
quotient-reduction spot set was registered by SIZE only (the drafter
session was killed by a container restart; its scratch spot set is
unrecoverable) — this sim chose a deterministic six (identity · the
Luhn fold · rotation +1 · reflection 9−y · ×3 · ×7), disclosed in
fixtures.json, all 36 pairs passing; (2) the Arm-R per-episode draw
order was never registered (seeds, N, and the 600,000-draw sentinel
were) — sim-chosen, disclosed, and vindicated by the exact preview
match; (3) no stability-leg values were disclosed — printed beside the
exact rates with nothing to compare.

## The decision clauses (all exact)

**R1 — THE FLOOR (fires).** Over ALL 3,628,800 quotient permutations
(the complete function space, exhaustively enumerated — the pipeline's
first full census of a 10!-cell permutation space):

- the Σ-certificate holds symbolically (any permutation of Z10 sums to
  45 ≡ 5 mod 10; every boundary's τ sums to 0; 0 ≠ 5 — so τ is never
  injective) AND exhaustively (no U = 0 bin exists);
- min U = **2** exactly, attained by **46,400** quotients; max U = 90
  on exactly the **10** rotations (verified as the rotation set
  element-by-element, not just counted);
- **Luhn's quotient sits ON the floor**: census 2, miss set exactly
  {(0,9),(9,0)} — among all position-wise mod-10 schemes none does
  better, only equally well; every "improved mod-10 scheme" pitch is
  refutable by this census;
- the best all-singles LINEAR cell misses **10** (the 16 unit-weight
  cells partition {4 diagonal → 90, 12 off-diagonal → 10}; all-singles
  weights are odd units, so boundary differences are even and the
  |a−b| = 5 swaps escape) — nonlinearity buys 5×, never zero.

**R2 — THE MIGRATION REGRESSION (fires).** ISBN-10 (mod 11, weights
10…1): **0** undetected substitutions (10 × 110 checks) and **0**
undetected transpositions at EVERY distance (45 × 110 checks) —
complete, at the price of the eleventh symbol. EAN-13 (mod 10, weights
1,3 alternating — the 2007 successor to ISBN-10 for the world's book
numbers): singles complete, but **10/90** missed per adjacent boundary
(exactly the ten ordered |a−b| = 5 pairs) and **90/90** missed at every
distance-2 pair (same weight — total blindness), i.e. **120 adjacent +
990 distance-2** escape patterns over the full 13-digit code where
ISBN-10 had zero. Strict weakening in both transposition classes with
SUB coverage preserved.

**R3 — THE EXITS ARE REAL (fires).** The pinned Damm quasigroup table
passes all three property gates (rows permutations, columns
permutations, zero diagonal) and scores **0/900 SUB + 0/900 ADJ** on
the same ten digits — the T1 barrier is a fact about position-wise
ABELIAN-LINEAR checks, not about the alphabet (honesty row, reporting:
Damm's distance-2 state census is 958/9000 — completeness at every
distance remains ISBN-10's alone among the pinned schemes). The 11-ary
mini-code (weights 4,3,2,1 mod 11) word-enumerates to 1331 valid /
0 SUB / 0 ADJ. The blind spot is a CHOICE, not a law of digits.

## The word-level twin (Arm B, the typed contacts)

Independently-written full enumerations at length 4, exact-equal to the
Arm-A position censuses through the FOUR typed must-equal contacts:
LUHN 1000/0/**60 = 3 × 2 × 10** · EAN-style 1000/0/**300 = 3 × 10 ×
10**/**1800 = 2 × 90 × 10** · 11-ary 1331/0/**0** · DAMM 1000/0/0 —
with the ordered-pair multiplicity law (each ORDERED digit pair at a
boundary sits in exactly 10 valid words) asserted directly, per
boundary and per pair, for all three mod-10 word schemes. The drafter's
disclosed drafting-run correction was genuinely live here: reproducing
the unordered counts 30/150/900 was the pre-registered census-contact
NULL axis, and the enumeration returned the ordered counts 60/300/1800
— the corrected multiplicity law, confirmed from scratch. The twin also
carries its own reduced quotient census (the π(0) = 0 slice, 362,880
cells, pairwise-comparison U — a different algorithm on a different
iteration space) and the full census equals 10 × the slice on every
bin (the shift-orbit lemma, spot-verified on all 60 shifted spot
perms).

## The hand worlds (F4, pencil-checkable)

(a) weights (1,1), length 2: a swap never changes the sum — 90/90
undetected, by inspection. (b) The famous miss by hand: with the left
digit doubled, 09 digests to 0 + L(9) = 9 and 90 to 9 + L(0) = 9 —
identical, undetected. (c) The certificate itself: 0+1+…+9 = 45; 45
mod 10 = 5; Στ ≡ 0 ≠ 5 — three lines.

## Typed margin ledger (the V086/V087 practice)

Every REJECT clause is an exact-equality census — the margin concept
degenerates to theorem-vs-not, and the ledger names the three
registered EQUALITY cells, all landed exactly: **Luhn U = 2 = min U**
(ON the floor — margin ×1.00 BY CONSTRUCTION: optimality, not
clearance); **EAN D2 = 90/90** (saturated cell — the maximum possible,
no room above; the Arm-R trace agrees: 17966/17966 = 1.0 measured);
**Damm ADJ = 0/900** (zero cell — the minimum possible, no room below).
No census landed off its registered exact value (that would have been
INVALID-or-NULL by the pre-registered axes, never "close enough").

## Arms

- **Arm A** — seedless exact integer counting; decision-bearing: the
  complete 10! census, the quotient-reduction lemma (36 pairs), the
  weight grid + 16-cell multiplicative cross contact, all position and
  state censuses, pencil worlds, degeneracy controls.
- **Arm B** — independently-written twin: the four word-level
  enumerations with the typed contacts, its own reduced census, its own
  boundary scans; powers the second decision evaluator; equals Arm A on
  every contacted number.
- **Arm R** — reporting-only seeded identifier careers (16-digit Luhn +
  13-digit EAN, one ADJ + one D2 injection per episode): main seed
  20261680 (N = 20,000; 600,000 draws counted and asserted) — Luhn ADJ
  412/17954 ≈ 0.022948 beside exact 2/90 ≈ 0.022222; EAN ADJ 1948/18026
  ≈ 0.108066 beside exact 10/90 ≈ 0.111111; EAN D2 17966/17966 = 1.0
  beside exact 90/90; stability seed 20261681 (N = 8,000) — 169/7195 ·
  767/7241 · 7179/7179; presentation shuffle 20261682 (read by the
  presentation leg only); aux 20261683 asserted never read (constructor
  registry). NO statistical gate rides Arm R.

## Falsifiability (was real, and checked live)

The **eleventh-symbol world**: ISBN-10's censuses are 0 at every
distance — one extra symbol dissolves the entire impossibility, so the
floor is alphabet-exact, verified firsthand in R2. The **non-abelian
world**: the Damm table hits 0/900 on the SAME ten digits — the
registered theorem names its true scope (position-wise abelian mod-10)
and would be false one algebra away, verified firsthand in R3. The
**drafting-run correction**: the census-contact NULL axis (unordered
30/150/900) was genuinely reachable and did NOT fire — the enumeration
lands on the ordered law. APPROVE was one certificate error away (a
U = 0 quotient — excluded both symbolically and by the exhaustive
census); the Damm-failure NULL was one table transcription error away
(all three property gates passed).

## Scope

The error taxonomy is the classic transcription pair (SUB +
transpositions at distances 1 and 2), uniform within class, no
keystroke priors — the censuses are class-exact, not risk-weighted
(a frequency-weighted objective is a named data-requiring follow-up).
The impossibility's scope is position-wise abelian mod-10 — Damm sits
OUTSIDE the scope and is priced as the exit, which is the point.
Length-4 word enumerations stand in for full-length codes via the
position-census reduction, verified by the typed contacts (the
multiplicity law asserted directly); full-length pattern counts
(120/990) are boundary-count products — an identity, not an
approximation. Twin/jump/phonetic errors, insertion/deletion, weighted
priors, and alphanumeric alphabets (odd-order groups, where the parity
obstruction vanishes) are named follow-ups, none in scope. Per the
registered consequence: the REJECT retires "a check digit means typos
are handled" with numbers — a check digit is a designed instrument
with an exact, named miss SET (Luhn = {09↔90}; EAN-13 = five twin
pairs adjacent plus EVERYTHING at distance 2); never assume the newer
standard is stronger (the world's book numbers are the counterexample);
and if swap coverage matters the exits are priced — one symbol
(mod 11) or one table lookup (Damm).
