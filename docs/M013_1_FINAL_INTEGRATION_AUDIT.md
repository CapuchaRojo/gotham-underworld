# M013.1 final integration audit

Mission 006, November 3, 2026. Reviewed PR #13 from M013 master
`eb931ce33c079018159aad14c2327561d9fa195f`, initially at feature commit
`47ee203f43ca01bb7adae7f716e97c196a8c8ed4`. This report records the source/design
audit and executable checks; GitHub records the final reviewed commit, CI and
conditional merge disposition. It does not predict a merge or authorize M014.

## Scope and repository evidence

The incoming complete diff contained 20 Markdown files and `gameplay.py`. All
18 design documents, README, project state, and the complete changed display
code were inspected together. M013 is on master through PR #12. The starting
working tree was clean; no conflicting changes or generated files were present.
No dependencies, workflow/test changes, save schemas, gameplay reducers, content
identifiers or package/repository renames are part of this PR. The only Python
change is four banner lines replacing one line and `underworld>` becoming `goon>`.
The reproducible check below compares Python ASTs after exactly those changes.

Corrections in this audit are Markdown only: travel, career geography, project
state, README navigation and this report. Runtime tests remain the 198-test M013
baseline. This document's checker is an optional specification review excerpt,
not an installed module, gameplay implementation or new regression-suite test.

## Confirmed defects and corrections

