# M030-C1.3 — secure local browser host

Implemented from clean `master` at
`1a129e83be6629b7a27c2826626856ec7fae85f7` on
`feature/m030-c1-3-browser-host`. This is Python host infrastructure, not React
gameplay integration. No compiled frontend is shipped or approved by this change.

## Authority and modules

- [bridge_assets.py](../bridge_assets.py): bounded, release-pinned asset loading,
  immutable in-memory responses and restrictive content policy.
- [bridge_bootstrap.py](../bridge_bootstrap.py): process-only authorization codes,
  monotonic expiry, atomic redemption and attempt limits.
- [browser_host.py](../browser_host.py): browser HTTP routes, stable port,
  checkpoint resume, foreground launcher and shutdown.
- [bridge_http.py](../bridge_http.py): two small extension points, an optional
  handler class and a request-body limit parameter. Existing defaults, API routes,
  capabilities and the headless launcher remain unchanged.

All gameplay API traffic delegates to the existing handler and
[Bridge.execute](../engine_bridge.py). World/receipt formats, request digests,
revision checks, command allowlists, player projection, navigation, RNG and
three-action/18-TU budgets are unchanged. Neither assets nor authorization
exchange reads or advances the world. Host expiry uses monotonic wall time only;
it is not a simulation clock.

## Trusted distribution and release pin

The launcher serves only:

```text
<directory containing browser_host.py>/ui_dist/<bundle-id>/public/
```

The manifest is the sibling `ui_dist/<bundle-id>/manifest.json`, outside the
served directory. There is no HTTP or CLI arbitrary asset-root option. Bundle IDs
contain 1–64 ASCII letters/digits/underscores/hyphens and begin with a letter/digit.
An operator supplies an independently trusted manifest SHA-256. Computing a hash
from an unreviewed archive is not evidence that its contents are safe.

Exact manifest fields:

```json
{
  "asset_manifest_version": 1,
  "host_protocol_version": 1,
  "bridge_protocol_version": 1,
  "engine_release": "1a129e83be6629b7a27c2826626856ec7fae85f7",
  "bundle_id": "approved-build",
  "mode": "local_engine",
  "files": [
    {
      "path": "index.html",
      "size": 123,
      "sha256": "REPLACE_WITH_THE_ACTUAL_64_CHARACTER_SHA256",
      "mime": "text/html; charset=utf-8"
    }
  ]
}
```

The example is a schema illustration, not an installable bundle. Each real file
requires its exact byte size/hash. Version fields are integers, not booleans.
`engine_release` identifies the unchanged engine compatibility baseline; the
runtime does not need Git. A release update must deliberately review this pin.

Rules enforced before checkpoint opening or browser launch:

- At most 64 KiB of manifest JSON, 256 files and 64 MiB of total file bytes.
- `index.html` is mandatory and at most 256 KiB. Other files are at most 8 MiB.
- All other files must have flat `assets/<filename>` paths. Supported suffixes:
  `.js`, `.css`, `.woff2`, `.png`, `.jpg`, `.webp`, `.ico`. MIME must exactly match
  the module's explicit table. HTML is allowed only as `index.html`.
- Reject extra manifest fields, duplicate JSON keys, duplicate files, unsupported
  versions/modes, wrong release identity, missing files, incorrect hashes/sizes,
  unlisted public files, nested asset directories, links and reparse points.
- Index script/link/image/source resource URLs must resolve to manifest entries.
  Source-only `/src/main.tsx`, external resources, inline scripts/styles,
  event-handler attributes, base tags and iframes fail index validation.
- Asset bytes are preloaded and immutable; HTTP requests never open paths.

No directory listings, SPA fallback, source maps, Python files, saves, ZIPs,
documentation or design/reference directories are served. `GET /index.html` is
not an alias for `/`. HTTP paths with queries, percent encoding, backslashes,
control characters or non-manifest paths fail. Standard-library parser
normalization still occurs before dispatch.

Only a trusted, reviewed bundle can be pinned. Text checks reject Court of Owls
and Talon references, but cannot prove that opaque images or constructed strings
contain no restricted material. Exclude all authoring/reference images and
documents; inspect the actual compiled artifact before approval. HTML validation
is not a JavaScript/CSS import-graph analyzer or proof of React compatibility.

Every asset uses `Cache-Control: no-store`, `nosniff`, `Referrer-Policy:
no-referrer`, same-origin resource/opener policies and this CSP:

```text
default-src 'none'; script-src 'self'; style-src 'self'; font-src 'self';
img-src 'self'; connect-src 'self'; base-uri 'none'; object-src 'none';
frame-ancestors 'none'; form-action 'none'; worker-src 'none'
```

