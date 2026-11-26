# GTG-26 safe Builder UI port - 2026-11-19

This candidate selectively ports preview presentation onto accepted M030-C2B commit `09370a4e4c78596c9c42e4a1c0aa6d837778881a`. It does not enable browser gameplay or replace the Python engine. Development occurs only in `C:/Users/mich3/Projects/gotham_underworld_gtg26_ui_port`, branch `feature/gtg26-builder-ui-port`; review evidence is in the sibling `gotham_underworld_gtg26_ui_port_review_20261119` directory. Accepted/original repositories and Godot projects are not development targets.

## Reference source and selection

The operator-supplied ZIP's plain filename was absent. Downloads contained its URL-encoded name `Gotham--The-Goon-source-code%20%285%29.zip`; it was used only after matching the mission's exact 18,027,424 bytes and SHA-256 `ef88a5c76de365a6c11a27939639227722cc0dda9afc1305c79e9631065caeab`. All 479 entries (438 files) passed CRC, duplicate/case-collision, traversal and symlink checks. Bounded credential signatures found no match. No ZIP-provided script was executed.

The normalized frontend comparison reproduces 38 shared paths, 28 equivalent, 10 different, with nine new TS/TSX files. Four changed views and nine new interaction/relative-time files were reviewed individually; four new test/helper files were adapted. The 263-copy nested baseline subtree, duplicate Python, artwork and embedded-image storyboard were excluded. The four Builder export-note documents were absent; this report and the exact evidence replace unsupported QA claims.

Ported: Streets counts/reset/empty-state controls; Life relative deadlines and separated money explanations; Story confidence summary; Today counts/deadlines and a separately labelled synthetic interaction demonstration. App adds explicit preview opt-in; Today defaults to no demo. A single legacy Tess role string now matches the repair/cooperative role, while Marlon remains a separate store-owner fixture. Other legacy scenario data remains synthetic reference display, not an authoritative projection; for example, its old work cards are not real Python opportunities.

The new interaction keeps all eight presentation states, native controls, focus management, polite announcements, disabled Confirm, unavailable/missing-data handling and input purity. The undiscovered panel withholds offer detail. Invalid selected IDs and attempts to suppress missing-data errors fail closed. No imported module reaches host/outbox APIs or persistent storage. The accepted local entry graph never imports this preview, and `?engine=live` cannot select live mode.

## Continuity and transport corrections

Opening repair shift terms match `content/neighborhood_life_v1.json`: one-action/$20 work or zero-action decline, one-day exclusive window; no invented two-action shelving work or week-long reservation. IDs are `preview.*`; the shape is daily-life `choose(choice_id, option_id)`, never ordinary-work `ordinary_choose`. Real IDs and eligibility remain Python-issued. The separate late-week audit example is at p032, assumes Tess's reference is known, and is blocked by illustrative standing 1 versus required 2; it is not opening_shift or a Wayne Tower offer.

Refusal is a genuine alternative that can have consequences. A selected, unsent choice may be cancelled. A transmitted/uncertain illustration offers no Cancel or retry; it explains original-request receipt recovery. Confirm is hard-disabled even if a caller attempts to enable it. Confirmed/consequence views explicitly describe hypothetical display, not paid wages or applied standing.

Confidence is not source count: unconfirmed means unverified, without asserting exactly one source. Existing observational/institutional information separation is retained.

## Protected core and validation

Eighty protected host/outbox/session/authentication/CSP/build/tool/Python files remain byte-identical to the new clone's baseline. A normalized SHA regression fixture requires explicit future review before changing them. Existing tests, all Python/content/save formats, lockfile and dependency versions are preserved. Additional import-graph and functional checks cover disabled submissions, uncertain outcomes, missing data, gating, authoritative Tess terms, roles, source count and relative dates.

