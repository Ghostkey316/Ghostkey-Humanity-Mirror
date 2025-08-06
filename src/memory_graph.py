"""Simple in-memory graph with sentiment and trait tagging."""

from typing import Dict, List

# Store all reflections with their analysis for later dashboard use
_MEMORY_GRAPH: List[Dict[str, object]] = []

# Keyword based mapping for quick trait extraction
_TRAIT_KEYWORDS = {
    "honesty": ["honest", "truth", "transparent"],
    "compassion": ["compassion", "empathy", "kind"],
    "fear": ["fear", "afraid", "scared", "anxious"],
    "doubt": ["doubt", "uncertain", "unsure"],
}

_POSITIVE = {"honesty", "compassion"}
_NEGATIVE = {"fear", "doubt"}


def _analyze(entry: str) -> Dict[str, object]:
    """Return sentiment and moral traits for an entry."""

    text = entry.lower()

    traits = [
        trait
        for trait, keywords in _TRAIT_KEYWORDS.items()
        if any(word in text for word in keywords)
    ]

    positive_hits = any(word in text for word in ["good", "great", "love"])
    negative_hits = any(word in text for word in ["bad", "terrible", "hate"])
    sentiment = "neutral"
    if positive_hits and not negative_hits:
        sentiment = "positive"
    elif negative_hits and not positive_hits:
        sentiment = "negative"

    score = sum(1 for t in traits if t in _POSITIVE) - sum(
        1 for t in traits if t in _NEGATIVE
    )

    return {
        "text": entry,
        "sentiment": sentiment,
        "traits": traits,
        "score": score,
    }


def update_graph(entry: str) -> Dict[str, object]:
    """Analyze entry and append to the memory graph."""

    node = _analyze(entry)
    _MEMORY_GRAPH.append(node)
    print("🧠 Memory graph updated: entry logged for future moral map.")
    return node


def get_memory_graph() -> List[Dict[str, object]]:
    """Return all recorded memory graph nodes."""

    return list(_MEMORY_GRAPH)
