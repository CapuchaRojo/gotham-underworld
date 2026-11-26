# M030-C2B source inventory - 2026-11-19

The active work continues in the isolated `M030_C2B_20261118/work` copy on branch `stabilize/m030-c2b-20261118`, parent `f2e75dd959c55a2f7d8207a7d3b0160d60efb444`. The original repository remains on `feature/m030-c2b-frontend-integration` at the same HEAD with its original 82 status entries. Save All was confirmed before capture.

## Preservation and counts

The private full backup contains 7,650 files, including Git, ignored dependencies, local saves and opaque browser profiles. SHA-256: `ae1812de7833e74bb2522ddbdb6659c82565cc8b9db8d446d0960e46ca943ea4`. It remains separately under `protected/M030_C2B_FULL_20261118.zip`; never redistribute it as source. The November 10 recovery point was not modified.

The source baseline contains 184 tracked files and 75 ordinary untracked files: 259 source/reference paths. Seven tracked modifications plus 75 untracked files produce 82 Git status entries; ZIP entries additionally count directories, ignored output and profiles. All 259 original source paths were rehashed unchanged on resumption. The original status, branch and HEAD also match the capture.

`.git/FETCH_HEAD` changed during capture through a background process; source, branch and HEAD did not. On November 19 the isolated clone lacked 638 Git object files. They were recovered exclusively from the verified backup, each loose object checked against its SHA-1 name, without changing source or refs. Git connectivity now passes; restored dangling historical objects are private Git metadata and are not exported. The cause of the missing files is not established.

## Existing work accounted for

| Paths | Classification and handling |
| --- | --- |
| `.gitignore` | Existing generated-output/profile exclusions preserved; private-file exclusions added |
| `PROJECT_STATE.md`, `README.md` | Existing November 7 direction/interrupted-work history preserved; current verified status added |
| `docs/GOON_GAMEPLAY_PRINCIPLES.md`, `GOON_MAP_VISUAL_SPEC.md`, `GOON_MILESTONE_ROADMAP.md`, `GOON_WORLD_RUNTIME.md` | Existing design addenda preserved, distinguished from implementation; roadmap current status added |
| `docs/GOON_ROADMAP_TO_PLAYABLE_1_0.md`, `GOON_THIRD_PERSON_VERTICAL_SLICE.md` | Two previously untracked design documents preserved, not gameplay authorization |
| `frontend/` | 73 original untracked frontend source/config/test/tool files preserved, then bounded stabilization changes applied |
| `.integration/`, installed dependencies, generated distributions, local saves | Private backup only; not staged or distributed |
| `GOON_NATIVELY_CANON_REFERENCE_PACK.zip` | Existing tracked reference archive left untouched; excluded from sanitized ZIP because its nested contents are not part of this release audit |

`M030_C2B_SOURCE_MANIFEST.json` classifies every original source path and hashes original versus candidate. The external review evidence contains exact staging paths, normalized text diffs and raw-byte hashes. Five explicitly named, already committed synthetic migration fixtures under `tests/fixtures` and `tests/mobility_fixtures` are retained as test source. These are not personal saved careers. Other career/save paths remain excluded.

## Builder comparison

The supplied Builder ZIP contains 160 non-directory files. Mapping its frontend-relative paths to local frontend yields 52 identical files, 10 differing files and 98 reference-only paths. These counts include configs; they are not a claim that 98 UI components are missing. The complete file-by-file record is `M030_C2B_BUILDER_COMPARISON.json`.

TodayView, StreetsView, LifeView, StoryView, contact/work/place cards, player presentation and original icons are already present. Reuse those source-backed presentation components in a later approved gameplay slice. Retain local entry-point separation, session binding, external CSS meter rules and host packaging. Do not import Builder's permissive Vite configuration, postMessage theme bridge, environment/query live-mode selection, fixture authority or Python copies. Reference docs and images remain reference-only. No new Builder visual port was needed for this stabilization.

The original Godot P1V-B and separate P1W integration copy were not edit or test targets. No Freebuff transfer occurred.
