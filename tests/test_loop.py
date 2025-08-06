import json
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(ROOT)
sys.path.append(os.path.join(ROOT, "src"))

from loop_engine import run_loop


def _write(path, data):
    with open(path, "w") as f:
        json.dump(data, f)


def test_loop_engine_xp_level_and_traits(tmp_path):
    levels_path = tmp_path / "levels.json"
    _write(
        levels_path,
        {"1": "Moral Novice", "2": "Ethical Explorer", "3": "Compassionate Thinker"},
    )

    reflection_path = tmp_path / "reflection.json"
    streak_path = tmp_path / "streak.json"
    signal_path = tmp_path / "signal.json"
    state_path = tmp_path / "loop_state.json"

    _write(signal_path, {"top_traits": ["honesty"], "reward_multiplier": 1.0})
    _write(streak_path, {"streak": 3})
    _write(reflection_path, {"score": 2, "traits": ["honesty", "compassion"]})

    state1 = run_loop(
        str(reflection_path),
        str(streak_path),
        str(signal_path),
        state_path=str(state_path),
        levels_path=str(levels_path),
    )

    assert state1["xp_gained"] == 6
    assert state1["level"] == 1
    assert "compassion emerged" in state1["trait_evolution"]

    _write(signal_path, {"top_traits": ["honesty", "compassion"], "reward_multiplier": 1.2})
    _write(streak_path, {"streak": 4})
    _write(reflection_path, {"score": 1, "traits": ["honesty"]})

    state2 = run_loop(
        str(reflection_path),
        str(streak_path),
        str(signal_path),
        state_path=str(state_path),
        levels_path=str(levels_path),
    )

    assert state2["xp_gained"] == 6
    assert state2["level"] == 2
    assert state2["level_name"] == "Ethical Explorer"
    assert "compassion faded" in state2["trait_evolution"]
