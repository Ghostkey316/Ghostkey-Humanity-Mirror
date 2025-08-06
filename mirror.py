"""CLI utility for the AI Mirror reflection engine."""

from __future__ import annotations

import argparse
import json

from src.mirror_engine import MirrorEngine


def main() -> None:
    parser = argparse.ArgumentParser(description="Interact with the AI Mirror")
    parser.add_argument("--ask", dest="ask", type=str, required=True, help="Question to pose to the mirror")
    parser.add_argument("--archive", dest="archive", type=str, default=None, help="Optional archive path")
    args = parser.parse_args()

    engine = MirrorEngine(args.archive)
    matches = engine.recall(args.ask)

    output = []
    for m in matches:
        output.append(
            {
                "timestamp": m.timestamp,
                "reflection": m.reflection,
                "echo": m.echo,
                "xp_then": m.xp,
                "xp_diff": m.xp_diff,
                "trait_drift": m.trait_drift,
            }
        )

    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
