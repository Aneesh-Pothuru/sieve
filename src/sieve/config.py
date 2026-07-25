from __future__ import annotations

from dataclasses import asdict, dataclass
import ipaddress
import os
from pathlib import Path


def _env_int(name: str, default: int) -> int:
    value = os.getenv(name)
    return int(value) if value is not None else default


def _env_bool(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().casefold() in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class ServiceConfig:
    host: str = "127.0.0.1"
    port: int = 8765
    database: Path = Path("work/sieve.sqlite")
    data_root: Path = Path(".")
    max_budget: int = 10_000
    max_request_bytes: int = 1_048_576
    allow_remote: bool = False
    allowed_origins: tuple[str, ...] = (
        "http://127.0.0.1",
        "http://localhost",
        "https://aneesh-pothuru.github.io",
    )

    @classmethod
    def from_env(
        cls,
        *,
        host: str | None = None,
        port: int | None = None,
        database: str | Path | None = None,
        data_root: str | Path | None = None,
        allow_remote: bool | None = None,
    ) -> ServiceConfig:
        origins = tuple(
            value.strip().rstrip("/")
            for value in os.getenv(
                "SIEVE_ALLOWED_ORIGINS",
                ",".join(cls.allowed_origins),
            ).split(",")
            if value.strip()
        )
        config = cls(
            host=host or os.getenv("SIEVE_HOST", cls.host),
            port=port if port is not None else _env_int("SIEVE_PORT", cls.port),
            database=Path(
                database
                if database is not None
                else os.getenv("SIEVE_DB", str(cls.database))
            ),
            data_root=Path(
                data_root
                if data_root is not None
                else os.getenv("SIEVE_DATA_ROOT", str(cls.data_root))
            ),
            max_budget=_env_int("SIEVE_MAX_BUDGET", cls.max_budget),
            max_request_bytes=_env_int(
                "SIEVE_MAX_REQUEST_BYTES",
                cls.max_request_bytes,
            ),
            allow_remote=(
                allow_remote
                if allow_remote is not None
                else _env_bool("SIEVE_ALLOW_REMOTE")
            ),
            allowed_origins=origins,
        )
        config.validate()
        return config

    def validate(self) -> None:
        if not 0 <= self.port <= 65_535:
            raise ValueError("port must be between 0 and 65535")
        if self.max_budget < 1:
            raise ValueError("max budget must be positive")
        if self.max_request_bytes < 1:
            raise ValueError("max request size must be positive")
        if not self.allow_remote and not _is_loopback(self.host):
            raise ValueError(
                "refusing a non-loopback bind without --allow-remote or "
                "SIEVE_ALLOW_REMOTE=1"
            )

    def public_dict(self) -> dict[str, object]:
        payload = asdict(self)
        payload["database"] = str(self.database)
        payload["data_root"] = str(self.data_root.resolve())
        payload["allowed_origins"] = list(self.allowed_origins)
        return payload


def _is_loopback(host: str) -> bool:
    if host.casefold() == "localhost":
        return True
    try:
        return ipaddress.ip_address(host).is_loopback
    except ValueError:
        return False
