# M030-C2B findings and repair report - 2026-11-19

This milestone stabilizes the existing browser foundation. The local client is an authenticated, explicitly read-only inspection surface. The separate preview is synthetic. No browser gameplay action, Godot integration or new Python gameplay feature is enabled.

## Confirmed repairs

- Validate durable outbox records, their exact original envelope/identity/scope, receipts and IndexedDB key/index schema. Corrupt storage fails closed and is preserved for review.
- Insert new requests with IndexedDB `add`, preventing a reused ID from replacing a committed or cross-career envelope. The transaction still serializes unresolved intents across cooperating tabs.
- Bind command acknowledgments and operation lookups to the original career, lineage, command, request ID and revision. A `not_found` response must agree with both the original revision and the caller's observation before any permitted adapter retry.
- Do not replay superseded/quarantined records. Preserve a known committed receipt through repeated unsuccessful recovery instead of downgrading it into a retryable intent.
- Enforce a monotonic identity/revision floor for inspection operation reads, including after reload.
- Serialize pairing and session revalidation so overlapping refreshes cannot race to promote stale state.
- Validate a privately staged host bundle before publishing its immutable candidate directory. Rejected HTML/content cannot occupy the final candidate path. Reject reparse inputs/publication targets.
- Add a sanitized source exporter with explicit generated/private-path exclusions, bounded credential signatures, CRC/hash verification and a narrow allowlist for existing synthetic migration fixtures. Preserve browser smoke scripts and test attributes. A false-positive secret signature inside a hyphenated design word was corrected with a token boundary and a regression test; actual credential rejection remains tested.
- Extend real Edge smoke coverage to pending outbox preservation, corrupt storage, duplicate bootstrap rejection and no automatic command submission. One existing cross-tab fixture incorrectly acknowledged `req.1` for `req.tabA`; its receipt now matches the intended request.

Ten new targeted frontend cases failed before the initial repair and passed afterward. Final review added and reproduced a further committed-recovery regression before fixing it. An invalid-bundle publication regression also failed before repair. These are real failing-before/passing-after cases, not renamed baseline passes. Raw logs are retained outside the source worktree.

## Security and authority assessment

The Python game service, engine bridge, checkpoint, projection, HTTP server, browser host, bootstrap, asset validator, content and engine tests are unchanged from the captured source. Python remains standard-library-only and owns money, actions, TU, location, history, RNG, saves and consequences. Three actions/day and 18 TU/day are unchanged.

Local UI requests use authenticated same-origin endpoints. One-time pairing, exact Host/Origin, rotating process capability, no-store responses and strict CSP remain in the existing host. The native/browser host asset pin still requires independent operator review; candidate hashing is not release approval. Neither fixture data nor preview modules enter the local build. The native Godot protocol proposal remains separate and unapproved by this mission.

Real browser evidence shows zero `/api/v1/commands` calls, no external page requests, no CSP errors and byte-identical checkpoint data across reload/restart. The outbox submission adapter has isolated unit coverage but is deliberately not invoked by the inspection app. Its existence is not a claim of playable browser gameplay or a browser action E2E.

The original raw worktree export included Chromium profile filenames. Their contents were not inspected. Keep the complete backup private. If a raw profile export was shared beyond the intended trusted review, the owner should assess invalidating any associated sessions; this audit does not claim that credentials were found or that sharing can be undone. The delivered source/evidence includes no profile bytes, personal saves, databases, installed dependencies, build output or credentials detected by the signature scan. A finite pattern scan is not a universal proof that no secret can exist.

## Implemented and blocked

Implemented: separate synthetic preview; secure local pairing and revalidation; player-safe state/option inspection; read-only operation lookup transport; durable outbox primitives with fail-closed recovery tests; reproducible local packaging; safe source export and source provenance.

Intentionally unimplemented: live browser choose/work/travel/wait/adoption controls; automatic recovery submission during inspection; browser progression; Godot/Python gameplay integration; P1W/P1X and any Freebuff work. Opportunity text is displayed but cannot be executed in this build.

Remaining acceptance limits: one real Windows file-symlink test is blocked by WinError 1314; only installed Chromium/Edge headless browser smoke was executed, not Firefox/Safari, visible owner playtesting or a full accessibility audit. Physical power-loss and explicit operator timeline rollback limitations remain those of the unchanged engine. Independent source/release-pin approval is still pending; no push, merge, deployment or original-worktree backport is authorized by this handoff.

## Smallest next slice - proposal only

