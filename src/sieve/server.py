from __future__ import annotations

from datetime import UTC, datetime
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import re
import sys
from typing import Any
from urllib.parse import parse_qs, urlparse
from uuid import uuid4

from . import __version__
from .adapters import load_suite
from .audit import audit_suite
from .config import ServiceConfig
from .storage import AuditStore

PACKAGE_ROOT = Path(__file__).resolve().parent
BUNDLED_FLAWEDBENCH = PACKAGE_ROOT / "data" / "flawedbench"
RUN_PATH = re.compile(r"^/v1/audits/(audit_[0-9a-f]{32})$")
FINDINGS_PATH = re.compile(
    r"^/v1/audits/(audit_[0-9a-f]{32})/findings$"
)


class RequestError(Exception):
    def __init__(self, status: HTTPStatus, code: str, message: str):
        super().__init__(message)
        self.status = status
        self.code = code
        self.message = message


class SieveHTTPServer(ThreadingHTTPServer):
    daemon_threads = True
    allow_reuse_address = True

    def __init__(self, config: ServiceConfig):
        config.validate()
        self.config = config
        self.store = AuditStore(config.database)
        super().__init__((config.host, config.port), SieveRequestHandler)

    def readiness(self) -> tuple[bool, dict[str, object]]:
        root = self.config.data_root.resolve()
        checks = {
            "database": self.store.ready(),
            "data_root": root.exists() and root.is_dir(),
            "bundled_fixture": (
                BUNDLED_FLAWEDBENCH / "manifest.json"
            ).is_file(),
        }
        return all(checks.values()), checks


