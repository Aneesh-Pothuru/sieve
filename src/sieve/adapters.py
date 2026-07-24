from __future__ import annotations

import json
from pathlib import Path

from .models import AuditTask


class LocalManifestAdapter:
    name = "local"

    def load(self, path: str | Path) -> tuple[str, list[AuditTask]]:
        root = Path(path)
        manifest = root / "manifest.json" if root.is_dir() else root
        data = json.loads(manifest.read_text(encoding="utf-8"))
        tasks = [
            AuditTask(
                id=item["id"],
                prompt=item["prompt"],
                oracle=item.get("oracle"),
                grader=dict(item["grader"]),
                correct_variants=list(item.get("correct_variants", [])),
                wrong_mutations=list(item.get("wrong_mutations", [])),
                label_review=bool(item.get("label_review", False)),
                evidence_tier=item.get("evidence_tier", "declared-oracle"),
                metadata=dict(item.get("metadata", {})),
            )
            for item in data["tasks"]
        ]
        return data.get("name", root.name), tasks


class TerrariumFormatAdapter:
    """Static adapter for the vendored TERRARIUM JSON-subset YAML format."""

    name = "terrarium"

    def load(self, path: str | Path) -> tuple[str, list[AuditTask]]:
        root = Path(path)
        files = [root] if root.is_file() else sorted(root.glob("*.yaml"))
        tasks: list[AuditTask] = []
        for source in files:
            item = json.loads(source.read_text(encoding="utf-8"))
            criterion_ids = [criterion["id"] for criterion in item.get("evals", [])]
            mutation_ids = set(item.get("mutations", {}))
            declared_valid = bool(item.get("oracle")) and set(criterion_ids) == mutation_ids
            tasks.append(
                AuditTask(
                    id=item["id"],
                    prompt=item["instruction"],
                    oracle="DECLARED_VALID" if declared_valid else "DECLARED_INVALID",
                    grader={"mode": "exact", "expected": "DECLARED_VALID"},
                    correct_variants=["DECLARED_VALID"],
                    wrong_mutations=["DECLARED_INVALID", None],
                    label_review=False,
                    evidence_tier="declared-oracle",
                    metadata={
                        "source": str(source),
                        "adapter_scope": "static task-contract audit; world not executed",
                    },
                )
            )
        return f"terrarium:{root.name}", tasks


def load_suite(path: str | Path, format_name: str = "auto") -> tuple[str, list[AuditTask]]:
    root = Path(path)
    if format_name == "local":
        return LocalManifestAdapter().load(root)
    if format_name == "terrarium":
        return TerrariumFormatAdapter().load(root)
    if (root / "manifest.json").exists() or root.name == "manifest.json":
        return LocalManifestAdapter().load(root)
    return TerrariumFormatAdapter().load(root)

