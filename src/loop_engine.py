import json
import os
from typing import Dict, List

LEVELS_PATH = os.path.join("data", "levels.json")
STATE_PATH = "loop_state.json"


def _load_json(path: str) -> Dict[str, object]:
    with open(path) as f:
        return json.load(f)


def _save_json(data: Dict[str, object], path: str) -> None:
    with open(path, "w") as f:
        json.dump(data, f)


def _load_levels(path: str = LEVELS_PATH) -> Dict[int, str]:
    with open(path) as f:
        raw = json.load(f)
    return {int(k): v for k, v in raw.items()}


def _trait_evolution(current: List[str], previous: List[str]) -> List[str]:
    curr = set(current)
    prev = set(previous)
    notes: List[str] = []
    for t in sorted(curr - prev):
        notes.append(f"{t} emerged")
    for t in sorted(prev - curr):
        notes.append(f"{t} faded")
    return notes


def run_loop(
    reflection_path: str,
    streak_path: str,
    signal_path: str,
    state_path: str = STATE_PATH,
    levels_path: str = LEVELS_PATH,
) -> Dict[str, object]:
    """Run a single belief loop session."""

    reflection = _load_json(reflection_path)
    streak = _load_json(streak_path)
    signal = _load_json(signal_path) if os.path.exists(signal_path) else {}
    prev_state = _load_json(state_path) if os.path.exists(state_path) else {}

    notes = _trait_evolution(
        reflection.get("traits", []), signal.get("top_traits", [])
    )
    xp = streak.get("streak", 0) + reflection.get("score", 0) + len(notes)
    total_xp = prev_state.get("total_xp", 0) + xp

    levels = _load_levels(levels_path)
    max_level = max(levels)
    level = min(max_level, total_xp // 10 + 1)
    level_name = levels.get(level, "Unknown")
    next_threshold = level * 10

    state = {
        "level": level,
        "level_name": level_name,
        "xp_gained": xp,
        "next_level_threshold": next_threshold,
        "trait_evolution": notes,
        "vaultfire_multiplier": signal.get("reward_multiplier", 1.0),
        "total_xp": total_xp,
    }

    _save_json(state, state_path)
    return state
