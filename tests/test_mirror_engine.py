import json
from pathlib import Path

from src.mirror_engine import MirrorEngine


def make_entry(ts, text, traits, xp, level):
    return {
        "timestamp": ts,
        "reflection": text,
        "trait_summary": traits,
        "vaultfire_signal": None,
        "xp": xp,
        "level": level,
    }


def test_recall_returns_top_matches(tmp_path):
    archive = tmp_path / "archive.jsonl"
    entries = [
        make_entry("2024-01-01T00:00:00", "I believe in loyalty and honor.", {"loyalty": 5, "courage": 3}, 100, 1),
        make_entry(
            "2024-02-01T00:00:00",
            "Focusing on discipline helps with loyalty.",
            {"discipline": 4, "loyalty": 4},
            150,
            2,
        ),
        make_entry(
            "2024-03-01T00:00:00",
            "Sometimes loyalty conflicts with truth.",
            {"truth": 5, "loyalty": 3},
            200,
            3,
        ),
    ]
    with archive.open("w", encoding="utf-8") as f:
        for e in entries:
            f.write(json.dumps(e) + "\n")

    engine = MirrorEngine(archive)
    matches = engine.recall("What did I used to believe about loyalty?")

    assert len(matches) == 3
    assert matches[0].reflection.startswith("I believe in loyalty")
    # Current entry XP is 200, so first entry should show diff of 100
    assert matches[0].xp_diff == 100
    assert matches[0].trait_drift["loyalty"] == -2  # from 5 to 3
