# SIEVE v0.1 limits

- FlawedBench proves regression behavior against known synthetic defects; it
  does not establish ≥85% recall or ≤10% false-finding rate on external
  benchmark distributions.
- FP is a lower bound over the mutation library. Unknown exploits are not in
  its denominator. The report labels this explicitly.
- Correct variants and label review are declared by a suite author. SIEVE
  cannot prove semantic correctness when no trusted oracle exists; such
  evidence is `UNDETERMINED` or tiered as declarative.
- The trust-adjusted score is a transparent sensitivity band, not a
  confidence interval or de-biased estimator. It uses fractions of tasks
  affected by FP, FN, and validity findings.
- The TERRARIUM adapter performs a static audit of the vendored task format.
  It does not execute the simulated world or validate an oracle trajectory
  against a live TERRARIUM installation.
- LLM-generated probes are not implemented. All shipped probes are local and
  scripted, so demo cost is $0 and model-call count is zero.
- `sieve audit --changed` and automatic git diff discovery are not
  implemented; CI can invoke `sieve audit` on an explicitly selected suite.
- Fleet/simulation mode, policy/environment/grader partitioning, clustering,
  coverage, and GPU notebooks are P1/v1 and absent.
- No real public benchmark has been audited or disclosed. The launch
  measurement, maintainer coordination, external CI integrations, and public
  gallery remain external work and must not be claimed from this repository.
- FlawedBench has 20 tasks but only one canonical seed of most defect classes;
  it cannot by itself support a class-wise recall confidence claim.
- The local HTTP service executes audits synchronously in one process. It has
  durable SQLite evidence and concurrent request handling, but not a
  distributed queue, cancellation, admission control beyond budget/body
  limits, multi-node coordination, or retention policies.
- The service deliberately has no application-owned identity, authorization,
  or TLS. It binds to loopback by default and refuses a remote bind unless the
  operator explicitly opts in. Remote deployment requires an authenticated
  reverse proxy and a threat model.
- The configured Pages origin can call the loopback service through an exact
  CORS allowlist. Browser private-network and mixed-content policies vary; the
  CLI and HTTP API remain the authoritative integration surfaces when a
  browser blocks that connection.
- SQLite run storage is append-only through the API, but automated backup,
  encryption at rest, deletion/retention workflows, and external object
  storage are not implemented.

The demo has no skipped probes at budget 200 and therefore an abstention rate
of 0%. Lower budgets report skipped probes and a non-zero `UNDETERMINED` rate.
