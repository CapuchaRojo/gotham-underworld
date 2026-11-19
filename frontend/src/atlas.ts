// REAL AUTHORED GEOGRAPHY — extracted verbatim from `content/gotham_atlas_v1.json`.
//
// All 176 places (8 regions, 48 neighborhoods, 120 POIs) with their exact stable
// identifiers, authored names, region/neighborhood containment, access codes and
// profile references. The 17 named corridors (bridges/tunnels/causeways/ferries)
// are also transcribed verbatim. This is content data, not a runtime simulation.
//
// NOTE ON EDGES: the authored atlas also contains a per-region local street ring
// (46 local corridors) and 120 POI access spurs. Those are encoded verbatim in
// `src/navigation_data.ts` and consumed by the travel rules in `src/navigation.ts`.
// Nothing here is invented or renamed.

import type { AccessCode, Edge, Place } from "./types";

export const ROOT_ID = "goon.city.gotham";

function place(
  id: string,
  label: string,
  parentId: string | null,
  regionId: string,
  kind: Place["kind"],
  type: string,
  access: AccessCode[],
  economy: string[],
  security: string[],
  criminal: string[],
  civilian: string[],
  npcPool: string[],
  source: string,
): Place {
  return { id, label, parentId, regionId, kind, type, access, economy, security, criminal, civilian, npcPool, source };
}

