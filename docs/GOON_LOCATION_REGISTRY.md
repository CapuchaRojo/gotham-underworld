# Gotham: The Goon — Location Registry

**M013.1 source registry.** M014 converts these records to validated
[local runtime data](../content/gotham_atlas_v1.json); see the
[runtime contract](GOON_WORLD_RUNTIME.md) for current access/frontage semantics.
This source table itself adds no save state or admission rules.
Totals: **8 regions, 48 neighborhoods, 120 POIs = 176 place records**. The planning
root `goon.city.gotham` is a namespace/container, excluded from those totals.
Full proposed IDs are printed below; names may change without changing identity.

Source codes resolve to the [atlas research table](GOON_GOTHAM_ATLAS.md#research-hierarchy-and-limits).
O means an original project proposal, not a claim of worldwide name uniqueness
or clearance. A sourced name supports its existence/motif only: **all placements,
boundaries, access rules, economic/security/activity/NPC profiles are original
proposals**, including the profiles of canonical landmarks. No campaign is assumed
to contain every location/character at once.

## Profile definitions

Each row explicitly supplies all eleven fields. Profile codes expand to the
following bounded design meanings; plus signs combine listed profiles. They are
human-readable specification tokens, not implemented schema values. Neighborhood
access describes its public arrival hub, not a right to enter every building.
A POI's parent lists both neighborhood and region. Regions aggregate varied
conditions; their broad tags do not override individual locations.

| Access code | Proposed requirement |
| --- | --- |
| PUB | Public frontage/counter during published game-day availability; no membership requirement |
| ENT | Customer, ticket or booking terms where applicable; only public parts, with any price shown |
| WORK | Valid contract, invitation or work authorization for the selected area |
| HOME | Resident/owner consent or a valid housing agreement; public street remains separate |
| CARE | Public request/intake and informed care consent; evaluation/admission/ward access require distinct approved rules, never conviction alone |
| VIS | Valid visit, work, representation or transfer purpose; separate receiving permission; not access to every ward/cell |
| SEC | Explicit staff/service/investigation permission to the specific restricted area |
| HELP | Basic zero-cash information/support route; no arrest, villain meeting or purchased rescue prerequisite |

| Economy | Proposed character, not automatic income |
| --- | --- |
| E1 | Housing and household services; wages/agreements need their own funding rules |
| E2 | Retail, professional services and small business |
| E3 | Manufacturing, repair and skilled labor |
| E4 | Transport, freight and dispatch |
| E5 | Civic, education, advocacy or nonprofit services |
| E6 | Health, voluntary care, supported housing and reentry |
| E7 | Entertainment, hospitality and social work |
| E8 | Green space, ecology, utilities and maintenance |

| Security | Baseline access/law-enforcement profile, not an arrest probability |
| --- | --- |
| S1 | Public/community setting with ordinary service coverage and specific witnesses |
| S2 | Staffed commercial/service frontage; controlled back rooms |
| S3 | Civic/institutional/private controlled perimeter; public counter distinct from secure interior |
| S4 | Transport/port checks with separate public, worker and regulated areas |
| S5 | Safety-supervised industrial/utility area; hazards and authorization are explicit |

Police jurisdictions are a separate overlay. These tags grant no legal immunity
and do not generate evidence, cases, confiscation or universal NPC knowledge.

| Criminal opportunity tag | Potential authored conflict, never a mandatory offense or real-world method |
| --- | --- |
| C0 | No specific criminal commission scheduled by this profile |
| C1 | Disputed freight, contraband allegations or coercive delivery terms |
| C2 | Property loss, misrepresented identity or a disputed service claim |
| C3 | Intimidation, unpaid shares or coercive obligations |
| C4 | Corruption, confidentiality abuse or contested legal/institutional information |
| C5 | Unsafe/destructive commissions, exposure or responsibility for harm |
| C6 | Rumors, manipulative recruitment, uncertain promises or personal loyalties |
| C7 | Disputed ownership, fencing or a harmful acquisition commission |

| Civilian activity | Everyday use |
| --- | --- |
| V1 | Shopping, services, food and honest commerce |
| V2 | Housing, personal support, household commitments |
| V3 | Paid work, repair, training and maintenance |
| V4 | Lawful travel, cargo, dispatch and transfers |
| V5 | Public administration, education, legal aid and civic support |
| V6 | Medical care, voluntary counseling, recovery and reentry |
| V7 | Arts, leisure, hospitality and social contact |
| V8 | Parks, ecology, outdoor recreation and conservation |

| Potential NPC pool | Conditional association, not a guaranteed named encounter |
| --- | --- |
| N1 | Residents, tenants, local traders and ordinary coworkers |
| N2 | Drivers, dispatchers, transit and ferry workers |
| N3 | Advocates, court staff, civic workers and investigators |
| N4 | Ethical practitioners, care staff and independently consenting service users |
| N5 | Dock workers, brokers and eligible minor-crew contacts |
| N6 | Engineers, repairers, technical specialists and labor representatives |
| N7 | Performers, stagehands, hospitality workers and patrons |
| N8 | Park staff, gardeners, conservation workers and neighbors |
| N9 | Institutional administrators, guards, advocates and family visitors |
| N10 | Eligible rogues/employer intermediaries from approved content, never spawned merely by visiting |

## Regions

| Stable ID | Name | Parent | Type | Access | Economy | Security | Criminal activity | Civilian activity | NPC pool | Source |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `goon.region.r01` | Bristol Mainland | `goon.city.gotham` | region | PUB | E1+E4 | S1 | C2 | V2+V4 | N1+N2 | O; D name |
| `goon.region.r02` | West Mainland | `goon.city.gotham` | region | PUB | E1+E3 | S1 | C3 | V2+V3 | N1+N6 | O |
| `goon.region.r03` | North Borough | `goon.city.gotham` | region | PUB | E1+E7 | S1 | C6 | V2+V7 | N1+N7 | O |
| `goon.region.r04` | Central Borough | `goon.city.gotham` | region | PUB | E2+E5 | S2 | C4 | V1+V5 | N1+N3 | O |
| `goon.region.r05` | South Borough | `goon.city.gotham` | region | PUB | E1+E2 | S1 | C3 | V2+V3 | N1+N4 | O |
| `goon.region.r06` | East Mainland | `goon.city.gotham` | region | PUB | E3+E4 | S4 | C1 | V3+V4 | N5+N6 | O |
| `goon.region.r07` | South Mainland | `goon.city.gotham` | region | PUB | E1+E8 | S1 | C5 | V2+V8 | N1+N8 | O |
| `goon.region.r08` | Outer Islands | `goon.city.gotham` | region | PUB | E4+E5 | S3 | C6 | V4+V5 | N2+N9 | O; RPG island names |

## Neighborhoods

| Stable ID | Name | Parent | Type | Access | Economy | Security | Criminal activity | Civilian activity | NPC pool | Source |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `goon.neighborhood.n01` | Bristol Township | `goon.region.r01` | neighborhood | PUB | E1 | S1 | C2 | V2 | N1 | D |
| `goon.neighborhood.n02` | Cedar Slope | `goon.region.r01` | neighborhood | PUB | E1+E3 | S1 | C3 | V2+V3 | N1+N6 | O |
| `goon.neighborhood.n03` | Reservoir Terrace | `goon.region.r01` | neighborhood | PUB | E8 | S5 | C5 | V8 | N8 | O |
| `goon.neighborhood.n04` | Northgate Commons | `goon.region.r01` | neighborhood | PUB | E5+E6 | S2 | C4 | V5+V6 | N3+N4 | O |
| `goon.neighborhood.n05` | Airfield Ward | `goon.region.r01` | neighborhood | PUB | E4 | S4 | C1 | V4 | N2 | O |
| `goon.neighborhood.n06` | Meadow Exchange | `goon.region.r01` | neighborhood | PUB | E2+E4 | S1 | C1 | V1+V4 | N1+N2 | O |
| `goon.neighborhood.n07` | Westbank Terraces | `goon.region.r02` | neighborhood | PUB | E1 | S1 | C2 | V2 | N1 | O |
| `goon.neighborhood.n08` | Foundry Ward | `goon.region.r02` | neighborhood | PUB | E3 | S5 | C5 | V3 | N6 | O |
| `goon.neighborhood.n09` | Union Quarter | `goon.region.r02` | neighborhood | PUB | E5+E3 | S1 | C3 | V3+V5 | N1+N6 | O |
| `goon.neighborhood.n10` | Switchyard | `goon.region.r02` | neighborhood | PUB | E4 | S4 | C1 | V4 | N2 | O |
| `goon.neighborhood.n11` | Stonecross | `goon.region.r02` | neighborhood | PUB | E5 | S2 | C4 | V5 | N3 | O |
| `goon.neighborhood.n12` | West Canal | `goon.region.r02` | neighborhood | PUB | E2+E4 | S1 | C7 | V1+V4 | N1+N2 | O |
| `goon.neighborhood.n13` | Upper East Side | `goon.region.r03` | neighborhood | PUB | E1+E2 | S1 | C2 | V1+V2 | N1 | B |
| `goon.neighborhood.n14` | Robinson Gardens | `goon.region.r03` | neighborhood | PUB | E8 | S1 | C6 | V8 | N8 | O |
| `goon.neighborhood.n15` | Amusement Mile | `goon.region.r03` | neighborhood | PUB | E7 | S2 | C6 | V7 | N7 | A |
| `goon.neighborhood.n16` | Gables Ward | `goon.region.r03` | neighborhood | PUB | E1+E6 | S1 | C3 | V2+V6 | N1+N4 | O |
| `goon.neighborhood.n17` | Highbridge | `goon.region.r03` | neighborhood | PUB | E4+E5 | S2 | C4 | V4+V5 | N2+N3 | O |
| `goon.neighborhood.n18` | North Quay | `goon.region.r03` | neighborhood | PUB | E4 | S4 | C1 | V4 | N2+N5 | O |
| `goon.neighborhood.n19` | Midtown | `goon.region.r04` | neighborhood | PUB | E2+E6 | S2 | C4 | V1+V6 | N1+N4 | RPG |
| `goon.neighborhood.n20` | Diamond District | `goon.region.r04` | neighborhood | PUB | E2 | S2 | C7 | V1 | N1+N10 | B |
| `goon.neighborhood.n21` | Chinatown | `goon.region.r04` | neighborhood | PUB | E2+E5 | S1 | C2 | V1+V5 | N1+N3 | B |
| `goon.neighborhood.n22` | Civic Lanes | `goon.region.r04` | neighborhood | PUB | E5 | S3 | C4 | V5 | N3 | O |
| `goon.neighborhood.n23` | Canal Exchange | `goon.region.r04` | neighborhood | PUB | E4 | S4 | C1 | V4 | N2+N5 | O |
| `goon.neighborhood.n24` | Market Steps | `goon.region.r04` | neighborhood | PUB | E2+E5 | S1 | C3 | V1+V5 | N1+N3 | O |
| `goon.neighborhood.n25` | Park Row | `goon.region.r05` | neighborhood | PUB | E1+E6 | S1 | C6 | V2+V6 | N1+N4 | P |
| `goon.neighborhood.n26` | East End | `goon.region.r05` | neighborhood | PUB | E2+E3 | S1 | C7 | V1+V3 | N1+N6 | D |
| `goon.neighborhood.n27` | Narrows | `goon.region.r05` | neighborhood | PUB | E1+E6 | S1 | C3 | V2+V6 | N1+N4 | RPG |
| `goon.neighborhood.n28` | Old Dock Ward | `goon.region.r05` | neighborhood | PUB | E3+E4 | S5 | C1 | V3+V4 | N5+N6 | O |
| `goon.neighborhood.n29` | Theatre Steps | `goon.region.r05` | neighborhood | PUB | E7 | S1 | C6 | V7 | N7 | O |
| `goon.neighborhood.n30` | South Gate | `goon.region.r05` | neighborhood | PUB | E4+E5 | S2 | C4 | V4+V5 | N2+N3 | O |
| `goon.neighborhood.n31` | East Harbor | `goon.region.r06` | neighborhood | PUB | E4 | S4 | C1 | V4 | N2+N5 | O |
| `goon.neighborhood.n32` | Iron Quay | `goon.region.r06` | neighborhood | PUB | E1+E3 | S5 | C5 | V2+V3 | N1+N6 | O |
| `goon.neighborhood.n33` | Drydock Ward | `goon.region.r06` | neighborhood | PUB | E3+E4 | S4 | C1 | V3+V4 | N2+N6 | O |
| `goon.neighborhood.n34` | Saltmarket | `goon.region.r06` | neighborhood | PUB | E2 | S1 | C7 | V1 | N1+N5 | O |
| `goon.neighborhood.n35` | Chemical Reach | `goon.region.r06` | neighborhood | PUB | E3 | S5 | C5 | V3 | N6 | O |
| `goon.neighborhood.n36` | Tideworks | `goon.region.r06` | neighborhood | PUB | E8+E3 | S5 | C5 | V3+V8 | N6+N8 | O |
| `goon.neighborhood.n37` | South Exchange | `goon.region.r07` | neighborhood | PUB | E4+E6 | S2 | C4 | V4+V6 | N2+N4 | O |
| `goon.neighborhood.n38` | Sawmill Terrace | `goon.region.r07` | neighborhood | PUB | E1+E3 | S1 | C3 | V2+V3 | N1+N6 | O |
| `goon.neighborhood.n39` | Reed Marsh | `goon.region.r07` | neighborhood | PUB | E8 | S1 | C5 | V8 | N8 | O |
| `goon.neighborhood.n40` | Outfall Ward | `goon.region.r07` | neighborhood | PUB | E8+E6 | S5 | C5 | V6+V8 | N4+N8 | O |
| `goon.neighborhood.n41` | South Rail | `goon.region.r07` | neighborhood | PUB | E4+E5 | S4 | C1 | V4+V5 | N2+N3 | O |
| `goon.neighborhood.n42` | Millbrook | `goon.region.r07` | neighborhood | PUB | E1+E5 | S1 | C3 | V2+V5 | N1+N3 | O |
| `goon.neighborhood.n43` | Breakwater Village | `goon.region.r08` | neighborhood | PUB | E2+E4 | S1 | C6 | V1+V4 | N1+N2 | O |
| `goon.neighborhood.n44` | Lantern Harbor | `goon.region.r08` | neighborhood | PUB | E4+E6 | S2 | C6 | V4+V6 | N2+N4 | O |
| `goon.neighborhood.n45` | Arkham Reach | `goon.region.r08` | neighborhood | PUB | E5+E6 | S3 | C4 | V5+V6 | N4+N9 | O |
| `goon.neighborhood.n46` | Blackgate Landing | `goon.region.r08` | neighborhood | VIS | E5+E4 | S3 | C4 | V4+V5 | N3+N9 | O |
| `goon.neighborhood.n47` | Netmaker Rows | `goon.region.r08` | neighborhood | PUB | E1+E3 | S1 | C3 | V2+V3 | N1+N6 | O |
| `goon.neighborhood.n48` | Beacon Ward | `goon.region.r08` | neighborhood | PUB | E5+E8 | S1 | C6 | V5+V8 | N1+N8 | O |

## POIs — Bristol Mainland

| Stable ID | Name | Parent | Type | Access | Economy | Security | Criminal activity | Civilian activity | NPC pool | Source |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `goon.poi.p001` | Wayne Manor | `goon.neighborhood.n01` / `goon.region.r01` | residence | HOME | E1 | S3 | C2 | V2 | N1 | D |
| `goon.poi.p002` | Bristol Station | `goon.neighborhood.n01` / `goon.region.r01` | station | PUB | E4 | S2 | C2 | V4 | N2 | O |
| `goon.poi.p003` | Cedar Rooms | `goon.neighborhood.n02` / `goon.region.r01` | housing | HOME | E1 | S1 | C3 | V2 | N1 | O |
| `goon.poi.p004` | Cedar Repair Cooperative | `goon.neighborhood.n02` / `goon.region.r01` | workshop | WORK | E3 | S2 | C3 | V3 | N6 | O |
| `goon.poi.p005` | Reservoir Park | `goon.neighborhood.n03` / `goon.region.r01` | park | PUB | E8 | S1 | C6 | V8 | N8 | O |
| `goon.poi.p006` | North Reservoir Pump House | `goon.neighborhood.n03` / `goon.region.r01` | utility | SEC | E8 | S5 | C5 | V3 | N6 | O |
| `goon.poi.p007` | Northgate Community Hospital | `goon.neighborhood.n04` / `goon.region.r01` | hospital | CARE | E6 | S2 | C4 | V6 | N4 | O |
| `goon.poi.p008` | Northgate Transit Exchange | `goon.neighborhood.n04` / `goon.region.r01` | interchange | PUB | E4 | S2 | C2 | V4 | N2 | O |
| `goon.poi.p009` | Archie Goodwin International Airport | `goon.neighborhood.n05` / `goon.region.r01` | airport | ENT | E4 | S4 | C1 | V4 | N2 | B |
| `goon.poi.p010` | Airport Worker Canteen | `goon.neighborhood.n05` / `goon.region.r01` | cafe | ENT | E2 | S1 | C6 | V1 | N1+N2 | O |
| `goon.poi.p011` | Meadow Freight Terminal | `goon.neighborhood.n06` / `goon.region.r01` | freight terminal | WORK | E4 | S4 | C1 | V4 | N2+N5 | O |
| `goon.poi.p012` | Meadow Market | `goon.neighborhood.n06` / `goon.region.r01` | market | PUB | E2 | S1 | C7 | V1 | N1 | O |
| `goon.poi.p013` | Bristol Community Counseling | `goon.neighborhood.n02` / `goon.region.r01` | voluntary care | CARE | E6 | S2 | C4 | V6 | N4 | O |
| `goon.poi.p014` | Northgate Police Desk | `goon.neighborhood.n04` / `goon.region.r01` | police public counter | PUB | E5 | S3 | C4 | V5 | N3 | O |
| `goon.poi.p015` | Meadow Emergency Shelter | `goon.neighborhood.n06` / `goon.region.r01` | shelter | HELP | E6 | S1 | C6 | V2+V6 | N1+N4 | O |

## POIs — West Mainland

| Stable ID | Name | Parent | Type | Access | Economy | Security | Criminal activity | Civilian activity | NPC pool | Source |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `goon.poi.p016` | Westbank Flats | `goon.neighborhood.n07` / `goon.region.r02` | housing | HOME | E1 | S1 | C3 | V2 | N1 | O |
| `goon.poi.p017` | Westbank Tenants Office | `goon.neighborhood.n07` / `goon.region.r02` | civic support | PUB | E5 | S1 | C3 | V5 | N1+N3 | O |
| `goon.poi.p018` | Foundry Repair Cooperative | `goon.neighborhood.n08` / `goon.region.r02` | workshop | WORK | E3 | S5 | C5 | V3 | N6 | O |
| `goon.poi.p019` | Foundry Safety Training Hall | `goon.neighborhood.n08` / `goon.region.r02` | training | ENT | E5 | S2 | C5 | V3 | N6 | O |
| `goon.poi.p020` | Union Hall | `goon.neighborhood.n09` / `goon.region.r02` | community workplace | PUB | E5 | S1 | C3 | V3+V5 | N1+N6 | O |
| `goon.poi.p021` | Union Quarter Library | `goon.neighborhood.n09` / `goon.region.r02` | library | PUB | E5 | S1 | C6 | V5 | N1 | O |
| `goon.poi.p022` | West Regional Station | `goon.neighborhood.n10` / `goon.region.r02` | station | PUB | E4 | S2 | C2 | V4 | N2 | O |
| `goon.poi.p023` | Switchyard Maintenance Depot | `goon.neighborhood.n10` / `goon.region.r02` | depot | WORK | E3 | S5 | C5 | V3 | N6 | O |
| `goon.poi.p024` | Stonecross Court Annex | `goon.neighborhood.n11` / `goon.region.r02` | court public counter | PUB | E5 | S3 | C4 | V5 | N3 | O |
| `goon.poi.p025` | Stonecross Legal Aid | `goon.neighborhood.n11` / `goon.region.r02` | advocacy | HELP | E5 | S2 | C4 | V5 | N3 | O |
| `goon.poi.p026` | West Canal Passenger Pier | `goon.neighborhood.n12` / `goon.region.r02` | ferry terminal | PUB | E4 | S4 | C1 | V4 | N2 | O |
| `goon.poi.p027` | Wharf Corner Cafe | `goon.neighborhood.n12` / `goon.region.r02` | cafe | ENT | E2 | S1 | C6 | V1+V7 | N1+N7 | O |
| `goon.poi.p028` | Foundry Urgent Clinic | `goon.neighborhood.n08` / `goon.region.r02` | clinic | CARE | E6 | S2 | C4 | V6 | N4 | O |
| `goon.poi.p029` | West Mainland Police Precinct | `goon.neighborhood.n11` / `goon.region.r02` | police public counter | PUB | E5 | S3 | C4 | V5 | N3 | O |
| `goon.poi.p030` | Switchyard Goods Depot | `goon.neighborhood.n10` / `goon.region.r02` | freight depot | WORK | E4 | S4 | C1 | V4 | N2+N5 | O |

## POIs — North Borough

| Stable ID | Name | Parent | Type | Access | Economy | Security | Criminal activity | Civilian activity | NPC pool | Source |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `goon.poi.p031` | East Side Housing Cooperative | `goon.neighborhood.n13` / `goon.region.r03` | housing | HOME | E1 | S1 | C3 | V2 | N1 | O |
| `goon.poi.p032` | Uptown General Store | `goon.neighborhood.n13` / `goon.region.r03` | shop | ENT | E2 | S2 | C2 | V1 | N1 | O |
| `goon.poi.p033` | Robinson Park | `goon.neighborhood.n14` / `goon.region.r03` | park | PUB | E8 | S1 | C6 | V8 | N8+N10 | D |
| `goon.poi.p034` | Garden Learning Center | `goon.neighborhood.n14` / `goon.region.r03` | education | PUB | E5 | S1 | C6 | V5+V8 | N1+N8 | O |
| `goon.poi.p035` | Amusement Mile Boardwalk | `goon.neighborhood.n15` / `goon.region.r03` | leisure frontage | PUB | E7 | S2 | C6 | V7 | N7 | A name; O frontage |
| `goon.poi.p036` | Nightshift Diner | `goon.neighborhood.n15` / `goon.region.r03` | diner | ENT | E2 | S1 | C3 | V1 | N1+N7 | O |
| `goon.poi.p037` | Gables Community Clinic | `goon.neighborhood.n16` / `goon.region.r03` | clinic | CARE | E6 | S2 | C4 | V6 | N4 | O |
| `goon.poi.p038` | Gables Social Club | `goon.neighborhood.n16` / `goon.region.r03` | social venue | ENT | E7 | S1 | C6 | V7 | N1+N7 | O |
| `goon.poi.p039` | Highbridge Metro Stop | `goon.neighborhood.n17` / `goon.region.r03` | metro station | PUB | E4 | S2 | C2 | V4 | N2 | O |
| `goon.poi.p040` | Highbridge Court Counter | `goon.neighborhood.n17` / `goon.region.r03` | court public counter | PUB | E5 | S3 | C4 | V5 | N3 | O |
| `goon.poi.p041` | North Quay Passenger Pier | `goon.neighborhood.n18` / `goon.region.r03` | ferry terminal | PUB | E4 | S4 | C1 | V4 | N2 | O |
| `goon.poi.p042` | North Quay Boat Repair | `goon.neighborhood.n18` / `goon.region.r03` | workshop | WORK | E3 | S5 | C5 | V3 | N2+N6 | O |
| `goon.poi.p043` | Gardens Voluntary Care | `goon.neighborhood.n14` / `goon.region.r03` | voluntary care | CARE | E6 | S2 | C4 | V6 | N4 | O |
| `goon.poi.p044` | North Borough Police Station | `goon.neighborhood.n17` / `goon.region.r03` | police public counter | PUB | E5 | S3 | C4 | V5 | N3 | O |
| `goon.poi.p045` | Fairground Crew Dispatch | `goon.neighborhood.n15` / `goon.region.r03` | work referral | PUB | E4 | S1 | C3 | V3 | N2+N7 | O |

## POIs — Central Borough

| Stable ID | Name | Parent | Type | Access | Economy | Security | Criminal activity | Civilian activity | NPC pool | Source |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `goon.poi.p046` | Wayne Tower | `goon.neighborhood.n19` / `goon.region.r04` | office tower | ENT | E2 | S3 | C4 | V3 | N1+N6 | D |
| `goon.poi.p047` | Central Interchange | `goon.neighborhood.n19` / `goon.region.r04` | interchange | PUB | E4 | S2 | C2 | V4 | N2 | O |
| `goon.poi.p048` | Iceberg Lounge | `goon.neighborhood.n20` / `goon.region.r04` | nightclub | ENT | E7 | S3 | C6 | V7 | N7+N10 | I |
| `goon.poi.p049` | Jewelers Repair Guild | `goon.neighborhood.n20` / `goon.region.r04` | workshop | WORK | E3 | S2 | C7 | V3 | N1+N6 | O |
| `goon.poi.p050` | Chinatown Market Hall | `goon.neighborhood.n21` / `goon.region.r04` | market | PUB | E2 | S1 | C2 | V1 | N1 | O |
| `goon.poi.p051` | Community Translation Desk | `goon.neighborhood.n21` / `goon.region.r04` | public service | HELP | E5 | S1 | C0 | V5 | N1+N3 | O |
| `goon.poi.p052` | Gotham City Courthouse | `goon.neighborhood.n22` / `goon.region.r04` | court public counter | PUB | E5 | S3 | C4 | V5 | N3 | O civic category |
| `goon.poi.p053` | GCPD Public Headquarters | `goon.neighborhood.n22` / `goon.region.r04` | police public counter | PUB | E5 | S3 | C4 | V5 | N3 | O facility; RPG institution |
| `goon.poi.p054` | Central Canal Ferry Terminal | `goon.neighborhood.n23` / `goon.region.r04` | ferry terminal | PUB | E4 | S4 | C1 | V4 | N2 | O |
| `goon.poi.p055` | Freight Broker Exchange | `goon.neighborhood.n23` / `goon.region.r04` | office | ENT | E2 | S2 | C1 | V3+V4 | N2+N5 | O |
| `goon.poi.p056` | Market Steps Community Hall | `goon.neighborhood.n24` / `goon.region.r04` | community venue | PUB | E5 | S1 | C6 | V5+V7 | N1 | O |
| `goon.poi.p057` | Day Labor Referral Desk | `goon.neighborhood.n24` / `goon.region.r04` | work referral | PUB | E5 | S1 | C3 | V3 | N1+N6 | O |
| `goon.poi.p058` | Gotham General Hospital | `goon.neighborhood.n19` / `goon.region.r04` | hospital | CARE | E6 | S2 | C4 | V6 | N4 | H |
| `goon.poi.p059` | Metro Control Office | `goon.neighborhood.n23` / `goon.region.r04` | operations office | SEC | E4 | S3 | C4 | V3 | N2+N6 | O |
| `goon.poi.p060` | Civic Public Defender Office | `goon.neighborhood.n22` / `goon.region.r04` | advocacy | HELP | E5 | S2 | C4 | V5 | N3 | O |

## POIs — South Borough

| Stable ID | Name | Parent | Type | Access | Economy | Security | Criminal activity | Civilian activity | NPC pool | Source |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `goon.poi.p061` | Crime Alley | `goon.neighborhood.n25` / `goon.region.r05` | street/public place | PUB | E5 | S1 | C6 | V2+V5 | N1+N3 | P |
| `goon.poi.p062` | Park Row Community Clinic | `goon.neighborhood.n25` / `goon.region.r05` | clinic | CARE | E6 | S2 | C4 | V6 | N4 | O |
| `goon.poi.p063` | East End Repair Market | `goon.neighborhood.n26` / `goon.region.r05` | market/workshops | PUB | E2+E3 | S1 | C7 | V1+V3 | N1+N6 | O |
| `goon.poi.p064` | Night Rooms Housing | `goon.neighborhood.n26` / `goon.region.r05` | housing | HOME | E1 | S1 | C3 | V2 | N1 | O |
| `goon.poi.p065` | Narrows Public Bathhouse | `goon.neighborhood.n27` / `goon.region.r05` | civilian service | ENT | E2 | S1 | C0 | V2 | N1 | O |
| `goon.poi.p066` | Narrows Care and Reentry Center | `goon.neighborhood.n27` / `goon.region.r05` | care/reentry | CARE | E6 | S2 | C4 | V5+V6 | N3+N4 | O |
| `goon.poi.p067` | Old Dock Warehouse Cooperative | `goon.neighborhood.n28` / `goon.region.r05` | warehouse | WORK | E4 | S4 | C1 | V3+V4 | N5 | O |
| `goon.poi.p068` | Old Dock Fire Station | `goon.neighborhood.n28` / `goon.region.r05` | fire/public counter | PUB | E5 | S2 | C5 | V5 | N6 | O |
| `goon.poi.p069` | Monarch Theatre | `goon.neighborhood.n25` / `goon.region.r05` | theater | ENT | E7 | S2 | C6 | V7 | N7 | P |
| `goon.poi.p070` | Stagehands Hall | `goon.neighborhood.n29` / `goon.region.r05` | work/community hall | PUB | E5 | S1 | C3 | V3+V7 | N6+N7 | O |
| `goon.poi.p071` | South Gate Subway Stop | `goon.neighborhood.n30` / `goon.region.r05` | metro station | PUB | E4 | S2 | C2 | V4 | N2 | O |
| `goon.poi.p072` | South Gate Bus Terminal | `goon.neighborhood.n30` / `goon.region.r05` | bus station | PUB | E4 | S2 | C2 | V4 | N2 | O |
| `goon.poi.p073` | South Borough Court Counter | `goon.neighborhood.n30` / `goon.region.r05` | court public counter | PUB | E5 | S3 | C4 | V5 | N3 | O |
| `goon.poi.p074` | South Borough Police Counter | `goon.neighborhood.n30` / `goon.region.r05` | police public counter | PUB | E5 | S3 | C4 | V5 | N3 | O |
| `goon.poi.p075` | Reentry Employment Office | `goon.neighborhood.n27` / `goon.region.r05` | work referral | HELP | E6 | S1 | C3 | V3+V5 | N1+N3 | O |

## POIs — East Mainland

| Stable ID | Name | Parent | Type | Access | Economy | Security | Criminal activity | Civilian activity | NPC pool | Source |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `goon.poi.p076` | Eastern Commercial Port | `goon.neighborhood.n31` / `goon.region.r06` | port | WORK | E4 | S4 | C1 | V4 | N2+N5 | O |
| `goon.poi.p077` | East Harbor Customs Counter | `goon.neighborhood.n31` / `goon.region.r06` | port public counter | PUB | E5 | S4 | C4 | V5 | N3+N5 | O |
| `goon.poi.p078` | Iron Quay Foundry | `goon.neighborhood.n32` / `goon.region.r06` | plant | WORK | E3 | S5 | C5 | V3 | N6 | O |
| `goon.poi.p079` | Iron Quay Worker Clinic | `goon.neighborhood.n32` / `goon.region.r06` | clinic | CARE | E6 | S2 | C4 | V6 | N4 | O |
| `goon.poi.p080` | Drydock Services Cooperative | `goon.neighborhood.n33` / `goon.region.r06` | workshop | WORK | E3 | S5 | C5 | V3 | N5+N6 | O |
| `goon.poi.p081` | East Mainland Regional Station | `goon.neighborhood.n33` / `goon.region.r06` | station | PUB | E4 | S2 | C2 | V4 | N2 | O |
| `goon.poi.p082` | Saltmarket Fish Hall | `goon.neighborhood.n34` / `goon.region.r06` | market | PUB | E2 | S1 | C7 | V1 | N1+N5 | O |
| `goon.poi.p083` | Saltmarket Civic Square | `goon.neighborhood.n34` / `goon.region.r06` | square | PUB | E5 | S1 | C6 | V5+V7 | N1 | O |
| `goon.poi.p084` | Ace Chemicals | `goon.neighborhood.n35` / `goon.region.r06` | industrial plant | WORK | E3 | S5 | C5 | V3 | N6+N10 | D |
| `goon.poi.p085` | Chemical Reach Safety School | `goon.neighborhood.n35` / `goon.region.r06` | training | PUB | E5 | S2 | C5 | V3 | N6 | O |
| `goon.poi.p086` | Tideworks Power Plant | `goon.neighborhood.n36` / `goon.region.r06` | utility | SEC | E8 | S5 | C5 | V3 | N6 | O |
| `goon.poi.p087` | Tideworks Water Works | `goon.neighborhood.n36` / `goon.region.r06` | utility | SEC | E8 | S5 | C5 | V3 | N6+N8 | O |
| `goon.poi.p088` | Hazard Review Office | `goon.neighborhood.n35` / `goon.region.r06` | public service | PUB | E5 | S2 | C4 | V5 | N3+N6 | O |
| `goon.poi.p089` | East Harbor Marine Police Counter | `goon.neighborhood.n31` / `goon.region.r06` | marine/public counter | PUB | E5 | S4 | C4 | V5 | N3 | O |
| `goon.poi.p090` | Port Worker Housing Cooperative | `goon.neighborhood.n32` / `goon.region.r06` | housing | HOME | E1 | S1 | C3 | V2 | N1+N5 | O |

## POIs — South Mainland

| Stable ID | Name | Parent | Type | Access | Economy | Security | Criminal activity | Civilian activity | NPC pool | Source |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `goon.poi.p091` | South Exchange Coach Station | `goon.neighborhood.n37` / `goon.region.r07` | intercity station | PUB | E4 | S2 | C2 | V4 | N2 | O |
| `goon.poi.p092` | South Market Community Hospital | `goon.neighborhood.n37` / `goon.region.r07` | hospital | CARE | E6 | S2 | C4 | V6 | N4 | O |
| `goon.poi.p093` | Sawmill Repair Collective | `goon.neighborhood.n38` / `goon.region.r07` | workshop | WORK | E3 | S5 | C5 | V3 | N6 | O |
| `goon.poi.p094` | Sawmill Rooms | `goon.neighborhood.n38` / `goon.region.r07` | housing | HOME | E1 | S1 | C3 | V2 | N1 | O |
| `goon.poi.p095` | Reed Marsh Reserve | `goon.neighborhood.n39` / `goon.region.r07` | wetland park | PUB | E8 | S1 | C5 | V8 | N8 | O |
| `goon.poi.p096` | Wetland Field Laboratory | `goon.neighborhood.n39` / `goon.region.r07` | research facility | WORK | E8 | S5 | C5 | V3+V8 | N6+N8 | O |
| `goon.poi.p097` | Outfall Maintenance Depot | `goon.neighborhood.n40` / `goon.region.r07` | utility depot | WORK | E8 | S5 | C5 | V3 | N6 | O |
| `goon.poi.p098` | Outfall Community Clinic | `goon.neighborhood.n40` / `goon.region.r07` | clinic | CARE | E6 | S2 | C4 | V6 | N4 | O |
| `goon.poi.p099` | South Rail Passenger Station | `goon.neighborhood.n41` / `goon.region.r07` | station | PUB | E4 | S2 | C2 | V4 | N2 | O |
| `goon.poi.p100` | South Freight Yard | `goon.neighborhood.n41` / `goon.region.r07` | freight depot | WORK | E4 | S4 | C1 | V4 | N2+N5 | O |
| `goon.poi.p101` | Millbrook School and Adult Education | `goon.neighborhood.n42` / `goon.region.r07` | education | ENT | E5 | S2 | C0 | V5 | N1+N3 | O |
| `goon.poi.p102` | Millbrook Social Hall | `goon.neighborhood.n42` / `goon.region.r07` | social venue | PUB | E7 | S1 | C6 | V7 | N1+N7 | O |
| `goon.poi.p103` | South Mainland Court Counter | `goon.neighborhood.n37` / `goon.region.r07` | court public counter | PUB | E5 | S3 | C4 | V5 | N3 | O |
| `goon.poi.p104` | South Mainland Police Desk | `goon.neighborhood.n41` / `goon.region.r07` | police public counter | PUB | E5 | S3 | C4 | V5 | N3 | O |
| `goon.poi.p105` | Supported Housing Referral | `goon.neighborhood.n42` / `goon.region.r07` | support service | HELP | E6 | S1 | C0 | V2+V5 | N1+N3 | O |

## POIs — Outer Islands

| Stable ID | Name | Parent | Type | Access | Economy | Security | Criminal activity | Civilian activity | NPC pool | Source |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `goon.poi.p106` | Breakwater Main Pier | `goon.neighborhood.n43` / `goon.region.r08` | ferry terminal | PUB | E4 | S4 | C1 | V4 | N2 | O |
| `goon.poi.p107` | Breakwater Daily Store | `goon.neighborhood.n43` / `goon.region.r08` | shop | ENT | E2 | S1 | C2 | V1 | N1 | O |
| `goon.poi.p108` | Lantern Harbor Rescue Station | `goon.neighborhood.n44` / `goon.region.r08` | marine/public service | PUB | E5 | S2 | C5 | V5 | N2+N6 | O |
| `goon.poi.p109` | Lantern Care Referral Desk | `goon.neighborhood.n44` / `goon.region.r08` | care support | HELP | E6 | S1 | C0 | V6 | N4 | O |
| `goon.poi.p110` | Arkham Asylum | `goon.neighborhood.n45` / `goon.region.r08` | psychiatric institution | CARE | E6 | S3 | C4 | V6 | N4+N9 | D; RPG island name |
| `goon.poi.p111` | Arkham Family Reception | `goon.neighborhood.n45` / `goon.region.r08` | institution reception | VIS | E5 | S3 | C6 | V5 | N4+N9 | O |
| `goon.poi.p112` | Blackgate Penitentiary | `goon.neighborhood.n46` / `goon.region.r08` | prison | VIS | E5 | S3 | C6 | V5 | N3+N9 | K |
| `goon.poi.p113` | Blackgate Authorized Visiting Hall | `goon.neighborhood.n46` / `goon.region.r08` | institution reception | VIS | E5 | S3 | C6 | V5 | N9 | O |
| `goon.poi.p114` | Netmaker Repair Cooperative | `goon.neighborhood.n47` / `goon.region.r08` | workshop | WORK | E3 | S2 | C3 | V3 | N5+N6 | O |
| `goon.poi.p115` | Netmaker Worker Rooms | `goon.neighborhood.n47` / `goon.region.r08` | housing | HOME | E1 | S1 | C3 | V2 | N1+N5 | O |
| `goon.poi.p116` | Beacon Lighthouse | `goon.neighborhood.n48` / `goon.region.r08` | navigation facility | SEC | E8 | S5 | C5 | V3 | N2+N6 | O |
| `goon.poi.p117` | Beacon Community Hall | `goon.neighborhood.n48` / `goon.region.r08` | community venue | PUB | E5 | S1 | C6 | V5+V7 | N1 | O |
| `goon.poi.p118` | Lantern Ferry Worker Canteen | `goon.neighborhood.n44` / `goon.region.r08` | cafe | ENT | E2 | S1 | C3 | V1 | N1+N2 | O |
| `goon.poi.p119` | Island Public Aid and Advocacy | `goon.neighborhood.n43` / `goon.region.r08` | support service | HELP | E5 | S1 | C4 | V5 | N3+N4 | O |
| `goon.poi.p120` | Archipelago Staff Ferry Office | `goon.neighborhood.n43` / `goon.region.r08` | transport office | WORK | E4 | S3 | C4 | V3+V4 | N2+N9 | O |

## Interpretation and future validation

These are distinct places/categories, not additional factions, simulated salaries,
automatically reachable interiors or a collection checklist. Each row's source
and proposed profile remain separate. For example, Iceberg Lounge's name/function
has a source; its Diamond District address and N10 pool do not guarantee Penguin.
Wayne Manor does not reveal a hidden base to a player who knows only its public
name. An Arkham intake request does not satisfy Joker initiation.

Public arrival hubs can expose basic wayfinding/help without publishing private
residences, safehouses, patient records or every actor's true location. A temporary
shelter/referral is not immunity or free ownership. Named contacts follow their
own availability, knowledge, consent and continuity requirements.

Before implementation, validate unique IDs/names where required, all parent
references, profile tokens, source metadata, gated interiors, disconnected public
routes, practical care/work alternatives, and exact per-region totals. New POIs
can be added with new IDs without subdividing income or replaying historical
control events. The [migration specification](GOON_MAP_SIMULATION_INTEGRATION.md)
owns compatibility; no historical save gains locations from this document alone.
