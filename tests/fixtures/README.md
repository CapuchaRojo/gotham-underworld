# Historical career fixtures

These are outputs from the repository's actual historical implementations,
not current worlds with fields removed. Tests read these JSON files without
requiring Git or a network connection.

| Fixture | Source commit |
| --- | --- |
| m001.json | 002bc43 |
| m002.json | 19068c4 |
| m003.json | 64d37fb |
| m004.json | fc7a704 |
| m005.json | 8dbbb1f |
| m006.json | dc99c95 |
| m007.json | d0f3247 |
| m008.json | be0cc5e |
| m009.json | 161a1b9 |
| m010.json | 821a416 |

Generation recipe: load each revision's Python modules together in isolation.
For M001 use `simulation.run(seed=42, days=3)`. For M002-M010 call that revision's
`prepare(new_world(42))`, join Harbor Syndicate, resolve three collection jobs,
then call `next_day` three times. Serialize the resulting world as UTF-8 JSON.
M001's historical accelerated-custody clock behavior is preserved in its fixture.

The migration tests preserve historical events and values, verify idempotent
initialization and a disk round trip, then advance another day. The M010 fixture
also supplies fixed expected job outcomes for the legacy resolver.