export const PLACES: Place[] = [
  // --- Regions (8) ---
  place("goon.region.r01", "Bristol Mainland", ROOT_ID, "goon.region.r01", "region", "region", ["PUB"], ["E1", "E4"], ["S1"], ["C2"], ["V2", "V4"], ["N1", "N2"], "O; D name"),
  place("goon.region.r02", "West Mainland", ROOT_ID, "goon.region.r02", "region", "region", ["PUB"], ["E1", "E3"], ["S1"], ["C3"], ["V2", "V3"], ["N1", "N6"], "O"),
  place("goon.region.r03", "North Borough", ROOT_ID, "goon.region.r03", "region", "region", ["PUB"], ["E1", "E7"], ["S1"], ["C6"], ["V2", "V7"], ["N1", "N7"], "O"),
  place("goon.region.r04", "Central Borough", ROOT_ID, "goon.region.r04", "region", "region", ["PUB"], ["E2", "E5"], ["S2"], ["C4"], ["V1", "V5"], ["N1", "N3"], "O"),
  place("goon.region.r05", "South Borough", ROOT_ID, "goon.region.r05", "region", "region", ["PUB"], ["E1", "E2"], ["S1"], ["C3"], ["V2", "V3"], ["N1", "N4"], "O"),
  place("goon.region.r06", "East Mainland", ROOT_ID, "goon.region.r06", "region", "region", ["PUB"], ["E3", "E4"], ["S4"], ["C1"], ["V3", "V4"], ["N5", "N6"], "O"),
  place("goon.region.r07", "South Mainland", ROOT_ID, "goon.region.r07", "region", "region", ["PUB"], ["E1", "E8"], ["S1"], ["C5"], ["V2", "V8"], ["N1", "N8"], "O"),
  place("goon.region.r08", "Outer Islands", ROOT_ID, "goon.region.r08", "region", "region", ["PUB"], ["E4", "E5"], ["S3"], ["C6"], ["V4", "V5"], ["N2", "N9"], "O; RPG island names"),

  // --- R01 neighborhoods ---
  place("goon.neighborhood.n01", "Bristol Township", "goon.region.r01", "goon.region.r01", "neighborhood", "neighborhood", ["PUB"], ["E1"], ["S1"], ["C2"], ["V2"], ["N1"], "D"),
  place("goon.neighborhood.n02", "Cedar Slope", "goon.region.r01", "goon.region.r01", "neighborhood", "neighborhood", ["PUB"], ["E1", "E3"], ["S1"], ["C3"], ["V2", "V3"], ["N1", "N6"], "O"),
  place("goon.neighborhood.n03", "Reservoir Terrace", "goon.region.r01", "goon.region.r01", "neighborhood", "neighborhood", ["PUB"], ["E8"], ["S5"], ["C5"], ["V8"], ["N8"], "O"),
  place("goon.neighborhood.n04", "Northgate Commons", "goon.region.r01", "goon.region.r01", "neighborhood", "neighborhood", ["PUB"], ["E5", "E6"], ["S2"], ["C4"], ["V5", "V6"], ["N3", "N4"], "O"),
  place("goon.neighborhood.n05", "Airfield Ward", "goon.region.r01", "goon.region.r01", "neighborhood", "neighborhood", ["PUB"], ["E4"], ["S4"], ["C1"], ["V4"], ["N2"], "O"),
  place("goon.neighborhood.n06", "Meadow Exchange", "goon.region.r01", "goon.region.r01", "neighborhood", "neighborhood", ["PUB"], ["E2", "E4"], ["S1"], ["C1"], ["V1", "V4"], ["N1", "N2"], "O"),

  // --- R02 neighborhoods ---
  place("goon.neighborhood.n07", "Westbank Terraces", "goon.region.r02", "goon.region.r02", "neighborhood", "neighborhood", ["PUB"], ["E1"], ["S1"], ["C2"], ["V2"], ["N1"], "O"),
  place("goon.neighborhood.n08", "Foundry Ward", "goon.region.r02", "goon.region.r02", "neighborhood", "neighborhood", ["PUB"], ["E3"], ["S5"], ["C5"], ["V3"], ["N6"], "O"),
  place("goon.neighborhood.n09", "Union Quarter", "goon.region.r02", "goon.region.r02", "neighborhood", "neighborhood", ["PUB"], ["E5", "E3"], ["S1"], ["C3"], ["V3", "V5"], ["N1", "N6"], "O"),
  place("goon.neighborhood.n10", "Switchyard", "goon.region.r02", "goon.region.r02", "neighborhood", "neighborhood", ["PUB"], ["E4"], ["S4"], ["C1"], ["V4"], ["N2"], "O"),
  place("goon.neighborhood.n11", "Stonecross", "goon.region.r02", "goon.region.r02", "neighborhood", "neighborhood", ["PUB"], ["E5"], ["S2"], ["C4"], ["V5"], ["N3"], "O"),
  place("goon.neighborhood.n12", "West Canal", "goon.region.r02", "goon.region.r02", "neighborhood", "neighborhood", ["PUB"], ["E2", "E4"], ["S1"], ["C7"], ["V1", "V4"], ["N1", "N2"], "O"),

  // --- R03 neighborhoods ---
  place("goon.neighborhood.n13", "Upper East Side", "goon.region.r03", "goon.region.r03", "neighborhood", "neighborhood", ["PUB"], ["E1", "E2"], ["S1"], ["C2"], ["V1", "V2"], ["N1"], "B"),
  place("goon.neighborhood.n14", "Robinson Gardens", "goon.region.r03", "goon.region.r03", "neighborhood", "neighborhood", ["PUB"], ["E8"], ["S1"], ["C6"], ["V8"], ["N8"], "O"),
  place("goon.neighborhood.n15", "Amusement Mile", "goon.region.r03", "goon.region.r03", "neighborhood", "neighborhood", ["PUB"], ["E7"], ["S2"], ["C6"], ["V7"], ["N7"], "A"),
  place("goon.neighborhood.n16", "Gables Ward", "goon.region.r03", "goon.region.r03", "neighborhood", "neighborhood", ["PUB"], ["E1", "E6"], ["S1"], ["C3"], ["V2", "V6"], ["N1", "N4"], "O"),
  place("goon.neighborhood.n17", "Highbridge", "goon.region.r03", "goon.region.r03", "neighborhood", "neighborhood", ["PUB"], ["E4", "E5"], ["S2"], ["C4"], ["V4", "V5"], ["N2", "N3"], "O"),
  place("goon.neighborhood.n18", "North Quay", "goon.region.r03", "goon.region.r03", "neighborhood", "neighborhood", ["PUB"], ["E4"], ["S4"], ["C1"], ["V4"], ["N2", "N5"], "O"),

  // --- R04 neighborhoods ---
  place("goon.neighborhood.n19", "Midtown", "goon.region.r04", "goon.region.r04", "neighborhood", "neighborhood", ["PUB"], ["E2", "E6"], ["S2"], ["C4"], ["V1", "V6"], ["N1", "N4"], "RPG"),
  place("goon.neighborhood.n20", "Diamond District", "goon.region.r04", "goon.region.r04", "neighborhood", "neighborhood", ["PUB"], ["E2"], ["S2"], ["C7"], ["V1"], ["N1", "N10"], "B"),
  place("goon.neighborhood.n21", "Chinatown", "goon.region.r04", "goon.region.r04", "neighborhood", "neighborhood", ["PUB"], ["E2", "E5"], ["S1"], ["C2"], ["V1", "V5"], ["N1", "N3"], "B"),
  place("goon.neighborhood.n22", "Civic Lanes", "goon.region.r04", "goon.region.r04", "neighborhood", "neighborhood", ["PUB"], ["E5"], ["S3"], ["C4"], ["V5"], ["N3"], "O"),
  place("goon.neighborhood.n23", "Canal Exchange", "goon.region.r04", "goon.region.r04", "neighborhood", "neighborhood", ["PUB"], ["E4"], ["S4"], ["C1"], ["V4"], ["N2", "N5"], "O"),
  place("goon.neighborhood.n24", "Market Steps", "goon.region.r04", "goon.region.r04", "neighborhood", "neighborhood", ["PUB"], ["E2", "E5"], ["S1"], ["C3"], ["V1", "V5"], ["N1", "N3"], "O"),

  // --- R05 neighborhoods ---
  place("goon.neighborhood.n25", "Park Row", "goon.region.r05", "goon.region.r05", "neighborhood", "neighborhood", ["PUB"], ["E1", "E6"], ["S1"], ["C6"], ["V2", "V6"], ["N1", "N4"], "P"),
  place("goon.neighborhood.n26", "East End", "goon.region.r05", "goon.region.r05", "neighborhood", "neighborhood", ["PUB"], ["E2", "E3"], ["S1"], ["C7"], ["V1", "V3"], ["N1", "N6"], "D"),
  place("goon.neighborhood.n27", "Narrows", "goon.region.r05", "goon.region.r05", "neighborhood", "neighborhood", ["PUB"], ["E1", "E6"], ["S1"], ["C3"], ["V2", "V6"], ["N1", "N4"], "RPG"),
  place("goon.neighborhood.n28", "Old Dock Ward", "goon.region.r05", "goon.region.r05", "neighborhood", "neighborhood", ["PUB"], ["E3", "E4"], ["S5"], ["C1"], ["V3", "V4"], ["N5", "N6"], "O"),
  place("goon.neighborhood.n29", "Theatre Steps", "goon.region.r05", "goon.region.r05", "neighborhood", "neighborhood", ["PUB"], ["E7"], ["S1"], ["C6"], ["V7"], ["N7"], "O"),
  place("goon.neighborhood.n30", "South Gate", "goon.region.r05", "goon.region.r05", "neighborhood", "neighborhood", ["PUB"], ["E4", "E5"], ["S2"], ["C4"], ["V4", "V5"], ["N2", "N3"], "O"),

  // --- R06 neighborhoods ---
  place("goon.neighborhood.n31", "East Harbor", "goon.region.r06", "goon.region.r06", "neighborhood", "neighborhood", ["PUB"], ["E4"], ["S4"], ["C1"], ["V4"], ["N2", "N5"], "O"),
  place("goon.neighborhood.n32", "Iron Quay", "goon.region.r06", "goon.region.r06", "neighborhood", "neighborhood", ["PUB"], ["E1", "E3"], ["S5"], ["C5"], ["V2", "V3"], ["N1", "N6"], "O"),
  place("goon.neighborhood.n33", "Drydock Ward", "goon.region.r06", "goon.region.r06", "neighborhood", "neighborhood", ["PUB"], ["E3", "E4"], ["S4"], ["C1"], ["V3", "V4"], ["N2", "N6"], "O"),
  place("goon.neighborhood.n34", "Saltmarket", "goon.region.r06", "goon.region.r06", "neighborhood", "neighborhood", ["PUB"], ["E2"], ["S1"], ["C7"], ["V1"], ["N1", "N5"], "O"),
  place("goon.neighborhood.n35", "Chemical Reach", "goon.region.r06", "goon.region.r06", "neighborhood", "neighborhood", ["PUB"], ["E3"], ["S5"], ["C5"], ["V3"], ["N6"], "O"),
  place("goon.neighborhood.n36", "Tideworks", "goon.region.r06", "goon.region.r06", "neighborhood", "neighborhood", ["PUB"], ["E8", "E3"], ["S5"], ["C5"], ["V3", "V8"], ["N6", "N8"], "O"),

  // --- R07 neighborhoods ---
  place("goon.neighborhood.n37", "South Exchange", "goon.region.r07", "goon.region.r07", "neighborhood", "neighborhood", ["PUB"], ["E4", "E6"], ["S2"], ["C4"], ["V4", "V6"], ["N2", "N4"], "O"),
  place("goon.neighborhood.n38", "Sawmill Terrace", "goon.region.r07", "goon.region.r07", "neighborhood", "neighborhood", ["PUB"], ["E1", "E3"], ["S1"], ["C3"], ["V2", "V3"], ["N1", "N6"], "O"),
  place("goon.neighborhood.n39", "Reed Marsh", "goon.region.r07", "goon.region.r07", "neighborhood", "neighborhood", ["PUB"], ["E8"], ["S1"], ["C5"], ["V8"], ["N8"], "O"),
  place("goon.neighborhood.n40", "Outfall Ward", "goon.region.r07", "goon.region.r07", "neighborhood", "neighborhood", ["PUB"], ["E8", "E6"], ["S5"], ["C5"], ["V6", "V8"], ["N4", "N8"], "O"),
  place("goon.neighborhood.n41", "South Rail", "goon.region.r07", "goon.region.r07", "neighborhood", "neighborhood", ["PUB"], ["E4", "E5"], ["S4"], ["C1"], ["V4", "V5"], ["N2", "N3"], "O"),
  place("goon.neighborhood.n42", "Millbrook", "goon.region.r07", "goon.region.r07", "neighborhood", "neighborhood", ["PUB"], ["E1", "E5"], ["S1"], ["C3"], ["V2", "V5"], ["N1", "N3"], "O"),

  // --- R08 neighborhoods ---
  place("goon.neighborhood.n43", "Breakwater Village", "goon.region.r08", "goon.region.r08", "neighborhood", "neighborhood", ["PUB"], ["E2", "E4"], ["S1"], ["C6"], ["V1", "V4"], ["N1", "N2"], "O"),
  place("goon.neighborhood.n44", "Lantern Harbor", "goon.region.r08", "goon.region.r08", "neighborhood", "neighborhood", ["PUB"], ["E4", "E6"], ["S2"], ["C6"], ["V4", "V6"], ["N2", "N4"], "O"),
  place("goon.neighborhood.n45", "Arkham Reach", "goon.region.r08", "goon.region.r08", "neighborhood", "neighborhood", ["PUB"], ["E5", "E6"], ["S3"], ["C4"], ["V5", "V6"], ["N4", "N9"], "O"),
  place("goon.neighborhood.n46", "Blackgate Landing", "goon.region.r08", "goon.region.r08", "neighborhood", "neighborhood", ["VIS"], ["E5", "E4"], ["S3"], ["C4"], ["V4", "V5"], ["N3", "N9"], "O"),
  place("goon.neighborhood.n47", "Netmaker Rows", "goon.region.r08", "goon.region.r08", "neighborhood", "neighborhood", ["PUB"], ["E1", "E3"], ["S1"], ["C3"], ["V2", "V3"], ["N1", "N6"], "O"),
  place("goon.neighborhood.n48", "Beacon Ward", "goon.region.r08", "goon.region.r08", "neighborhood", "neighborhood", ["PUB"], ["E5", "E8"], ["S1"], ["C6"], ["V5", "V8"], ["N1", "N8"], "O"),

  // --- R01 POIs ---
  place("goon.poi.p001", "Wayne Manor", "goon.neighborhood.n01", "goon.region.r01", "poi", "residence", ["HOME"], ["E1"], ["S3"], ["C2"], ["V2"], ["N1"], "D"),
  place("goon.poi.p002", "Bristol Station", "goon.neighborhood.n01", "goon.region.r01", "poi", "station", ["PUB"], ["E4"], ["S2"], ["C2"], ["V4"], ["N2"], "O"),
  place("goon.poi.p003", "Cedar Rooms", "goon.neighborhood.n02", "goon.region.r01", "poi", "housing", ["HOME"], ["E1"], ["S1"], ["C3"], ["V2"], ["N1"], "O"),
  place("goon.poi.p004", "Cedar Repair Cooperative", "goon.neighborhood.n02", "goon.region.r01", "poi", "workshop", ["WORK"], ["E3"], ["S2"], ["C3"], ["V3"], ["N6"], "O"),
  place("goon.poi.p005", "Reservoir Park", "goon.neighborhood.n03", "goon.region.r01", "poi", "park", ["PUB"], ["E8"], ["S1"], ["C6"], ["V8"], ["N8"], "O"),
  place("goon.poi.p006", "North Reservoir Pump House", "goon.neighborhood.n03", "goon.region.r01", "poi", "utility", ["SEC"], ["E8"], ["S5"], ["C5"], ["V3"], ["N6"], "O"),
  place("goon.poi.p007", "Northgate Community Hospital", "goon.neighborhood.n04", "goon.region.r01", "poi", "hospital", ["CARE"], ["E6"], ["S2"], ["C4"], ["V6"], ["N4"], "O"),
  place("goon.poi.p008", "Northgate Transit Exchange", "goon.neighborhood.n04", "goon.region.r01", "poi", "interchange", ["PUB"], ["E4"], ["S2"], ["C2"], ["V4"], ["N2"], "O"),
  place("goon.poi.p009", "Archie Goodwin International Airport", "goon.neighborhood.n05", "goon.region.r01", "poi", "airport", ["ENT"], ["E4"], ["S4"], ["C1"], ["V4"], ["N2"], "B"),
  place("goon.poi.p010", "Airport Worker Canteen", "goon.neighborhood.n05", "goon.region.r01", "poi", "cafe", ["ENT"], ["E2"], ["S1"], ["C6"], ["V1"], ["N1", "N2"], "O"),
  place("goon.poi.p011", "Meadow Freight Terminal", "goon.neighborhood.n06", "goon.region.r01", "poi", "freight terminal", ["WORK"], ["E4"], ["S4"], ["C1"], ["V4"], ["N2", "N5"], "O"),
  place("goon.poi.p012", "Meadow Market", "goon.neighborhood.n06", "goon.region.r01", "poi", "market", ["PUB"], ["E2"], ["S1"], ["C7"], ["V1"], ["N1"], "O"),
  place("goon.poi.p013", "Bristol Community Counseling", "goon.neighborhood.n02", "goon.region.r01", "poi", "voluntary care", ["CARE"], ["E6"], ["S2"], ["C4"], ["V6"], ["N4"], "O"),
  place("goon.poi.p014", "Northgate Police Desk", "goon.neighborhood.n04", "goon.region.r01", "poi", "police public counter", ["PUB"], ["E5"], ["S3"], ["C4"], ["V5"], ["N3"], "O"),
  place("goon.poi.p015", "Meadow Emergency Shelter", "goon.neighborhood.n06", "goon.region.r01", "poi", "shelter", ["HELP"], ["E6"], ["S1"], ["C6"], ["V2", "V6"], ["N1", "N4"], "O"),

  // --- R02 POIs ---
  place("goon.poi.p016", "Westbank Flats", "goon.neighborhood.n07", "goon.region.r02", "poi", "housing", ["HOME"], ["E1"], ["S1"], ["C3"], ["V2"], ["N1"], "O"),
  place("goon.poi.p017", "Westbank Tenants Office", "goon.neighborhood.n07", "goon.region.r02", "poi", "civic support", ["PUB"], ["E5"], ["S1"], ["C3"], ["V5"], ["N1", "N3"], "O"),
  place("goon.poi.p018", "Foundry Repair Cooperative", "goon.neighborhood.n08", "goon.region.r02", "poi", "workshop", ["WORK"], ["E3"], ["S5"], ["C5"], ["V3"], ["N6"], "O"),
  place("goon.poi.p019", "Foundry Safety Training Hall", "goon.neighborhood.n08", "goon.region.r02", "poi", "training", ["ENT"], ["E5"], ["S2"], ["C5"], ["V3"], ["N6"], "O"),
  place("goon.poi.p020", "Union Hall", "goon.neighborhood.n09", "goon.region.r02", "poi", "community workplace", ["PUB"], ["E5"], ["S1"], ["C3"], ["V3", "V5"], ["N1", "N6"], "O"),
  place("goon.poi.p021", "Union Quarter Library", "goon.neighborhood.n09", "goon.region.r02", "poi", "library", ["PUB"], ["E5"], ["S1"], ["C6"], ["V5"], ["N1"], "O"),
  place("goon.poi.p022", "West Regional Station", "goon.neighborhood.n10", "goon.region.r02", "poi", "station", ["PUB"], ["E4"], ["S2"], ["C2"], ["V4"], ["N2"], "O"),
  place("goon.poi.p023", "Switchyard Maintenance Depot", "goon.neighborhood.n10", "goon.region.r02", "poi", "depot", ["WORK"], ["E3"], ["S5"], ["C5"], ["V3"], ["N6"], "O"),
  place("goon.poi.p024", "Stonecross Court Annex", "goon.neighborhood.n11", "goon.region.r02", "poi", "court public counter", ["PUB"], ["E5"], ["S3"], ["C4"], ["V5"], ["N3"], "O"),
  place("goon.poi.p025", "Stonecross Legal Aid", "goon.neighborhood.n11", "goon.region.r02", "poi", "advocacy", ["HELP"], ["E5"], ["S2"], ["C4"], ["V5"], ["N3"], "O"),
  place("goon.poi.p026", "West Canal Passenger Pier", "goon.neighborhood.n12", "goon.region.r02", "poi", "ferry terminal", ["PUB"], ["E4"], ["S4"], ["C1"], ["V4"], ["N2"], "O"),
  place("goon.poi.p027", "Wharf Corner Cafe", "goon.neighborhood.n12", "goon.region.r02", "poi", "cafe", ["ENT"], ["E2"], ["S1"], ["C6"], ["V1", "V7"], ["N1", "N7"], "O"),
  place("goon.poi.p028", "Foundry Urgent Clinic", "goon.neighborhood.n08", "goon.region.r02", "poi", "clinic", ["CARE"], ["E6"], ["S2"], ["C4"], ["V6"], ["N4"], "O"),
  place("goon.poi.p029", "West Mainland Police Precinct", "goon.neighborhood.n11", "goon.region.r02", "poi", "police public counter", ["PUB"], ["E5"], ["S3"], ["C4"], ["V5"], ["N3"], "O"),
  place("goon.poi.p030", "Switchyard Goods Depot", "goon.neighborhood.n10", "goon.region.r02", "poi", "freight depot", ["WORK"], ["E4"], ["S4"], ["C1"], ["V4"], ["N2", "N5"], "O"),

  // --- R03 POIs ---
  place("goon.poi.p031", "East Side Housing Cooperative", "goon.neighborhood.n13", "goon.region.r03", "poi", "housing", ["HOME"], ["E1"], ["S1"], ["C3"], ["V2"], ["N1"], "O"),
  place("goon.poi.p032", "Uptown General Store", "goon.neighborhood.n13", "goon.region.r03", "poi", "shop", ["ENT"], ["E2"], ["S2"], ["C2"], ["V1"], ["N1"], "O"),
  place("goon.poi.p033", "Robinson Park", "goon.neighborhood.n14", "goon.region.r03", "poi", "park", ["PUB"], ["E8"], ["S1"], ["C6"], ["V8"], ["N8", "N10"], "D"),
  place("goon.poi.p034", "Garden Learning Center", "goon.neighborhood.n14", "goon.region.r03", "poi", "education", ["PUB"], ["E5"], ["S1"], ["C6"], ["V5", "V8"], ["N1", "N8"], "O"),
  place("goon.poi.p035", "Amusement Mile Boardwalk", "goon.neighborhood.n15", "goon.region.r03", "poi", "leisure frontage", ["PUB"], ["E7"], ["S2"], ["C6"], ["V7"], ["N7"], "A name; O frontage"),
  place("goon.poi.p036", "Nightshift Diner", "goon.neighborhood.n15", "goon.region.r03", "poi", "diner", ["ENT"], ["E2"], ["S1"], ["C3"], ["V1"], ["N1", "N7"], "O"),
  place("goon.poi.p037", "Gables Community Clinic", "goon.neighborhood.n16", "goon.region.r03", "poi", "clinic", ["CARE"], ["E6"], ["S2"], ["C4"], ["V6"], ["N4"], "O"),
  place("goon.poi.p038", "Gables Social Club", "goon.neighborhood.n16", "goon.region.r03", "poi", "social venue", ["ENT"], ["E7"], ["S1"], ["C6"], ["V7"], ["N1", "N7"], "O"),
  place("goon.poi.p039", "Highbridge Metro Stop", "goon.neighborhood.n17", "goon.region.r03", "poi", "metro station", ["PUB"], ["E4"], ["S2"], ["C2"], ["V4"], ["N2"], "O"),
  place("goon.poi.p040", "Highbridge Court Counter", "goon.neighborhood.n17", "goon.region.r03", "poi", "court public counter", ["PUB"], ["E5"], ["S3"], ["C4"], ["V5"], ["N3"], "O"),
  place("goon.poi.p041", "North Quay Passenger Pier", "goon.neighborhood.n18", "goon.region.r03", "poi", "ferry terminal", ["PUB"], ["E4"], ["S4"], ["C1"], ["V4"], ["N2"], "O"),
  place("goon.poi.p042", "North Quay Boat Repair", "goon.neighborhood.n18", "goon.region.r03", "poi", "workshop", ["WORK"], ["E3"], ["S5"], ["C5"], ["V3"], ["N2", "N6"], "O"),
  place("goon.poi.p043", "Gardens Voluntary Care", "goon.neighborhood.n14", "goon.region.r03", "poi", "voluntary care", ["CARE"], ["E6"], ["S2"], ["C4"], ["V6"], ["N4"], "O"),
  place("goon.poi.p044", "North Borough Police Station", "goon.neighborhood.n17", "goon.region.r03", "poi", "police public counter", ["PUB"], ["E5"], ["S3"], ["C4"], ["V5"], ["N3"], "O"),
  place("goon.poi.p045", "Fairground Crew Dispatch", "goon.neighborhood.n15", "goon.region.r03", "poi", "work referral", ["PUB"], ["E4"], ["S1"], ["C3"], ["V3"], ["N2", "N7"], "O"),

  // --- R04 POIs ---
  place("goon.poi.p046", "Wayne Tower", "goon.neighborhood.n19", "goon.region.r04", "poi", "office tower", ["ENT"], ["E2"], ["S3"], ["C4"], ["V3"], ["N1", "N6"], "D"),
  place("goon.poi.p047", "Central Interchange", "goon.neighborhood.n19", "goon.region.r04", "poi", "interchange", ["PUB"], ["E4"], ["S2"], ["C2"], ["V4"], ["N2"], "O"),
  place("goon.poi.p048", "Iceberg Lounge", "goon.neighborhood.n20", "goon.region.r04", "poi", "nightclub", ["ENT"], ["E7"], ["S3"], ["C6"], ["V7"], ["N7", "N10"], "I"),
  place("goon.poi.p049", "Jewelers Repair Guild", "goon.neighborhood.n20", "goon.region.r04", "poi", "workshop", ["WORK"], ["E3"], ["S2"], ["C7"], ["V3"], ["N1", "N6"], "O"),
  place("goon.poi.p050", "Chinatown Market Hall", "goon.neighborhood.n21", "goon.region.r04", "poi", "market", ["PUB"], ["E2"], ["S1"], ["C2"], ["V1"], ["N1"], "O"),
  place("goon.poi.p051", "Community Translation Desk", "goon.neighborhood.n21", "goon.region.r04", "poi", "public service", ["HELP"], ["E5"], ["S1"], ["C0"], ["V5"], ["N1", "N3"], "O"),
  place("goon.poi.p052", "Gotham City Courthouse", "goon.neighborhood.n22", "goon.region.r04", "poi", "court public counter", ["PUB"], ["E5"], ["S3"], ["C4"], ["V5"], ["N3"], "O civic category"),
  place("goon.poi.p053", "GCPD Public Headquarters", "goon.neighborhood.n22", "goon.region.r04", "poi", "police public counter", ["PUB"], ["E5"], ["S3"], ["C4"], ["V5"], ["N3"], "O facility; RPG institution"),
  place("goon.poi.p054", "Central Canal Ferry Terminal", "goon.neighborhood.n23", "goon.region.r04", "poi", "ferry terminal", ["PUB"], ["E4"], ["S4"], ["C1"], ["V4"], ["N2"], "O"),
  place("goon.poi.p055", "Freight Broker Exchange", "goon.neighborhood.n23", "goon.region.r04", "poi", "office", ["ENT"], ["E2"], ["S2"], ["C1"], ["V3", "V4"], ["N2", "N5"], "O"),
  place("goon.poi.p056", "Market Steps Community Hall", "goon.neighborhood.n24", "goon.region.r04", "poi", "community venue", ["PUB"], ["E5"], ["S1"], ["C6"], ["V5", "V7"], ["N1"], "O"),
  place("goon.poi.p057", "Day Labor Referral Desk", "goon.neighborhood.n24", "goon.region.r04", "poi", "work referral", ["PUB"], ["E5"], ["S1"], ["C3"], ["V3"], ["N1", "N6"], "O"),
  place("goon.poi.p058", "Gotham General Hospital", "goon.neighborhood.n19", "goon.region.r04", "poi", "hospital", ["CARE"], ["E6"], ["S2"], ["C4"], ["V6"], ["N4"], "H"),
  place("goon.poi.p059", "Metro Control Office", "goon.neighborhood.n23", "goon.region.r04", "poi", "operations office", ["SEC"], ["E4"], ["S3"], ["C4"], ["V3"], ["N2", "N6"], "O"),
  place("goon.poi.p060", "Civic Public Defender Office", "goon.neighborhood.n22", "goon.region.r04", "poi", "advocacy", ["HELP"], ["E5"], ["S2"], ["C4"], ["V5"], ["N3"], "O"),

  // --- R05 POIs ---
  place("goon.poi.p061", "Crime Alley", "goon.neighborhood.n25", "goon.region.r05", "poi", "street/public place", ["PUB"], ["E5"], ["S1"], ["C6"], ["V2", "V5"], ["N1", "N3"], "P"),
  place("goon.poi.p062", "Park Row Community Clinic", "goon.neighborhood.n25", "goon.region.r05", "poi", "clinic", ["CARE"], ["E6"], ["S2"], ["C4"], ["V6"], ["N4"], "O"),
  place("goon.poi.p063", "East End Repair Market", "goon.neighborhood.n26", "goon.region.r05", "poi", "market/workshops", ["PUB"], ["E2", "E3"], ["S1"], ["C7"], ["V1", "V3"], ["N1", "N6"], "O"),
  place("goon.poi.p064", "Night Rooms Housing", "goon.neighborhood.n26", "goon.region.r05", "poi", "housing", ["HOME"], ["E1"], ["S1"], ["C3"], ["V2"], ["N1"], "O"),
  place("goon.poi.p065", "Narrows Public Bathhouse", "goon.neighborhood.n27", "goon.region.r05", "poi", "civilian service", ["ENT"], ["E2"], ["S1"], ["C0"], ["V2"], ["N1"], "O"),
  place("goon.poi.p066", "Narrows Care and Reentry Center", "goon.neighborhood.n27", "goon.region.r05", "poi", "care/reentry", ["CARE"], ["E6"], ["S2"], ["C4"], ["V5", "V6"], ["N3", "N4"], "O"),
  place("goon.poi.p067", "Old Dock Warehouse Cooperative", "goon.neighborhood.n28", "goon.region.r05", "poi", "warehouse", ["WORK"], ["E4"], ["S4"], ["C1"], ["V3", "V4"], ["N5"], "O"),
  place("goon.poi.p068", "Old Dock Fire Station", "goon.neighborhood.n28", "goon.region.r05", "poi", "fire/public counter", ["PUB"], ["E5"], ["S2"], ["C5"], ["V5"], ["N6"], "O"),
  place("goon.poi.p069", "Monarch Theatre", "goon.neighborhood.n25", "goon.region.r05", "poi", "theater", ["ENT"], ["E7"], ["S2"], ["C6"], ["V7"], ["N7"], "P"),
  place("goon.poi.p070", "Stagehands Hall", "goon.neighborhood.n29", "goon.region.r05", "poi", "work/community hall", ["PUB"], ["E5"], ["S1"], ["C3"], ["V3", "V7"], ["N6", "N7"], "O"),
  place("goon.poi.p071", "South Gate Subway Stop", "goon.neighborhood.n30", "goon.region.r05", "poi", "metro station", ["PUB"], ["E4"], ["S2"], ["C2"], ["V4"], ["N2"], "O"),
  place("goon.poi.p072", "South Gate Bus Terminal", "goon.neighborhood.n30", "goon.region.r05", "poi", "bus station", ["PUB"], ["E4"], ["S2"], ["C2"], ["V4"], ["N2"], "O"),
  place("goon.poi.p073", "South Borough Court Counter", "goon.neighborhood.n30", "goon.region.r05", "poi", "court public counter", ["PUB"], ["E5"], ["S3"], ["C4"], ["V5"], ["N3"], "O"),
  place("goon.poi.p074", "South Borough Police Counter", "goon.neighborhood.n30", "goon.region.r05", "poi", "police public counter", ["PUB"], ["E5"], ["S3"], ["C4"], ["V5"], ["N3"], "O"),
  place("goon.poi.p075", "Reentry Employment Office", "goon.neighborhood.n27", "goon.region.r05", "poi", "work referral", ["HELP"], ["E6"], ["S1"], ["C3"], ["V3", "V5"], ["N1", "N3"], "O"),

  // --- R06 POIs ---
  place("goon.poi.p076", "Eastern Commercial Port", "goon.neighborhood.n31", "goon.region.r06", "poi", "port", ["WORK"], ["E4"], ["S4"], ["C1"], ["V4"], ["N2", "N5"], "O"),
  place("goon.poi.p077", "East Harbor Customs Counter", "goon.neighborhood.n31", "goon.region.r06", "poi", "port public counter", ["PUB"], ["E5"], ["S4"], ["C4"], ["V5"], ["N3", "N5"], "O"),
  place("goon.poi.p078", "Iron Quay Foundry", "goon.neighborhood.n32", "goon.region.r06", "poi", "plant", ["WORK"], ["E3"], ["S5"], ["C5"], ["V3"], ["N6"], "O"),
  place("goon.poi.p079", "Iron Quay Worker Clinic", "goon.neighborhood.n32", "goon.region.r06", "poi", "clinic", ["CARE"], ["E6"], ["S2"], ["C4"], ["V6"], ["N4"], "O"),
  place("goon.poi.p080", "Drydock Services Cooperative", "goon.neighborhood.n33", "goon.region.r06", "poi", "workshop", ["WORK"], ["E3"], ["S5"], ["C5"], ["V3"], ["N5", "N6"], "O"),
  place("goon.poi.p081", "East Mainland Regional Station", "goon.neighborhood.n33", "goon.region.r06", "poi", "station", ["PUB"], ["E4"], ["S2"], ["C2"], ["V4"], ["N2"], "O"),
  place("goon.poi.p082", "Saltmarket Fish Hall", "goon.neighborhood.n34", "goon.region.r06", "poi", "market", ["PUB"], ["E2"], ["S1"], ["C7"], ["V1"], ["N1", "N5"], "O"),
  place("goon.poi.p083", "Saltmarket Civic Square", "goon.neighborhood.n34", "goon.region.r06", "poi", "square", ["PUB"], ["E5"], ["S1"], ["C6"], ["V5", "V7"], ["N1"], "O"),
  place("goon.poi.p084", "Ace Chemicals", "goon.neighborhood.n35", "goon.region.r06", "poi", "industrial plant", ["WORK"], ["E3"], ["S5"], ["C5"], ["V3"], ["N6", "N10"], "D"),
  place("goon.poi.p085", "Chemical Reach Safety School", "goon.neighborhood.n35", "goon.region.r06", "poi", "training", ["PUB"], ["E5"], ["S2"], ["C5"], ["V3"], ["N6"], "O"),
  place("goon.poi.p086", "Tideworks Power Plant", "goon.neighborhood.n36", "goon.region.r06", "poi", "utility", ["SEC"], ["E8"], ["S5"], ["C5"], ["V3"], ["N6"], "O"),
  place("goon.poi.p087", "Tideworks Water Works", "goon.neighborhood.n36", "goon.region.r06", "poi", "utility", ["SEC"], ["E8"], ["S5"], ["C5"], ["V3"], ["N6", "N8"], "O"),
  place("goon.poi.p088", "Hazard Review Office", "goon.neighborhood.n35", "goon.region.r06", "poi", "public service", ["PUB"], ["E5"], ["S2"], ["C4"], ["V5"], ["N3", "N6"], "O"),
  place("goon.poi.p089", "East Harbor Marine Police Counter", "goon.neighborhood.n31", "goon.region.r06", "poi", "marine/public counter", ["PUB"], ["E5"], ["S4"], ["C4"], ["V5"], ["N3"], "O"),
  place("goon.poi.p090", "Port Worker Housing Cooperative", "goon.neighborhood.n32", "goon.region.r06", "poi", "housing", ["HOME"], ["E1"], ["S1"], ["C3"], ["V2"], ["N1", "N5"], "O"),

  // --- R07 POIs ---
  place("goon.poi.p091", "South Exchange Coach Station", "goon.neighborhood.n37", "goon.region.r07", "poi", "intercity station", ["PUB"], ["E4"], ["S2"], ["C2"], ["V4"], ["N2"], "O"),
  place("goon.poi.p092", "South Market Community Hospital", "goon.neighborhood.n37", "goon.region.r07", "poi", "hospital", ["CARE"], ["E6"], ["S2"], ["C4"], ["V6"], ["N4"], "O"),
  place("goon.poi.p093", "Sawmill Repair Collective", "goon.neighborhood.n38", "goon.region.r07", "poi", "workshop", ["WORK"], ["E3"], ["S5"], ["C5"], ["V3"], ["N6"], "O"),
  place("goon.poi.p094", "Sawmill Rooms", "goon.neighborhood.n38", "goon.region.r07", "poi", "housing", ["HOME"], ["E1"], ["S1"], ["C3"], ["V2"], ["N1"], "O"),
  place("goon.poi.p095", "Reed Marsh Reserve", "goon.neighborhood.n39", "goon.region.r07", "poi", "wetland park", ["PUB"], ["E8"], ["S1"], ["C5"], ["V8"], ["N8"], "O"),
  place("goon.poi.p096", "Wetland Field Laboratory", "goon.neighborhood.n39", "goon.region.r07", "poi", "research facility", ["WORK"], ["E8"], ["S5"], ["C5"], ["V3", "V8"], ["N6", "N8"], "O"),
  place("goon.poi.p097", "Outfall Maintenance Depot", "goon.neighborhood.n40", "goon.region.r07", "poi", "utility depot", ["WORK"], ["E8"], ["S5"], ["C5"], ["V3"], ["N6"], "O"),
  place("goon.poi.p098", "Outfall Community Clinic", "goon.neighborhood.n40", "goon.region.r07", "poi", "clinic", ["CARE"], ["E6"], ["S2"], ["C4"], ["V6"], ["N4"], "O"),
  place("goon.poi.p099", "South Rail Passenger Station", "goon.neighborhood.n41", "goon.region.r07", "poi", "station", ["PUB"], ["E4"], ["S2"], ["C2"], ["V4"], ["N2"], "O"),
  place("goon.poi.p100", "South Freight Yard", "goon.neighborhood.n41", "goon.region.r07", "poi", "freight depot", ["WORK"], ["E4"], ["S4"], ["C1"], ["V4"], ["N2", "N5"], "O"),
  place("goon.poi.p101", "Millbrook School and Adult Education", "goon.neighborhood.n42", "goon.region.r07", "poi", "education", ["ENT"], ["E5"], ["S2"], ["C0"], ["V5"], ["N1", "N3"], "O"),
  place("goon.poi.p102", "Millbrook Social Hall", "goon.neighborhood.n42", "goon.region.r07", "poi", "social venue", ["PUB"], ["E7"], ["S1"], ["C6"], ["V7"], ["N1", "N7"], "O"),
  place("goon.poi.p103", "South Mainland Court Counter", "goon.neighborhood.n37", "goon.region.r07", "poi", "court public counter", ["PUB"], ["E5"], ["S3"], ["C4"], ["V5"], ["N3"], "O"),
  place("goon.poi.p104", "South Mainland Police Desk", "goon.neighborhood.n41", "goon.region.r07", "poi", "police public counter", ["PUB"], ["E5"], ["S3"], ["C4"], ["V5"], ["N3"], "O"),
  place("goon.poi.p105", "Supported Housing Referral", "goon.neighborhood.n42", "goon.region.r07", "poi", "support service", ["HELP"], ["E6"], ["S1"], ["C0"], ["V2", "V5"], ["N1", "N3"], "O"),

  // --- R08 POIs ---
  place("goon.poi.p106", "Breakwater Main Pier", "goon.neighborhood.n43", "goon.region.r08", "poi", "ferry terminal", ["PUB"], ["E4"], ["S4"], ["C1"], ["V4"], ["N2"], "O"),
  place("goon.poi.p107", "Breakwater Daily Store", "goon.neighborhood.n43", "goon.region.r08", "poi", "shop", ["ENT"], ["E2"], ["S1"], ["C2"], ["V1"], ["N1"], "O"),
  place("goon.poi.p108", "Lantern Harbor Rescue Station", "goon.neighborhood.n44", "goon.region.r08", "poi", "marine/public service", ["PUB"], ["E5"], ["S2"], ["C5"], ["V5"], ["N2", "N6"], "O"),
  place("goon.poi.p109", "Lantern Care Referral Desk", "goon.neighborhood.n44", "goon.region.r08", "poi", "care support", ["HELP"], ["E6"], ["S1"], ["C0"], ["V6"], ["N4"], "O"),
  place("goon.poi.p110", "Arkham Asylum", "goon.neighborhood.n45", "goon.region.r08", "poi", "psychiatric institution", ["CARE"], ["E6"], ["S3"], ["C4"], ["V6"], ["N4", "N9"], "D; RPG island name"),
  place("goon.poi.p111", "Arkham Family Reception", "goon.neighborhood.n45", "goon.region.r08", "poi", "institution reception", ["VIS"], ["E5"], ["S3"], ["C6"], ["V5"], ["N4", "N9"], "O"),
  place("goon.poi.p112", "Blackgate Penitentiary", "goon.neighborhood.n46", "goon.region.r08", "poi", "prison", ["VIS"], ["E5"], ["S3"], ["C6"], ["V5"], ["N3", "N9"], "K"),
  place("goon.poi.p113", "Blackgate Authorized Visiting Hall", "goon.neighborhood.n46", "goon.region.r08", "poi", "institution reception", ["VIS"], ["E5"], ["S3"], ["C6"], ["V5"], ["N9"], "O"),
  place("goon.poi.p114", "Netmaker Repair Cooperative", "goon.neighborhood.n47", "goon.region.r08", "poi", "workshop", ["WORK"], ["E3"], ["S2"], ["C3"], ["V3"], ["N5", "N6"], "O"),
  place("goon.poi.p115", "Netmaker Worker Rooms", "goon.neighborhood.n47", "goon.region.r08", "poi", "housing", ["HOME"], ["E1"], ["S1"], ["C3"], ["V2"], ["N1", "N5"], "O"),
  place("goon.poi.p116", "Beacon Lighthouse", "goon.neighborhood.n48", "goon.region.r08", "poi", "navigation facility", ["SEC"], ["E8"], ["S5"], ["C5"], ["V3"], ["N2", "N6"], "O"),
  place("goon.poi.p117", "Beacon Community Hall", "goon.neighborhood.n48", "goon.region.r08", "poi", "community venue", ["PUB"], ["E5"], ["S1"], ["C6"], ["V5", "V7"], ["N1"], "O"),
  place("goon.poi.p118", "Lantern Ferry Worker Canteen", "goon.neighborhood.n44", "goon.region.r08", "poi", "cafe", ["ENT"], ["E2"], ["S1"], ["C3"], ["V1"], ["N1", "N2"], "O"),
  place("goon.poi.p119", "Island Public Aid and Advocacy", "goon.neighborhood.n43", "goon.region.r08", "poi", "support service", ["HELP"], ["E5"], ["S1"], ["C4"], ["V5"], ["N3", "N4"], "O"),
  place("goon.poi.p120", "Archipelago Staff Ferry Office", "goon.neighborhood.n43", "goon.region.r08", "poi", "transport office", ["WORK"], ["E4"], ["S3"], ["C4"], ["V3", "V4"], ["N2", "N9"], "O"),
];

