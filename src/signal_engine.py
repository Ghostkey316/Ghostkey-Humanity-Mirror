import json
from datetime import datetime
from typing import Dict, Optional

from streak_tracker import streak_bonus


def _growth_summary(current: Dict[str, object], previous: Optional[Dict[str, object]]) -> str:
    if not previous:
        return ", ".join(f"+1 {t}" for t in current.get("traits", []))

    summary = []
    prev_traits = set(previous.get("traits", []))
    curr_traits = set(current.get("traits", []))
    for t in curr_traits - prev_traits:
        summary.append(f"+1 {t}")
    for t in prev_traits - curr_traits:
        summary.append(f"-1 {t}")
    diff = current.get("score", 0) - previous.get("score", 0)
    if diff:
        sign = "+" if diff > 0 else "-"
        summary.append(f"{sign}{abs(diff)} integrity")
    return ", ".join(summary)


def emit_signal(
    node: Dict[str, object],
    streak_info: Dict[str, object],
    prev_node: Optional[Dict[str, object]] = None,
    path: str = "vaultfire_signal.json",
) -> Dict[str, object]:
    bonus = streak_bonus(streak_info.get("streak", 0))
    multiplier = round(1 + node.get("score", 0) * 0.1 + bonus, 2)
    data = {
        "timestamp": datetime.utcnow().isoformat(),
        "top_traits": node.get("traits", []),
        "reward_multiplier": multiplier,
        "growth": _growth_summary(node, prev_node),
        "streak": streak_info.get("streak", 0),
        "trait_streaks": streak_info.get("trait_streaks", {}),
    }
    with open(path, "w") as f:
        json.dump(data, f)
    return data
