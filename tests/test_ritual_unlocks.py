import json
import json
from datetime import datetime, timedelta, timezone
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT))

from vaultfire import app as vf


def setup_files(tmp_path, monkeypatch):
    users_file = tmp_path / "users.json"
    users_file.write_text("{}")
    reflections_file = tmp_path / "reflections.json"
    reflections_file.write_text("[]")
    rituals_file = tmp_path / "rituals.json"
    rituals_file.write_text("[]")
    monkeypatch.setattr(vf, "USERS_FILE", users_file)
    monkeypatch.setattr(vf, "REFLECTIONS_FILE", reflections_file)
    monkeypatch.setattr(vf, "RITUALS_FILE", rituals_file)
    monkeypatch.setattr(vf, "VAULT_LOG", tmp_path / "vaultfire.log")
    return users_file, reflections_file, rituals_file


def test_ritual_of_fire_unlock(tmp_path, monkeypatch):
    setup_files(tmp_path, monkeypatch)
    user = "alice"
    start = datetime(2024, 1, 1, tzinfo=timezone.utc)
    for i in range(7):
        vf.process_reflection(
            user,
            "word " * 8,
            False,
            "#fff",
            now=start + timedelta(days=i),
        )
        vf.check_and_unlock_rituals(user)
    rituals = json.loads(vf.RITUALS_FILE.read_text())
    assert any(r["ritual"] == "Ritual of Fire" for r in rituals)
    users = json.loads(vf.USERS_FILE.read_text())
    assert "Ritual of Fire" in users[user]["rituals"]


def test_eyes_opened_unlock(tmp_path, monkeypatch):
    setup_files(tmp_path, monkeypatch)
    user = "bob"
    vf.process_reflection(
        user, "test reflection", True, "#fff", now=datetime(2024, 1, 1, tzinfo=timezone.utc)
    )
    vf.check_and_unlock_rituals(user, public_signal=True)
    rituals = json.loads(vf.RITUALS_FILE.read_text())
    assert any(r["ritual"] == "Eyes Opened" for r in rituals)


def test_chainbreaker_unlock(tmp_path, monkeypatch):
    setup_files(tmp_path, monkeypatch)
    vf.update_user_record("alice", 500)
    vf.update_user_record("bob", 400)
    vf.update_user_record("carol", 300)
    vf.update_user_record("dave", 100)
    vf.check_and_unlock_rituals("carol", top3=True)
    rituals = json.loads(vf.RITUALS_FILE.read_text())
    assert any(r["user"] == "carol" and r["ritual"] == "Chainbreaker" for r in rituals)