// The 17 named crossings (bridges / tunnels / causeways / ferries) — verbatim.
export const NAMED_CORRIDORS: Edge[] = [
  { id: "goon.edge.e01", label: "Northgate Bridge", from: "goon.neighborhood.n04", to: "goon.neighborhood.n17", kind: "corridor", description: "bridge / north West Channel", bidirectional: true, modes: { walk: 4, car: 2, bus: 2, rail: 2 }, access: "public" },
  { id: "goon.edge.e02", label: "Westbank Bridge", from: "goon.neighborhood.n07", to: "goon.neighborhood.n13", kind: "corridor", description: "bridge / West Channel", bidirectional: true, modes: { walk: 4, car: 2, bus: 2 }, access: "public" },
  { id: "goon.edge.e03", label: "Union Bridge", from: "goon.neighborhood.n09", to: "goon.neighborhood.n22", kind: "corridor", description: "bridge / West Channel", bidirectional: true, modes: { walk: 4, car: 2, bus: 2, rail: 2 }, access: "public" },
  { id: "goon.edge.e04", label: "Old Dock Bridge", from: "goon.neighborhood.n12", to: "goon.neighborhood.n28", kind: "corridor", description: "bridge / West Channel", bidirectional: true, modes: { walk: 4, car: 2, bus: 2 }, access: "public" },
  { id: "goon.edge.e05", label: "Garden Bridge", from: "goon.neighborhood.n14", to: "goon.neighborhood.n19", kind: "corridor", description: "bridge / North Cut", bidirectional: true, modes: { walk: 4, car: 2, bus: 2 }, access: "public" },
  { id: "goon.edge.e06", label: "Quay Tunnel", from: "goon.neighborhood.n18", to: "goon.neighborhood.n23", kind: "corridor", description: "road/rail tunnel / North Cut", bidirectional: true, modes: { car: 2, bus: 2, rail: 2 }, access: "public" },
  { id: "goon.edge.e07", label: "Market Bridge", from: "goon.neighborhood.n24", to: "goon.neighborhood.n29", kind: "corridor", description: "bridge / South Cut", bidirectional: true, modes: { walk: 4, car: 2, bus: 2 }, access: "public" },
  { id: "goon.edge.e08", label: "Civic Rail Tunnel", from: "goon.neighborhood.n22", to: "goon.neighborhood.n30", kind: "corridor", description: "subway tunnel / South Cut", bidirectional: true, modes: { rail: 2 }, access: "public" },
  { id: "goon.edge.e09", label: "East Channel Bridge", from: "goon.neighborhood.n23", to: "goon.neighborhood.n31", kind: "corridor", description: "bridge / East Channel", bidirectional: true, modes: { walk: 4, car: 2, bus: 2, rail: 2 }, access: "public" },
  { id: "goon.edge.e10", label: "Tide Tunnel", from: "goon.neighborhood.n36", to: "goon.neighborhood.n28", kind: "corridor", description: "road tunnel / East Channel", bidirectional: true, modes: { car: 2, bus: 2 }, access: "public" },
  { id: "goon.edge.e11", label: "South Bay Causeway", from: "goon.neighborhood.n30", to: "goon.neighborhood.n37", kind: "corridor", description: "causeway / South Bay", bidirectional: true, modes: { walk: 5, car: 3, bus: 3 }, access: "public" },
  { id: "goon.edge.e12", label: "Marsh Rail Tunnel", from: "goon.neighborhood.n41", to: "goon.neighborhood.n33", kind: "corridor", description: "regional rail / bay approaches", bidirectional: true, modes: { rail: 3 }, access: "public" },
  { id: "goon.edge.e13", label: "Breakwater Public Ferry", from: "goon.neighborhood.n31", to: "goon.neighborhood.n43", kind: "corridor", description: "water / Outer Roadstead", bidirectional: true, modes: { ferry: 3, boat: 3 }, access: "public" },
  { id: "goon.edge.e14", label: "Coastal Ferry", from: "goon.neighborhood.n18", to: "goon.neighborhood.n43", kind: "corridor", description: "water / East Channel/Outer Roadstead", bidirectional: true, modes: { ferry: 4, boat: 4 }, access: "public" },
  { id: "goon.edge.e15", label: "Arkham Access Bridge", from: "goon.neighborhood.n43", to: "goon.neighborhood.n45", kind: "corridor", description: "bridge / Outer Roadstead local reach", bidirectional: true, modes: { walk: 2, car: 1, bus: 1 }, access: "public" },
  { id: "goon.edge.e16", label: "Blackgate Controlled Ferry", from: "goon.neighborhood.n43", to: "goon.neighborhood.n46", kind: "corridor", description: "controlled water connection", bidirectional: true, modes: { ferry: 2, boat: 2 }, access: "authorized" },
  { id: "goon.edge.e17", label: "Outer Service Ferry", from: "goon.neighborhood.n37", to: "goon.neighborhood.n43", kind: "corridor", description: "water / South Bay/Outer Roadstead", bidirectional: true, modes: { ferry: 4, boat: 4 }, access: "public" },
];

export const placeById: ReadonlyMap<string, Place> = new Map(PLACES.map((p) => [p.id, p]));

export const REGIONS = PLACES.filter((p) => p.kind === "region");
export const NEIGHBORHOODS = PLACES.filter((p) => p.kind === "neighborhood");
export const POIS = PLACES.filter((p) => p.kind === "poi");

export function childrenOf(parentId: string): Place[] {
  return PLACES.filter((p) => p.parentId === parentId);
}

export function regionOf(placeId: string): Place | undefined {
  const p = placeById.get(placeId);
  return p ? placeById.get(p.regionId) : undefined;
}

export function parentOf(placeId: string): Place | undefined {
  const p = placeById.get(placeId);
  return p && p.parentId ? placeById.get(p.parentId) : undefined;
}
