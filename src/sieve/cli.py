from __future__ import annotations

import argparse
import json
from pathlib import Path

from .adapters import load_suite
from .audit import audit_suite
from .report import render
from .storage import save_audit

ROOT = Path(__file__).resolve().parents[2]
PACKAGE_ROOT = Path(__file__).resolve().parent
DEMO_SUITE = (
    ROOT / "flawedbench"
    if (ROOT / "flawedbench").exists()
    else PACKAGE_ROOT / "data" / "flawedbench"
)


def _run_audit(args: argparse.Namespace, default_suite: Path | None = None) -> int:
    requested_suite = getattr(args, "suite", None)
    suite_path = Path(requested_suite) if requested_suite else default_suite
    if suite_path is None:
        raise ValueError("suite path is required")
    if requested_suite == "flawedbench" and not suite_path.exists():
        suite_path = DEMO_SUITE
    suite_name, tasks = load_suite(suite_path, args.format)
    if getattr(args, "task", None):
        tasks = [task for task in tasks if task.id == args.task]
        if not tasks:
            raise SystemExit(f"task not found in suite: {args.task}")
    if not tasks:
        raise SystemExit(f"suite contains no auditable tasks: {suite_path}")
    suite_reference = (
        "flawedbench"
        if suite_path.resolve() == DEMO_SUITE.resolve()
        else str(suite_path)
    )
    result = audit_suite(
        suite_name,
        tasks,
        args.budget,
        args.reported_score,
        suite_reference=suite_reference,
    )
    if args.output:
        render(result, args.output)
    if args.json_output:
        destination = Path(args.json_output)
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(
            json.dumps(result.to_dict(), indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    if args.db:
        save_audit(result, args.db)
    print(
        f"{result.suite_name}: {result.task_count} tasks · "
        f"{len(result.findings)} findings · "
        f"budget {result.budget['used']}/{result.budget['limit']} · "
        f"skipped {result.budget['skipped']}"
    )
    for finding in result.findings:
        print(f"{finding.verdict:18} {finding.task_id:10} {finding.detail}")
    band = result.trust_band
    print(
        f"trust-adjusted: {band['reported']:.0%} -> "
        f"{band['low']:.0%}–{band['high']:.0%}"
    )
    if result.metadata["decision_status"] == "UNDETERMINED":
        print(
            "decision status: UNDETERMINED "
            f"({result.abstention_rate:.1%} probe abstention)"
        )
    return 0


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(prog="sieve")
    commands = root.add_subparsers(dest="command", required=True)
    for name in ("demo", "audit"):
        command = commands.add_parser(name)
        if name == "audit":
            command.add_argument("suite")
        command.add_argument("--format", choices=("auto", "local", "terrarium"), default="auto")
        command.add_argument("--budget", type=int, default=200)
        command.add_argument("--reported-score", type=float, default=0.80)
        command.add_argument("--output")
        command.add_argument("--json-output")
        command.add_argument("--db")
        command.add_argument("--task")
        if name == "demo":
            command.set_defaults(
                handler=lambda args: _run_audit(args, DEMO_SUITE),
                output="docs/demo/report.html",
            )
        else:
            command.set_defaults(handler=_run_audit)
    return root


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    if args.budget < 0:
        raise SystemExit("--budget must be non-negative")
    return int(args.handler(args))
