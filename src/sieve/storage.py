from __future__ import annotations

from contextlib import contextmanager
import json
import sqlite3
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Iterator
from uuid import uuid4

from .models import AuditResult


def save_audit(result: AuditResult, path: str | Path) -> Path:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(destination)
    try:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS audits(
              suite_name TEXT PRIMARY KEY, task_count INTEGER NOT NULL,
              finding_count INTEGER NOT NULL, payload_json TEXT NOT NULL
            )
            """
        )
        connection.execute(
            """
            INSERT INTO audits(suite_name,task_count,finding_count,payload_json)
            VALUES(?,?,?,?)
            ON CONFLICT(suite_name) DO UPDATE SET
              task_count=excluded.task_count,
              finding_count=excluded.finding_count,
              payload_json=excluded.payload_json
            """,
            (
                result.suite_name,
                result.task_count,
                len(result.findings),
                json.dumps(result.to_dict(), sort_keys=True),
            ),
        )
        connection.commit()
    finally:
        connection.close()
    return destination


class AuditStore:
    """Immutable, queryable audit-run persistence for the local service."""

    def __init__(self, path: str | Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.path, timeout=5)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys=ON")
        connection.execute("PRAGMA busy_timeout=5000")
        return connection

    @contextmanager
    def _connection(self) -> Iterator[sqlite3.Connection]:
        connection = self._connect()
        try:
            with connection:
                yield connection
        finally:
            connection.close()

    def _initialize(self) -> None:
        with self._connection() as connection:
            connection.execute("PRAGMA journal_mode=WAL")
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS audit_runs(
                  run_id TEXT PRIMARY KEY,
                  created_at TEXT NOT NULL,
                  suite_reference TEXT NOT NULL,
                  task_filter TEXT,
                  budget_limit INTEGER NOT NULL,
                  reported_score REAL NOT NULL,
                  suite_name TEXT NOT NULL,
                  task_count INTEGER NOT NULL,
                  finding_count INTEGER NOT NULL,
                  decision_status TEXT NOT NULL,
                  payload_json TEXT NOT NULL
                )
                """
            )
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS run_findings(
                  run_id TEXT NOT NULL REFERENCES audit_runs(run_id)
                    ON DELETE CASCADE,
                  ordinal INTEGER NOT NULL,
                  task_id TEXT NOT NULL,
                  verdict TEXT NOT NULL,
                  severity TEXT NOT NULL,
                  payload_json TEXT NOT NULL,
                  PRIMARY KEY(run_id, ordinal)
                )
                """
            )
            connection.execute(
                """
                CREATE INDEX IF NOT EXISTS audit_runs_created_at
                ON audit_runs(created_at DESC)
                """
            )
            connection.execute(
                """
                CREATE INDEX IF NOT EXISTS run_findings_task
                ON run_findings(task_id, verdict)
                """
            )

    def ready(self) -> bool:
        try:
            with self._connection() as connection:
                connection.execute("SELECT 1").fetchone()
                connection.execute("BEGIN IMMEDIATE")
                connection.execute("ROLLBACK")
            return True
        except sqlite3.Error:
            return False

    def create(
        self,
        result: AuditResult,
        *,
        suite_reference: str,
        task_filter: str | None,
        budget_limit: int,
        reported_score: float,
        request: dict[str, Any],
    ) -> dict[str, Any]:
        run_id = f"audit_{uuid4().hex}"
        created_at = datetime.now(UTC).isoformat()
        envelope = {
            "api_version": "v1",
            "run_id": run_id,
            "created_at": created_at,
            "request": request,
            "result": result.to_dict(),
        }
        encoded = json.dumps(envelope, sort_keys=True)
        with self._connection() as connection:
            connection.execute(
                """
                INSERT INTO audit_runs(
                  run_id,created_at,suite_reference,task_filter,budget_limit,
                  reported_score,suite_name,task_count,finding_count,
                  decision_status,payload_json
                ) VALUES(?,?,?,?,?,?,?,?,?,?,?)
                """,
                (
                    run_id,
                    created_at,
                    suite_reference,
                    task_filter,
                    budget_limit,
                    reported_score,
                    result.suite_name,
                    result.task_count,
                    len(result.findings),
                    result.metadata["decision_status"],
                    encoded,
                ),
            )
            connection.executemany(
                """
                INSERT INTO run_findings(
                  run_id,ordinal,task_id,verdict,severity,payload_json
                ) VALUES(?,?,?,?,?,?)
                """,
                [
                    (
                        run_id,
                        ordinal,
                        finding.task_id,
                        finding.verdict,
                        finding.severity,
                        json.dumps(finding_payload, sort_keys=True),
                    )
                    for ordinal, finding_payload in enumerate(
                        envelope["result"]["findings"]
                    )
                    for finding in (result.findings[ordinal],)
                ],
            )
        return envelope

    def get(self, run_id: str) -> dict[str, Any] | None:
        with self._connection() as connection:
            row = connection.execute(
                "SELECT payload_json FROM audit_runs WHERE run_id=?",
                (run_id,),
            ).fetchone()
        return json.loads(row["payload_json"]) if row else None

    def findings(self, run_id: str) -> list[dict[str, Any]] | None:
        with self._connection() as connection:
            exists = connection.execute(
                "SELECT 1 FROM audit_runs WHERE run_id=?",
                (run_id,),
            ).fetchone()
            if not exists:
                return None
            rows = connection.execute(
                """
                SELECT payload_json FROM run_findings
                WHERE run_id=? ORDER BY ordinal
                """,
                (run_id,),
            ).fetchall()
        return [json.loads(row["payload_json"]) for row in rows]

    def list(self, limit: int = 50) -> list[dict[str, Any]]:
        with self._connection() as connection:
            rows = connection.execute(
                """
                SELECT run_id,created_at,suite_reference,task_filter,
                       budget_limit,reported_score,suite_name,task_count,
                       finding_count,decision_status
                FROM audit_runs
                ORDER BY created_at DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()
        return [dict(row) for row in rows]
