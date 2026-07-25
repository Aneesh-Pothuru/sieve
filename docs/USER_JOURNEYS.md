# Sieve site user journeys

The site serves four roles with different questions and decision rights. Every
journey begins with an honest explanation of the thesis and ends in either a
pass, a finding with a reproducer, or an explicit undetermined state.

## Shared information architecture

| Surface | User question it answers |
| --- | --- |
| Landing / problem | Why should I test evaluation infrastructure at all? |
| Assurance method | What probes does Sieve run, and in what order? |
| Proof | Does the current implementation find known defects reproducibly? |
| Architecture | What is implemented, what data enters, and what evidence exits? |
| Audit desk | What happens when I configure and run a realistic audit? |
| Task register | Which tasks passed, produced a finding, or remain undetermined? |
| Finding register | Which exceptions could change a benchmark decision? |
| Evidence packet | What exact inputs, observations, evidence tier, and reproducer support a verdict? |
| Calibration | In which direction does the grader fail, and how uncertain is the measured rate? |
| Assurance boundary | What must not be inferred from this run? |

The browser application is a deterministic replay of FlawedBench. It is a
functional interaction model, not a claim that JavaScript is executing the
Python auditor. `sieve audit` and the generated HTML/JSON artifacts are the
authoritative execution path. The benchmark selector also exposes the vendored
Terrarium inbox-triage adapter fixture so users can inspect the separate
one-task static-contract journey; the UI repeats the implementation's explicit
boundary that the Terrarium world is not executed.

The audit desk also offers an explicit **local service** mode. An operator
starts `sieve serve`, checks readiness from the audit desk, and then runs the
same configuration through `POST /v1/audits`. In this mode the interface does
not animate or substitute fixture output: it waits for the actual Python
auditor, hydrates the returned task states/findings/rates, and exports the
persisted API envelope. A failed service call remains visibly failed and never
falls back to replay data.

## Benchmark owner

**Goal:** determine whether a suite is safe to publish or use for a model
decision.

### Primary path

1. Reads the problem and assurance method on the landing page.
2. Opens the audit desk with the canonical FlawedBench configuration.
3. Confirms the declared scope: 20 tasks, manifest oracles, full mutations,
   budget 200.
4. Starts the audit and watches task states, budget, findings, abstentions, and
   the trust band update together.
5. Filters the exception register to critical findings.
6. Opens a finding’s evidence packet and copies its exact reproducer.
7. Exports the structured audit for review or a remediation issue.
8. Runs the reproducer in the Python implementation, fixes or excludes the
   defective task/grader, and re-audits.

### Actual execution path

1. Installs the package and starts the loopback service.
2. Verifies health/readiness and the SQLite/config boundary.
3. Switches the audit desk from fixture replay to local service.
4. Runs the audit and receives an immutable run ID only after persistence.
5. Retrieves the run or its indexed findings through the API after restart.
6. Uses task-level and overall `UNDETERMINED` states to block incomplete
   decisions.

### Pass path

- A task changes from queued to pass only after its configured probe set runs.
- The task inspection view still exposes the oracle, grader mode, planned
  probe counts, and reproducer.
- A pass means “no exception observed under this configuration,” not proof
  that no unknown exploit exists.

### Finding path

- A task changes to finding with a named primary verdict, severity, evidence
  tier, observed detail, lower-bound label when applicable, and reproducer.
- The owner can reach the same evidence packet from the task row or finding
  card.
- The score remains reported separately from the trust-adjusted sensitivity
  band so the owner cannot mistake an audit adjustment for a new point
  estimate.

### Undetermined path

- If budget is exhausted, the partially tested and unstarted tasks are marked
  undetermined and the remaining work is not counted as passing.
- If oracle evidence is withheld, oracle-dependent classifications become
  undetermined while oracle-free probes still run.
- Exit criterion: no consequential benchmark decision until the evidence gap
  is accepted, funded, or resolved.

## Evaluation engineer

**Goal:** calibrate graders and tune the probe plan without hiding uncertainty.

### Primary path

1. Opens the audit desk directly.
2. Uses scenario presets to compare canonical assurance, a constrained budget,
   and missing-oracle review.
