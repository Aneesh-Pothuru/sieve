from __future__ import annotations

from http import HTTPStatus
from threading import Thread
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from sieve.config import ServiceConfig
from sieve.server import SieveHTTPServer

ROOT = Path(__file__).resolve().parents[1]


class ServiceJourneyTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.database = Path(self.temporary.name) / "state" / "sieve.sqlite"
        self.config = ServiceConfig(
            host="127.0.0.1",
            port=0,
            database=self.database,
            data_root=ROOT,
        )
        self._start()

    def tearDown(self) -> None:
        self._stop()
        self.temporary.cleanup()

    def _start(self) -> None:
        self.server = SieveHTTPServer(self.config)
        self.thread = Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        host, port = self.server.server_address[:2]
        self.base_url = f"http://{host}:{port}"

    def _stop(self) -> None:
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=2)

    def request(
        self,
        method: str,
        path: str,
        payload: object | None = None,
        *,
        headers: dict[str, str] | None = None,
    ) -> tuple[int, dict[str, object], dict[str, str]]:
        data = None
        request_headers = dict(headers or {})
        if payload is not None:
            data = json.dumps(payload).encode("utf-8")
            request_headers["Content-Type"] = "application/json"
        request = Request(
            f"{self.base_url}{path}",
            data=data,
            method=method,
            headers=request_headers,
        )
        try:
            response = urlopen(request, timeout=3)
        except HTTPError as error:
            response = error
        try:
            raw = response.read()
            body = json.loads(raw) if raw else {}
            return response.status, body, dict(response.headers)
        finally:
            response.close()

    def test_operator_health_readiness_and_config_journey(self) -> None:
        status, health, _ = self.request("GET", "/healthz")
        self.assertEqual(status, HTTPStatus.OK)
        self.assertEqual(health["status"], "ok")

        status, readiness, _ = self.request("GET", "/readyz")
        self.assertEqual(status, HTTPStatus.OK)
        self.assertEqual(readiness["status"], "ready")
        self.assertTrue(all(readiness["checks"].values()))

        status, payload, _ = self.request("GET", "/v1/config")
        self.assertEqual(status, HTTPStatus.OK)
        self.assertEqual(payload["capabilities"]["persistence"], "sqlite")
        self.assertEqual(
            payload["capabilities"]["bundled_suites"],
            ["flawedbench"],
        )

    def test_eval_owner_runs_and_retrieves_canonical_audit(self) -> None:
        status, run, headers = self.request(
            "POST",
            "/v1/audits",
            {
                "suite": "flawedbench",
                "budget": 200,
                "reported_score": 0.8,
            },
            headers={"X-Request-ID": "journey-canonical"},
        )
        self.assertEqual(status, HTTPStatus.CREATED)
        self.assertEqual(headers["X-Request-ID"], "journey-canonical")
        self.assertEqual(headers["Location"], f"/v1/audits/{run['run_id']}")
        result = run["result"]
        self.assertEqual(result["task_count"], 20)
        self.assertEqual(len(result["findings"]), 5)
        self.assertEqual(result["budget"]["used"], 165)
        self.assertEqual(result["metadata"]["decision_status"], "DETERMINED")
        self.assertEqual(
            (result["trust_band"]["low"], result["trust_band"]["high"]),
            (0.65, 0.9),
        )

        status, stored, _ = self.request(
            "GET",
            f"/v1/audits/{run['run_id']}",
        )
        self.assertEqual(status, HTTPStatus.OK)
        self.assertEqual(stored, run)

        status, findings, _ = self.request(
            "GET",
            f"/v1/audits/{run['run_id']}/findings",
        )
        self.assertEqual(status, HTTPStatus.OK)
        self.assertEqual(len(findings["findings"]), 5)
        self.assertEqual(
            findings["findings"][0]["reproducer"],
            "sieve audit flawedbench --task task-03",
        )

        status, listing, _ = self.request("GET", "/v1/audits?limit=10")
        self.assertEqual(status, HTTPStatus.OK)
        self.assertEqual(listing["audits"][0]["run_id"], run["run_id"])
        self.assertEqual(listing["audits"][0]["finding_count"], 5)

    def test_budget_exhaustion_propagates_undetermined(self) -> None:
        status, run, _ = self.request(
            "POST",
            "/v1/audits",
            {"suite": "flawedbench", "budget": 10},
        )
        self.assertEqual(status, HTTPStatus.CREATED)
        result = run["result"]
        self.assertEqual(result["budget"]["used"], 10)
        self.assertEqual(result["budget"]["skipped"], 155)
        self.assertGreater(result["abstention_rate"], 0.9)
        self.assertEqual(result["metadata"]["decision_status"], "UNDETERMINED")
        self.assertEqual(
            result["metadata"]["task_states"]["task-02"]["status"],
            "UNDETERMINED",
        )

    def test_eval_engineer_can_select_and_reproduce_one_task(self) -> None:
        status, run, _ = self.request(
            "POST",
            "/v1/audits",
            {
                "suite": "flawedbench",
                "task": "task-19",
                "budget": 20,
            },
        )
        self.assertEqual(status, HTTPStatus.CREATED)
        self.assertEqual(run["result"]["task_count"], 1)
        self.assertEqual(run["result"]["budget"]["used"], 12)
        self.assertEqual(
            run["result"]["findings"][0]["verdict"],
            "WEAK_GRADER",
        )

    def test_runs_survive_service_restart(self) -> None:
        _, run, _ = self.request(
            "POST",
            "/v1/audits",
            {"suite": "flawedbench", "task": "task-03"},
        )
        self._stop()
        self._start()
        status, stored, _ = self.request(
            "GET",
            f"/v1/audits/{run['run_id']}",
        )
        self.assertEqual(status, HTTPStatus.OK)
        self.assertEqual(stored["run_id"], run["run_id"])
        self.assertEqual(stored["result"]["findings"][0]["verdict"], "GRADER_FP")

    def test_service_rejects_unsafe_or_invalid_requests(self) -> None:
        status, payload, _ = self.request(
            "POST",
            "/v1/audits",
            {"suite": "../outside", "budget": 200},
        )
        self.assertEqual(status, HTTPStatus.FORBIDDEN)
        self.assertEqual(payload["error"]["code"], "suite_outside_data_root")

        status, payload, _ = self.request(
            "POST",
            "/v1/audits",
            {"suite": "flawedbench", "task": "missing"},
        )
        self.assertEqual(status, HTTPStatus.UNPROCESSABLE_ENTITY)
        self.assertEqual(payload["error"]["code"], "task_not_found")

        status, payload, _ = self.request(
            "POST",
            "/v1/audits",
            {"suite": "flawedbench", "budget": 10_001},
        )
        self.assertEqual(status, HTTPStatus.BAD_REQUEST)
        self.assertEqual(payload["error"]["code"], "invalid_budget")

    def test_pages_origin_receives_explicit_cors_preflight(self) -> None:
        status, _, headers = self.request(
            "OPTIONS",
            "/v1/audits",
            headers={
                "Origin": "https://aneesh-pothuru.github.io",
                "Access-Control-Request-Private-Network": "true",
            },
        )
        self.assertEqual(status, HTTPStatus.NO_CONTENT)
        self.assertEqual(
            headers["Access-Control-Allow-Origin"],
            "https://aneesh-pothuru.github.io",
        )
        self.assertEqual(
            headers["Access-Control-Allow-Private-Network"],
            "true",
        )


