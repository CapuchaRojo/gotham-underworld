import { test } from "node:test";
import assert from "node:assert/strict";
import {
  PLACES,
  REGIONS,
  NEIGHBORHOODS,
  POIS,
  NAMED_CORRIDORS,
  ROOT_ID,
  placeById,
} from "../src/atlas";
import { LOCAL_CORRIDORS, ACCESS_SPURS } from "../src/navigation_data";
import type { Edge } from "../src/types";
import { loadJson } from "./helpers";

interface JsonPlace {
  id: string;
  label: string;
  parent_id: string | null;
  region_id: string;
  kind: string;
  type: string;
  access: string[];
  economy: string[];
  security: string[];
  criminal: string[];
  civilian: string[];
  npc_pool: string[];
  source: string;
}

interface JsonEdge {
  id: string;
  label: string;
  from: string;
  to: string;
  kind: string;
  description: string;
  bidirectional: boolean;
  modes: Record<string, number>;
  access: string;
}

interface JsonAtlas {
  root_id: string;
  places: JsonPlace[];
  edges: JsonEdge[];
}

const atlas = loadJson<JsonAtlas>("../content/gotham_atlas_v1.json");

test("atlas counts are preserved (176 places / 183 edges)", () => {
  assert.equal(atlas.places.length, 176);
  assert.equal(atlas.edges.length, 183);

  assert.equal(PLACES.length, 176);
  assert.equal(REGIONS.length, 8);
  assert.equal(NEIGHBORHOODS.length, 48);
  assert.equal(POIS.length, 120);

  assert.equal(NAMED_CORRIDORS.length, 17);
  assert.equal(LOCAL_CORRIDORS.length, 46);
  assert.equal(ACCESS_SPURS.length, 120);
  assert.equal(NAMED_CORRIDORS.length + LOCAL_CORRIDORS.length + ACCESS_SPURS.length, 183);
});

test("place identifiers are stable and follow the authored conventions", () => {
  const ids = PLACES.map((p) => p.id);
  assert.equal(new Set(ids).size, ids.length, "place ids must be unique");
  assert.equal(ROOT_ID, "goon.city.gotham");
  for (const p of PLACES) {
    assert.match(p.id, /^goon\.(region\.r|neighborhood\.n|poi\.p)\d+$/, p.id);
  }
});

test("every TS place matches the authored atlas JSON verbatim", () => {
  const jsonById = new Map(atlas.places.map((p) => [p.id, p]));
  assert.equal(jsonById.size, PLACES.length);
  for (const p of PLACES) {
    const j = jsonById.get(p.id);
    assert.ok(j, `missing JSON place ${p.id}`);
    assert.equal(p.label, j.label, `${p.id} label`);
    assert.equal(p.parentId, j.parent_id, `${p.id} parent_id`);
    assert.equal(p.regionId, j.region_id, `${p.id} region_id`);
    assert.equal(p.kind, j.kind, `${p.id} kind`);
    assert.equal(p.type, j.type, `${p.id} type`);
    assert.deepEqual(p.access, j.access, `${p.id} access`);
    assert.deepEqual(p.economy, j.economy, `${p.id} economy`);
    assert.deepEqual(p.security, j.security, `${p.id} security`);
    assert.deepEqual(p.criminal, j.criminal, `${p.id} criminal`);
    assert.deepEqual(p.civilian, j.civilian, `${p.id} civilian`);
    assert.deepEqual(p.npcPool, j.npc_pool, `${p.id} npc_pool`);
    assert.equal(p.source, j.source, `${p.id} source`);
  }
});

test("regions are rooted and containment is valid", () => {
  for (const r of REGIONS) {
    assert.equal(r.parentId, ROOT_ID, `${r.id} must sit under the city root`);
    assert.equal(r.regionId, r.id, `${r.id} must be its own region`);
  }
  for (const n of NEIGHBORHOODS) {
    assert.equal(placeById.get(n.regionId)?.kind, "region", `${n.id} regionId`);
  }
  for (const poi of POIS) {
    const parent = placeById.get(poi.parentId ?? "");
    assert.equal(parent?.kind, "neighborhood", `${poi.id} parent`);
    assert.equal(poi.regionId, parent?.regionId, `${poi.id} region consistency`);
  }
});

test("every authored edge endpoint is a real, distinct place", () => {
  for (const e of atlas.edges) {
    assert.ok(placeById.has(e.from), `edge ${e.id} bad from ${e.from}`);
    assert.ok(placeById.has(e.to), `edge ${e.id} bad to ${e.to}`);
    assert.notEqual(e.from, e.to, `edge ${e.id} self-loop`);
  }
});

test("TS edges (named + local + spurs) match the authored JSON verbatim", () => {
  const jsonEdges = new Map(atlas.edges.map((e) => [e.id, e]));
  const tsEdges: Edge[] = [...NAMED_CORRIDORS, ...LOCAL_CORRIDORS, ...ACCESS_SPURS];
  assert.equal(tsEdges.length, atlas.edges.length);
  for (const e of tsEdges) {
    const j = jsonEdges.get(e.id);
    assert.ok(j, `missing JSON edge ${e.id}`);
    assert.equal(e.label, j.label, `${e.id} label`);
    assert.equal(e.from, j.from, `${e.id} from`);
    assert.equal(e.to, j.to, `${e.id} to`);
    assert.equal(e.kind, j.kind, `${e.id} kind`);
    assert.equal(e.description, j.description, `${e.id} description`);
    assert.equal(e.bidirectional, j.bidirectional, `${e.id} bidirectional`);
    assert.equal(e.access, j.access, `${e.id} access`);
    assert.deepEqual(e.modes, j.modes, `${e.id} modes`);
  }
});

test("every POI has exactly one authored access spur from its parent neighborhood", () => {
  const spurCounts = new Map<string, number>();
  for (const e of ACCESS_SPURS) {
    assert.equal(e.kind, "access");
    assert.equal(e.access, "location");
    assert.equal(e.from, placeById.get(e.to)?.parentId, `${e.id} must originate at the POI's parent`);
    spurCounts.set(e.to, (spurCounts.get(e.to) ?? 0) + 1);
  }
  for (const poi of POIS) {
    assert.equal(spurCounts.get(poi.id), 1, `POI ${poi.id} must have one spur`);
  }
  assert.equal(ACCESS_SPURS.length, POIS.length);
});

test("the authorized corridor (e16) targets a restricted receiving endpoint", () => {
  const authorized = [...NAMED_CORRIDORS, ...LOCAL_CORRIDORS].filter(
    (e) => e.access === "authorized",
  );
  assert.equal(authorized.length, 1);
  const e = authorized[0];
  assert.equal(e.id, "goon.edge.e16");
  const target = placeById.get(e.to);
  assert.ok(target);
  const RESTRICTED = new Set(["HOME", "WORK", "VIS", "SEC"]);
  assert.ok(
    target.access.some((a) => RESTRICTED.has(a)),
    "e16 must end at a restricted-access place",
  );
});