In a separately approved C2C mission, present one existing lawful `choose` opportunity at canonical Uptown General Store (`goon.poi.p032`, Upper East Side), with Python eligibility, one-action/$20 terms and refusal. Keep travel explicit and Python-owned. Submit the original envelope through the validated outbox, display the committed public projection, restart, recover the same ID without duplicate wages/standing and demonstrate a later source-backed consequence. Start from an explicitly selected/adopted career; no automatic new game or gameplay activation. This proposal is not implemented here.

## Independent-review correction - 2026-11-19

The independent review conditionally accepted the isolated read-only stabilization candidate. This correction does not grant release-pin approval or enable gameplay.

Repaired 19 malformed punctuation sequences (15 em dashes, four right arrows) in `frontend/src/gameplay/outbox.ts`, `frontend/src/gameplay/LiveEngineProvider.tsx` and `frontend/tests/outbox.test.ts`, including five user-visible error messages. Repaired three milestone-heading separators in `README.md`, `PROJECT_STATE.md` and `docs/GOON_MILESTONE_ROADMAP.md`. Explicit UTF-8 read/write and exact substitution comparisons confirm no control-flow, request, receipt or shared-interface change.

Added `frontend/tests/text-integrity.test.ts`: strict UTF-8 decoding, corruption signatures across frontend source/tests, milestone-heading checks, and controls permitting genuine Unicode/questions. Before correction: one PASS, two FAIL; after correction: all three PASS. Full frontend suite: 176 PASS, zero FAIL/SKIP. Typecheck, both builds and candidate packaging exit 0. Host packaging: 8 PASS; source exporter: 4 PASS. Compiled preview/local assets and the host bundle are byte-identical to the reviewed candidate; no new browser run is claimed. An initial restricted-process directory enumeration could not see the generated bundle; normal-permission verification found all four files and confirmed their hashes. This was a verification visibility limitation, not a bundle-test failure.

The two original commit objects and exact single-parent chain were verified: `f2e75dd959c55a2f7d8207a7d3b0160d60efb444` -> `84df1dab70e189631c5cc6a25d655f00e2502a59` -> `b25a9d1b3cfed4de065ed5e340870dfc268c4c96`. The correction follows this chain on `stabilize/m030-c2b-20261118`. Its actual SHA, explicit staging hashes and final clean status are in the separate correction handoff; no history rewrite was used.

All 259 original source hashes, branch/HEAD and 82 status entries still match capture. All 115 authoritative Python/content/test paths remain byte-identical. Shared interfaces did not change, so no additional Python engine suite was required or claimed. Prior full Python 619 PASS / 1 SKIP and independently reported bridge/host 97 PASS / 1 SKIP remain distinct from this correction's executed checks. The Windows symlink privilege blocker, independent production pin approval and other previously reported acceptance limits remain unresolved.

Previous archives remain immutable. The corrected archive has its own per-file manifest; the 259-row source inventory remains historical provenance, not the final archive manifest.

## Lossless integration plan - awaiting owner approval

These are proposed steps only. Approval must identify the reviewed correction SHA and permanent target location/branch. No integration or gameplay activation is authorized by this report.

1. Keep the original dirty worktree and private 7,650-file backup intact. Obtain owner approval of this correction and a new permanent sibling integration location. Do not reset, clean, stash, force checkout or overlay an archive onto the original.
2. Before approved integration, request Save All, then recheck original HEAD/branch/status and captured source hashes, plus the isolated correction SHA and clean status. If anything changed, preserve the new edits in a new private snapshot before reconciling; retain the existing backup. Do not assume the 82 entries are disposable.
3. Create a permanent sibling clone from the verified isolated local repository, check out the approved correction SHA on a new integration branch, and verify all three commits and source hashes. Do not switch or cherry-pick into the dirty original. The stabilization commits already incorporate its seven modified tracked paths and 75 untracked source paths; copying them wholesale would replace reviewed repairs.
4. Reconcile any new original edits using the captured 259-file source snapshot as the content base, the approved candidate as one side, and the newly saved original as the other. Account for every new file, edit and deletion. Retain conflicting versions for owner resolution; never automatically choose ours/theirs. If original source still matches capture, no source delta is needed. Keep personal saves/configuration in place for explicit host selection after review; never commit them, browser profiles or generated output.
5. Rebuild and rerun applicable tests in the permanent sibling. Produce fresh evidence/hashes if reconciliation changes content. Have the owner open the verified sibling as the development workspace. Leave the original repository and branch intact as the recovery reference until its disposition is separately approved.
6. Stop for owner review. Updating the original branch, publishing, merging, deploying, approving a release pin, or beginning gameplay requires separate explicit authorization. No Godot P1V-B/P1W, P1X or Freebuff work is included.