class ServiceConfigTests(unittest.TestCase):
    def test_non_loopback_bind_requires_explicit_authority(self) -> None:
        with self.assertRaisesRegex(ValueError, "non-loopback"):
            ServiceConfig(host="0.0.0.0").validate()
        ServiceConfig(host="0.0.0.0", allow_remote=True).validate()


class ServiceProcessJourneyTests(unittest.TestCase):
    def test_installed_style_serve_command_reaches_health(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            command = [
                sys.executable,
                "-m",
                "sieve",
                "serve",
                "--port",
                "0",
                "--db",
                str(Path(directory) / "sieve.sqlite"),
                "--data-root",
                str(ROOT),
            ]
            process = subprocess.Popen(
                command,
                cwd=ROOT,
                env=os.environ.copy(),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            try:
                assert process.stdout is not None
                startup = json.loads(process.stdout.readline())
                self.assertEqual(startup["event"], "service_started")
                response = urlopen(
                    f"http://127.0.0.1:{startup['port']}/healthz",
                    timeout=3,
                )
                try:
                    health = json.loads(response.read())
                finally:
                    response.close()
                self.assertEqual(health["status"], "ok")
            finally:
                process.terminate()
                process.wait(timeout=3)
                if process.stdout is not None:
                    process.stdout.close()
                if process.stderr is not None:
                    process.stderr.close()


class SiteExecutionContractTests(unittest.TestCase):
    def test_audit_desk_separates_replay_from_actual_service_execution(self) -> None:
        html = (ROOT / "docs" / "demo" / "index.html").read_text(encoding="utf-8")
        script = (ROOT / "docs" / "demo" / "app.js").read_text(encoding="utf-8")
        for marker in (
            'id="execution-mode"',
            'value="fixture"',
            'value="live"',
            'id="service-endpoint"',
            'id="connect-service"',
        ):
            self.assertIn(marker, html)
        for marker in (
            'serviceUrl("/readyz")',
            'serviceUrl("/v1/audits")',
            "state.liveEnvelope = envelope",
            "Actual audit completed and persisted.",
            "no replay data was substituted",
        ):
            self.assertIn(marker, script)


if __name__ == "__main__":
    unittest.main()
