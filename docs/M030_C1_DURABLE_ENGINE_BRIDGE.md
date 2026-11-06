# Mission 030-C1 — durable offline engine bridge

Implemented November 6, 2026 from clean master
`50a11f18046bccbb379a843ebb52364e7045b936` on
`feature/m030-c1-durable-engine-bridge`. Baseline: **522 tests passed in 159.535s**.
No React, frontend assets, deployment, gameplay content or engine save-schema
changes accompany this foundation. No original historical save is rewritten.

## Modules and authority

| Module | Responsibility |
| --- | --- |
| [bridge_checkpoint.py](../bridge_checkpoint.py) | Strict JSON/requests, checkpoint and source-backed receipt validation, OS writer lock, backup and atomic publication |
| [engine_bridge.py](../engine_bridge.py) | Private candidates, revision checks, deduplication, uncertain-outcome recovery, local import/export and engine quotes |
| [bridge_projection.py](../bridge_projection.py) | Explicit player-safe fields; no snapshots or raw command events |
| [bridge_http.py](../bridge_http.py) | Loopback-only standard-library JSON API and operator launcher |
| [engine tests](../tests/test_engine_bridge.py) | Real effects, faults, process crashes, historical imports and replay |
| [HTTP tests](../tests/test_bridge_http.py) | Actual loopback requests, hostile inputs, lost acknowledgment and restart |

