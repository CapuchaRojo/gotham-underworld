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

`career_m011.json` comes from merged M011 commit `c8d6bf6`, generated before M012:
`create_career(42)`, join Harbor Syndicate through `execute_command`, run three
collection commands, then `advance_day` twice. It retains a completed case,
command sequence, allowance, and M011 state without a legal profile. M012 tests
preserve every original value and do not invent historical fine amounts/dates.

`career_m012.json` comes from merged M012 commit `e6539cc`, generated before M013:
`create_career(17)`, join Harbor Syndicate, run one collection command, then advance
three days through the game service. M013 tests preserve every original value,
including legal state and action usage, add profiles without replay, and activate
the new competition policy only on the next advanced day.

`career_m013_1.json` comes from merged M013.1 commit
`8b68e1efc338a532293262edafd85240cdfa65a3`, with that revision's root Python
modules loaded together in an isolated temporary directory. Recipe:
`create_career(17)`, join Harbor through the service, twice run one collection
then `advance_day`, then run three courier commands and save. Day 2 retains
active M013 profiles/operations and all three spent actions, with no navigation.
M014 tests preserve its resources/events on load, require explicit public-anchor
adoption and next-day activation, and never invent a historical home or refresh
the spent action budget on adoption/loading.

`m014/career.json` was generated in isolation from the merged M014 root Python
modules and atlas at `fa2f9f5bbf081bde080c6d8b2e46512487027c66`. Recipe:
`create_career(17)`, service join Harbor, three courier jobs, travel to p032, save.
It preserves day 0, $115, three spent actions, p032 and 1 spent TU, with no
daily-life extension. M015 requires exact load equality and explicit room
adoption without a budget refresh. This fixture uses a subdirectory because the
unchanged M014 migration test intentionally treats root fixtures as pre-navigation saves.
