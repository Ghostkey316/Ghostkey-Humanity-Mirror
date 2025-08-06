import datetime
import json
import os
from typing import Dict, List


DATA_PATH = "streak.json"


def _load(path: str = DATA_PATH) -> Dict[str, object]:
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)
    return {"last_date": "", "streak": 0, "trait_streaks": {}}


def _save(data: Dict[str, object], path: str = DATA_PATH) -> None:
    with open(path, "w") as f:
        json.dump(data, f)


def update_streak(date: str = None, traits: List[str] = None, path: str = DATA_PATH) -> Dict[str, object]:
    if date is None:
        date = datetime.date.today().isoformat()
    if traits is None:
        traits = []

    data = _load(path)
    last_date = data.get("last_date")
    streak = data.get("streak", 0)
    trait_streaks: Dict[str, int] = data.get("trait_streaks", {})

    if last_date:
        last = datetime.date.fromisoformat(last_date)
        today = datetime.date.fromisoformat(date)
        delta = (today - last).days
        if delta == 1:
            streak += 1
        elif delta > 1:
            streak = 1
        # if delta == 0: same day, streak unchanged
    else:
        streak = 1

    for trait in list(trait_streaks.keys()):
        if trait not in traits:
            trait_streaks[trait] = 0
    for trait in traits:
        trait_streaks[trait] = trait_streaks.get(trait, 0) + 1

    data = {"last_date": date, "streak": streak, "trait_streaks": trait_streaks}
    _save(data, path)
    return data


def get_streak(path: str = DATA_PATH) -> Dict[str, object]:
    return _load(path)


def streak_bonus(streak: int) -> float:
    if streak >= 7:
        return 0.2
    if streak >= 3:
        return 0.1
    return 0.0
