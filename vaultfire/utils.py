from __future__ import annotations

"""Utility helpers for Vaultfire."""

from datetime import datetime, timezone
from pathlib import Path
import json
from typing import Any


def utcnow() -> datetime:
    """Return a timezone aware ``datetime`` in UTC."""
    return datetime.now(timezone.utc)


def read_json(path: Path, default: Any) -> Any:
    """Read JSON from ``path`` returning ``default`` on error."""
    try:
        return json.loads(path.read_text())
    except Exception:
        return default


def write_json(path: Path, data: Any) -> None:
    """Write ``data`` as pretty JSON to ``path``."""
    path.write_text(json.dumps(data, indent=2))
