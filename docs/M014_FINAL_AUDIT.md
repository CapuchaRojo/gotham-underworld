# M014 final integration audit — Mission 008

November 3, 2026. PR #14: `feature/m014-world-navigation` into `master`.
Incoming PR head `567e1c31727a3f14ee7f0fd0daae629fe37f3e02`; fetched base
`8b68e1efc338a532293262edafd85240cdfa65a3`. The incoming tree was clean,
the PR open and mergeable, and both submitted PR checks passed. This report
records the independent audit and corrections. Final PR disposition and merge
commit are recorded in GitHub and the Mission 008 final response.

## Scope and confirmed corrections

The incoming diff had 23 files: local atlas, registry/navigation runtime,
service/persistence/day/CLI integration, one historical fixture, 31 new tests,
and documentation. It changed no dependency manifest, workflow, existing job,
legal, NPC, faction, or district rule module. The 198 prior tests were not edited.
The atlas data and its fingerprint remain unchanged by this audit:
`14a38c5376989351d83bf90ed172c557a3dbf13c1323a115d2c2144f5136860a`.

| Confirmed defect before correction | Correction and regression |
| --- | --- |
| A save could claim a different location or lower spent TU than its last committed journey and still load. | [Navigation validation](../navigation.py) now matches the last arrival and current-day TU against travel history; malformed disk saves are rejected by [audit tests](../tests/test_m014_audit.py). |
| A duplicate journey outcome for one player command, a missing outcome, or a journey dated differently from its command could pass validation. | Exactly one travel result per committed travel command and matching day are required. |
| A detained player saw an `affordable: true` route preview despite being unable to travel. | The preview rejects while detained; location inspection remains available and the court/day recovery path works. |
| A future atlas could mark a public-to-public corridor `authorized`; the router ignored that label because no receiving endpoint had a restricted gate. | [Atlas validation](../location_registry.py) now rejects that definition and rejects POI-only access policy on corridors. Existing Blackgate access, separate POI admission, and lawful outward egress still pass. |

These are **confirmed** defects from small pre-fix reproductions. They did not
require changing the save schema, public atlas data, game economy, action rules,
or career history. The extra save checks validate recorded internal consistency;
they are not a cryptographic defense against deliberately rewritten JSON.

## Acceptance evidence

| Gate | Executed evidence and result |
| --- | --- |
| Complete atlas and links | `location_registry.load()`/`validate()` and source-row regression: 176 places (8 regions, 48 neighborhoods, 120 POIs), 63 corridors, 120 access spurs; all 183 links had valid endpoints and nonnegative costs, with strictly positive corridors. |
| Determinism and restrictions | Reversed place/edge dictionaries produced identical sampled route records; the 31 navigation regressions cover all public nodes, insertion-order replay, new process/hash seed, one-way links, closure mode/direction, private frontages, custody, 18-TU cap and zero-cost spur bounds. |
| A: fresh home/store/return | Service travel p031→p032→p031, `wait`, disk save/resume returned the exact world. The existing real CLI subprocess test also passed. |
| B: historical opt-in | M001–M013.1 fixtures load without a fabricated location/home or new rewards. Unmodified PR-head code generated pending/active M013.1 adoption saves; audited code loaded them exactly. Three spent actions stayed spent until a real `wait`. |
| C: unexpected closure | Controlled hidden closure stopped at safe n18, spent only 2 actual TU, marked the closure known and survived save/load. A first-edge discovery costs zero and gives no movement/reward. The runtime does not randomly generate closures. |
| D: exhausted allowance | Eighteen local moves consumed 18 TU; the nineteenth rejected without changing the world. Saving, inspection and explicit `wait` remained available; the valid day transition restored travel. |
| E: unused navigation isolation | A 30-day enabled-versus-navigation-free service replay produced equal complete worlds after removing only the navigation extension, including job, legal, faction and event outcomes. |
| F: repeated travel/resume | Eight repeated 18-move days, disk resumes and day transitions matched an uninterrupted reference exactly. Two 100-day campaigns separately completed 200 journeys/300 jobs each with six saves/resumes and equal nonnavigation domain state to controls. |
| Persistence and historical M014 compatibility | Three saves produced by the **unmodified** PR-head modules (hidden interruption, pending adoption, active adoption) loaded to exact JSON-equivalent worlds under the audited code. Existing failure-injection, backup and malformed-data regressions passed. |
| Full regression | `python -B -m unittest discover -s tests -q`: **237 passed in 34.757 s** under permitted temporary-file execution. Original incoming baseline was **229 passed in 31.528 s**; eight focused audit tests were added. |
| Targeted regression | `python -B -m unittest discover -s tests -p test_navigation.py -v`: **31 passed in 3.539 s**. Same command with `test_m014_audit.py`: **8 passed in 2.706 s**. |
| Long-run and resume | Executed the Python smoke block in [M014 validation](M014_VALIDATION_REPORT.md): seed 17: `b2d4e7237b1d9cc68030511ae313fff69dfe766c6e000fd44df1d002f222c595`; seed 42: `f9883e9e8a0b0d511c34012520c02014b564ebf10828d5459adf648d8deb86bf`. Both match the original submitted run exactly. The full suite also includes four 365-day and one 1,000-day faction campaigns. |
| Documentation | `python -B -` checker parsed all local Markdown references, Python code fences, and atlas JSON on the final content: **28 documents, 238 local links, four Python fences, zero failures**. |

GitHub CI for the **final pushed head** and the post-merge master test run are
separate final gates. Do not infer their result from the incoming PR checks.

## Gameplay and architecture assessment

Navigation adds an observable choice of destination, mode, return budget and
explicit old-career adoption. A journey persists position, spent TU and discovered
closures; no money, experience or faction income is awarded for moving. The
existing command service remains the player mutation boundary. Its detached
location views can feed a graphical interface; `route` is an advisory quote
recomputed at commitment. A GUI must use these public views for navigation and
must not expose the full debug snapshot as in-world intelligence.

The public graph has no free movement loop: corridor costs are positive, a
completed POI-to-POI movement costs at least 1 TU, and 18 TU bounds each day.
Restricted destinations require recorded permission; Blackgate's neighborhood
gate and POI admission are separate. An unexpected closure stops at a valid node,
and every controlled closure expires within two advanced days. Waiting is always
explicit and continues the existing legal/economic day pipeline once. Location
inspection is read-only. Travel does not advance faction or legal processing.

**Remaining limitations, not merge blockers:** most places are metadata-only
frontages; legacy work is still location-independent. The runtime has controlled
closure inputs but no incident generator, schedule, vehicle, housing payment, or
NPC encounter. The 18-TU budget can make a distant round trip impossible in one
day; preview and a safe waypoint make this explicit. Loaded atlas arrays are
fingerprint-pinned, so changing their order is a content compatibility change
even though route search itself is order-independent. The unrestricted full
snapshot is appropriate for save/debug consumers only. None of these is claimed
as implemented M015 gameplay.

The smallest M015 proposal and an unexecuted seven-day acceptance scenario are
in the [daily-life contract](GOON_M015_DAILY_LIFE_CONTRACT.md). M015 requires its
own implementation review; this audit changes no daily-life gameplay.
