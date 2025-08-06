"""Utilities for exporting belief certificates to disk."""

from __future__ import annotations

import json
import os
from typing import Dict, List

from memory_graph import get_memory_graph
from vaultfire import rewards
from vaultfire.simulator import simulate_passive_yield


def _integrity_level(score: int) -> str:
    if score > 6:
        return "legendary"
    if score > 3:
        return "high"
    if score > 0:
        return "medium"
    return "low"


def export_certificate(certificate: Dict[str, object]) -> str:
    """Augment certificate with metadata and save it to ``exports``.

    Parameters
    ----------
    certificate: Dict[str, object]
        Base certificate produced by :func:`identity.bridge.generate_belief_certificate`.

    Returns
    -------
    str
        Path to the written JSON file.
    """

    graph: List[Dict[str, object]] = get_memory_graph()
    traits_summary = sorted({t for node in graph for t in node["traits"]})
    trait_score = sum(node["score"] for node in graph) if graph else 0
    frequency = len(graph)
    vaultfire_output = simulate_passive_yield(trait_score, frequency)

    enriched = dict(certificate)
    enriched.update(
        {
            "integrity_level": _integrity_level(int(certificate.get("integrity_score", 0))),
            "reward_preview": rewards.get_last_signal(),
            "traits_summary": traits_summary,
            "vaultfire_output": vaultfire_output,
        }
    )

    timestamp_safe = enriched["timestamp"].replace(":", "-")
    os.makedirs("exports", exist_ok=True)
    path = f"exports/belief_certificate_{timestamp_safe}.json"
    with open(path, "w") as f:
        json.dump(enriched, f, indent=2)
    return path


__all__ = ["export_certificate"]
