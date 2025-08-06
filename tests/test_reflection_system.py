from datetime import datetime, timedelta
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT))

from vaultfire import app as vf


def test_process_reflection_awards_xp_and_streak(tmp_path, monkeypatch):
    users_file = tmp_path / "users.json"
    refs_file = tmp_path / "reflections.json"
    users_file.write_text("{}")
    refs_file.write_text("[]")

    monkeypatch.setattr(vf, "USERS_FILE", users_file)
    monkeypatch.setattr(vf, "REFLECTIONS_FILE", refs_file)

    base_time = datetime(2024, 1, 1, 12, 0, 0)
    xp, gain = vf.process_reflection(
        "alice", "hope " * 31, True, "#ff0000", now=base_time
    )
    assert gain == 50 + 10 + 25
    data = json.loads(users_file.read_text())
    assert data["alice"]["xp"] == gain
    assert data["alice"]["streak"] == 1

    xp, gain = vf.process_reflection(
        "alice", "truth " * 31, False, "#00ff00", now=base_time + timedelta(days=1)
    )
    assert gain == 50 + 10 + 25
    data = json.loads(users_file.read_text())
    assert data["alice"]["streak"] == 2
    assert data["alice"]["xp"] == 2 * (50 + 10 + 25)

    reflections = json.loads(refs_file.read_text())
    assert len(reflections) == 2
    assert reflections[0]["public"] is True
    assert reflections[1]["public"] is False