No remote fonts, CDNs, inline-style exception, permissive CORS or service worker
is introduced. Binary file signatures and all possible generated runtime content
are not independently authenticated; trust comes from the approved release pin.

## Routes and schemas

| Method/path | Authentication | Result |
| --- | --- | --- |
| `GET /` | Exact host/context | Verified index bytes |
| `GET /assets/<manifest filename>` | Exact host/context | Verified asset bytes |
| `POST /host/v1/bootstrap` | Exact same-origin plus one-time code | Capability and session metadata |
| `GET /host/v1/session` | Existing Bearer capability | Session metadata, no capability |
| Existing `/api/v1/...` routes | Existing C1 authentication | Existing protocol-1 behavior |

Host/context validation rejects duplicate security headers, Host aliases,
foreign/null Origin, cross-site Fetch Metadata and Transfer-Encoding. POST
requires Origin. GET may omit Origin. `X-Forwarded-*` is never trusted.
Numeric `127.0.0.1:PORT` is the only accepted authority. Simulated rebinding with
an attacker hostname fails even when the TCP connection goes to loopback.

Bootstrap accepts exactly these fields in at most 1,024 bytes:

```json
{"host_protocol_version":1,"bundle_id":"approved-build","code":"OPERATOR_CODE"}
```

A successful response has exactly:

```text
host_protocol_version, bridge_protocol_version, bundle_id, manifest_sha256,
engine_release, instance_id, mode, session_lifetime, capability
```

Session inspection returns the same metadata without `capability`.
`session_lifetime` is `process`; `mode` is `local_engine`. These are compatibility
declarations, not proof that an untested frontend correctly renders live state.

Codes use 32 cryptographically random bytes, expire at 120 seconds and are consumed
under one lock. Issuing a new code invalidates the old one. Invalid, expired,
closed and reused codes receive the same 401 denial. At most ten redemption
attempts (including successful attempts) are admitted per rolling 60 seconds;
further attempts receive 429. Reissuing a code does not reset this limit. The
limit is process-global, not a user-account system; local denial of service is
still possible. Invalid host/origin/schema requests do not consume a code.

Host errors contain `host_protocol_version` and a generic `error` object. Existing
gameplay API error envelopes are unchanged. Unsupported host methods require the
capability and receive JSON 405 with the inherited security headers. Wrong
methods at exact bootstrap/session paths receive 405. No CORS preflight is enabled.
Malformed parser failures retain the C1.1 standard-library behavior. Request-body
rejections reuse its bounded teardown; JSON is not guaranteed after malformed or
excessive streams and peer aborts.

The bearer credential is returned only by successful bootstrap, never in URLs,
assets, log output, host configuration or checkpoints. HTTP logging remains off.
The one-time code is deliberately printed to the private operator console.
Extensions, local malware, hostile local administrators and a compromised trusted
bundle are not isolated by this loopback host.

## Operator lifecycle

First create or explicitly import a bridge career with the existing operator
tools. The browser host only resumes an existing valid bridge checkpoint; it
does not accept ordinary engine JSON or automatically import/adopt a career.

After installing an independently approved compiled bundle:

```powershell
python -B browser_host.py --checkpoint "C:\private-data\career.bridge.json" --bundle-id approved-build --manifest-sha256 TRUSTED_RELEASE_MANIFEST_SHA256
```

`--no-browser` suppresses browser launch; the URL is still printed. The browser
must provide a pairing screen and live provider in a separately approved task.
This mission does not supply either UI. Node/npm are not needed to run the host.

