from __future__ import annotations

import json
import sqlite3
import tempfile
import unittest
from pathlib import Path

from sieve.adapters import TerrariumFormatAdapter, load_suite
from sieve.audit import audit_suite
from sieve.models import AuditTask
from sieve.report import render
from sieve.stats import trust_adjusted_band, wilson
from sieve.storage import save_audit

ROOT = Path(__file__).resolve().parents[1]
FLAWEDBENCH = ROOT / "flawedbench"


class SieveTests(unittest.TestCase):
    def test_flawedbench_has_exact_expected_findings(self) -> None:
        name, tasks = load_suite(FLAWEDBENCH)
        result = audit_suite(name, tasks, 200)
        actual = {item.task_id: item.verdict for item in result.findings}
        expected = json.loads(
            (FLAWEDBENCH / "manifest.json").read_text(encoding="utf-8")
        )["expected_findings"]
        self.assertEqual(len(tasks), 20)
        self.assertEqual(actual, expected)
        self.assertEqual(result.budget["skipped"], 0)
        self.assertEqual(result.abstention_rate, 0.0)

    def test_flawedbench_trust_band_is_exact_demo_claim(self) -> None:
        name, tasks = load_suite(FLAWEDBENCH)
        band = audit_suite(name, tasks, 200).trust_band
        self.assertEqual((band["low"], band["high"]), (0.65, 0.90))
        self.assertEqual(trust_adjusted_band(0.8, 0.1, 0.05, 0.1), (0.65, 0.9))

    def test_wilson_interval_contains_observed_rate(self) -> None:
        interval = wilson(4, 6)
        self.assertAlmostEqual(interval.rate, 2 / 3)
        self.assertLess(interval.low, interval.rate)
        self.assertGreater(interval.high, interval.rate)
        empty = wilson(0, 0)
        self.assertEqual((empty.low, empty.high), (0.0, 1.0))

    def test_budget_exhaustion_is_explicit(self) -> None:
        name, tasks = load_suite(FLAWEDBENCH)
        result = audit_suite(name, tasks, 10)
        self.assertEqual(result.budget["used"], 10)
        self.assertGreater(result.budget["skipped"], 0)
        self.assertGreater(result.abstention_rate, 0)
        self.assertEqual(result.budget["skipped_reason"], "budget exhausted")

    def test_missing_oracle_abstains_but_runs_oracle_free_probes(self) -> None:
        task = AuditTask(
            id="oracle-free",
            prompt="A task without a trusted oracle",
            oracle=None,
            grader={"mode": "exact", "expected": "answer"},
            correct_variants=[],
            wrong_mutations=["wrong"],
            evidence_tier="oracle-free",
            metadata={"oracle_available": False},
        )
        result = audit_suite("oracle-free", [task], 20)
        self.assertEqual(result.budget["oracle_undetermined"], 1)
        self.assertGreater(result.abstention_rate, 0)
        self.assertGreater(result.budget["used"], 0)

    def test_terrarium_adapter_is_static_and_standalone(self) -> None:
        source = ROOT / "fixtures" / "terrarium" / "inbox-triage.yaml"
        name, tasks = TerrariumFormatAdapter().load(source)
        self.assertTrue(name.startswith("terrarium:"))
        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0].oracle, "DECLARED_VALID")
        self.assertIn("static", tasks[0].metadata["adapter_scope"])

    def test_report_and_sqlite_store(self) -> None:
        name, tasks = load_suite(FLAWEDBENCH)
        result = audit_suite(name, tasks, 200)
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            report = render(result, root / "index.html")
            self.assertIn("65%–90%", report.read_text(encoding="utf-8"))
            database = save_audit(result, root / "findings.sqlite")
            connection = sqlite3.connect(database)
            try:
                row = connection.execute(
                    "SELECT task_count,finding_count FROM audits WHERE suite_name=?",
                    ("FlawedBench",),
                ).fetchone()
            finally:
                connection.close()
            self.assertEqual(row, (20, 5))


if __name__ == "__main__":
    unittest.main()