All gameplay changes still enter [execute_command](../game_service.py#L92).
Existing service, navigation, life, RNG and persistence modules are unchanged.
The bridge never consults frontend fixtures or TypeScript navigation.

## Operator lifecycle

The separate [C1.3 browser-host contract](M030_C1_3_BROWSER_HOST.md) adds opt-in
verified assets and a one-time browser authorization exchange. The headless
launcher and protocol described here retain their existing behavior. C1.3's new
bootstrap endpoint is the explicit exception to the original no-endpoint
capability-return rule; it is not a new gameplay mutation boundary.

Use an existing private data directory outside the repository. Paths below are
placeholders; parent directories must already exist.

```powershell
python -B bridge_http.py --checkpoint "C:\private-data\career.bridge.json" --new --seed 42
python -B bridge_http.py --checkpoint "C:\private-data\career.bridge.json"
python -B bridge_http.py --checkpoint "C:\private-data\imported.bridge.json" --import-save "C:\private-data\historical.json"
python -B bridge_http.py --checkpoint "C:\private-data\career.bridge.json" --export-save "C:\private-data\exported.json"
```

Creation and import are exclusive. Resume never ticks, moves, enrolls or refreshes
allowances. Import uses the existing validated loader/preparation on a copy;
export writes a new ordinary engine JSON via existing persistence with
`overwrite=False`, then exits without HTTP. These file operations are local Python/
operator APIs only. An envelope is not an ordinary engine save and must not be
passed to the legacy loader. Inner engine schema/version and historical opt-in
behavior remain unchanged.
Import/export paths cannot alias the checkpoint, its future backup or lock;
otherwise a later backup could overwrite an operator's historical/exported file.

The launcher prints an ephemeral `http://127.0.0.1:PORT` and a private capability.
No UI is served. The capability is never saved or returned by an endpoint and
rotates on restart; career/operation identities do not. Keep the console private.
The `.lock` sidecar holds an OS advisory lock for the session. The handle, not
file existence, owns the lock; do not unlink live lock files. OS release after
process death is tested. Locks do not fence deliberately copied/edited files.

## Protocol version 1

| Method and exact path | Purpose |
| --- | --- |
| `GET /api/v1/state` | Current identity/revision, allowed commands and safe state |
| `POST /api/v1/commands` | Exact command envelope; committed receipt acknowledges save |
| `GET /api/v1/operations/{request_id}` | Original receipt plus current state, or `operation_status: not_found` with null receipt |
| `POST /api/v1/travel-quotes` | Exact fields `protocol_version`, `destination`, `mode`; read-only Python quote with actual execution command/arguments |

```json
{
  "protocol_version": 1,
  "career_id": "FROM_STATE",
  "lineage_id": "FROM_STATE",
  "request_id": "intent-4",
  "expected_revision": 3,
  "command": "choose",
  "arguments": {"choice_id": "goon.choice.0.opening_shift", "option_id": "work"}
}
```

Only these seven request fields are accepted. Versions/revisions are actual
integers, not booleans. Identifiers are 1–128 letters/digits/periods/underscores/
hyphens and begin with a letter/digit. Argument names must exactly match the
existing command registry and values must be strings of at most 256 characters.
Costs, money, locations-as-state and replacement worlds cannot be supplied.

The C1 allowlist is `settle_in`, `wait`, `choose`, `pay_room`, `travel`,
`enable_navigation`, `enable_mobility`, `journey`, `enable_ordinary`,
`ordinary_choose`. No future engine command is automatically exposed.

Success includes protocol/career/lineage, current revision, allowed commands,
`duplicate`, safe `state` and this receipt shape:

```json
{"request_id":"intent-4","revision":4,"command_sequence":4,"command":"choose","day":1,"status":"committed"}
```

`committed` is the durable save acknowledgment; no separate save endpoint exists.
A duplicate returns the original receipt with `duplicate: true`; accompanying
state is current and may be newer. Existing-ID lookup precedes revision checking;
different contents under a committed ID fail `REQUEST_ID_REUSED`, while a new
stale intent fails `STALE_REVISION`. Committed commands reserve IDs. Rejections
create no receipt or disk/gameplay/RNG change; use a new ID after rejection.
For an uncertain operation preserve its exact original request for recovery.

Errors are `{protocol_version, error: {code, message}}`: 400 malformed input;
401 unauthorized; 403 unsafe Host/Origin; 404 absent route; 405 unsupported method;
409 version/identity/revision conflict; 413 oversized body; 415 content type;
422 ineligible command/route; 503 uncertain publication/recovery. Unexpected
failures return generic 500, never raw engine diagnostics, paths or tracebacks.

## Checkpoint version 1

The exact eight root fields are `bridge_version`, `career_id`, `lineage_id`,
`revision`, `base_sequence`, `world`, `world_hash`, `operations`. The inner world
is an unchanged prepared engine save, validated by the existing contract.
`world_hash` is SHA-256 of UTF-8 JSON with sorted keys, compact separators and
non-finite values forbidden. Unsupported versions/extra bridge fields fail.

`base_sequence` records the imported engine command sequence; bridge revision
starts at zero. Engine sequence must equal base plus revision. Operations are an
ordered list of `{request, digest, receipt}`; digests use the same canonical JSON.
Validation requires unique IDs, contiguous revisions, matching identity/lineage,
exact receipt fields and matching actual engine `player_command` arguments/day.
Bridge-owned command frames must be in sequence order, belong to the player and
use the real fixed action cost where the engine registry defines one. Historical
frames before import are preserved without inventing missing history.
Validation remains active under `python -O`. Hashes detect inconsistency, not
hostile local forgery; receipts are transport metadata, not parallel world history.

Under a session mutex: check identity/dedup/revision; refuse external checkpoint
replacement; execute on a private candidate through the game service; build its
receipt and safe response; validate the full candidate checkpoint; stage/fsync;
back up the previous valid checkpoint; atomically replace primary; only then
publish as live state and acknowledge. World and receipt share one replacement.
Initial publication is exclusive and requires hard-link support, like existing
engine exclusive saves. POSIX directory synchronization is included. Windows uses
staged file flush and filesystem replacement; physical power-loss guarantees for
all storage hardware/filesystems are not claimed.

## Uncertain outcomes and recovery

Publication exceptions conservatively quarantine the session with
`OUTCOME_UNKNOWN`; they do not imply failed gameplay. Further commands are blocked
until a state/operation recovery read validates primary against the previous or
attempted checkpoint hash. Recovery does not execute a command or write a save.

- Previous checkpoint: operation is `not_found`; a deliberate exact retry at the
  original revision may execute once.
- Attempted checkpoint: world and committed receipt recover together; retry
  returns the receipt without repeating effects.
- Unreadable, malformed, missing or unexpectedly different primary: recovery
  remains `OUTCOME_UNKNOWN`; no automatic backup rewind or blind retry.

Restart validates primary under the OS lock without replaying operations. A
corrupt primary requires operator recovery. Restoring an older backup is an
explicit timeline rollback outside ordinary retry guarantees. Export/import
creates fresh identities/lineage. Accepted request identities are retained
without pruning. Abrupt exits can leave orphan temporary files; they are ignored
and never interpreted as committed checkpoints. No broad automatic cleanup runs.

## Knowledge and security boundaries

Projection selects personal cash/heat/custody, day, authoritative budget constants,
remaining actions/TU, current place label, independent navigation/mobility/life/
ordinary adoption states, own housing, Tess/Cal identity/role/standing, visible
assessed life/ordinary options and the last ten personal life-choice outcomes.
Options identify their actual command and arguments. No raw events, world seed,
faction strategy, people dictionary, NPC memories, incident identities/truth,
institution queues or arbitrary extension fields are exposed. Known incident/
institution narratives are deliberately also omitted in C1. No developer toggle
changes this scope. Quotes use engine navigation/mobility and omit graph/debug
data; active mobility returns the existing `journey`/quote-token arguments.

The server binds only 127.0.0.1, with exact Host and a Bearer session capability
required for every parsed API request, including unsupported methods. Supplied
Origin must match; POST must include Origin.
GET may omit Origin but still requires authorization. Cross-site Fetch Metadata
is rejected. There is no permissive CORS/preflight or cookie authentication.
POST requires exactly `application/json`, bounded Content-Length and at most
**16,384 bytes**. Duplicate security/framing headers, transfer encodings, duplicate
JSON keys, non-finite numbers and malformed UTF-8 fail. Connections have a five-
second inactivity timeout and at most eight admitted worker slots. API responses
are JSON, no-store/nosniff and disallow framing. URLs, bodies and capabilities
are not logged.
There are no static/source/snapshot/arbitrary-path or HTTP import/export routes.

### HTTP rejection and framing contract — 030-C1.1

A parsed request is authorized before method dispatch. `TRACE`, `CONNECT`, `PUT`,
`PATCH`, `DELETE`, `OPTIONS`, `HEAD` and unknown methods cannot execute commands.
Authorized unsupported methods receive `405 METHOD_NOT_ALLOWED`, the same JSON
security headers as API responses and `Allow: GET, POST`. `HEAD` has no response
body, as required by HTTP. Missing capabilities and unsafe Host/Origin/Fetch
Metadata still receive their normal 401/403 errors. No CORS permission is added.

Policy rejection sends the error before draining incoming bytes, flushes it and
half-closes the socket's write side. It then discards (never parses) at most
16,384 additional bytes for at most **0.2 seconds**, using an absolute deadline.
This does not rely on a rejected Content-Length and accommodates buffered/split
body arrival without waiting indefinitely. Client disconnects during socket
teardown do not change gameplay or operation receipts. Handler/programming
exceptions are not converted into successful rejection tests.

Complete, bounded requests rejected for policy reasons are expected to receive
the structured response. Malformed/missing/negative Content-Length, truncated
bodies, excessive trailing data, clients that keep sending past the drain budget,
and peer aborts may instead end in EOF/reset. No JSON acknowledgment is guaranteed
for those malformed or excessive streams. A rejected request never reaches the
game service. Error recovery must not infer a command's outcome from a connection
reset; use the existing operation-ID recovery protocol for uncertain commands.

HTTP Content-Length delimits the body. Bytes beyond that length are not part of
the declared JSON body, and this single-request connection never executes them as
a second request. An invalid declared JSON body plus extra bytes is rejected. A
valid declared command can execute once even if the peer appends excess bytes;
later bytes cannot retroactively invalidate it. Detecting arbitrary future bytes
before execution is not a transport guarantee. The 16,384-byte parse limit is
unchanged.

Failures in the standard-library HTTP parser (bad request syntax/version or header
limits) happen before API authorization/dispatch and remain standard-library
errors, which can be HTML or connection termination rather than the API JSON
envelope. They cannot execute commands. Security-header/JSON guarantees above
apply to API responses, not those parser failures.

## Validation and gameplay evidence

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'
python -B -m unittest discover -s tests -p '*bridge*.py'
python -B -m unittest discover -s tests
```

The focused run passed **44 tests in 37.502s**; the final shared path-guard change
also passed its targeted exclusive-creation/export regression. Coverage includes actual HTTP,
capability rotation, conflicting requests, forged inputs, wages/waits, partial
handler failures, legacy preservation/export, true two-action home work and
pending/active mobility. Two subprocesses use `os._exit` immediately before and
after primary replacement; fresh processes recover the correct checkpoint and
receipt. A real HTTP client closes without reading acknowledgment and recovers
the original receipt. Other faults cover staging, flush, backup, final replacement,
unreadable recovery and malformed metadata. All test files are temporary.

Final complete regression on the finalized implementation: **566 tests passed in
538.975s**, comprising all 522 unchanged baseline tests plus 44 new acceptance
tests. No GitHub CI, publication, React test or deployment result is claimed.

Seeds 17 and 93 run thirty days with checkpoint reopen/duplicate submission each
day; inner worlds equal direct engine replay after every transition. Tess's
repair world retains the 030-B frozen hash:
`c0f74312014e5cd2dbc930493d2cee61936f8e459096250400a03672cc1cc352`.
Imports cover root M001–M013 fixtures, M014 navigation, M015 life and M018 incidents;
original bytes remain unchanged and optional systems are not silently adopted.

A separate actual CLI smoke run created a temporary career, executed Tess's repair
over HTTP, terminated/restarted the test-owned server, recovered and retried the
same paid request, and exported a legacy save. Cash remained $60, two actions and
17 TU remained, the capability rotated, the original receipt was returned and the
exported world retained the frozen hash above. No frontend or real save was used.

Review regressions were demonstrated failing before their repairs: bridge receipt
sources with reordered/non-player commands, and historical source paths colliding
with future backup/lock files. Windows aborted-connection handling was corrected
after actual lost-ack/rejection HTTP testing. No inherited gameplay change was needed.

### 030-C1.1 correction evidence

The independent C1 audit observed one `WinError 10053` during a Content-Length
rejection test, followed by a passing 566-test run. C1.1's unchanged baseline
bridge suite passed **44 tests in 8.294s**; the original intermittent reset was not
reproduced in that run. Inspection established a contributing weakness: draining
preceded the error response, malformed lengths skipped draining, and bounded
`read(n)` could wait for an incomplete body before sending the rejection. The
exact packet timing behind the original reset is not established.

The implementation review read the installed Python 3.14.2 standard-library
`BaseHTTPRequestHandler.handle_one_request`, `parse_request` and `send_error`,
plus `StreamRequestHandler.finish` and `TCPServer.shutdown_request`. The narrow
`do_*` fallback preserves parsing and the existing API dispatcher instead of
copying the standard-library request loop.

Before the repair, new regressions demonstrated inherited HTML errors for TRACE,
CONNECT and unknown methods, and a blocked response when rejection draining was
held pending. After the repair, tests require strict JSON responses for complete
policy rejections; only explicitly malformed/excessive streams permit EOF/reset.
They also cover missing/non-numeric/negative/oversized lengths, actual oversized
data, delayed split bodies, forced socket abort, bounded drain bytes/deadlines,
unsupported-method authorization, parser failures and no extra command execution.

C1.1 focused HTTP tests: **20 passed in 2.586s**. Combined bridge tests:
**53 passed in 9.446s**, including the existing duplicate-request, subprocess
crash/recovery, historical import and two-seed replay regressions. Nine tests
were added. A separate 320-request rejection stress run returned the expected
JSON statuses for all 120 complete policy rejections, 160 malformed-length split
requests and 40 complete oversized requests. No resets or server-handler errors
occurred in that run; checkpoint bytes, projected state and RNG were unchanged.
Final full regression: `python -B -m unittest discover -s tests` passed
**575 tests in 168.344s**, preserving all 566 existing tests plus nine new HTTP
regressions. Only `bridge_http.py`, `tests/test_bridge_http.py` and this contract
changed. Gameplay, navigation, save/checkpoint formats, projections and the
three-action/18-TU budgets are unchanged. No C2, push, PR, merge or deployment was
performed. Parser failures and malformed-stream termination remain the explicit
transport limitations described above; non-Windows behavior remains unverified.
Original C1 results above describe the historical baseline, not a new C1.1 run.

The first real sequence is `settle_in`, explicit `wait`, separately quoted and
authorized travel to p032, then `choose` opening shift/work: $40 → $60, one action,
one TU, Tess standing +1. Decline is free and closes the offer; postponing has no
effect until an explicit transition expires it. These are existing meaningful
choices/consequences; no job, NPC, content variety or grind loop is invented.

## Limits and 030-C2 recommendation

Receipt/history retention, copies and validation cost grow with career length;
no unsafe eviction policy is introduced. Windows is tested; other platforms and
filesystems remain unverified. This is a trusted single-player loopback service,
not an Internet server or sandbox against the local OS owner. Legal/incident UI,
browser bootstrap, assets, React and packaging remain outside C1.

After separate approval, C2 should connect one Today repair interaction: secure
launcher bootstrap, Python-backed provider, engine-supplied options/quotes, one
request ID per intent, no optimistic resource mutations, timeout recovery and
restart persistence. Keep preview fixtures separate and use actual Tess wording;
do not add Marlon/shelf mechanics, TypeScript gameplay authority or UI redesign.
Preserve the distinct home-kit two-action cost and existing budgets. No C2 work,
push, PR, merge or deployment is authorized by this contract.
