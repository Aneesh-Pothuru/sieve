(() => {
  "use strict";

  const FINDINGS = {
    "task-03": {
      verdict: "GRADER_FP",
      severity: "high",
      detail: "Accepted 1/3 constructed wrong answers.",
      evidence: "declared-oracle",
      lowerBound: true,
      rateType: "FP",
      failures: 1,
      trials: 3,
      low: .061,
      rate: .333,
      high: .792
    },
    "task-07": {
      verdict: "TASK_UNSOLVABLE",
      severity: "high",
      detail: "Declared oracle solution rejected by the grader.",
      evidence: "declared-oracle",
      lowerBound: false,
      needsOracle: true,
      rateType: "FN",
      failures: 1,
      trials: 1,
      low: .207,
      rate: 1,
      high: 1
    },
    "task-12": {
      verdict: "TASK_UNFAILABLE",
      severity: "critical",
      detail: "3/3 null, refusal, and echo probes accepted.",
      evidence: "declared-oracle",
      lowerBound: false,
      rateType: "FP",
      failures: 4,
      trials: 4,
      low: .51,
      rate: 1,
      high: 1
    },
    "task-15": {
      verdict: "GRADER_FN",
      secondary: "LABEL_ERROR",
      severity: "high",
      detail: "Trusted oracle rejected; the keyed answer is a label-error candidate.",
      evidence: "bundled-oracle",
      lowerBound: false,
      needsOracle: true,
      rateType: "FN",
      failures: 2,
      trials: 2,
      low: .342,
      rate: 1,
      high: 1
    },
    "task-19": {
      verdict: "WEAK_GRADER",
      severity: "critical",
      detail: "Accepted 4/6 constructed wrong answers.",
      evidence: "declared-oracle",
      lowerBound: true,
      rateType: "FP",
      failures: 4,
      trials: 6,
      low: .3,
      rate: .667,
      high: .903
    }
  };

  const TASKS = [
    ["task-01", "Return the lowercase color of a clear daytime sky.", "blue", "normalized", 2, 2],
    ["task-02", "Return the sum of 10 and 5.", "15", "normalized", 2, 2],
    ["task-03", "Submit the exact patch status.", "patch-ok", "accept_empty_diff", 3, 2],
    ["task-04", "Return the opposite of false.", "true", "normalized", 2, 2],
    ["task-05", "Return the number of letters in cat.", "3", "normalized", 2, 2],
    ["task-06", "Return the extension of report.json.", "json", "normalized", 2, 2],
    ["task-07", "Return the path created by the fixture.", "file:real.txt", "exact", 2, 1],
    ["task-08", "Return the first month of the year.", "january", "normalized", 2, 2],
    ["task-09", "Return 2 multiplied by 6.", "12", "normalized", 2, 2],
    ["task-10", "Return the protocol in https://example.test.", "https", "normalized", 2, 2],
    ["task-11", "Return the final letter of audit.", "t", "normalized", 2, 2],
    ["task-12", "Return done only after completing the task.", "done", "always_pass", 4, 1],
    ["task-13", "Return the number after 20.", "21", "normalized", 2, 2],
    ["task-14", "Return the lowercase form of SIEVE.", "sieve", "normalized", 2, 2],
    ["task-15", "Return the correct value of 2+2.", "4", "exact / key=5", 2, 2],
    ["task-16", "Return the file separator used in a URL.", "/", "normalized", 2, 2],
    ["task-17", "Return the number of days in a standard week.", "7", "normalized", 2, 2],
    ["task-18", "Return the first letter of grader.", "g", "normalized", 2, 2],
    ["task-19", "Return safe when the local check passes.", "safe", "weak_allowlist", 6, 2],
    ["task-20", "Return the number before 100.", "99", "normalized", 2, 2]
  ].map(([id, prompt, oracle, grader, wrongCount, correctCount]) => ({
    id, prompt, oracle, grader, wrongCount, correctCount, finding: FINDINGS[id] || null
  }));
  const TERRARIUM_TASKS = [{
    id: "inbox-triage",
    prompt: "Read the refund policy, triage Maya's CRM case, and email her a response.",
    oracle: "DECLARED_VALID",
    grader: "exact / expected=DECLARED_VALID",
    wrongCount: 2,
    correctCount: 1,
    finding: null
  }];

  const els = {
    status: document.querySelector("#audit-status"),
    statusText: document.querySelector("#audit-status strong"),
    budgetInput: document.querySelector("#budget-input"),
    budgetOutput: document.querySelector("#budget-output"),
    budgetPreview: document.querySelector("#budget-preview"),
    budgetMetric: document.querySelector("#budget-metric"),
    budgetDetail: document.querySelector("#budget-detail"),
    progressMetric: document.querySelector("#progress-metric"),
    progressDetail: document.querySelector("#progress-detail"),
    findingMetric: document.querySelector("#finding-metric"),
    findingDetail: document.querySelector("#finding-detail"),
    undeterminedMetric: document.querySelector("#undetermined-metric"),
    undeterminedDetail: document.querySelector("#undetermined-detail"),
    bandMetric: document.querySelector("#band-metric"),
    plotBand: document.querySelector("#plot-band"),
    taskList: document.querySelector("#task-list"),
    inspector: document.querySelector("#task-inspector-content"),
    findingRegister: document.querySelector("#finding-register"),
    railFindingCount: document.querySelector("#rail-finding-count"),
    undeterminedFilterCount: document.querySelector("#undetermined-filter-count"),
    eventLog: document.querySelector("#event-log"),
    eventCount: document.querySelector("#event-count"),
    matrix: document.querySelector("#confusion-matrix"),
    matrixState: document.querySelector("#matrix-state"),
    trustCanvas: document.querySelector("#trust-canvas"),
    wilsonCanvas: document.querySelector("#wilson-canvas"),
    benchmark: document.querySelector("#benchmark-select"),
    start: document.querySelector("#start-button"),
    pause: document.querySelector("#pause-button"),
    step: document.querySelector("#step-button"),
    reset: document.querySelector("#reset-button"),
    scenario: document.querySelector("#scenario-select"),
    oracle: document.querySelector("#oracle-select"),
    mutation: document.querySelector("#mutation-select"),
    planNote: document.querySelector("#plan-note"),
    suiteTitle: document.querySelector("#suite-title"),
    suiteDescription: document.querySelector("#suite-description"),
    allFilterCount: document.querySelector("#all-filter-count"),
    criticalFilterCount: document.querySelector("#critical-filter-count"),
    highFilterCount: document.querySelector("#high-filter-count"),
    runIdentity: document.querySelector("#run-identity"),
    executionMode: document.querySelector("#execution-mode"),
    serviceEndpoint: document.querySelector("#service-endpoint"),
    connectService: document.querySelector("#connect-service"),
    executionStatus: document.querySelector("#execution-status"),
    executionBadge: document.querySelector("#execution-badge"),
    executionHelp: document.querySelector("#execution-help"),
    drawer: document.querySelector("#evidence-drawer"),
    drawerTitle: document.querySelector("#drawer-title"),
    drawerContent: document.querySelector("#drawer-content"),
    openEvidence: document.querySelector("#open-evidence"),
    toast: document.querySelector("#toast")
  };

  const state = {
    mode: "idle",
    timer: null,
    used: 0,
    reviewed: 0,
    selected: "task-01",
    results: {},
    events: [],
    history: [{ low: .8, high: .8, reported: .8 }],
    findingFilter: "all",
    taskView: "all",
    returnFocus: null,
    liveEnvelope: null,
    liveConnected: false
  };

  function escapeHtml(value) {
    return String(value)
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;");
  }

  function config() {
    return {
      benchmark: els.benchmark.value,
      budget: Number(els.budgetInput.value),
      oracle: els.oracle.value === "manifest",
      mutation: Number(els.mutation.value)
    };
  }

  function activeTasks() {
    return els.benchmark.value === "terrarium" ? TERRARIUM_TASKS : TASKS;
  }

  function isLive() {
    return els.executionMode.value === "live";
  }

  function serviceUrl(path) {
    return `${els.serviceEndpoint.value.trim().replace(/\/+$/, "")}${path}`;
  }

  function wrongTrials(task) {
    const depth = config().mutation;
    return depth === 3 ? task.wrongCount : Math.min(depth, task.wrongCount);
  }

  function taskCost(task) {
    return 3 + wrongTrials(task) + task.correctCount + (config().oracle ? 1 : 0);
  }

  function projectedCost() {
    return activeTasks().reduce((total, task) => total + taskCost(task), 0);
  }

  function dynamicFinding(task) {
    if (!task.finding) return null;
    if (task.finding.needsOracle && !config().oracle) {
      return {
        verdict: "UNDETERMINED",
        severity: "undetermined",
        detail: "Trusted oracle evidence was withheld for this replay.",
        evidence: "oracle-free",
        lowerBound: false
      };
    }
    if (task.id === "task-19" && config().mutation < 3) {
      const trials = wrongTrials(task);
      return {
        ...task.finding,
        verdict: "GRADER_FP",
        severity: "high",
        detail: `Accepted ${Math.min(trials, 4)}/${trials} observed wrong mutations; full weak-grader classification requires the complete battery.`,
        failures: Math.min(trials, 4),
        trials,
        rate: 1,
        low: trials === 1 ? .207 : .342,
        high: 1
      };
    }
    if (task.id === "task-03") {
      const trials = wrongTrials(task);
      return {
        ...task.finding,
        detail: `Accepted 1/${trials} observed wrong mutations.`,
        trials,
        rate: 1 / trials,
        low: trials === 1 ? .207 : trials === 2 ? .095 : .061,
        high: trials === 1 ? 1 : trials === 2 ? .905 : .792
      };
    }
    if (task.id === "task-12" && config().mutation < 3) {
      const trials = wrongTrials(task);
      return { ...task.finding, failures: trials, trials, rate: 1, low: trials === 1 ? .207 : .342 };
    }
    return { ...task.finding };
  }

  function setStatus(mode, label) {
    state.mode = mode;
    els.status.className = `audit-status ${mode}`;
    els.statusText.textContent = label;
    els.start.disabled = mode === "running" || state.reviewed === activeTasks().length;
    els.pause.disabled = isLive() || mode !== "running";
    els.step.disabled = isLive() || mode === "running" || state.reviewed === activeTasks().length;
    els.start.innerHTML = isLive()
      ? 'Run actual audit <span aria-hidden="true">▶</span>'
      : mode === "paused"
        ? 'Resume audit <span aria-hidden="true">▶</span>'
        : 'Start replay <span aria-hidden="true">▶</span>';
  }

  function resetAudit(announce = false) {
    if (state.timer) window.clearInterval(state.timer);
    state.timer = null;
    state.used = 0;
    state.reviewed = 0;
    state.selected = activeTasks()[0].id;
    state.results = {};
    state.events = [];
    state.history = [{ low: .8, high: .8, reported: .8 }];
    state.liveEnvelope = null;
    setStatus("idle", "Ready to run");
    updateAll();
    if (announce) showToast("Audit reset to configured probe plan.");
  }

  function startAudit() {
    if (isLive()) {
      runLiveAudit();
      return;
    }
    if (state.reviewed >= activeTasks().length) return;
    setStatus("running", `Probing task ${String(state.reviewed + 1).padStart(2, "0")}`);
    state.timer = window.setInterval(() => {
      stepAudit();
      if (state.reviewed >= activeTasks().length || state.mode === "complete") {
        window.clearInterval(state.timer);
        state.timer = null;
      }
    }, 520);
  }

  async function checkLiveService(announce = true) {
    els.executionStatus.innerHTML = "<strong>Connecting.</strong> Checking readiness and persistence.";
    try {
      const response = await fetch(serviceUrl("/readyz"), {
        headers: { "X-Request-ID": `sieve-ui-${Date.now()}` }
      });
      const payload = await response.json();
      if (!response.ok || payload.status !== "ready") {
        throw new Error("service is not ready");
      }
      state.liveConnected = true;
      els.executionBadge.className = "fixture-label live";
      els.executionBadge.innerHTML = "<i></i> Local auditor ready";
      els.executionStatus.innerHTML = "<strong>Connected.</strong> Runs execute in Python and persist to SQLite.";
      if (announce) showToast("Local Sieve service is ready.");
      return true;
    } catch (error) {
      state.liveConnected = false;
      els.executionBadge.className = "fixture-label error";
      els.executionBadge.innerHTML = "<i></i> Local auditor offline";
      els.executionStatus.innerHTML = `<strong>Unavailable.</strong> Start <code>sieve serve</code> and retry. ${escapeHtml(error.message)}`;
      if (announce) showToast("Local service unavailable; fixture replay still works.");
      return false;
    }
  }

  function apiFinding(item, rates) {
    const rateType = ["GRADER_FP", "WEAK_GRADER", "TASK_UNFAILABLE"].includes(item.verdict)
      ? "FP"
      : ["GRADER_FN", "TASK_UNSOLVABLE"].includes(item.verdict)
        ? "FN"
        : null;
    const interval = rateType ? rates?.[rateType.toLowerCase()] : null;
    return {
      verdict: item.verdict,
      secondary: item.secondary?.join(" + ") || null,
      severity: item.severity,
      detail: item.detail,
      evidence: item.evidence_tier,
      lowerBound: item.fp_lower_bound,
      rateType,
      failures: interval?.failures,
      trials: interval?.trials,
      low: interval?.low,
      rate: interval?.rate,
      high: interval?.high
    };
  }

  function hydrateLiveRun(envelope) {
    const result = envelope.result;
    const tasks = activeTasks();
    const findings = Object.fromEntries(result.findings.map(item => [item.task_id, item]));
    const taskStates = result.metadata.task_states || {};
    state.liveEnvelope = envelope;
    state.used = result.budget.used;
    state.reviewed = tasks.length;
    state.results = {};
    state.events = [];
    tasks.forEach(task => {
      const taskState = taskStates[task.id] || {};
      const item = findings[task.id];
      if (taskState.status === "UNDETERMINED") {
        state.results[task.id] = {
          status: "undetermined",
          finding: {
            verdict: "UNDETERMINED",
            severity: "undetermined",
            detail: taskState.probes_skipped
              ? `${taskState.probes_skipped} planned probes were skipped after the budget was exhausted.`
              : "Trusted oracle evidence was unavailable to the actual auditor.",
            evidence: taskState.probes_skipped ? "budget-exhausted" : "oracle-free",
            lowerBound: false
          }
        };
      } else if (item) {
        state.results[task.id] = {
          status: "finding",
          finding: apiFinding(item, result.grader_rates[task.id])
        };
      } else {
        state.results[task.id] = { status: "pass", finding: null };
      }
      const observed = state.results[task.id];
      state.events.unshift({
        task: task.id,
        text: observed.finding?.detail || `${taskState.budget_used || 0} actual probes matched declared expectations`,
        outcome: observed.finding?.verdict || "PASS",
        kind: observed.finding ? "finding" : "pass"
      });
    });
    state.history = [
      { low: result.trust_band.reported, high: result.trust_band.reported, reported: result.trust_band.reported },
      { ...result.trust_band }
    ];
    state.selected = result.findings[0]?.task_id || tasks[0].id;
    setStatus(
      "complete",
      result.metadata.decision_status === "UNDETERMINED"
        ? "Persisted with abstentions"
        : "Actual audit persisted"
    );
    els.runIdentity.textContent = envelope.run_id.toUpperCase();
    updateAll();
  }

  async function runLiveAudit() {
    if (state.mode === "running") return;
    setStatus("running", "Calling local auditor");
    const suite = config().benchmark === "terrarium"
      ? "fixtures/terrarium/inbox-triage.yaml"
      : "flawedbench";
    try {
      const response = await fetch(serviceUrl("/v1/audits"), {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-Request-ID": `sieve-ui-${Date.now()}`
        },
        body: JSON.stringify({
          suite,
          format: config().benchmark === "terrarium" ? "terrarium" : "auto",
          budget: config().budget,
          reported_score: .8
        })
      });
      const payload = await response.json();
      if (!response.ok) {
        throw new Error(payload.error?.message || `service returned ${response.status}`);
      }
      state.liveConnected = true;
      els.executionBadge.className = "fixture-label live";
      els.executionBadge.innerHTML = "<i></i> Actual run persisted";
      els.executionStatus.innerHTML = `<strong>Persisted.</strong> Run <code>${escapeHtml(payload.run_id)}</code> is retrievable from the local API.`;
      hydrateLiveRun(payload);
      showToast("Actual audit completed and persisted.");
    } catch (error) {
      state.liveConnected = false;
      setStatus("idle", "Local service unavailable");
      els.executionBadge.className = "fixture-label error";
      els.executionBadge.innerHTML = "<i></i> Local auditor offline";
      els.executionStatus.innerHTML = `<strong>Run failed.</strong> ${escapeHtml(error.message)} Start <code>sieve serve</code> or return to fixture replay.`;
      showToast("Actual audit failed; no replay data was substituted.");
    }
  }

  function pauseAudit() {
    if (state.timer) window.clearInterval(state.timer);
    state.timer = null;
    setStatus("paused", `Paused after ${state.reviewed} tasks`);
  }

  function stepAudit() {
    const tasks = activeTasks();
    if (state.reviewed >= tasks.length) return;
    const cfg = config();
    const remaining = cfg.budget - state.used;
    const task = tasks[state.reviewed];
    const cost = taskCost(task);

    if (cost > remaining) {
      state.used = cfg.budget;
      for (let index = state.reviewed; index < tasks.length; index += 1) {
        const pending = tasks[index];
        state.results[pending.id] = {
          status: "undetermined",
          finding: {
            verdict: "UNDETERMINED",
            severity: "undetermined",
            detail: index === state.reviewed
              ? `Probe budget exhausted during ${pending.id}; incomplete evidence was not classified.`
              : "Probe budget exhausted before this task was reached.",
            evidence: "budget-exhausted",
            lowerBound: false
          }
        };
      }
      state.events.unshift({
        task: task.id,
        text: `Budget exhausted with ${remaining} calls remaining`,
        outcome: "UNDETERMINED",
        kind: "finding"
      });
      state.reviewed = tasks.length;
      pushHistory();
      setStatus("complete", "Complete with abstentions");
      updateAll();
      return;
    }

    state.used += cost;
    let finding = dynamicFinding(task);
    if (!cfg.oracle && finding && finding.verdict !== "UNDETERMINED") {
      finding = { ...finding, evidence: "oracle-free-probes" };
    } else if (!cfg.oracle && !finding) {
      finding = {
        verdict: "UNDETERMINED",
        severity: "undetermined",
        detail: "Oracle-free probes passed, but solvability remains undetermined because oracle evidence was withheld.",
        evidence: "oracle-free",
        lowerBound: false
      };
    }
    const isUndetermined = finding && finding.verdict === "UNDETERMINED";
    state.results[task.id] = {
      status: isUndetermined ? "undetermined" : finding ? "finding" : "pass",
      finding
    };
    state.reviewed += 1;
    state.selected = task.id;
    state.events.unshift({
      task: task.id,
      text: finding ? finding.detail : `${cost} probes matched declared expectations`,
      outcome: finding ? finding.verdict : "PASS",
      kind: finding ? "finding" : "pass"
    });
    pushHistory();

    if (state.reviewed >= tasks.length) {
      setStatus("complete", isUndetermined ? "Complete with evidence gaps" : "Audit complete");
    } else if (state.mode === "running") {
      els.statusText.textContent = `Probing task ${String(state.reviewed + 1).padStart(2, "0")}`;
    } else {
      setStatus("paused", `Stepped through ${state.reviewed} tasks`);
    }
    updateAll();
  }

  function detectedFindings() {
    return Object.entries(state.results)
      .filter(([, result]) => result.finding && result.finding.verdict !== "UNDETERMINED")
      .map(([taskId, result]) => ({ taskId, ...result.finding }));
  }

  function undeterminedFindings() {
    return Object.entries(state.results)
      .filter(([, result]) => result.finding && result.finding.verdict === "UNDETERMINED")
      .map(([taskId, result]) => ({ taskId, ...result.finding }));
  }

  function trustBand() {
    const findings = detectedFindings();
    const denominator = activeTasks().length || 1;
    const fp = findings.filter(item => ["GRADER_FP", "WEAK_GRADER"].includes(item.verdict)).length / denominator;
    const fn = findings.filter(item => item.verdict === "GRADER_FN").length / denominator;
    const invalid = findings.filter(item => ["TASK_UNSOLVABLE", "TASK_UNFAILABLE", "TASK_DEGENERATE"].includes(item.verdict)).length / denominator;
    return {
      low: Math.max(0, .8 - fp - invalid / 2),
      high: Math.min(1, .8 + fn + invalid / 2),
      reported: .8
    };
  }

  function pushHistory() {
    state.history.push(trustBand());
  }

  function formatBand(band) {
    return `${Math.round(band.low * 100)}–${Math.round(band.high * 100)}%`;
  }

  function reproducerFor(taskId) {
    return config().benchmark === "terrarium"
      ? `sieve audit fixtures/terrarium/inbox-triage.yaml --format terrarium --task ${taskId}`
      : `sieve audit flawedbench --task ${taskId}`;
  }

  function traceClass(probe, outcome) {
    if (outcome === "PLANNED" || outcome === "UNDETERMINED") return "neutral";
    const expected = {
      ORACLE: "PASS",
      NULL: "REJECT",
      MUTATE: "REJECT",
      VARIANT: "PASS"
    };
    return outcome === expected[probe] ? "pass" : "fail";
  }

  function updateAll() {
    updatePlan();
    renderTaskList();
    renderInspector();
    renderFindings();
    renderEvents();
    renderMetrics();
    renderMatrix();
    drawTrustChart();
    drawWilsonChart();
  }

  function updatePlan() {
    const cost = projectedCost();
    const cfg = config();
    els.budgetOutput.textContent = `${cfg.budget} runs`;
    els.budgetPreview.style.width = `${Math.min(100, cost / cfg.budget * 100)}%`;
    const gap = cfg.budget < cost;
    els.planNote.textContent = isLive()
      ? `${cost} projected grader calls · actual Python auditor · immutable SQLite run · ${gap ? `${cost - cfg.budget} calls beyond budget` : "$0, keyless"}.`
      : `${cost} projected local grader calls · ${cfg.oracle ? "manifest oracles" : "oracles withheld"} · ${gap ? `${cost - cfg.budget} calls beyond budget` : "no model calls, $0"}.`;
  }

  function renderMetrics() {
    const cfg = config();
    const findings = detectedFindings();
    const undetermined = undeterminedFindings();
    const band = trustBand();
    const tasks = activeTasks();
    const expectedFindings = tasks.filter(task => task.finding);
    const observedExceptions = [...findings, ...undetermined];
    els.progressMetric.textContent = `${state.reviewed} / ${tasks.length}`;
    els.progressDetail.textContent = state.reviewed ? `${Math.round(state.reviewed / tasks.length * 100)}% reviewed` : "No tasks probed";
    els.budgetMetric.textContent = `${state.used} / ${cfg.budget}`;
    els.budgetDetail.textContent = state.liveEnvelope ? "Actual service usage" : `${projectedCost()} projected`;
    els.findingMetric.textContent = String(findings.length);
    els.findingDetail.textContent = state.reviewed === tasks.length ? `${findings.length} evidenced exceptions` : `${expectedFindings.length} seeded defects`;
    els.undeterminedMetric.textContent = String(undetermined.length);
    els.undeterminedDetail.textContent = undetermined.length ? "Review before decision" : "No abstentions yet";
    const bandLabel = undetermined.length ? "UNDETERMINED" : formatBand(band);
    els.bandMetric.textContent = bandLabel;
    els.plotBand.textContent = bandLabel;
    els.railFindingCount.textContent = String(findings.length + undetermined.length);
    els.undeterminedFilterCount.textContent = String(undetermined.length);
    els.allFilterCount.textContent = String(observedExceptions.length);
    els.criticalFilterCount.textContent = String(observedExceptions.filter(item => item.severity === "critical").length);
    els.highFilterCount.textContent = String(observedExceptions.filter(item => item.severity === "high").length);
    if (state.liveEnvelope) {
      els.runIdentity.textContent = state.liveEnvelope.run_id.toUpperCase();
    } else if (cfg.benchmark === "terrarium") {
      els.suiteTitle.innerHTML = 'Terrarium task <em>under test.</em>';
      els.suiteDescription.textContent = isLive()
        ? "Run the installed auditor against the vendored Terrarium contract and persist the result. The world is not executed in v0.1."
        : "Inspect the static adapter contract for a declared inbox-triage task. The world is not executed in v0.1.";
      els.runIdentity.textContent = "SV-002 / TERRARIUM:INBOX";
    } else {
      els.suiteTitle.innerHTML = 'FlawedBench <em>under test.</em>';
      els.suiteDescription.textContent = isLive()
        ? "Call the installed Python auditor, persist the full evidence envelope, and inspect its actual findings in this interface."
        : "Challenge a known 20-task fixture, inspect each grader decision, and see how evidence changes the score you can responsibly claim.";
      els.runIdentity.textContent = "SV-001 / FLAWEDBENCH";
    }
  }

  function renderTaskList() {
    const visible = activeTasks().filter(task => {
      if (state.taskView === "all") return true;
      return Boolean(state.results[task.id]?.finding);
    });
    if (!visible.length) {
      els.taskList.innerHTML = '<div class="empty-event">No exceptions have been observed yet.</div>';
      return;
    }
    els.taskList.innerHTML = visible.map(task => {
      const result = state.results[task.id];
      const status = result?.status || "queued";
      const symbol = status === "finding" ? "!" : status === "pass" ? "✓" : status === "undetermined" ? "?" : "·";
      return `<button class="task-row ${status} ${state.selected === task.id ? "selected" : ""}" type="button" role="option" aria-selected="${state.selected === task.id}" data-task-id="${task.id}">
        <span class="task-state">${symbol}</span>
        <span><b>${task.id}</b><small>${escapeHtml(task.prompt)}</small></span>
        <em>${result?.finding?.verdict || status}</em>
      </button>`;
    }).join("");
  }

  function renderInspector() {
    const tasks = activeTasks();
    const task = tasks.find(item => item.id === state.selected) || tasks[0];
    const result = state.results[task.id];
    const finding = result?.finding;
    const cfg = config();
    const status = result?.status || "queued";
    els.inspector.innerHTML = `<div class="inspector-body">
      <div class="inspector-id"><strong>${task.id.toUpperCase()}</strong><span class="state-chip ${status}">${status}</span></div>
      <h3>${escapeHtml(task.prompt)}</h3>
      <p>This inspection view separates the declared task contract from observed grader behavior.</p>
      <div class="spec-list">
        <div class="spec-row"><span>Oracle</span><code>${cfg.oracle ? escapeHtml(task.oracle) : "[withheld]"}</code></div>
        <div class="spec-row"><span>Grader mode</span><code>${escapeHtml(task.grader)}</code></div>
        <div class="spec-row"><span>Evidence tier</span><code>${escapeHtml(finding?.evidence || (cfg.oracle ? "declared-oracle" : "oracle-free"))}</code></div>
        <div class="spec-row"><span>Reproducer</span><code>${escapeHtml(reproducerFor(task.id))}</code></div>
      </div>
      <div class="probe-grid">
        <span>Oracle probes<b>${cfg.oracle ? "1 planned" : "withheld"}</b></span>
        <span>Null probes<b>3 planned</b></span>
        <span>Wrong mutations<b>${wrongTrials(task)} planned</b></span>
        <span>Correct variants<b>${task.correctCount} planned</b></span>
      </div>
      ${finding ? `<div class="inspector-finding"><span>${escapeHtml(finding.verdict)}${finding.secondary ? ` + ${escapeHtml(finding.secondary)}` : ""}</span><p>${escapeHtml(finding.detail)}</p></div>` : ""}
      <div class="inspector-actions">
        <button class="button ghost" type="button" data-inspect-evidence>Evidence packet</button>
        <button class="button ghost" type="button" data-copy-reproducer>Copy reproducer</button>
      </div>
    </div>`;
  }

  function renderFindings() {
    const items = [...detectedFindings(), ...undeterminedFindings()].filter(item => (
      state.findingFilter === "all" ||
      item.severity === state.findingFilter ||
      (state.findingFilter === "undetermined" && item.verdict === "UNDETERMINED")
    ));
    if (!items.length) {
      els.findingRegister.innerHTML = `<div class="empty-register"><span>${state.findingFilter === "all" ? "NO FINDINGS YET" : "NO MATCHING FINDINGS"}</span><p>${state.findingFilter === "all" ? "Run the probe battery to populate the evidence register." : "Change the filter or continue the audit."}</p></div>`;
      return;
    }
    els.findingRegister.innerHTML = items.map(item => `<button class="finding-card ${item.severity}" type="button" data-finding-task="${item.taskId}">
      <span class="finding-top"><span>${item.taskId}</span><span>${item.severity}</span></span>
      <span class="finding-title">${escapeHtml(item.verdict)}${item.secondary ? `<br>+ ${escapeHtml(item.secondary)}` : ""}</span>
      <span class="finding-detail">${escapeHtml(item.detail)}</span>
      <span class="finding-meta">
        <span>Evidence <b>${escapeHtml(item.evidence)}</b></span>
        <span>FP lower bound <b>${item.lowerBound ? "yes" : "no"}</b></span>
        <span>Reproducer <b>attached ↗</b></span>
      </span>
    </button>`).join("");
  }

  function renderEvents() {
    els.eventCount.textContent = `${state.events.length} event${state.events.length === 1 ? "" : "s"}`;
    if (!state.events.length) {
      els.eventLog.innerHTML = '<li class="empty-event">Start or step the audit to inspect the probe stream.</li>';
      return;
    }
    els.eventLog.innerHTML = state.events.slice(0, 30).map((event, index) => `<li class="${event.kind === "finding" ? "event-finding" : ""}">
      <b>${event.task}</b><span>${escapeHtml(event.text)}</span><em>${escapeHtml(event.outcome)}</em>
    </li>`).join("");
  }

  function confusion() {
    let correct = 0;
    let wrong = 0;
    let falseAccept = 0;
    let falseReject = 0;
    activeTasks().forEach(task => {
      if (!state.results[task.id] || state.results[task.id].status === "undetermined") return;
      const taskWrong = wrongTrials(task);
      correct += task.correctCount;
      wrong += taskWrong;
      if (task.id === "task-03") falseAccept += Math.min(1, taskWrong);
      if (task.id === "task-12") falseAccept += taskWrong;
      if (task.id === "task-19") falseAccept += Math.min(4, taskWrong);
      if (task.id === "task-07") falseReject += task.correctCount;
      if (task.id === "task-15") falseReject += task.correctCount;
    });
    return { trueAccept: correct - falseReject, falseReject, falseAccept, trueReject: wrong - falseAccept };
  }

  function renderMatrix() {
    const values = confusion();
    els.matrix.innerHTML = `<span></span><b>Grader pass</b><b>Grader fail</b>
      <b>Correct variants</b><strong class="good">${values.trueAccept}</strong><strong class="bad">${values.falseReject}</strong>
      <b>Wrong mutations</b><strong class="bad">${values.falseAccept}</strong><strong class="good">${values.trueReject}</strong>`;
    els.matrixState.textContent = state.reviewed ? `${state.reviewed} tasks observed` : "Awaiting audit";
  }

  function canvasContext(canvas) {
    const ratio = window.devicePixelRatio || 1;
    const rect = canvas.getBoundingClientRect();
    const width = Math.max(300, rect.width);
    const height = Number(canvas.getAttribute("height"));
    canvas.width = width * ratio;
    canvas.height = height * ratio;
    const context = canvas.getContext("2d");
    context.scale(ratio, ratio);
    return { context, width, height };
  }

  function drawTrustChart() {
    const { context: ctx, width, height } = canvasContext(els.trustCanvas);
    const pad = { left: 42, right: 20, top: 24, bottom: 30 };
    const plotW = width - pad.left - pad.right;
    const plotH = height - pad.top - pad.bottom;
    ctx.clearRect(0, 0, width, height);
    ctx.font = "8px ui-monospace, monospace";
    ctx.fillStyle = "#696458";
    ctx.strokeStyle = "#c9c1ae";
    ctx.lineWidth = 1;
    [0, .25, .5, .75, 1].forEach(value => {
      const y = pad.top + plotH * (1 - value);
      ctx.beginPath();
      ctx.moveTo(pad.left, y);
      ctx.lineTo(width - pad.right, y);
      ctx.stroke();
      ctx.fillText(`${value * 100}%`, 7, y + 3);
    });
    const points = state.history;
    const xAt = index => pad.left + (points.length === 1 ? 0 : index / Math.max(1, activeTasks().length) * plotW);
    const yAt = value => pad.top + plotH * (1 - value);
    if (points.length > 1) {
      ctx.beginPath();
      points.forEach((point, index) => {
        const x = xAt(index);
        const y = yAt(point.high);
        index ? ctx.lineTo(x, y) : ctx.moveTo(x, y);
      });
      for (let index = points.length - 1; index >= 0; index -= 1) {
        ctx.lineTo(xAt(index), yAt(points[index].low));
      }
      ctx.closePath();
      ctx.fillStyle = "rgba(255,215,46,.78)";
      ctx.fill();
      ctx.strokeStyle = "#171713";
      ctx.stroke();
    }
    ctx.strokeStyle = "#2447ff";
    ctx.lineWidth = 2;
    ctx.setLineDash([5, 4]);
    ctx.beginPath();
    ctx.moveTo(pad.left, yAt(.8));
    ctx.lineTo(width - pad.right, yAt(.8));
    ctx.stroke();
    ctx.setLineDash([]);
    ctx.fillStyle = "#696458";
    ctx.fillText("0 tasks", pad.left, height - 10);
    const taskLabel = `${activeTasks().length} task${activeTasks().length === 1 ? "" : "s"}`;
    ctx.fillText(taskLabel, width - pad.right - (activeTasks().length === 1 ? 30 : 36), height - 10);
  }

  function drawWilsonChart() {
    const { context: ctx, width, height } = canvasContext(els.wilsonCanvas);
    const items = detectedFindings().filter(item => item.rateType && typeof item.rate === "number");
    const pad = { left: 72, right: 25, top: 27, bottom: 28 };
    const plotW = width - pad.left - pad.right;
    ctx.clearRect(0, 0, width, height);
    ctx.font = "8px ui-monospace, monospace";
    ctx.strokeStyle = "#d1c9b5";
    [0, .25, .5, .75, 1].forEach(value => {
      const x = pad.left + value * plotW;
      ctx.beginPath();
      ctx.moveTo(x, pad.top);
      ctx.lineTo(x, height - pad.bottom);
      ctx.stroke();
      ctx.fillStyle = "#696458";
      ctx.fillText(`${value * 100}%`, x - 8, height - 10);
    });
    if (!items.length) {
      ctx.fillStyle = "#696458";
      ctx.fillText("Run the audit to plot measured error intervals.", pad.left, height / 2);
      return;
    }
    const rowH = Math.min(35, (height - pad.top - pad.bottom) / items.length);
    items.forEach((item, index) => {
      const y = pad.top + rowH * index + rowH / 2;
      ctx.fillStyle = "#171713";
      ctx.fillText(`${item.taskId} ${item.rateType}`, 6, y + 3);
      ctx.strokeStyle = "#171713";
      ctx.lineWidth = 2;
      ctx.beginPath();
      ctx.moveTo(pad.left + item.low * plotW, y);
      ctx.lineTo(pad.left + item.high * plotW, y);
      ctx.stroke();
      ctx.fillStyle = item.rateType === "FP" ? "#e94b36" : "#2447ff";
      ctx.beginPath();
      ctx.arc(pad.left + item.rate * plotW, y, 5, 0, Math.PI * 2);
      ctx.fill();
    });
  }

  function openDrawer(taskId = state.selected) {
    const tasks = activeTasks();
    const task = tasks.find(item => item.id === taskId) || tasks[0];
    const result = state.results[task.id];
    const finding = result?.finding;
    state.selected = task.id;
    state.returnFocus = document.activeElement;
    els.drawerTitle.textContent = `${task.id} evidence`;
    const evidenceObserved = Boolean(result);
    const budgetExhausted = finding?.evidence === "budget-exhausted";
    const observedStatus = outcome => (
      !evidenceObserved ? "PLANNED" : budgetExhausted ? "UNDETERMINED" : outcome
    );
    const acceptedMutations = task.id === "task-03"
      ? Math.min(1, wrongTrials(task))
      : task.id === "task-12"
        ? wrongTrials(task)
        : task.id === "task-19"
          ? Math.min(4, wrongTrials(task))
          : 0;
    const mutationOutcome = acceptedMutations === 0
      ? "REJECT"
      : acceptedMutations === wrongTrials(task)
        ? "ACCEPT"
        : "MIXED";
    const traces = [
      ["ORACLE", config().oracle ? task.oracle : "[withheld]", observedStatus(!config().oracle ? "UNDETERMINED" : task.id === "task-07" || task.id === "task-15" ? "REJECT" : "PASS")],
      ["NULL", "none / refusal / echo", observedStatus(task.id === "task-12" ? "ACCEPT" : "REJECT")],
      ["MUTATE", `${wrongTrials(task)} constructed wrong`, observedStatus(mutationOutcome)],
      ["VARIANT", `${task.correctCount} declared correct`, observedStatus(["task-07","task-15"].includes(task.id) ? "REJECT" : "PASS")]
    ];
    els.drawerContent.innerHTML = `<div class="drawer-body">
      <section class="evidence-block"><h3>Task contract</h3><pre>${escapeHtml(JSON.stringify({
        id: task.id,
        prompt: task.prompt,
        oracle: config().oracle ? task.oracle : null,
        grader_mode: task.grader,
        evidence_tier: finding?.evidence || (config().oracle ? "declared-oracle" : "oracle-free")
      }, null, 2))}</pre></section>
      <section class="evidence-block"><h3>Probe trace</h3><ol class="trace-list">${traces.map(trace => `<li><span>${trace[0]}</span><b>${escapeHtml(trace[1])}</b><em class="${traceClass(trace[0], trace[2])}">${trace[2]}</em></li>`).join("")}</ol></section>
      <section class="evidence-block"><h3>Observed verdict</h3><pre>${finding ? escapeHtml(`${finding.verdict}${finding.secondary ? ` + ${finding.secondary}` : ""}\n${finding.detail}`) : result ? "PASS\nNo exception observed under this configuration." : "QUEUED\nNo probe evidence has been observed yet."}</pre></section>
      <section class="evidence-block"><h3>Exact reproducer</h3><div class="reproducer-box"><code>${escapeHtml(reproducerFor(task.id))}</code><button class="button ghost" type="button" data-copy-reproducer>Copy</button></div></section>
      <section class="evidence-block"><h3>Interpretation boundary</h3><pre>Browser interaction: ${isLive() ? "local-service result viewer" : "deterministic fixture replay"}
Authoritative execution: ${isLive() ? "persisted Python audit run" : "Python audit core; replay is illustrative"}
FP interpretation: lower bound over constructed mutations
Trust band: sensitivity analysis, not confidence interval</pre></section>
    </div>`;
    els.drawer.classList.add("open");
    els.drawer.setAttribute("aria-hidden", "false");
    els.openEvidence.setAttribute("aria-expanded", "true");
    document.body.style.overflow = "hidden";
    els.drawer.querySelector("button[data-close-drawer]").focus();
    renderTaskList();
    renderInspector();
  }

  function closeDrawer() {
    els.drawer.classList.remove("open");
    els.drawer.setAttribute("aria-hidden", "true");
    els.openEvidence.setAttribute("aria-expanded", "false");
    document.body.style.overflow = "";
    if (state.returnFocus && typeof state.returnFocus.focus === "function") {
      state.returnFocus.focus();
    }
  }

  function auditPayload() {
    if (state.liveEnvelope) return state.liveEnvelope;
    const band = trustBand();
    return {
      schema_version: "sieve.demo.v1",
      generated_at: new Date().toISOString(),
      fixture: config().benchmark === "terrarium"
        ? { name: "terrarium:inbox-triage", tasks: 1, synthetic: true, scope: "static adapter; world not executed" }
        : { name: "FlawedBench", tasks: 20, synthetic: true },
      configuration: { ...config(), mutation: els.mutation.options[els.mutation.selectedIndex].text },
      state: state.mode,
      summary: {
        reviewed: state.reviewed,
        budget_used: state.used,
        finding_count: detectedFindings().length,
        undetermined_count: undeterminedFindings().length,
        decision_status: undeterminedFindings().length ? "UNDETERMINED" : "DETERMINED",
        reported_score: band.reported,
        trust_adjusted_band: { low: band.low, high: band.high },
        trust_band_interpretation: undeterminedFindings().length
          ? "Observed-finding sensitivity only; not decision-grade while evidence is undetermined"
          : "Sensitivity band, not confidence interval"
      },
      findings: [...detectedFindings(), ...undeterminedFindings()],
      task_states: Object.fromEntries(activeTasks().map(task => [task.id, state.results[task.id]?.status || "queued"]))
    };
  }

  async function copyText(text, message) {
    try {
      await navigator.clipboard.writeText(text);
    } catch {
      const area = document.createElement("textarea");
      area.value = text;
      document.body.append(area);
      area.select();
      document.execCommand("copy");
      area.remove();
    }
    showToast(message);
  }

  function showToast(message) {
    els.toast.textContent = message;
    els.toast.classList.add("show");
    window.clearTimeout(showToast.timer);
    showToast.timer = window.setTimeout(() => els.toast.classList.remove("show"), 2200);
  }

  function exportAudit() {
    const blob = new Blob([`${JSON.stringify(auditPayload(), null, 2)}\n`], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = config().benchmark === "terrarium" ? "sieve-terrarium-audit.json" : "sieve-flawedbench-audit.json";
    document.body.append(link);
    link.click();
    link.remove();
    window.setTimeout(() => URL.revokeObjectURL(url), 1000);
    showToast("Audit evidence exported.");
  }

  els.start.addEventListener("click", startAudit);
  els.pause.addEventListener("click", pauseAudit);
  els.step.addEventListener("click", stepAudit);
  els.reset.addEventListener("click", () => resetAudit(true));
  els.connectService.addEventListener("click", () => checkLiveService());
  els.executionMode.addEventListener("change", () => {
    if (isLive()) {
      if (els.scenario.value === "oracle-gap") els.scenario.value = "canonical";
      els.oracle.value = "manifest";
      els.mutation.value = "3";
      els.oracle.disabled = true;
      els.mutation.disabled = true;
      els.executionHelp.textContent = "Live mode calls the installed Python auditor and persists the returned evidence. Step and pause are replay-only controls.";
      els.executionBadge.className = "fixture-label live";
      els.executionBadge.innerHTML = "<i></i> Local auditor not checked";
      els.executionStatus.innerHTML = "<strong>Live mode.</strong> Check the loopback service, then run the actual audit.";
    } else {
      els.oracle.disabled = false;
      els.mutation.disabled = false;
      state.liveConnected = false;
      els.executionHelp.textContent = "Configure a deterministic browser replay. Select local service to call the installed auditor and persist a real run.";
      els.executionBadge.className = "fixture-label";
      els.executionBadge.innerHTML = "<i></i> Fixture replay";
      els.executionStatus.innerHTML = "<strong>Replay mode.</strong> No backend request is made.";
    }
    resetAudit();
  });
  els.budgetInput.addEventListener("input", () => {
    resetAudit();
    updatePlan();
  });
  [els.oracle, els.mutation].forEach(control => control.addEventListener("change", () => resetAudit(true)));
  els.scenario.addEventListener("change", () => {
    if (isLive() && els.scenario.value === "oracle-gap") {
      els.scenario.value = "canonical";
      showToast("Oracle withholding is a fixture-replay control; live mode audits the suite contract as stored.");
    }
    if (els.scenario.value === "canonical") {
      els.budgetInput.value = "200";
      els.oracle.value = "manifest";
      els.mutation.value = "3";
    } else if (els.scenario.value === "budget") {
      els.budgetInput.value = "85";
      els.oracle.value = "manifest";
      els.mutation.value = "3";
    } else {
      els.budgetInput.value = "200";
      els.oracle.value = "withhold";
      els.mutation.value = "3";
    }
    resetAudit(true);
  });
  els.benchmark.addEventListener("change", () => {
    els.scenario.value = "canonical";
    els.budgetInput.value = "200";
    els.oracle.value = "manifest";
    els.mutation.value = "3";
    resetAudit(true);
  });
  els.taskList.addEventListener("click", event => {
    const row = event.target.closest("[data-task-id]");
    if (!row) return;
    state.selected = row.dataset.taskId;
    renderTaskList();
    renderInspector();
  });
  document.querySelectorAll("[data-task-view]").forEach(button => button.addEventListener("click", () => {
    document.querySelectorAll("[data-task-view]").forEach(item => item.classList.toggle("active", item === button));
    state.taskView = button.dataset.taskView;
    renderTaskList();
  }));
  document.querySelectorAll("[data-filter]").forEach(button => button.addEventListener("click", () => {
    document.querySelectorAll("[data-filter]").forEach(item => item.classList.toggle("active", item === button));
    state.findingFilter = button.dataset.filter;
    renderFindings();
  }));
  els.findingRegister.addEventListener("click", event => {
    const card = event.target.closest("[data-finding-task]");
    if (card) openDrawer(card.dataset.findingTask);
  });
  els.inspector.addEventListener("click", event => {
    if (event.target.closest("[data-inspect-evidence]")) openDrawer();
    if (event.target.closest("[data-copy-reproducer]")) copyText(reproducerFor(state.selected), "Reproducer copied.");
  });
  els.openEvidence.addEventListener("click", () => openDrawer());
  els.drawer.addEventListener("click", event => {
    if (event.target.closest("[data-close-drawer]")) closeDrawer();
    if (event.target.closest("[data-copy-reproducer]")) copyText(reproducerFor(state.selected), "Reproducer copied.");
  });
  document.addEventListener("keydown", event => {
    if (!els.drawer.classList.contains("open")) return;
    if (event.key === "Escape") {
      closeDrawer();
      return;
    }
    if (event.key === "Tab") {
      const focusable = [...els.drawer.querySelectorAll("button, a[href], input, select, [tabindex]:not([tabindex='-1'])")]
        .filter(element => !element.disabled);
      if (!focusable.length) return;
      const first = focusable[0];
      const last = focusable[focusable.length - 1];
      if (event.shiftKey && document.activeElement === first) {
        event.preventDefault();
        last.focus();
      } else if (!event.shiftKey && document.activeElement === last) {
        event.preventDefault();
        first.focus();
      }
    }
  });
  document.querySelector("#copy-audit").addEventListener("click", () => copyText(JSON.stringify(auditPayload(), null, 2), "Audit JSON copied."));
  document.querySelector("#export-audit").addEventListener("click", exportAudit);
  window.addEventListener("resize", () => {
    drawTrustChart();
    drawWilsonChart();
  });

  resetAudit();
})();