| Severity | Verified defect in the incoming design | Correction / evidence |
| --- | --- | --- |
| Medium | The network counted 120 POI links without defining their stable IDs or direction. A future implementation could derive incompatible identities or treat entry gates as containment. | [Travel: POI link contract](GOON_TRAVEL_NETWORK.md#poi-link-identity-direction-and-lawful-return) defines `goon.edge.access.pNNN`, exact parent endpoints, zero-cost walking spurs, physical bidirectionality and direction-specific traversal keys. All 120 derived IDs/parents are checked below. |
| Medium | Bidirectional e16 required receiving permission without a return entitlement; expiring visitor authorization or repeatedly extended closures could strand a free visitor on Blackgate's sole connection. | Entry and lawful egress are distinct. Outbound authorization includes disclosed return rights; occupied-hub isolation requires a pinned finite reopening/alternate/authorized-transfer outcome and free help. Actual custody, safety, admission and discharge remain separate authorities. No visitor escape rule is introduced. |
| Medium | The [career commute](GOON_CAREER_GEOGRAPHY.md#worked-paper-scenarios) stated a 16-TU bus return cost, overlooking n13–n18–n23–n31 at 12 TU. Its Garden Bridge disruption did not affect that faster route. | Corrected both documents: baseline 6 TU each way; Quay Tunnel closure raises the fastest public trip to 8 each way. The old arithmetic was valid for its selected detour, but did not establish the claimed choice constraint. |
| Low | Suggested routing state omitted mobile vehicle identity/location, although the same proposal allowed parked cars/boats and mode changes. | Limited the simplified search to fixed eligibility/public transit; future vehicle planning needs vehicle/location/authorization state or a fixed itinerary. |
| Low | Project state said not to merge automatically under the earlier review-only mission, conflicting with Mission 006's explicit conditional merge authorization. Validation wording also predated the final audit. | State now names the conditional gates, links actual evidence, and keeps M014 unapproved. |

No confirmed runtime regression, Critical/High defect, or remaining merge blocker
was found in the reviewed scope. The clarified rules remain proposed contracts;
their future implementation must prove the safeguards with executable tests.

## Geography and the provisional 18 TU

Validated 8 regions, 48 neighborhoods and 120 POIs: 176 unique place records,
excluding the city container. Each region has six neighborhoods/fifteen POIs;
all parent chains and profile tokens resolve, and every neighborhood has a POI.
There are 63 physical corridors (17 named plus 46 local) and 120 derived access
links. Local streets never cross the separate Arkham/Blackgate water. Named
crossings match the atlas's region/water relationships; schematic coordinates
are not metric distances or routing heuristics.

With all services available, walking/bus/rail/ferry reach 47 public neighborhoods;
n46 is intentionally inaccessible without Blackgate authorization. Authorized
public-mode travel connects all 48. Closing e16 isolates n46 physically, explaining
why return/support guarantees are necessary. Physical bidirectionality does not
override direction/mode closures or area-entry permission. Player-known routing,
actual revalidation and safe-prefix discovery are distinct from omniscient views.

Independent shortest-path calculations include boarding on each separate journey,
no free vehicles, no private interiors and no service schedules. All 2,304
authorized origin/destination queries selected the same path when edge insertion
order was reversed. This validates the written base graph, not future travel code.

| Representative proposed trip | Out / return TU | Assessment against 18 TU |
| --- | --- | --- |
| Upper East Side n13 → East Harbor n31 work | 6 / 6 | 12 total; useful commute, six TU remain |
| Same trip, Quay Tunnel e06 closed | 8 / 8 | 16 total; only two TU of flexibility |
| Iron Quay n32 → East Harbor n31 work | 2 / 2 | 4 total; local work preserves flexibility |
| Narrows n27 → local p066 care/reentry frontage | 0 / 0 | Local approach is abstracted; care eligibility, consent and activity costs remain separate |
| Millbrook n42 → South Market hospital p092/n37 | 2 / 2 | 4 total; care near home is practical in the base graph |
| Upper East Side n13 → Arkham arrival n45 | 9 / 9 | 18 total; no spare travel; no automatic admission or Joker meeting |
| Upper East Side n13 → authorized Blackgate visitor arrival n46 | 9 / 9 | 18 total; permission/return arrangement required, no spare travel |
| Reservoir Terrace n03 → Outfall Ward n40 work | 17 / 17 | 34 total; same-day commute fails, so alternative work/waypoints are necessary |
| Arkham arrival n45 → Lantern support p109/n44 | 3 / 3 | 6 total while e15/local service is open; reception/support is not treatment or discharge |

Of 2,162 ordered distinct public pairs, 1,414 (65.4%) fit an 18-TU round trip;
the maximum shortest one-way cost is 19 TU. Thus connectivity does **not** imply
same-day access. Eighteen TU is a tuning hypothesis, not an approved minimum or
proof against softlocks. Emergency help at an occupied hub must be available when
TU/actions are exhausted; urgent care/authorized transport needs its own bounded
future contract. A compulsory distant hospital commute or prisoner journey cannot
be implemented as an ordinary unaffordable visitor route. Custody transfer time
and review horizons remain unapproved; this audit does not invent them.

## Narrative integration findings

The career web permits overlapping skills, civilian work, informing, reform,
retirement, independence and responsibility without compulsory leadership or
killing. References, personal code and relationships are audience/actor-specific;
refusal can lose work while preserving a friendship. Conditional opportunities
persist eligibility/draw results, including no offer, and provide other routes
when a named actor is absent. These are proposals, not implemented careers.

The 35-entry rogue registry separates actors, mantles/personas and crews. Terrible
Trio has three actor references; Scarface/Wesker must not duplicate payments.
Minor workers/crews can rise, dissolve, defect, be arrested or retire without
district ownership, full treasuries or warfare. A future promotion to full faction
status needs explicit economic activation with the same identity and one turn.

Joker street/cell work remains independent of membership. Formal initiation is
an original campaign proposal requiring direct encounter during an Arkham story,
an eligible offer and voluntary acceptance. It is neither universal DC lore nor
a current command. Absence/refusal does not block care, release or completion.
Autonomous cells may operate during his absence. Institutions distinguish custody,
evaluation, psychiatric admission, voluntary care and supervision. Finite review,
ordinary staff, zero-cash support and alternative providers preserve agency.
No conviction-only psychiatric commitment or mandatory villain cure is proposed.

Canon fields are labeled separately from original workplace/gameplay proposals.
Primary-source spot checks included [Brown's design account](https://www.eliotrbrown.com/wp/gotham-city-map/),
[DC's Gotham guide](https://www.dc.com/blog/2021/03/29/take-a-tour-of-batmans-hometown-with-exploring-gotham-city),
[Monolith's publisher description](https://monolithedition.com/en/product/batmanrpg-gotham-city-guide-eng/),
[Condiment King's distinct holders](https://www.dc.com/blog/2020/07/08/lets-get-saucy-everything-you-need-to-know-about-condiment-king),
[Johnny's solicitation spelling](https://www.dc.com/comics/batman-660),
[Killer Moth's mantle overview](https://www.dc.com/blog/2017/04/26/miles-to-go-the-un-familiar-faces-of-all-star-batman),
[Killer Croc's capability profile](https://www.dc.com/characters/killer-croc) and
[Gotham General's name reference](https://www.dc.com/blog/2026-10-26/rounding-up-the-easter-eggs-in-clayface).
These support conservative motifs/names, not this game's placements or mechanics.
Secondary anchors and unresolved spellings/holders are explicitly provisional.
Every cited comic edition and every external URL was not independently verified.
Primary-edition/continuity review is required before a character pack, not before
retaining clearly qualified research proposals. No copied scripts, panels, media,
third-party narrator cast or reproduced storyline was found in the diff; this is
an inspection finding, not a legal clearance or exhaustive provenance guarantee.

## Technical compatibility and remaining risks

| Verified current boundary | Consequence for incremental adoption |
| --- | --- |
| `game_service.py`: allowlisted named string arguments, candidate-world copy, commit on success, three shared costly actions, detached envelopes/snapshots | Future travel/tactical continuations need explicit costs and conflict guards. Views cannot mutate, tick, refresh or reroll. Three actions remain unchanged here. |
| `career_state.py`, `career_persistence.py`, subsystem validators: strict known fields/versions and additive defaults; validated staged replacement/backup | Optional geography needs pinned definitions and explicit opt-in/activation. Unknown old homes/history remain unknown. Single writer and filesystem hard-link/replace support remain limitations. |
| `gameplay.next_day`: clock/legacy activity → legal review/cooling → career investigation → NPC activity → economy/plans/warfare → court | New phases require explicit order and markers; don't advance per street, screen or combat animation. Existing investigation guards preserve legitimate NPC acceleration. |
| `faction_competition.py` and `territory.capture`: one economic area/account, funded actions, bounded recovery/power and shared exhausted-control capture | Eight regions/48 neighborhoods create no income, upkeep, faction or capture tick. Footprints are read projections of the three preserved district accounts. |
| `simulation.event` / service sequence: structured domain metadata; unique command IDs, no universal event identity | Future incidents/encounters need explicit domain instance/turn/outcome IDs and settlement markers. This is snapshot persistence, not complete event sourcing. |
| `consequence_engine.py`, `career_state.py`: pending cases require a witnessed job's `source_attempt`; legal responses/court depend on that contract | Combat needs the documented additive case-source adapter across validation, investigation, NPC acceleration, responses/court and events. Fabricating a job is invalid. |
| `city_intelligence.py`, strategy views: detached actual facts, no knowledge filter | A future ordinary map needs a separate knowledge read adapter. Relabeling full-state facts as rumors leaks information. |

Nonblocking design risks remain: no selected universal DC continuity/title/rights
clearance; no approved institution durations, travel constant, transit schedules,
vehicle-state model or emergency transport; no proof of fun from tables alone.
Nineteen specialties/35 rogues/176 places are a content budget risk. Current jobs,
three-district economy, threshold NPCs and fine-based courts remain shallow.
Existing name keys, fixed legacy feud roster and named NPC policies require
compatible adapters before a larger cast. Copy-on-command and growing logs need
measurement before optimization. No framework/rewrite is justified by this PR.

M014 is ready for **bounded contract review only**: approve daily/tactical costs,
six-turn cap, provisional statistics, zero-action exits, defeat/recovery behavior,
neutral fixture scope and compatible legal-source migration before implementation.
Atlas, careers, institutional chapters and licensed actors are not M014 scope.
No M014 implementation or public distribution is authorized by merging this PR.

## Executed validation and reproduction

Windows / Python 3.14.2:

- `python -B -m unittest discover -s tests -v`: **198 passed**, 32.794 seconds
  during this audit. Includes existing persistence-failure/malformed-save cases,
  M001–M012 migrations, CLI/resume, atomic rejections, detached reports,
  daily idempotency, insertion-order/fresh-process hash-seed replay, 365-day disk
  resumes, 90-day legal replay, four 365-day campaigns and one 1,000-day campaign.
- The checker below validates local links/anchors, fenced JSON and Python syntax,
  exact geography/profile/parent totals, named crossings, public/authorized
  reachability, closure examples, route ordering and display-only AST equivalence.
  Its specification calculations do not test unimplemented travel/institutions.
- `python -B -m unittest discover -s tests -v -k migrate -k migration -k determinism -k deterministic -k replay -k resume -k round_trip -k failed_ -k malformed`:
  **35 passed**, 22.937 seconds. These are existing tests selected for a focused
  migration/failure/replay pass, not 35 added tests.
- Embedded checker: **21 Markdown files, 192 local links/anchors, two JSON
  examples**, Python fences, geography and display-only scope checks passed.
- Existing-game service walkthrough was also executed in memory: seed 42, join
  Harbor, three collections, wait → case 1/evidence 2; fork accept/cooperate/
  contest, then advance each branch twice. All branches validated; assessed
  conviction fines were $35/$30/$50 respectively (contest additionally costs $20).
  This reproduces the gameplay-principles recipe without creating a save file;
  it does not exercise a new narrative feature.
- `git diff --check` and final staged/full-diff review are merge gates. GitHub CI
  must succeed on the final reviewed feature SHA; initial checks on `47ee203`
  alone are insufficient. Merge must match that final head without admin bypass.
- After merge: synchronize master, rerun the complete suite, verify a clean tree,
  and report the actual merge/master hashes and CI links in the mission response.

Run the embedded standard-library checker from the repository root in PowerShell:

```powershell
@'
from pathlib import Path
text = Path('docs/M013_1_FINAL_INTEGRATION_AUDIT.md').read_text(encoding='utf-8')
exec(text.split('```python\n', 1)[1].split('\n```', 1)[0])
'@ | python -B -
```

The excerpt reconstructs a proposal from tables/ring rules. It does not import a
graph into the engine, persist locations or establish future route safety.

```python
from pathlib import Path
from collections import Counter
from urllib.parse import unquote
import ast
import heapq
import json
import re
import subprocess

BASE = 'eb931ce33c079018159aad14c2327561d9fa195f'
root = Path.cwd()
docs = [root / 'README.md', root / 'PROJECT_STATE.md', *sorted((root / 'docs').glob('*.md'))]
def plain(text):
    return re.sub(r'^```[^\n]*\n.*?\n```[ \t]*$', '', text, flags=re.S | re.M)
def anchors(text):
    found, counts = set(), Counter()
    for heading in re.findall(r'^#{1,6} (.+)$', plain(text), re.M):
        slug = re.sub(r'[^\w\- ]', '', heading.lower()).replace(' ', '-')
        found.add(slug + (f'-{counts[slug]}' if counts[slug] else ''))
        counts[slug] += 1
    return found
links = blocks = 0
for doc in docs:
    text = doc.read_text(encoding='utf-8')
    assert len(re.findall(r'^```', text, re.M)) % 2 == 0, doc
    for language, body in re.findall(r'^```([^\n]*)\n(.*?)\n```[ \t]*$', text, re.S | re.M):
        if language == 'json': json.loads(body); blocks += 1
        if language == 'python': ast.parse(body)
    for target in re.findall(r'\]\(([^)]+)\)', plain(text)):
        if re.match(r'\w+://|mailto:', target): continue
        file, _, fragment = unquote(target).partition('#')
        dest = (doc.parent / file).resolve() if file else doc
        assert dest.exists(), (doc, target)
        if fragment: assert fragment in anchors(dest.read_text(encoding='utf-8')), (doc, target)
        links += 1
print(f'Documents={len(docs)}; local links/anchors={links}; JSON examples={blocks}; Python fences parse')

rogues = (root / 'docs/GOON_ROGUES_GALLERY_REGISTRY.md').read_text(encoding='utf-8')
entries = re.split(r'^## \d{2}\. ', rogues, flags=re.M)[1:]
identities = [re.search(r'\*\*ID / identity:\*\* `([^`]+)`', entry).group(1) for entry in entries]
assert len(identities) == len(set(identities)) == 35
assert all(ident.startswith(('dc.character.', 'dc.crew.', 'dc.persona.')) for ident in identities)
print('Rogue entries=35; primary proposed IDs unique; actor/persona/group types explicit')

registry = (root / 'docs/GOON_LOCATION_REGISTRY.md').read_text(encoding='utf-8')
rows = {}
for line in registry.splitlines():
    if not re.match(r'\| `goon\.(region|neighborhood|poi)\.', line): continue
    cells = [c.strip() for c in line.strip('|').split('|')]
    assert len(cells) == 11
    ident = re.fullmatch(r'`([^`]+)`', cells[0]).group(1)
    assert ident not in rows
    rows[ident] = cells
assert [sum(k.startswith('goon.' + t + '.') for k in rows) for t in ('region', 'neighborhood', 'poi')] == [8, 48, 120]
for k, c in rows.items():
    parents = re.findall(r'`([^`]+)`', c[2])
    assert all(p == 'goon.city.gotham' or p in rows for p in parents)
    if k.startswith('goon.poi.'):
        assert len(parents) == 2 and re.findall(r'`([^`]+)`', rows[parents[0]][2]) == [parents[1]]
    for value, pattern in zip(c[4:10], (r'(PUB|ENT|WORK|HOME|CARE|VIS|SEC|HELP)', r'E[1-8]', r'S[1-5]', r'C[0-7]', r'V[1-8]', r'N(?:10|[1-9])')):
        assert all(re.fullmatch(pattern, t) for t in value.split('+')), (k, value)
for r in range(1, 9):
    rid = f'goon.region.r{r:02}'
    assert sum(c[2] == f'`{rid}`' for c in rows.values()) == 6
    assert sum(k.startswith('goon.poi.') and f'`{rid}`' in c[2] for k, c in rows.items()) == 15
assert all(any(f'`{n}`' in c[2] for k, c in rows.items() if k.startswith('goon.poi.')) for n in rows if n.startswith('goon.neighborhood.'))
network = (root / 'docs/GOON_TRAVEL_NETWORK.md').read_text(encoding='utf-8')
assert 'goon.edge.access.pNNN' in network and 'bidirectional physical spurs' in network
edges = []
for line in network.splitlines():
    if not re.match(r'\| e\d\d ', line): continue
    c = [x.strip() for x in line.strip('|').split('|')]
    a, b = map(int, re.findall(r'n(\d\d)', c[1]))
    modes = {m: int(t) for m, t in re.findall(r'(walk|car|bus|rail|ferry|boat) (\d+)', c[3])}
    assert modes and all(t > 0 for t in modes.values())
    edges.append((f'goon.edge.{c[0].split()[0]}', a, b, modes))
expected_regions = [(1,3),(2,3),(2,4),(2,5),(3,4),(3,4),(4,5),(4,5),(4,6),(6,5),(5,7),(7,6),(6,8),(3,8),(8,8),(8,8),(7,8)]
assert [((a-1)//6+1, (b-1)//6+1) for _, a, b, _ in edges] == expected_regions
rail = {frozenset(p) for p in [(4,5),(5,6),(9,10),(17,18),(31,32),(32,33)]}
for r in range(1, 9):
    nodes = list(range((r-1)*6+1, r*6+1)) if r < 8 else [43,44,47,48]
    for j, (a,b) in enumerate(zip(nodes, nodes[1:] + nodes[:1]), 1):
        modes = {'walk':2, 'car':1, 'bus':1}
        if r == 4 or frozenset((a,b)) in rail: modes['rail'] = 1
        edges.append((f'goon.edge.local.r{r:02}.{j:02}', a, b, modes))
assert len(edges) == len({e[0] for e in edges}) == 63
assert all(f'goon.neighborhood.n{n:02}' in rows for _, a, b, _ in edges for n in (a,b))
access = [(f'goon.edge.access.{k.rsplit(".",1)[1]}', re.findall(r'`([^`]+)`', c[2])[0], k) for k,c in rows.items() if k.startswith('goon.poi.')]
assert len(access) == len({e[0] for e in access}) == 120

def route(a, b, closed=frozenset(), permit=False, reverse=False):
    adj = {n:[] for n in range(1,49)}
    for eid,x,y,modes in reversed(edges) if reverse else edges:
        if eid in closed or (eid == 'goon.edge.e16' and not permit): continue
        for m,tu in modes.items():
            if m not in ('walk','bus','rail','ferry'): continue
            for s,t in ((x,y),(y,x)): adj[s].append((eid,t,m,tu))
    queue, best = [(0,0,(),a,'walk')], {}
    while queue:
        cost,changes,path,node,mode = heapq.heappop(queue)
        rank = (cost,changes,path)
        if best.get((node,mode),rank) < rank: continue
        if node == b: return cost,changes,path
        for eid,t,m,tu in sorted(adj[node]):
            change = int(m != mode)
            nxt = (cost + tu + int(m != 'walk' and change), changes + change, path + (eid,))
            if nxt < best.get((t,m),(10**9,10**9,())):
                best[t,m] = nxt
                heapq.heappush(queue,(*nxt,t,m))
    return None

public = [n for n in range(1,49) if n != 46]
assert all(route(a,b) for a in public for b in public)
assert route(43,46) is None and route(43,46,permit=True)[0] == 3
assert all(route(a,b,permit=True) == route(a,b,permit=True,reverse=True) for a in range(1,49) for b in range(1,49))
assert route(43,46,closed={'goon.edge.e16'},permit=True) is None
assert route(13,31)[0] == 6 and route(13,31,closed={'goon.edge.e06'})[0] == 8
assert route(13,31,closed={'goon.edge.e05'})[0] == 6
costs = [route(a,b)[0] for a in public for b in public if a != b]
assert len(costs) == 2162 and max(costs) == 19 and sum(c*2 <= 18 for c in costs) == 1414
for a,b,cost in [(32,31,2),(27,27,0),(42,37,2),(13,45,9),(13,46,9),(3,40,17),(45,44,3)]:
    assert route(a,b,permit=True)[0] == route(b,a,permit=True)[0] == cost
print('Places=8/48/120; corridors=63; access links=120; public hubs=47; authorized=48')
print('All 2304 ordered authorized queries stable; public round trips <=18: 1414/2162; max one-way=19')

changed = subprocess.check_output(['git','diff','--name-only',BASE], text=True).splitlines()
assert all(p.endswith('.md') or p == 'gameplay.py' for p in changed), changed
old = ast.parse(subprocess.check_output(['git','show',BASE + ':gameplay.py'], text=True))
new = ast.parse((root / 'gameplay.py').read_text(encoding='utf-8'))
oldplay = next(n for n in old.body if isinstance(n,ast.FunctionDef) and n.name == 'play')
newplay = next(n for n in new.body if isinstance(n,ast.FunctionDef) and n.name == 'play')
assert oldplay.body[2].value.args[0].value == 'UNDERWORLD - M013 faction competition. Three actions per day; wait to refresh.'
assert [n.value.args[0].value for n in newplay.body[2:6]] == [
    'Gotham: The Goon - A Living Gotham Crime RPG',
    "Everybody wants to rule Gotham. You're just trying to survive it.",
    'Unofficial DC-inspired prototype; no claimed endorsement or license. Working title not legally cleared.',
    'M013 faction competition. Three actions per day; wait to refresh.']
oldplay.body[2:3] = newplay.body[2:6]
prompts = 0
for n in ast.walk(old):
    if isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id == 'input' and n.args and isinstance(n.args[0],ast.Constant) and n.args[0].value == 'underworld> ':
        n.args[0].value = 'goon> '
        prompts += 1
assert prompts == 1 and ast.dump(old) == ast.dump(new)
print('Full tracked diff stays Markdown/display-only; Python AST differs only by approved banner/prompt')
```