Default host configuration is `%LOCALAPPDATA%\GothamTheGoon\browser-host.json`
(or the user's `.local/share` fallback). `--host-config` is an operator-only
override, never an HTTP argument. It must be separate from checkpoint/backup/lock
paths. Its exact schema is `{"host_config_version":1,"port":PORT}`.

A short OS lock serializes config initialization. First launch binds an available
port and publishes the config exclusively using staged/flushed bytes. Later
launches reuse that exact port; invalid config or collision fails without trying
another port. Windows listeners use exclusive address ownership, so a second
listener using SO_REUSEADDR cannot join them. Configuration contains no secrets.
Do not delete or change it while browser pending intents need the old origin.
Config deletion cannot be distinguished from a first installation; loss of that
file can strand origin-scoped browser storage. Physical power-loss guarantees
remain limited by the filesystem, as with existing C1 saves.

Startup order: validate bundle, reserve/configure listener, open existing career,
start HTTP, issue code, then optionally open the credential-free URL. A browser
GET cannot create or adopt a career. Enter in the foreground terminal issues a
fresh code; `quit`, EOF or Ctrl+C stops the host. The console must remain open.
Shutdown revokes bootstrap, rotates the in-memory capability, stops the listener
and waits for an already-authorized engine transaction before releasing its lock.
Restart rotates credentials/instance identity while preserving career, lineage,
port, revision and receipts. There is no HTTP shutdown or filesystem endpoint.

## GTG-13 handoff and blocked acceptance

The frontend still needs an approved pairing screen, same-origin Bearer client,
host/session version check and persistent exact-request outbox. It must recover
uncertain commands by original operation ID, not infer failure from transport
errors. Capability expiry must preserve pending intents; reauthorization is not a
new gameplay intent. No outbox or browser sessionStorage implementation is added
here. Multiple HTTP clients are serialized/revision-checked by the existing bridge;
real browser tab coordination is a later acceptance gate.

Use the actual Python projection and quote arguments. Reconcile the provisional
GTG-12 option/receipt/route shapes; do not fabricate institution/incident data,
reuse fixture eligibility, implement TypeScript navigation authority, silently
adopt systems, travel or wait, or introduce another save operation. A committed
receipt already acknowledges durable publication. The current preview must not
fall back into a purported live career on connection failure.

| Acceptance | Status |
| --- | --- |
| Synthetic pinned files and real loopback HTTP | Tested; see validation below |
| Windows directory-junction rejection | Tested with an actual junction |
| Direct file-symlink creation/rejection | BLOCKED by Windows privilege (WinError 1314); test skipped |
| Lstat/reparse-point refusal | Tested independently of symlink-creation privilege |
| Actual compiled React distribution/CSP/import graph | BLOCKED: no approved compiled bundle |
| Browser pairing, reload, IndexedDB and multiple tabs | BLOCKED: no live frontend integration authorized |
| Real browser DNS rebinding/CSRF behavior | BLOCKED: only server-side header simulations executed |
| Windows Firewall prompt/packaged offline browser smoke | BLOCKED: not executed |
| Non-Windows filesystem/socket behavior | BLOCKED: not executed |

The source export's inline budget-meter style, wildcard Builder theme messaging,
preview fixture fallback and raw TypeScript route quoting need reconciliation in
the separate local build. SVG/public authoring files are not automatically allowed
by this host. No Builder tasks are marked unblocked by infrastructure tests.

## Validation evidence

Baseline bridge suite: **53 passed in 16.081s** before implementation. Focused host
suite: **42 run in 4.097s; 41 passed, one BLOCKED/skipped**. Tests use synthetic
assets and temporary careers; they do not establish browser compatibility.

Executed coverage includes trusted pins, corrupt/missing assets, manifest/HTML
compatibility, path/source/reference exclusions, strict headers/origins, code
expiry/rate limits/concurrent reuse, port collision/reuse, configuration faults,
secret-free launch URLs, explicit legacy import, read-only inspection and existing
command mutation through the host.

A separate 150-request stress run returned the expected results for 60 asset
GETs, 30 foreign-origin bootstrap attempts and 60 unauthorized engine/session
GETs, with no handler errors or checkpoint/RNG changes. Late startup failure
after opening a career is also fault-injected; the listener and career lock are
released without changing the checkpoint.

A child host process commits a wait whose HTTP acknowledgment is discarded,
exits with `os._exit`, then a fresh process reopens the same port/checkpoint. A new
code authorizes recovery of the original receipt; retry keeps day at one. This is
a real process test, not a browser reload claim.

The HTTP Tess opening shift matches direct Python replay after every command:
$60 cash, two remaining actions, 17 TU and Tess standing +1. Its quote uses the
canonical `goon.poi.p032` argument and produces world hash
`61c395ac64c42ac603a5dddf24010db343db2c8620e5654c8122707639645718`.
The historical C1 frozen replay uses the `p032` alias; preserving that distinct
recorded command argument preserves its existing `c0f743...` hash. No event history
was normalized or rewritten to force the hashes to match.

Final full regression: `python -B -m unittest discover -s tests` ran **617 tests
in 171.059s: 616 passed, one BLOCKED/skipped**. All 575 existing tests, including
the original C1 HTTP tests, replay, checkpoint publication, receipt recovery and
historical-save regressions, passed. The 42 new host tests contribute 41 passes
and the explicitly blocked OS file-symlink acceptance item.

Review verified no changes to `game_service.py`, career/save schemas,
`bridge_checkpoint.py`, `engine_bridge.py`, `bridge_projection.py`, navigation,
mobility, gameplay content or the frontend export. Python syntax, documentation
links and diff whitespace checks passed. No dependency was installed, no React
build or browser-gameplay test was run, and nothing was pushed, merged or deployed.
