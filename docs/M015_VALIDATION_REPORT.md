# M015 validation — Living Gotham

Mission 009, November 4, 2026. Base: merged M014/PR #14 at
`fa2f9f5bbf081bde080c6d8b2e46512487027c66`. Feature branch:
`feature/m015-living-gotham`. Submit a PR against master and **leave it open**.

## Foundation audit and implementation decisions

Fetched master, verified equal local/remote hashes and a clean tree, read the
M015 readiness, navigation, prologue, narrative, gameplay and roadmap contracts,
and inspected service, save/migration, navigation, daily phases, jobs, legal,
NPC, relationship and faction accounting boundaries. The baseline actually ran:
**237 tests passed in 70.883 seconds** on Python 3.14.2/Windows.

No confirmed baseline defect blocked this slice. The important integration risks
were duplicating authoritative money/home state, inventing historical rent,
double-paying a criminal job, refreshing allowances on enrollment, and contacts
learning private actions. The existing fixed faction NPC roster cannot hold a
civilian contact without inventing a faction. The implementation therefore uses
one optional life extension with separate original contact records and pinned
content, while retaining player cash and navigation home as authorities.

The initial findings/plan was provided before implementation. The
[choice contract](GOON_CONSEQUENTIAL_CHOICE_CONTRACT.md) defines the bounded
scenario and integration. The game service supports an option-specific action
cost callback but retains its existing private-copy transaction. Core choices
inject known-condition/effect adapters; there is no scripting interpreter or
external framework. One post-court/post-navigation phase owns daily processing.
Receipts, cash ledger, memories and selections are validated against their events.

During final review, a saved unknown contact field could collide with public
identity fields in the report. The public view now selects explicit fields;
a regression proves that unknown/private metadata neither crashes the view nor
overwrites identity or leaks. Follow-up work also checks current known standing:
an earned reference can be held after broken commitments and restored through
ordinary interactions. Mixed-source menus use the player's planner as speaker,
without implying that one NPC knows another's private referrals.

## Executed commands and checks

All commands below ran from the repository root, with permitted temporary-file
execution for save/subprocess tests. No dependency was installed.

| Command | Actual result |
| --- | --- |
| `git fetch origin master`, `git rev-parse HEAD origin/master` before branch creation | Both hashes equaled the M014 merge above; tree clean. |
| `python -B -m unittest discover -s tests -q` baseline | 237 passed, 70.883 s. |
| `python -B -m unittest discover -s tests -p test_daily_life.py -v` initial focused implementation | 34 passed, 60.978 s; subsequent edge cases increased coverage. |
| `python -B -m unittest discover -s tests -p test_daily_life.py -k known_reference -k unknown_saved_contact -v` | Two final review regressions passed, 0.235 s. |
| `python -B -m unittest discover -s tests -q` final | **274 passed in 220.464 s**: 237 unchanged baseline tests plus 37 new regressions. |
| `python -B daily_life_campaigns.py --days 7 --resume` final | All five paths completed; exact world equality on each daily disk resume. Results below. |
| `python -B daily_life_campaigns.py --days 56` final | Five longer campaigns; final result table below. |
| `python -B -` documentation/AST checker | 30 documents, 252 local links, four Python fences and 45 Python modules checked; zero failures. Both content JSON files parse. |
| `git diff --check` | Passed; no whitespace errors. |

The new tests cover stable IDs, hidden/disabled choices, stale place/action
preconditions, service rejection and injected-effect atomicity, shared action/TU
limits, criminal resolver equivalence, privacy, exactly-once wages and room
payments, prepayment/partial payment, expiration, kept/broken/moved promises,
roster conflicts, restored work access, bounded grace, zero resources, detached
views, pure presentation, malformed saves/content, failed saves, actual M014 and
older fixtures, insertion-order replay, independent-process hash seeds, CLI
letters and resume. Longer regression paths include 56 days of lawful,
relationship and recovery play; one retains daily disk resumes, while all five
branches resume daily in their first-week regression.

The 237 baseline tests remain unchanged, including the existing long faction,
legal and navigation regressions. New atlas data, economic rules, faction policies,
job risk tables, workflows, dependencies and save identifiers were not altered.

## Five actual seven-day paths

These are service executions, not paper scenarios. Each starts at day 0 with $40,
the existing home and explicit `settle_in`; day 1 starts opportunities after a
real `wait`. The runner uses real travel and never edits gameplay state.

| Policy / seed | Cash day 7 | Unpaid room balance | Tess / Cal standing | Persistent consequence |
| --- | ---: | ---: | --- | --- |
| Lawful / 42 | $90 | $0 | 4 / 0 | Four funded repair shifts; promise honestly declined. |
| Criminal / 3 | $110 | $0 | 0 / 4 | Collection and quieter courier completed; affiliation and original job consequences persist. Includes unchanged $15 faction support. |
| Relationship / 17 | $75 | $0 | 6 / 0 | Promise kept; reference used for the two-action audit. |
| Low cash / 17 | $0 | $20 | -2 / -1 | Failed witnessed collection, conviction, missed promise, bounded room shortfall and one maintenance credit. Home remains usable. |
| Mixed / 42 | $70 | $0 | 1 / 0 | Favor renegotiated, then displaced by a paid shift; original promise breaks once. |

Final sorted-key world SHA-256 values, in the same policy order:

