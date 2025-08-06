"""Identity bridge linking reflections and reward signals to anchors."""

from __future__ import annotations

from datetime import datetime
from typing import Dict, List, Optional

from memory_graph import get_memory_graph
from vaultfire import rewards


def generate_belief_certificate(
    ens: str, cb_id: str, biometric_hash: Optional[str] = None
) -> Dict[str, object]:
    """Return a belief certificate with identity anchors and history.

    Parameters
    ----------
    ens: str
        ENS tag for the user (e.g. ``ghostkey316.eth``).
    cb_id: str
        cb.id tag for the user (e.g. ``bpow20.cb.id``).
    biometric_hash: Optional[str]
        Placeholder for future biometric syncs.
    """

    graph: List[Dict[str, object]] = get_memory_graph()
    recent_reflections = [node["text"] for node in graph[-3:]]
    integrity_score = sum(node["score"] for node in graph[-3:]) if graph else 0

    certificate = {
        "timestamp": datetime.utcnow().isoformat(),
        "ens": ens,
        "cb_id": cb_id,
        "biometric_hash": biometric_hash,
        "integrity_score": integrity_score,
        "recent_reflections": recent_reflections,
        "reward_signal": rewards.get_last_signal(),
    }
    return certificate


__all__ = ["generate_belief_certificate"]
