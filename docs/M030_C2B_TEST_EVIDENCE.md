# M030-C2B test evidence - 2026-11-19

Commands, working directories, elapsed times, exit codes and original logs are retained in the separate sanitized review evidence. No Python runtime or gameplay source was changed, so the completed full Python run applies to the final candidate after hash comparison.

| Check | Result | Exit |
| --- | --- | --- |
| Full Python regression | 620 run in 499.633 s: 619 PASS, 1 SKIP | 0 |
| Clean-extraction Python bridge/HTTP/browser-host suite | 98 run in 16.218 s: 97 PASS, same 1 SKIP | 0 |
| Offline npm installation | 177 locked packages, lifecycle scripts disabled; no dependency download required on this machine | 0 |
| Frontend typecheck | PASS | 0 |
| Baseline frontend before repairs | 161 PASS | 0 |
| Final frontend including committed-recovery repair | 173 PASS, 0 FAIL/SKIP | 0 |
| Preview and local production builds | PASS | 0 |
| Host package negative/integration tests | 8 PASS | 0 |
| Safe source exporter tests | 4 PASS | 0 |
| Real headless Edge smoke | 17 checks PASS; exact checkpoint bytes unchanged; zero command requests, external page requests or CSP errors | 0 |
| Clean extraction builds | Byte-identical preview/local asset files and candidate manifest to worktree | 0 |

The source exporter retains five vetted, committed synthetic migration fixtures. It excludes real player saves, browser profiles, generated distributions, caches and the unaudited nested reference ZIP. The final source ZIP has its own SHA-256 and per-file manifest; extraction and build verification records are supplied alongside it.

## Failure classification

- Before initial repairs: targeted frontend run 51 cases, 41 PASS / 10 FAIL. After those repairs, all 51 passed. Later malformed-schema and committed-recovery cases raise the final full suite to 173.
- Invalid candidate publication failed before repair; the repaired eight-case package suite passes. Its initial failing run inherited duplicate test methods (15 executed); that harness duplication was removed rather than counted as extra coverage.
- Final source review reproduced one more failure: a known committed intent could be replayed after repeated missing-operation responses. The final suite includes the passing regression for this repair.
- The Python SKIP is the actual file-symlink rejection test: Windows cannot create the test symlink without privilege (WinError 1314). It remains BLOCKED acceptance, not PASS. Existing real junction and mocked reparse checks execute separately.
- Restricted Git cloning failed with a Windows signal-pipe permission error. An authorized normal-permission local clone succeeded. The November 19 missing-object issue was repaired from the existing verified backup and Git connectivity rechecked; no source reset occurred.
- A source-export signature matched part of a hyphenated design word. Review established it was inside a word; the token-boundary correction and real-key rejection tests both pass. The first draft export also omitted required synthetic fixtures and the `.mjs` smoke script; the conservative allowlist was corrected before clean extraction.
- No remaining observed test failure is certified as passing. Independent review, owner-visible playtesting, Firefox/Safari and a full accessibility audit were not performed. No live gameplay-browser E2E is claimed because command UI is intentionally disabled.

## Reproduce

From repository root: `python -B -m unittest discover -s tests -v`.

From `frontend`: `npm ci --offline --ignore-scripts --no-audit --no-fund`, `npm run typecheck`, `npm test`, `npm run build`, `npm run build:local`, `npm run package:local`. Offline installation requires the dependencies already cached; after installation, the game host and built frontend require no network service.

From root: `python -B frontend/tools/test_package_host.py` and `python -B frontend/tools/test_package_source.py`. For browser smoke, run `node frontend/tools/browser_smoke.mjs <candidate-manifest-sha256>` with installed Edge (or `GOON_BROWSER` pointing to compatible Chromium). The harness explicitly creates a disposable synthetic career and profile under ignored `.integration`; its candidate pin is test-only and is not release approval. Never include that directory in a source handoff.

For an owner-run existing career, follow `M030_C1_3_BROWSER_HOST.md`: select the existing checkpoint and host config explicitly, independently review the generated bundle pin, then launch `browser_host.py` with `--checkpoint`, `--bundle-id goon-c2b-inspection-v1`, and `--manifest-sha256`. Pair using the console code. Inspect/refresh only: this milestone offers no choose/travel/wait buttons. The source ZIP contains no personal checkpoint and never silently creates one.

Final extraction verification repeated the full 173-case frontend suite, both production builds, 98-case Python security suite (97 pass, one platform skip), and 8 + 4 packaging tests. All completed with exit 0. All production asset files and the host manifest were byte-identical. Subsequent changes were documentation formatting and source manifests only.
