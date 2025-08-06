import os
import sys
from datetime import datetime
from pathlib import Path

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(ROOT)
sys.path.append(os.path.join(ROOT, "src"))

from soul_memory import log_memory, load_archive
from tools import query_memory


def test_archive_write_and_recall(tmp_path):
    archive = tmp_path / "archive.jsonl"
    log_memory(
        "Practiced empathy today",
        {"empathy": 1},
        0.5,
        120,
        2,
        timestamp=datetime(2024, 1, 1, 12, 0, 0),
        archive_path=archive,
    )

    entries = load_archive(archive)
    assert len(entries) == 1
    assert entries[0]["reflection"] == "Practiced empathy today"

    recalled = query_memory.recall("2024-01-01", path=archive)
    assert recalled is not None
    assert recalled["xp"] == 120


def test_search_trait(tmp_path):
    archive = tmp_path / "archive.jsonl"
    log_memory(
        "Helped a friend",
        {"empathy": 1},
        0.7,
        50,
        1,
        timestamp="2024-01-01T00:00:00",
        archive_path=archive,
    )
    log_memory(
        "Spoke honestly",
        {"honesty": 1},
        0.6,
        60,
        1,
        timestamp="2024-01-02T00:00:00",
        archive_path=archive,
    )

    results = query_memory.search_trait("empathy", path=archive)
    assert len(results) == 1
    assert results[0]["trait_summary"].get("empathy") == 1
