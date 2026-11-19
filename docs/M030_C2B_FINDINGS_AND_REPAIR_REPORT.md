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
