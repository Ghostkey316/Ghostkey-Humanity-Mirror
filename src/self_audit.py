from collections import Counter
from typing import Dict, List


def audit_feedback(graph: List[Dict[str, object]], window: int = 5) -> List[str]:
    """Analyze recent reflections and emit drift messages.

    Args:
        graph: List of reflection nodes with ``score``, ``sentiment`` and ``traits``.
        window: Number of recent reflections to scan.

    Returns:
        List of feedback strings describing moral drift and trends.
    """

    recent = graph[-window:]
    if len(recent) < 2:
        return ["Not enough data for self-audit"]

    messages: List[str] = []

    # Integrity drift based on score difference
    first_score = recent[0].get("score", 0)
    last_score = recent[-1].get("score", 0)
    if last_score != first_score:
        diff = last_score - first_score
        level = "severe" if abs(diff) >= 2 else "light"
        direction = "rising" if diff > 0 else "falling"
        messages.append(f"Integrity {direction} ({level})")

    # Trait frequency drift
    half = max(1, len(recent) // 2)
    first_traits = Counter(t for n in recent[:half] for t in n.get("traits", []))
    second_traits = Counter(t for n in recent[half:] for t in n.get("traits", []))
    all_traits = set(first_traits) | set(second_traits)
    for trait in all_traits:
        diff = second_traits.get(trait, 0) - first_traits.get(trait, 0)
        if diff != 0:
            level = "severe" if abs(diff) >= 2 else "light"
            direction = "Leaning into" if diff > 0 else "Drifting from"
            messages.append(f"{direction} {trait} ({level})")

    # Sentiment shift
    first_sent = recent[0].get("sentiment")
    last_sent = recent[-1].get("sentiment")
    if first_sent != last_sent:
        messages.append(f"Sentiment shift: {first_sent} -> {last_sent}")

    return messages
