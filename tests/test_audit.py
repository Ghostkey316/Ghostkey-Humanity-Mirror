import os
import sys
from datetime import date, timedelta

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(ROOT)
sys.path.append(os.path.join(ROOT, "src"))

import memory_graph
from memory_graph import update_graph
from self_audit import audit_feedback
from streak_tracker import update_streak


def test_drift_detection_and_streak(tmp_path):
    memory_graph._MEMORY_GRAPH = []

    update_graph("I was honest and kind.")
    update_graph("Felt some fear and doubt today.")
    update_graph("Staying honest with compassion.")
    update_graph("I was selfish and afraid.")
    update_graph("Fear returned and I felt doubt.")

    feedback = audit_feedback(memory_graph.get_memory_graph(), window=5)
    assert any("Integrity" in msg for msg in feedback)

    path = tmp_path / "streak.json"
    base = date.today()
    update_streak(date=base.isoformat(), traits=["honesty"], path=str(path))
    update_streak(date=(base + timedelta(days=1)).isoformat(), traits=["honesty"], path=str(path))
    data = update_streak(date=(base + timedelta(days=2)).isoformat(), traits=["compassion"], path=str(path))
    assert data["streak"] == 3
    assert data["trait_streaks"].get("honesty", 0) == 0
    assert data["trait_streaks"].get("compassion", 0) == 1
