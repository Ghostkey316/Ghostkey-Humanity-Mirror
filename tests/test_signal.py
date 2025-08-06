import json
import os
import sys
from datetime import date

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(ROOT)
sys.path.append(os.path.join(ROOT, "src"))

import memory_graph
from memory_graph import update_graph
from signal_engine import emit_signal
from streak_tracker import update_streak


def test_signal_output_formatting(tmp_path):
    memory_graph._MEMORY_GRAPH = []
    first = update_graph("Honest and kind reflection.")
    second = update_graph("Fear and doubt appeared.")

    streak_path = tmp_path / "streak.json"
    streak_info = update_streak(date=date.today().isoformat(), traits=second["traits"], path=str(streak_path))

    out_path = tmp_path / "vaultfire_signal.json"
    data = emit_signal(second, streak_info, prev_node=first, path=str(out_path))

    with open(out_path) as f:
        loaded = json.load(f)

    assert "timestamp" in loaded
    assert loaded["top_traits"] == second["traits"]
    assert "reward_multiplier" in loaded
    assert isinstance(loaded["growth"], str)
    assert loaded["streak"] == streak_info["streak"]