class SieveRequestHandler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"
    server: SieveHTTPServer

    def do_OPTIONS(self) -> None:
        self._send_json(HTTPStatus.NO_CONTENT, None)

    def do_GET(self) -> None:
        request_id = self._request_id()
        try:
            parsed = urlparse(self.path)
            if parsed.path == "/":
                self._send_json(
                    HTTPStatus.OK,
                    {
                        "service": "sieve",
                        "version": __version__,
                        "api_version": "v1",
                        "links": {
                            "health": "/healthz",
                            "readiness": "/readyz",
                            "config": "/v1/config",
                            "audits": "/v1/audits",
                        },
                    },
                    request_id=request_id,
                )
                return
            if parsed.path == "/healthz":
                self._send_json(
                    HTTPStatus.OK,
                    {
                        "status": "ok",
                        "service": "sieve",
                        "version": __version__,
                    },
                    request_id=request_id,
                )
                return
            if parsed.path == "/readyz":
                ready, checks = self.server.readiness()
                self._send_json(
                    HTTPStatus.OK if ready else HTTPStatus.SERVICE_UNAVAILABLE,
                    {"status": "ready" if ready else "not_ready", "checks": checks},
                    request_id=request_id,
                )
                return
            if parsed.path == "/v1/config":
                self._send_json(
                    HTTPStatus.OK,
                    {
                        "api_version": "v1",
                        "config": self.server.config.public_dict(),
                        "capabilities": {
                            "adapters": ["local", "terrarium"],
                            "bundled_suites": ["flawedbench"],
                            "persistence": "sqlite",
                            "execution": "synchronous",
                            "model_calls": False,
                        },
                    },
                    request_id=request_id,
                )
                return
            if parsed.path == "/v1/audits":
                values = parse_qs(parsed.query)
                limit = self._integer(
                    values.get("limit", ["50"])[0],
                    "limit",
                    minimum=1,
                    maximum=100,
                )
                self._send_json(
                    HTTPStatus.OK,
                    {
                        "api_version": "v1",
                        "audits": self.server.store.list(limit),
                    },
                    request_id=request_id,
                )
                return
            finding_match = FINDINGS_PATH.fullmatch(parsed.path)
            if finding_match:
                run_id = finding_match.group(1)
                findings = self.server.store.findings(run_id)
                if findings is None:
                    raise RequestError(
                        HTTPStatus.NOT_FOUND,
                        "run_not_found",
                        f"audit run not found: {run_id}",
                    )
                self._send_json(
                    HTTPStatus.OK,
                    {
                        "api_version": "v1",
                        "run_id": run_id,
                        "findings": findings,
                    },
                    request_id=request_id,
                )
                return
            run_match = RUN_PATH.fullmatch(parsed.path)
            if run_match:
                run_id = run_match.group(1)
                payload = self.server.store.get(run_id)
                if payload is None:
                    raise RequestError(
                        HTTPStatus.NOT_FOUND,
                        "run_not_found",
                        f"audit run not found: {run_id}",
                    )
                self._send_json(
                    HTTPStatus.OK,
                    payload,
                    request_id=request_id,
                )
                return
            raise RequestError(
                HTTPStatus.NOT_FOUND,
                "route_not_found",
                f"route not found: {parsed.path}",
            )
        except RequestError as exc:
            self._send_error(exc, request_id)
        except Exception as exc:
            self.log_error("unhandled request error: %r", exc)
            self._send_error(
                RequestError(
                    HTTPStatus.INTERNAL_SERVER_ERROR,
                    "internal_error",
                    "the service could not complete the request",
                ),
                request_id,
            )

    def do_POST(self) -> None:
        request_id = self._request_id()
        try:
            if urlparse(self.path).path != "/v1/audits":
                raise RequestError(
                    HTTPStatus.NOT_FOUND,
                    "route_not_found",
                    f"route not found: {urlparse(self.path).path}",
                )
            body = self._read_json()
            request = self._audit_request(body)
            suite_path, suite_reference = self._resolve_suite(request["suite"])
            try:
                suite_name, tasks = load_suite(suite_path, request["format"])
            except (FileNotFoundError, IsADirectoryError, json.JSONDecodeError) as exc:
                raise RequestError(
                    HTTPStatus.UNPROCESSABLE_ENTITY,
                    "invalid_suite",
                    f"suite could not be loaded: {exc}",
                ) from exc
            task_filter = request["task"]
            if task_filter:
                tasks = [task for task in tasks if task.id == task_filter]
                if not tasks:
                    raise RequestError(
                        HTTPStatus.UNPROCESSABLE_ENTITY,
                        "task_not_found",
                        f"task not found in suite: {task_filter}",
                    )
            if not tasks:
                raise RequestError(
                    HTTPStatus.UNPROCESSABLE_ENTITY,
                    "empty_suite",
                    "suite contains no auditable tasks",
                )
            result = audit_suite(
                suite_name,
                tasks,
                request["budget"],
                request["reported_score"],
                suite_reference=suite_reference,
            )
            envelope = self.server.store.create(
                result,
                suite_reference=suite_reference,
                task_filter=task_filter,
                budget_limit=request["budget"],
                reported_score=request["reported_score"],
                request=request,
            )
            self._send_json(
                HTTPStatus.CREATED,
                envelope,
                headers={
                    "Location": f"/v1/audits/{envelope['run_id']}",
                },
                request_id=request_id,
            )
        except RequestError as exc:
            self._send_error(exc, request_id)
        except Exception as exc:
            self.log_error("unhandled request error: %r", exc)
            self._send_error(
                RequestError(
                    HTTPStatus.INTERNAL_SERVER_ERROR,
                    "internal_error",
                    "the service could not complete the request",
                ),
                request_id,
            )

    def _audit_request(self, body: object) -> dict[str, Any]:
        if not isinstance(body, dict):
            raise RequestError(
                HTTPStatus.BAD_REQUEST,
                "invalid_request",
                "request body must be a JSON object",
            )
        allowed = {"suite", "format", "budget", "reported_score", "task"}
        unknown = sorted(set(body) - allowed)
        if unknown:
            raise RequestError(
                HTTPStatus.BAD_REQUEST,
                "unknown_fields",
                f"unknown request fields: {', '.join(unknown)}",
            )
        suite = body.get("suite", "flawedbench")
        if not isinstance(suite, str) or not suite.strip():
            raise RequestError(
                HTTPStatus.BAD_REQUEST,
                "invalid_suite_reference",
                "suite must be a non-empty string",
            )
        format_name = body.get("format", "auto")
        if format_name not in {"auto", "local", "terrarium"}:
            raise RequestError(
                HTTPStatus.BAD_REQUEST,
                "invalid_format",
                "format must be auto, local, or terrarium",
            )
        budget = self._integer(
            body.get("budget", 200),
            "budget",
            minimum=0,
            maximum=self.server.config.max_budget,
        )
        reported_score = body.get("reported_score", 0.8)
        if (
            isinstance(reported_score, bool)
            or not isinstance(reported_score, (int, float))
            or not 0 <= float(reported_score) <= 1
        ):
            raise RequestError(
                HTTPStatus.BAD_REQUEST,
                "invalid_reported_score",
                "reported_score must be a number between 0 and 1",
            )
        task = body.get("task")
        if task is not None and (not isinstance(task, str) or not task.strip()):
            raise RequestError(
                HTTPStatus.BAD_REQUEST,
                "invalid_task",
                "task must be a non-empty string when supplied",
            )
        return {
            "suite": suite.strip(),
            "format": format_name,
            "budget": budget,
            "reported_score": float(reported_score),
            "task": task.strip() if isinstance(task, str) else None,
        }

    def _resolve_suite(self, reference: str) -> tuple[Path, str]:
        if reference.casefold() in {"flawedbench", "builtin:flawedbench"}:
            return BUNDLED_FLAWEDBENCH, "flawedbench"
        root = self.server.config.data_root.resolve()
        candidate = Path(reference)
        resolved = (
            candidate.resolve()
            if candidate.is_absolute()
            else (root / candidate).resolve()
        )
        try:
            resolved.relative_to(root)
        except ValueError as exc:
            raise RequestError(
                HTTPStatus.FORBIDDEN,
                "suite_outside_data_root",
                "suite must resolve inside the configured data root",
            ) from exc
        if not resolved.exists():
            raise RequestError(
                HTTPStatus.NOT_FOUND,
                "suite_not_found",
                f"suite not found: {reference}",
            )
        return resolved, reference

    def _read_json(self) -> object:
        content_type = self.headers.get("Content-Type", "").split(";", 1)[0]
        if content_type != "application/json":
            raise RequestError(
                HTTPStatus.UNSUPPORTED_MEDIA_TYPE,
                "content_type_required",
                "Content-Type must be application/json",
            )
        length = self._integer(
            self.headers.get("Content-Length", "0"),
            "Content-Length",
            minimum=1,
            maximum=self.server.config.max_request_bytes,
        )
        raw = self.rfile.read(length)
        try:
            return json.loads(raw)
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise RequestError(
                HTTPStatus.BAD_REQUEST,
                "invalid_json",
                "request body is not valid JSON",
            ) from exc

    def _integer(
        self,
        value: object,
        field: str,
        *,
        minimum: int,
        maximum: int,
    ) -> int:
        if isinstance(value, bool):
            parsed = -1
        else:
            try:
                parsed = int(value)
            except (TypeError, ValueError):
                parsed = -1
        if parsed < minimum or parsed > maximum:
            raise RequestError(
                HTTPStatus.BAD_REQUEST,
                f"invalid_{field.casefold().replace('-', '_')}",
                f"{field} must be an integer from {minimum} to {maximum}",
            )
        return parsed

    def _request_id(self) -> str:
        requested = self.headers.get("X-Request-ID", "")
        if re.fullmatch(r"[A-Za-z0-9._-]{1,128}", requested):
            return requested
        return f"req_{uuid4().hex}"

    def _send_error(self, error: RequestError, request_id: str) -> None:
        self.close_connection = True
        self._send_json(
            error.status,
            {
                "error": {
                    "code": error.code,
                    "message": error.message,
                    "request_id": request_id,
                }
            },
            request_id=request_id,
        )

    def _send_json(
        self,
        status: HTTPStatus,
        payload: object,
        *,
        headers: dict[str, str] | None = None,
        request_id: str | None = None,
    ) -> None:
        encoded = (
            b""
            if payload is None
            else (json.dumps(payload, sort_keys=True) + "\n").encode("utf-8")
        )
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(encoded)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        if request_id:
            self.send_header("X-Request-ID", request_id)
        origin = self.headers.get("Origin", "").rstrip("/")
        if origin and origin in self.server.config.allowed_origins:
            self.send_header("Access-Control-Allow-Origin", origin)
            self.send_header("Vary", "Origin")
            self.send_header(
                "Access-Control-Allow-Headers",
                "Content-Type, X-Request-ID",
            )
            self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
            if (
                self.headers.get("Access-Control-Request-Private-Network")
                == "true"
            ):
                self.send_header("Access-Control-Allow-Private-Network", "true")
        for key, value in (headers or {}).items():
            self.send_header(key, value)
        self.end_headers()
        if encoded:
            self.wfile.write(encoded)

    def log_message(self, format: str, *args: object) -> None:
        event = {
            "timestamp": datetime.now(UTC).isoformat(),
            "remote": self.client_address[0],
            "method": self.command,
            "path": self.path,
            "message": format % args,
        }
        print(json.dumps(event, sort_keys=True), file=sys.stderr, flush=True)


def serve(config: ServiceConfig) -> None:
    server = SieveHTTPServer(config)
    host, port = server.server_address[:2]
    print(
        json.dumps(
            {
                "event": "service_started",
                "host": host,
                "port": port,
                "database": str(config.database),
                "data_root": str(config.data_root.resolve()),
            },
            sort_keys=True,
        ),
        flush=True,
    )
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
