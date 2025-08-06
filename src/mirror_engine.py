"""AI Mirror module for reflective dialogue using past soul memories."""

from __future__ import annotations

import math
import re
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

from .soul_memory import load_archive


@dataclass
class MirrorMatch:
    """Represents a recalled memory and commentary about its evolution."""

    timestamp: str
    reflection: str
    trait_summary: Dict[str, Any]
    xp: int
    level: int
    similarity: float
    xp_diff: int
    trait_drift: Dict[str, float]

    @property
    def echo(self) -> str:
        return f"Who you were on {self.timestamp} would say: {self.reflection}"  # noqa: D401


class MirrorEngine:
    """Recall past memories similar to a prompt and generate evolution notes."""

    def __init__(self, archive_path: Optional[str | Path] = None):
        self.entries = load_archive(archive_path)
        self.current = self.entries[-1] if self.entries else None

    # --- internal helpers -------------------------------------------------
    _WORD_RE = re.compile(r"\w+")

    @classmethod
    def _vectorize(cls, text: str) -> Counter:
        tokens = cls._WORD_RE.findall(text.lower())
        return Counter(tokens)

    @staticmethod
    def _cosine(a: Counter, b: Counter) -> float:
        if not a or not b:
            return 0.0
        dot = sum(v * b.get(k, 0) for k, v in a.items())
        norm_a = math.sqrt(sum(v * v for v in a.values()))
        norm_b = math.sqrt(sum(v * v for v in b.values()))
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return dot / (norm_a * norm_b)

    # --- public API -------------------------------------------------------
    def recall(self, prompt: str, top_n: int = 3) -> List[MirrorMatch]:
        """Return the top ``n`` memories matching ``prompt``.

        If the archive is empty this returns an empty list.
        """

        if not self.entries:
            return []

        prompt_vec = self._vectorize(prompt)
        scored: List[MirrorMatch] = []
        for entry in self.entries:
            reflection_vec = self._vectorize(entry.get("reflection", ""))
            sim = self._cosine(prompt_vec, reflection_vec)
            xp_then = entry.get("xp", 0)
            xp_now = self.current.get("xp", 0) if self.current else xp_then
            trait_drift = self._trait_drift(entry)
            scored.append(
                MirrorMatch(
                    timestamp=entry.get("timestamp", ""),
                    reflection=entry.get("reflection", ""),
                    trait_summary=entry.get("trait_summary", {}),
                    xp=xp_then,
                    level=entry.get("level", 0),
                    similarity=sim,
                    xp_diff=xp_now - xp_then,
                    trait_drift=trait_drift,
                )
            )

        scored.sort(key=lambda m: m.similarity, reverse=True)
        return scored[:top_n]

    # --- utilities --------------------------------------------------------
    def _trait_drift(self, past_entry: Dict[str, Any]) -> Dict[str, float]:
        """Compute drift in numeric trait values from ``past_entry`` to current."""

        if not self.current:
            return {}

        drift: Dict[str, float] = {}
        past_traits = past_entry.get("trait_summary", {})
        current_traits = self.current.get("trait_summary", {})
        for trait, past_val in past_traits.items():
            cur_val = current_traits.get(trait)
            if isinstance(past_val, (int, float)) and isinstance(cur_val, (int, float)):
                drift[trait] = cur_val - past_val
        return drift
