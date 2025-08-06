from datetime import datetime, timedelta
import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT))

from vaultfire import app as vf


def setup_files(tmp_path, monkeypatch):
    users = tmp_path / "users.json"
    refs = tmp_path / "reflections.json"
    rituals = tmp_path / "rituals.json"
    reactions = tmp_path / "reactions.json"
    users.write_text("{}")
    refs.write_text("[]")
    rituals.write_text("[]")
    reactions.write_text("{}")
    monkeypatch.setattr(vf, "USERS_FILE", users)
    monkeypatch.setattr(vf, "REFLECTIONS_FILE", refs)
    monkeypatch.setattr(vf, "RITUALS_FILE", rituals)
    monkeypatch.setattr(vf, "REACTIONS_FILE", reactions)


def test_chain_ritual_awards_xp(tmp_path, monkeypatch):
    setup_files(tmp_path, monkeypatch)
    base = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
    text = "hope " * 31
    vf.process_reflection("u1", text, True, "#111", now=base)
    vf.process_reflection("u2", text, True, "#222", now=base + timedelta(minutes=10))
    vf.process_reflection("u3", text, True, "#333", now=base + timedelta(minutes=20))
    participants = vf.evaluate_chain_rituals(now=base + timedelta(minutes=20))
    assert set(participants) == {"u1", "u2", "u3"}
    data = json.loads((tmp_path / "users.json").read_text())
    assert data["u1"]["xp"] == 235
    assert data["u2"]["xp"] == 235
    assert data["u3"]["xp"] == 235
    rituals = json.loads((tmp_path / "rituals.json").read_text())
    assert rituals[0]["type"] == "ChainRitual"
    assert set(rituals[0]["participants"]) == {"u1", "u2", "u3"}


def test_chain_ritual_respects_window(tmp_path, monkeypatch):
    setup_files(tmp_path, monkeypatch)
    base = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
    text = "hope " * 31
    vf.process_reflection("u1", text, True, "#111", now=base)
    vf.process_reflection("u2", text, True, "#222", now=base + timedelta(minutes=10))
    vf.process_reflection("u3", text, True, "#333", now=base + timedelta(minutes=31))
    participants = vf.evaluate_chain_rituals(now=base + timedelta(minutes=31))
    assert participants == []
    data = json.loads((tmp_path / "users.json").read_text())
    assert data["u1"]["xp"] == 85
    assert data["u2"]["xp"] == 85
    assert data["u3"]["xp"] == 85


def test_reactions_stored(tmp_path, monkeypatch):
    setup_files(tmp_path, monkeypatch)
    base = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
    vf.process_reflection("u1", "hope " * 31, True, "#111", now=base)
    reflections = json.loads((tmp_path / "reflections.json").read_text())
    ts = reflections[0]["timestamp"]
    vf.add_reaction(ts, "👏")
    vf.add_reaction(ts, "🔥")
    reactions = json.loads((tmp_path / "reactions.json").read_text())
    assert reactions[ts]["👏"] == 1
    assert reactions[ts]["🔥"] == 1
