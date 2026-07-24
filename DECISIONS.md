# Decisions

## 2026-07-24 — Local, constructed evidence first

The P0 probe engine is standard-library-only. Each grader input has a known
expected verdict by construction; no model-generated probe is presented as
ground truth.

## 2026-07-24 — P0 includes rates, CIs, bands, and budget

The brief repeats these in v0.2 but defines them as P0. The implementation
ships FP/FN point rates, Wilson 95% intervals, label-error tagging, the trust
band, and explicit budget accounting in v0.1.

## 2026-07-24 — TERRARIUM compatibility is vendored

The local adapter reads TERRARIUM's JSON-compatible YAML contract without a
runtime dependency. This satisfies standalone v0.1; live cross-project
integration remains v0.3.

## 2026-07-24 — One primary finding per seeded defect

To keep the Journey-0 contract exactly five findings, task-15 has primary
`GRADER_FN` with secondary `LABEL_ERROR`, and task-19 has primary
`WEAK_GRADER` rather than a duplicate `GRADER_FP`.

## 2026-07-24 — Trust band is a sensitivity calculation

For reported score S, the band is:
`[S - fp_affected - invalid/2, S + fn_affected + invalid/2]`, clamped to
`[0,1]`. FlawedBench has FP-affected=10%, FN-affected=5%, invalid=10%, so
80% becomes 65–90%. It is deliberately not called a statistical CI.

