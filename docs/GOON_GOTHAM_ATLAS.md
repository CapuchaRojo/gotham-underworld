# Gotham: The Goon — Metropolitan Atlas

**M013.1 geographical source specification, used by M014's local registry.**
[M014's runtime contract](GOON_WORLD_RUNTIME.md) identifies the implemented
location/navigation subset. This source defines no additional economic district,
GUI or rendered map; the three M013 territory accounts remain authoritative.
The remaining design sections retain proposed services and provenance, not a
claim that all metropolitan life is simulated. This is an original project continuity
proposal, not a definitive DC map or a claim of licensed status.

Companion specifications: [location registry](GOON_LOCATION_REGISTRY.md),
[travel network](GOON_TRAVEL_NETWORK.md),
[simulation/migration](GOON_MAP_SIMULATION_INTEGRATION.md),
[career geography](GOON_CAREER_GEOGRAPHY.md) and
[visual interface specification](GOON_MAP_VISUAL_SPEC.md).

## Research hierarchy and limits

Sources consulted November 3, 2026. Reference codes below identify *names or broad
design observations*, never a license to copy geometry, illustrations or stories.

| Priority / code | Available reference | Supported observation and design decision |
| --- | --- | --- |
| 1 / B | [Eliot R. Brown's account of designing Gotham for Cataclysm/No Man's Land](https://www.eliotrbrown.com/wp/gotham-city-map/) | Primary geographical inspiration: an island city, consequential mainland connections and mixed civic/working environments. Brown describes editorial revision and room for stories. Adopt that organizing approach; invent this atlas's boundaries and connections. His text also anchors Chinatown, Upper East Side, Diamond District and the airport's Archie Goodwin name. |
| 2 / AK | [Rocksteady producer's Arkham Knight city-design account](https://blog.playstation.com/?p=167402) | Secondary inspiration for density, layered urban activity and changes to familiar places. This account discusses a city full of missions and dynamic additions; it is not a street survey. No game coordinates, shoreline, mission layout or evacuation plot is reproduced. |
| 3 / GK | [Gotham Knights publisher site](https://www.gothamknightsgame.com/en-us?mode=html) | Borough organization is a useful navigation scale. Its five-borough game world and campaign premise are a separate continuity; neither its exact boundaries nor Batman's status become facts here. |
| 4 / RPG | [Monolith's Gotham Guide description](https://monolithedition.com/en/product/batmanrpg-gotham-city-guide-eng/) and [map-containing edition](https://monolithedition.com/en/product/batmanrpg-allin-skyline-en/) | Publisher text names Midtown, the Narrows, Arkham Island and Blackgate Island, and confirms a city map exists. The full commercial guide/map was not inspected. Treat it as a follow-up reference, not a verified source of detailed placements or additional copied districts. |
| 5 / D | [DC's Gotham location guide](https://www.dc.com/blog/2021/03/29/take-a-tour-of-batmans-hometown-with-exploring-gotham-city) | Name/function anchors for Bristol Township/Wayne Manor, Wayne Tower, Robinson Park, Arkham and Ace Chemical(s); East End is also mentioned. Proposed addresses and service rules below are ours. |
| 5 / P | [DC's Batman-origin history](https://www.dc.com/blog/2023/09/13/the-evolution-of-batman-s-origin) | Park Row/Crime Alley and Monarch Theatre are references whose depiction changes across versions. Choose names as content anchors; do not reenact the published origin or claim one universal block layout. |
| 5 / A | [Batman: Knightwatch #8 publisher description](https://www.dc.com/comics/batman-knightwatch-2021/batman-knightwatch-8) | Supports the Amusement Mile name. Its specific trap/story is not used. |
| 5 / I | [DC's Iceberg Lounge reference](https://www.dc.com/blog/2022/03/04/rounding-up-the-easter-eggs-in-matt-reeves-the-batman) | Supports a Penguin-associated nightclub, not this atlas's address, ownership timeline or guaranteed employer meeting. |
| 5 / H | [DC's Gotham General reference](https://www.dc.com/blog/2026-10-26/rounding-up-the-easter-eggs-in-clayface) | Supports the hospital name; no film storyline, staffing or current plot is imported. |
| 5 / K | [DC's Blackgate game description](https://www.dc.com/games/batman-arkham-origins-blackgate-2013) | Supports Blackgate as a prison on an island in that setting. Admission, transport and release in this design require their own fictional rules. |
| O | Original project proposal | Author-created label, category, arrangement or rule for this document; not a claim of uniqueness/title clearance or of established DC geography. |

No source map was traced, rasterized, embedded or converted to coordinates.
There is no GIS, image, asset, tile set, screenshot, GUI or rendered map artifact.
Game atmosphere is an influence, not evidence that two continuities share streets.
No exhaustive inspection of the games or paid RPG map is claimed. Before any
licensed content release, review chosen editions, naming, rights and continuity.

## Metropolitan boundary and hierarchy

Proposed planning root: `goon.city.gotham`. It contains **8 regions, 48 neighborhoods
and 120 named/categorized POIs**: 176 registered place records, excluding the root.
Regions are navigation/planning containers, not automatically legal boroughs,
electoral wards, police commands or faction territories. “Borough” in a display
name confers no simulation powers.

The metropolitan boundary includes three principal urban islands, adjacent
north/west/east/south mainland corridors and an outer-island group. Rural roads,
regional rail, airspace and coastal shipping continue beyond it through explicit
external portals. No real latitude, longitude, population, square-mile area or
Metropolis/Bludhaven distance is asserted. Exact survey geography remains open.

Original planning limits are the reservoir/airport catchment to the north, the
west-bank regional-rail service corridor to the west, Millbrook's catchment and
southern interchange to the south, and Outer Roadstead including the institutional
islands to the east. These are metropolitan design limits, not claimed canonical
municipal borders; external routes terminate at declared portals until extended.

The following anchors are *original schematic coordinates*, north at increasing
Y and east at increasing X. They organize prose, not a metric drawing, licensed
outline or travel heuristic. Never derive route cost from straight-line distance.

| Stable region ID | Label | Landform / schematic anchor | Character and boundary |
| --- | --- | --- | --- |
| `goon.region.r01` | Bristol Mainland | North mainland, (0, 3) | Outlying residences, reservoir and airport; southern edge meets North Borough across water |
| `goon.region.r02` | West Mainland | West bank, (-2, 0) | Housing, repair industry, rail yards and a canal frontage; West Channel separates it from the urban islands |
| `goon.region.r03` | North Borough | North urban island, (0, 2) | Park, older homes, entertainment and passenger quay; North Cut borders Central Borough |
| `goon.region.r04` | Central Borough | Central urban island, (0, 0) | Dense commerce, civic institutions, mixed markets and medical services between North and South cuts |
| `goon.region.r05` | South Borough | South urban island, (0, -2) | Park Row, East End, Narrows, theater work and older docks; South Bay faces the mainland |
| `goon.region.r06` | East Mainland | East bank, (2, 0) | Commercial port, industry, utilities and working households; Outer Roadstead faces the service islands |
| `goon.region.r07` | South Mainland | Southern shore, (0, -4) | Regional interchange, wetlands, repair work and housing; Millbrook River reaches South Bay |
| `goon.region.r08` | Outer Islands | Offshore group, (3, -2) | Breakwater service/residential island plus separate Arkham and Blackgate islands; their relative placement and connections are original proposals |

R01/R02/R06/R07 are named mainland planning sectors, not four disconnected
continents. Off-map regional roads may connect them, but no free off-map shortcut
exists in the playable graph. The three urban islands are not renamed copies of
Arkham Knight's islands. All eight region boundaries and anchor coordinates are O.

## Neighborhood organization and everyday life

The [registry](GOON_LOCATION_REGISTRY.md) is the authoritative spelling/ID list.
Each region has six planning neighborhoods and fifteen POIs. Names drawn from
sources retain a source code; *every placement, adjacency and profile is proposed*.

- R01 mixes Bristol, Cedar Slope, Reservoir Terrace, Northgate Commons, Airfield
  Ward and Meadow Exchange. Commuters, airport shifts, caregiving and reservoir
  maintenance create obligations beyond criminal work.
- R02 contains Westbank Terraces, Foundry Ward, Union Quarter, Switchyard,
  Stonecross and West Canal. Unions, tenants, repair businesses and public legal
  services matter independently of a gang's strength.
- R03 contains Upper East Side, Robinson Gardens, Amusement Mile, Gables Ward,
  Highbridge and North Quay. The sourced park is a POI within an original named
  neighborhood; entertainment has workers, neighbors and service demands.
- R04 contains Midtown, Diamond District, Chinatown, Civic Lanes, Canal Exchange
  and Market Steps. Retail, language access, courts, health and transport share
  a dense center. Identity or ethnicity never assigns a crime/security score.
- R05 contains Park Row, East End, Narrows, Old Dock Ward, Theatre Steps and South
  Gate. Poverty does not make every resident a criminal; lawful work, care,
  reentry and social ties remain credible here.
- R06 contains East Harbor, Iron Quay, Drydock Ward, Saltmarket, Chemical Reach
  and Tideworks. A port's inspection boundary differs from a worker's housing or
  public market; hazardous plants have specific safety rules, not faction immunity.
- R07 contains South Exchange, Sawmill Terrace, Reed Marsh, Outfall Ward, South
  Rail and Millbrook. Wetlands, education and recovery are useful destinations,
  not empty scenery between larger numbers.
- R08 contains Breakwater Village, Lantern Harbor, Arkham Reach, Blackgate Landing,
  Netmaker Rows and Beacon Ward. The first, second, fifth and sixth share Breakwater
  Island. Arkham Reach and Blackgate Landing are outside-perimeter arrival/service
  neighborhoods on the two distinct institutional islands, not labels for patients
  or automatic admission states. These residential/service layouts are proposals.

Housing exists in several price/support contexts, not only player-owned bases.
Shops, diners, schools, union halls, libraries, repair cooperatives, parks and
ordinary clinics create everyday routines and contacts. None is automatically a
safehouse, criminal enterprise, faction asset or encounter with a famous character.

## Water, shoreline and crossings

| Proposed water ID / name | Topological relationship | Work / disruption implications |
| --- | --- | --- |
| `goon.water.w01` — West Channel | R02 west bank to R03/R04/R05 urban shores | Bridge alternatives and passenger ferries; fog/maintenance events need finite, signaled effects |
| `goon.water.w02` — East Channel | Urban islands to R06 | Cargo, service travel and marine jurisdiction, without automatic illegal access |
| `goon.water.w03` — North Cut | R03 to R04 | Garden Bridge and Quay Tunnel are distinct road/rail connections |
| `goon.water.w04` — South Cut | R04 to R05 | Market Bridge and Civic Rail Tunnel provide distinct modes |
| `goon.water.w05` — South Bay | R05, R07 and outer shipping approaches | Causeway, regional rail and ferry choices; no invisible land edge across the bay |
| `goon.water.w06` — Outer Roadstead | R06 to R08 and open coast | Public/service ferries and coastal freight; institutions retain separate perimeter access |
| `goon.water.w07` — Millbrook River | R07 inland catchment to South Bay | Wetland/utility incidents affect known local services through bounded events |

All seven water names/shapes and the seventeen named travel corridors in the
[network specification](GOON_TRAVEL_NETWORK.md#named-crossings-and-regional-links)
are O. There are no implicit roads between separated islands. The Northgate
crossing also spans the northern inlet between R01 and R03, treated as the north
reach of West Channel. Breakwater-to-Arkham water is a local part of Outer Roadstead.

Proposed road hierarchy: **Civic Spine Expressway** links Northgate Bridge through
R03/R04/R05 to South Bay Causeway; **Westbank Distributor** links R02's crossings;
**Eastern Freight Road** joins the port/industrial neighborhoods; **South Shore
Connector** serves R07. Neighborhood streets are Lantern Avenue, Market Way,
Foundry Street and Quayside Road as local naming templates, with unique IDs per
actual segment. These names and alignments are O, not copies of Brown's road plan.
Highways do not permit walking where a separate path/bridge sidewalk is absent.

## Rail, airports and ports

The proposed **Civic metro corridor** connects Northgate, Highbridge, Midtown,
Civic Lanes and South Gate through explicitly listed crossing modes. **Regional
rail** connects Meadow Exchange, Switchyard, Civic Lanes, Drydock Ward and South
Rail using the defined local access and rail-enabled corridors. Route/service IDs
are overlays over graph edges; a line diagram cannot create a new physical link.
Public buses supply local connectors and road-crossing alternatives. No real-time
timetable, server clock, gliding or Batmobile-only route is required for a goon.

Archie Goodwin International Airport occupies proposed Airfield Ward; Brown's
account anchors the name, not this placement or terminal design. Commercial freight
uses East Harbor and Drydock; passenger services use North Quay, West Canal and
Breakwater. Air travel beyond the metropolitan boundary is a later optional
campaign transition, not free fast travel within the city. Port ownership,
customs/security access and faction influence are distinct.

## Civic, care, institutional and criminal landmarks

The registry includes hospitals, community care, voluntary counseling, legal aid,
public court counters, police/marine facilities, education, emergency shelter and
reentry services. Their availability, consent and confidentiality follow the
[institution proposal](GOON_INSTITUTIONS_AND_RECOVERY.md); travel to a reception
does not admit a patient, arrest someone, grant an appeal or finish treatment.

Proposed service overlays are `goon.jurisdiction.urban` for R03–R05 public GCPD
services, `goon.jurisdiction.mainland` for coordinated R01/R02/R06/R07 services,
and `goon.jurisdiction.marine` for the port/water network and island approaches.
Institutional administration is a separate mandate, not a general police district.
These boundaries/agency arrangements are original placeholders requiring fictional
legal review, not canonical claims. Court counters provide access to services;
crossing a service boundary neither deletes a case nor transfers custody by itself.

Arkham and Blackgate are separate locations with different mandates. A public
arrival area is not unrestricted access to a ward or prison. Visiting, work,
evaluation, lawful admission and custody transfer require distinct permissions.
Arkham access never guarantees Joker's presence or bypasses the
[direct-encounter initiation proposal](GOON_JOKER_RECRUITMENT.md).

Iceberg Lounge is proposed in Diamond District; this is an authored address, not
a canonical placement claim. Ace Chemicals, dock services and brokers can host
work, refusal or consequences without becoming collectible villain bases. A
[minor crew](GOON_MINOR_CRIMINAL_ECOSYSTEM.md) can be influential in a neighborhood
without owning it. Actual crimes require actors, decisions and evidence; a map
label or neighborhood profile never manufactures guilt.

## Open questions and approval boundaries

Reconcile exact names/spellings, selected editions, Arkham's and Blackgate's
placement, the airport, regional jurisdiction and institutional transport before
implementation. Review the full Brown map/annotations and available licensed RPG
reference through authorized access if a later milestone needs more precise
provenance; do not infer uninspected details from fan-redrawn maps. The design
does not adopt Arkham Knight's evacuation or Gotham Knights' campaign timeline.

The atlas supplies no licensed map imagery and makes no claim of DC authorization,
title clearance or distribution rights. An eventual content pack, geographical
migration, gameplay feature or GUI needs separate approval. M014 is not begun or
expanded by these documents.