```text
3599a46b3f305b8bbecf9a877ee71aaffd6e336d6c71d3e0ed4c8e67161f314e
63cd9b076d8b3f26af15847a27b272d94235d9fd3a03fe396d6739ad41411efd
1e4f2116957d254d01ade00aaa0a1382c4dd77dcb147cd3ab31270df64ff673a
2346f2b2c059a2fa8cd83eacbaeffc3026f4a1950c418d950de90b4b2fb4db5b
ca12c3d8921e12dfedfd0f7778f48b862189cec42b09d95ef0b0f3bc6ffc7296
```

The regression also executes each policy without resumes and compares complete
world equality to the resumed run. Insertion-order tests reverse dictionaries
throughout a two-week mixed replay; fresh processes use hash seeds 0, 17 and 99.

## Longer campaigns and balance

| Policy | Cash day 56 | Arrears | Tess / Cal standing | Convictions | Promise outcome |
| --- | ---: | ---: | --- | ---: | --- |
| Lawful | $440 | $0 | 10 / 0 | 0 | No accepted promises |
| Criminal | $440 | $0 | 0 / 10 | 3 | No accepted promises |
| Relationship | $320 | $0 | 10 / 0 | 0 | Eight kept |
| Low-cash recovery | $330 | $0 | 10 / -1 | 1 | One broken; then lawful recovery |
| Mixed | $280 | $0 | 8 / 0 | 0 | Eight moved, then broken |

Every final 56-day run validated each day's state. No expired offer remained open,
no obligation was stuck past a processed due date, and no same-source payout or
standing reward repeated. The low-cash policy deliberately returns to lawful work
after its first week, proving an available recovery route rather than granting
automatic money or debt cancellation.

A five-seed first-week comparison (1, 3, 17, 42, 99) gave lawful cash $90 with no
cases and relationship-first cash $75 with no cases in every sample. Criminal
cash ranged from $0 to $110; seeds 17 and 99 had a conviction and $30 arrears
before any maintenance. These selected samples are not an estimate of all-seed
win rates. The criminal path offers more pay for fewer work actions when it
succeeds, with real failure/case losses. The lawful path is more predictable;
relationship investment forgoes a shift and opens different later work.

Regular repair work pays $20 for one action. The audit pays $25 for two actions
and requires a known reference/current standing. One $30 weekly contribution
therefore needs fewer than two regular shifts, with four finite regular work
windows in a week. No daily commute is necessary: a player can stay near work,
and jobs never silently travel or advance time. Actual relationship-first play
uses just three local journeys across the week. Helping earns no money; maintenance
only reduces existing arrears. Waiting without work grants no new life income or
contact standing. Existing faction support may still pay a trusted affiliate
during a day transition; that legacy advantage is retained and visible in the ledger.

No sampled path proves universal balance or the absence of every dominant policy.
Cash can accumulate through weeks of real paid work, not through repeated reports,
reloads, same-day offer reuse or extra district revenue. Debt and standing are
bounded. A missed promise costs two standing, not a permanent exclusion; ordinary
work remains possible and can restore use of a known reference.

## Manual reproduction and gameplay assessment

The automated CLI subprocess actually executes `life`, `settle_in`, `wait`,
`travel p032`, `choices goon.choice.0.opening_shift`, letter A selection,
`travel home`, `home`, `contacts`, save, quit and resume; it rejects an attempted
second wage after resume. For the complete story, the following is a **human
reproduction recipe whose service equivalent was executed**:

1. Day 0: inspect terms and accept the room arrangement.
2. Day 1: promise Tess help, work the opening shift at the store; cash $60.
3. Day 2: return home and keep the promise; no payment, reference recorded.
4. Day 3: inspect the consequences; the reference is a known later opportunity.
5. Day 4: work the store's midweek shift; cash $80.
6. Day 5: use the reference for the two-action audit; cash $105.
7. Day 6: review the account with `life`, save/resume, leave time uncommitted.
8. Day 7: the real day transition settles $30 once; cash $75, promise still kept.

Meaningful decisions include accepting/refusing a promise, choosing wages versus
help versus legal risk, renegotiating, using a more demanding reference, paying
early, and offering work against arrears. Observable persistent changes are cash,
receipts, standing and specific memories, promise state, available work, legal
records and room balance. Variety comes from competing deadlines, current known
relationships and seeded criminal outcomes; flavor text itself earns nothing.

The loop remains mechanically shallow after several weeks: one neighborhood,
two contacts, fixed templates, no dynamic civilian employer treasury, full NPC
schedules, inventory, survival meters or authored campaign. Signed references and
simple standing thresholds are not a full social simulation. Basic grace housing
is intentionally generous. Repeating the same optimal lawful roster is a grind
risk; no daily chore, forced commute, XP loop or real-time timer was added. The
full prologue, combat, DC actors and later milestones remain design-only.

## Save compatibility and review gate

All historical fixtures load without daily life, including an actual M014 save
generated from the merged baseline modules in isolation. M014 load equality is
exact; enrollment preserves player progress, actions, location and TU. The fixture
[provenance](../tests/fixtures/README.md) explains its subdirectory, preserving the
unchanged pre-navigation migration tests. Missing/unsupported life versions,
changed pinned definitions, malformed nested data, inconsistent cash/receipts,
fabricated wages and missing outcomes fail validation before play. Atomic backup
and failure-injection checks remain in use.

Final Markdown/link, diff, regression and GitHub CI results accompany the PR and
Mission 009 report. PR submission does not authorize merge or M016 implementation.
