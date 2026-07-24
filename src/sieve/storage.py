from __future__ import annotations

import json
import sqlite3
from pathlib import Path

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