| Check executed in the new sibling | Result |
| --- | --- |
| Locked offline npm install, lifecycle scripts disabled | PASS |
| Accepted frontend baseline | 176 PASS |
| Full Python regression | 620 run, 619 PASS, 1 SKIP; 230.398 s; exit 0 |
| Final frontend suite | 220 PASS, 0 FAIL/SKIP; exit 0 |
| Frontend typecheck | PASS, exit 0 |
| Preview and local production builds | Both PASS, exit 0 |
| Host packaging / negative publication tests | 8 PASS, exit 0 |
| Source exporter tests | 4 PASS, exit 0 |
| Real installed Edge local inspection | 17 checks PASS; no command/external page requests or CSP errors; synthetic checkpoint byte-identical |
| Real installed Edge synthetic preview | 13 checks PASS under strict CSP, including native Enter/Tab/Escape, all eight states, empty browser storage and no API/host requests |

The full Python run includes bridge HTTP/host, persistence, replay, migration, exactly-once and security tests; it ran before UI edits, and all Python/content/test bytes remain unchanged. No Python test result is inferred from a mock frontend. The new local bundle hash changes because Tailwind discovers additional classes; source CSS, host release constant and pin policy are unchanged. New test-only candidate pin: `d1e28057e379ffeb9271de6e58b627cdd46521c2894c38bf428b3cca7d0b6121`. It is not production approval.

The first port suite had 219 PASS / 1 FAIL because the new graph-test helper rejected the existing `react-dom/client` entry import; permitting the existing React entry and CSS import corrected the test, not production code. The first preview browser run timed out on Enter because the new CDP harness omitted the Enter text event; adding its carriage-return text fixed native keyboard dispatch. Original failure logs are retained and not counted as passes. The initial PowerShell edit stopped at a Unicode literal mismatch before the substantive scenario replacement; explicit Unicode escapes completed the intended edits, and the existing encoding regression passes.

Screenshots of both final surfaces were visually inspected: the preview labels/terms and read-only authenticated inspection are readable, with no inline-style/CSP regression. Browser profile/checkpoint bytes are private ignored test data, not source or evidence payloads. Only selected synthetic screenshots and sanitized network/check results are exported.

## Reproduce and remaining limits

From `frontend`: `npm ci --offline --ignore-scripts --no-audit --no-fund`, `npm run typecheck`, `npm test`, `npm run build`, `npm run build:local`, `npm run package:local`. An offline install on another machine requires its locked packages already cached.

From root: `python -B -m unittest discover -s tests -v`, `python -B frontend/tools/test_package_host.py`, `python -B frontend/tools/test_package_source.py`. Run `node frontend/tools/preview_smoke.mjs` after the preview build; run `node frontend/tools/browser_smoke.mjs <actual-candidate-manifest-sha256>` after the local build/package. Installed Edge is used with separate disposable profiles, no browser download or authentication bypass. Use `GOON_BROWSER` only for another explicitly installed Chromium executable.

The real Windows file-symlink test remains SKIPPED/BLOCKED by WinError 1314; it is not a pass. Other browser engines, owner-visible manual playtesting, a full accessibility audit and production pin approval remain outstanding. No online dependency-advisory audit is claimed; dependencies did not change. Godot sources were never accessed or changed; no independent before/after Godot hash inventory is available.

No browser gameplay, P1W command wiring, GTG-13B/14/15, new economy/rules, save migration, Godot modifications or Freebuff work was implemented. The future live adapter cannot reuse synthetic IDs or treat selection cancellation as receipt recovery. Accepted and original checkouts remain preserved; do not overlay them or cherry-pick into the dirty original. Review this isolated commit and sanitized artifacts first; any later integration must recheck saved original edits and reconcile them losslessly in an approved sibling. No push, PR, merge or deployment is authorized here.

## Final extraction verification

The clean extraction repeated all 220 frontend tests, typecheck, both builds, candidate packaging and 8 + 4 packaging/export tests successfully. Its first comparison found one extra `.inline` CSS rule because the report was added after the original build and the unchanged Tailwind scanner includes documentation. Final builds and browser checks must run after documentation; exact comparison evidence is supplied separately. This is build-input freshness, not an engine or source-authority change. The first source-export invocation used a relative path with `..` and was rejected before writing output by the unchanged path guard; the explicit absolute review path succeeded.

The nested Builder subtree has 263 files; 262 correspond to versioned accepted files after line-ending normalization. Its additional `SOURCE_REVIEW_MANIFEST.json` is archive metadata, absent from a Git checkout. None was imported. The final deliverable manifest, not that embedded archive metadata, defines the new source payload.