3. Adjusts mutation coverage and reads the projected local grader-call count
   before execution.
4. Steps one task at a time while developing or runs the complete audit.
5. Selects a task to compare declared oracle, grader mode, mutation count,
   correct variants, and observed result.
6. Reads the confusion matrix to separate false accepts from false rejects.
7. Reads per-task Wilson intervals with observed counts and the explicit FP
   lower-bound warning.
8. Copies the browser evidence snapshot, then reproduces the selected task
   through `sieve audit flawedbench --task task-XX`.

### Pass path

- Verifies expected acceptance/rejection behavior in the evidence packet.
- Treats the pass as conditional on the chosen mutation library and evidence
  tier.

### Finding path

- Uses the direction of failure to choose remediation:
  - false positive / weak grader → strengthen rejection tests;
  - false negative → add valid variants or repair the grader;
  - unfailable task → make null/refusal/echo behavior score zero;
  - unsolvable task → repair fixture or oracle path;
  - label error candidate → perform trusted human/oracle review.
- Re-runs the single task before the full suite.

### Undetermined path

- Increases budget or restores a trusted oracle.
- Does not interpolate a rate from skipped probes.
- Keeps the evidence-tier and abstention state in the exported audit.

## Governance reviewer

**Goal:** understand whether a model or agent score is decision-grade without
having to read implementation code.

### Primary path

1. Reads the landing-page thesis, proof, and honest operating limits.
2. Confirms that FlawedBench is a synthetic regression fixture, not a public
   benchmark claim.
3. Opens the audit desk and reviews the persistent summary:
   reported score, trust band, findings, budget, and undetermined count.
4. Filters critical/high findings and opens evidence packets for spot checks.
5. Reviews the assurance boundary before exporting the audit.
6. Uses the exported snapshot as supporting evidence, not as a certification.

### Pass path

- Accepts only that the configured probes found no exception.
- Checks the mutation lower-bound and oracle tier before treating the pass as
  meaningful.

### Finding path

- Can identify the affected task, why it matters, and the exact reproduction
  path without interpreting raw logs.
- Requires disposition: fix, exclude, accept with rationale, or block the
  benchmark decision.

### Undetermined path

- Sees missing evidence as a first-class review outcome.
- Requires an explicit risk acceptance or further audit; undetermined cannot be
  merged into the pass count.

## Task author

**Goal:** make a new or changed benchmark item solvable, failable, and reliably
graded.

### Primary path

1. Reads the four-station method to understand authoring expectations.
2. Selects a representative task in the audit desk.
3. Inspects its prompt, oracle, grader mode, correct variants, wrong mutation
   budget, and evidence tier.
4. Steps the audit while varying mutation coverage.
5. Uses the task evidence packet and reproducer to update the task manifest or
   grader.
6. Runs the real CLI against the changed suite and checks the generated report.

### Pass path

- Oracle passes.
- Null, refusal, and echo probes fail.
- Constructed wrong mutations fail.
- Declared correct variants pass.
- Evidence tier and budget are sufficient for the intended decision.

### Finding path

- The finding names the contract that failed and preserves the exact task ID.
- The author fixes the smallest responsible layer—task, fixture, label, or
  grader—then re-runs the single-task reproducer.

### Undetermined path

- Adds trusted oracle material or labels the item oracle-free.
- Increases the probe budget if coverage, rather than evidence quality, is the
  limiting factor.
- Does not rewrite the task to “pass the audit” without addressing the missing
  assurance evidence.

## Accessibility and responsive journey requirements

- Primary navigation, run controls, selectors, filters, task rows, evidence
  actions, and disclosure sections are keyboard operable.
- Focus has a high-contrast visible outline; state is expressed in text and
  symbols as well as color.
- Audit status uses a live region; probe events update in an ordered log.
- Charts repeat their central message in visible numeric text. The task and
  finding registers provide the underlying categorical evidence.
- The desktop three-column audit desk collapses to one column without removing
  controls or evidence. On narrow screens, the persistent rail is removed
  because the same destinations remain in document order.
- Reduced-motion preferences disable substantive animation.
