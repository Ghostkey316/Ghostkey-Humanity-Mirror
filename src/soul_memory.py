"""Persistent archive for reflections and moral state."""

from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

# Default path for the archive
ARCHIVE_PATH = (
    Path(__file__).resolve().parent.parent / "data" / "archive.jsonl"
)


@dataclass
class MemoryEntry:
    """Represents a single soul memory snapshot."""

    timestamp: str
    reflection: str
    trait_summary: Dict[str, Any]
    vaultfire_signal: Any
    xp: int
    level: int


def log_memory(
    reflection: str,
    trait_summary: Dict[str, Any],
    vaultfire_signal: Any,
    xp: int,
    level: int,
    *,
    timestamp: Optional[datetime | str] = None,
    archive_path: Path | str | None = None,
) -> MemoryEntry:
    """Append a new memory entry to the archive.

    Args:
        reflection: User's written reflection.
        trait_summary: Summary from trait audit.
        vaultfire_signal: Signal emitted this session.
        xp: XP at time of reflection.
        level: Level at time of reflection.
        timestamp: Optional timestamp, defaults to current UTC time.
        archive_path: Optional override path for the archive.

    Returns:
        MemoryEntry: The entry that was written.
    """

    if archive_path is None:
        archive_path = ARCHIVE_PATH
    archive_path = Path(archive_path)
    archive_path.parent.mkdir(parents=True, exist_ok=True)

    if timestamp is None:
        ts = datetime.utcnow().isoformat()
    elif isinstance(timestamp, datetime):
        ts = timestamp.isoformat()
    else:
        ts = str(timestamp)

    entry = MemoryEntry(
        timestamp=ts,
        reflection=reflection,
        trait_summary=trait_summary,
        vaultfire_signal=vaultfire_signal,
        xp=xp,
        level=level,
    )

    with archive_path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(asdict(entry)) + "\n")

    return entry


def load_archive(archive_path: Path | str | None = None) -> List[Dict[str, Any]]:
    """Load all memory entries from the archive."""

    if archive_path is None:
        archive_path = ARCHIVE_PATH
    archive_path = Path(archive_path)

    if not archive_path.exists():
        return []

    entries: List[Dict[str, Any]] = []
    with archive_path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                entries.append(json.loads(line))
            except json.JSONDecodeError:
                # Skip malformed lines
                continue
    return entries
