# PROVENANCE — VERDICT 007 frozen evidence inputs

Every file under `runs/` is a byte-copy of a committed artifact fetched at its PINNED
commit SHA. Reproducibility for this verdict is redefined (per VERDICT 005) as a
byte-identical analyzer over these frozen inputs — the sources are committed contracts,
not a seedable engine.

## Frozen files (`<owner>/<repo> <path> @ <SHA>`)

- `games-web.character-sheet.schema.json`
  menno420/product-forge products/games-web/data/schema/game-state.schema.json @ 43563dccc874c58946576444fbba38600bb45f86
- `games-web.mining-character.fixture.json`
  menno420/product-forge products/games-web/data/mock/mining-character.json @ 43563dccc874c58946576444fbba38600bb45f86
- `games-web.recruit-character.fixture.json`
  menno420/product-forge products/games-web/data/mock/recruit-character.json @ 43563dccc874c58946576444fbba38600bb45f86
- `games-web.phase2-data-api-proposal.md`
  menno420/product-forge products/games-web/docs/phase2-data-api-proposal.md @ 43563dccc874c58946576444fbba38600bb45f86
- `mineverse.mining_snapshot.v1.schema.json`
  menno420/superbot-mineverse schemas/mining_snapshot.v1.schema.json @ 2b1bd0b9695ba4975d358895d0b9a52ab98507f4
- `mineverse.mining-data-contract.md`
  menno420/superbot-mineverse docs/mining-data-contract.md @ 2b1bd0b9695ba4975d358895d0b9a52ab98507f4

## Decided-transport fact (the criterion the conformance check asserts against)

- The decided transport for the mineverse mining data is the **superbot-lane
  committed-JSON `mining_snapshot.v1` feed** (fleet-manager ORDER 012/013). games-web's
  phase-2 presentation layer is scoped to render THAT feed.
- The superbot inbox @ 58040c6 carries only ORDER 001 → the games-web-facing ORDER is
  **UNROUTED** (no committed order wires games-web to a self-API; the self-API in the
  phase-2 proposal is a games-web-side request, not a decided transport).

## Fetch method

menno420/product-forge and menno420/superbot-mineverse were `git clone`d (recon method);
the sim-lab github MCP is scoped to menno420/sim-lab only, and the two source repos'
HEADs already sat at the pinned SHAs (product-forge HEAD = 43563dc; superbot-mineverse
HEAD = 2b1bd0b). menno420/mineverse and menno420/games-web are NOT accessible and were
not chased (games-web content lives inside product-forge).
