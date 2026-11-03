# M014 validation report

Mission 007, Python 3.14.2 on Windows. Baseline master/M013.1:
`8b68e1efc338a532293262edafd85240cdfa65a3`. Submission is for review; do not merge.

## Executed checks

| Command/check | Actual result |
| --- | --- |
| `python -B -m unittest discover -s tests -q` before implementation | 198 passed, 31.199 seconds |
| Same full-suite command after implementation and compatibility corrections | **229 passed**, 31.766 seconds; 198 prior tests unchanged plus 31 navigation tests |
| Documentation checker (`python -B -` using local-file/link/anchor, JSON and Python-fence parsing) | All checked local references resolve; count is reported in the PR, including this report |
| `git diff --check` | Passed |
| Real CLI subprocess walkthrough and resume from a temporary, separate working directory | Home/store/job/return/wait/save/resume passed: day 1, p031, TU used 0, one job, three refreshed actions |
| Two 100-day navigation campaigns with reference careers and six disk resumes each | Each completed 200 journeys/300 jobs; all resource, legal, NPC, job and non-command/non-travel domain events matched the reference |

Full-suite coverage includes the existing four 365-day and one 1,000-day faction
campaigns, 365-day disk resume, 90-day legal replay, failure injection and CLI
regressions. Navigation adds actual atlas/source parity, invalid definitions,
budget/boarding/return boundaries, unreachable and restricted destinations,
one-way links, known/unknown closures, bounded reopening, custody protection,
detached reports, event-cost/path validation, failed saves, content pinning,
historical adoption, 40-day insertion-order replay/resume and fresh-process
hash-seed checks. Every original test file remains unchanged.

Historical fixtures M001–M012 and the new **actual M013.1** fixture load without
navigation, relocated people, replayed income or changed historical events.
The M013.1 fixture is generated from the exact baseline modules, retaining three
spent actions; [fixture provenance](../tests/fixtures/README.md) gives the recipe.
Explicit adoption preserves spent actions and has no home; it activates only on
the next day. Pending adoption and interrupted movement survive disk resume.

During development, one over-budget test initially chose the wrong origin, and
three legacy faction regressions exposed direct-clock tooling compatibility.
The route fixture now checks n01→n40 at 19 TU; the validator accepts a retained
older TU-day marker without refreshing on load. Final checks above pass.

## Reproducible longer smoke check

Run the following with `python -B -` from the repository root (PowerShell can
pipe a single-quoted here-string). It uses temporary saves and current public
service commands only. This is a developer smoke scenario, not a new game mode.

```python
from pathlib import Path
import hashlib
import json
import tempfile
from game_service import create_career, execute_command, advance_day, save_career, load_career
from career_state import validate

for seed in (17, 42):
    world, reference = create_career(seed), create_career(seed)
    for w in (world, reference):
        execute_command(w, 'join', faction='Harbor Syndicate')
    with tempfile.TemporaryDirectory() as folder:
        path = Path(folder) / 'campaign.json'
        for day in range(100):
            execute_command(world, 'travel', destination='n31' if day % 2 else 'p032', mode='auto')
            for w in (world, reference):
                for kind in ('collection', 'courier', 'courier'):
                    execute_command(w, 'job', kind=kind)
            execute_command(world, 'travel', destination='home', mode='auto')
            advance_day(world)
            advance_day(reference)
            if day % 17 == 0:
                save_career(world, path)
                resumed = load_career(path)
                assert resumed == world
                world = resumed
            validate(world)
            for key in ('factions', 'districts', 'player', 'people', 'cases', 'legal', 'job_attempts'):
                assert world[key] == reference[key], (seed, day, key)
            def domain_events(w):
                return [e for e in w['events'] if e['kind'] not in ('travel', 'player_command')]
            assert domain_events(world) == domain_events(reference)
        print(seed, world['day'], world['navigation']['journey_sequence'], world['job_attempts'],
              hashlib.sha256(json.dumps(world, sort_keys=True).encode()).hexdigest())
```

Actual final campaign fingerprints:

| Seed | Days / journeys / jobs | SHA-256 of canonical sorted-key world JSON |
| --- | --- | --- |
| 17 | 100 / 200 / 300 | `b2d4e7237b1d9cc68030511ae313fff69dfe766c6e000fd44df1d002f222c595` |
| 42 | 100 / 200 / 300 | `f9883e9e8a0b0d511c34012520c02014b564ebf10828d5459adf648d8deb86bf` |

## Gameplay assessment

New decisions: choose an accessible place, mode and return commitment, spend TU
on a remote trip or preserve flexibility with local work, and explicitly adopt
geography in an old career. Observable persistent effects are location, remaining
TU, committed journeys and closure knowledge. A new player can inspect home,
visit the store, take an existing courier job and return home before advancing.
The [manual commands](GOON_WORLD_RUNTIME.md#manual-playable-slice-and-limits)
were executed through real CLI subprocesses as well as automated tests.

Variety currently comes from topology, modes, entry permission and controlled
closure fixtures. No dynamic incident generator or authored local mission exists.
Most places remain inspectable metadata/frontages; jobs are still location-free.
Repeated commuting can become empty grind, so no travel XP, income, mandatory
remote chain, automatic overnight travel or new recovery loop is introduced.
The 18-TU allowance and 1-TU local floor are initial policies, with bounded
two-day corridor reopening. Vehicle routing, institutional interiors, schedules,
emergency transport, prologue and combat remain outside this milestone.
