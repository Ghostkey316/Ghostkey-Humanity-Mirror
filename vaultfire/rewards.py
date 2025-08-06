"""Reward helpers hooking into the Vaultfire simulator."""

from typing import List

from .simulator import simulate_passive_yield
from memory_graph import get_memory_graph

_reflections: List[str] = []
_last_signal: str = ""


def calculate(entry: str) -> str:
    """Update reflection history and emit a reward signal."""

    global _last_signal
    _reflections.append(entry)

    graph = get_memory_graph()
    trait_score = graph[-1]["score"] if graph else 0
    frequency = len(_reflections)
    _last_signal = simulate_passive_yield(trait_score, frequency)
    print(_last_signal)
    return _last_signal


def get_last_signal() -> str:
    """Return the most recent simulated reward signal."""

    return _last_signal
