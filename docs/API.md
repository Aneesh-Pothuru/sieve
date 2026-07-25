# SIEVE local service API

The service is a keyless, local execution surface over the same auditor used
by `sieve audit`. It is not a mock server. Every accepted request loads a suite,
runs the real probe battery, computes Wilson intervals and the trust-adjusted
sensitivity band, and commits an immutable evidence envelope to SQLite before
returning `201 Created`.

## Start and verify

```bash
sieve serve
curl --fail http://127.0.0.1:8765/healthz
curl --fail http://127.0.0.1:8765/readyz
```

Liveness does not touch dependencies. Readiness checks SQLite write locking,
the configured data root, and the packaged FlawedBench fixture.

## Run an audit

```bash
curl --fail-with-body \
  -H 'Content-Type: application/json' \
  -H 'X-Request-ID: eval-review-42' \
  -d '{
    "suite": "flawedbench",
    "budget": 200,
    "reported_score": 0.8
  }' \
  http://127.0.0.1:8765/v1/audits
```

Request fields:

| Field | Default | Contract |
| --- | --- | --- |
| `suite` | `flawedbench` | `flawedbench`, `builtin:flawedbench`, or a path inside `SIEVE_DATA_ROOT` |
| `format` | `auto` | `auto`, `local`, or `terrarium` |
| `budget` | `200` | Integer from 0 through `SIEVE_MAX_BUDGET` |
| `reported_score` | `0.8` | Number from 0 through 1 |
| `task` | `null` | Optional exact task ID |

The response includes:

- a stable `run_id`, creation time, normalized request, and complete
  `AuditResult`;
- task-level `PASS`, `FINDING`, or `UNDETERMINED` state;
- exact budget usage and skipped probes;
- findings, secondary verdicts, evidence tiers, and executable reproducers;
- per-task FP/FN Wilson intervals;
- trust-band inputs and output;
- overall `DETERMINED` or `UNDETERMINED` decision status.

## Retrieve evidence

```bash
curl http://127.0.0.1:8765/v1/audits
curl http://127.0.0.1:8765/v1/audits/<run_id>
curl http://127.0.0.1:8765/v1/audits/<run_id>/findings
```

Runs are append-only. Restarting the service does not replace prior runs.
SQLite uses WAL mode, foreign keys, a busy timeout, and separate indexed
finding rows.

## Configuration

| Environment variable | Default |
| --- | --- |
| `SIEVE_HOST` | `127.0.0.1` |
| `SIEVE_PORT` | `8765` |
| `SIEVE_DB` | `work/sieve.sqlite` |
| `SIEVE_DATA_ROOT` | current directory |
| `SIEVE_MAX_BUDGET` | `10000` |
| `SIEVE_MAX_REQUEST_BYTES` | `1048576` |
| `SIEVE_ALLOWED_ORIGINS` | loopback origins and the project Pages origin |
| `SIEVE_ALLOW_REMOTE` | false |

The process refuses a non-loopback bind unless `--allow-remote` or
`SIEVE_ALLOW_REMOTE=1` is explicit. This escape hatch does not add identity,
authorization, or TLS; put an authenticated reverse proxy in front before any
remote use. Suite paths are restricted to `SIEVE_DATA_ROOT`.

## HTTP behavior

- JSON errors have a stable `error.code`, message, and request ID.
- Client `X-Request-ID` values are echoed when syntactically safe.
- Successful creates return a `Location` header.
- Request bodies are size-limited and unknown fields are rejected.
- CORS is exact-origin allowlisted; it is never `*`.
- Health, readiness, configuration, audit, retrieval, list, and finding
  journeys are covered by real HTTP integration tests.

The service is synchronous in v0.1. See `LIMITS.md` for scaling and security
boundaries.
