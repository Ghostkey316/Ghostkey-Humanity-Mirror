"""CLI utilities to query the soul memory archive."""

from __future__ import annotations

import argparse
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List, Optional

from soul_memory import ARCHIVE_PATH, load_archive


def recall(date: str, path: str | Path = ARCHIVE_PATH) -> Optional[Dict[str, Any]]:
    """Return the entry that matches a given date (YYYY-MM-DD)."""
    entries = load_archive(path)
    for entry in entries:
        if entry["timestamp"].startswith(date):
            return entry
    return None


def search_trait(trait: str, path: str | Path = ARCHIVE_PATH) -> List[Dict[str, Any]]:
    """Return entries where the given trait appears."""
    trait = trait.lower()
    results: List[Dict[str, Any]] = []
    for entry in load_archive(path):
        # Search in reflection text
        if trait in entry.get("reflection", "").lower():
            results.append(entry)
            continue
        # Search in trait summary keys
        summary = entry.get("trait_summary", {})
        if isinstance(summary, dict):
            keys = [k.lower() for k in summary.keys()]
            if trait in keys:
                results.append(entry)
    return results


def generate_summary(path: str | Path = ARCHIVE_PATH) -> str:
    """Provide a lightweight summary of the archive."""
    entries = load_archive(path)
    if not entries:
        return "No soul memories recorded."

    start = entries[0]["timestamp"]
    end = entries[-1]["timestamp"]
    trait_counter: Counter[str] = Counter()
    for e in entries:
        summary = e.get("trait_summary", {})
        if isinstance(summary, dict):
            trait_counter.update(summary.keys())
    top = ", ".join(f"{t}({c})" for t, c in trait_counter.most_common(3))
    return f"{len(entries)} reflections from {start} to {end}. Top traits: {top}."


def main(argv: Optional[List[str]] = None) -> None:
    parser = argparse.ArgumentParser(description="Query Soul Memory Archive")
    parser.add_argument("--recall", help="Show reflection from given date (YYYY-MM-DD)")
    parser.add_argument(
        "--search", nargs=2, metavar=("field", "value"), help="Search archive"
    )
    parser.add_argument("--summary", action="store_true", help="Summarize archive")
    parser.add_argument(
        "--path", default=ARCHIVE_PATH, help="Path to archive file", type=str
    )
    args = parser.parse_args(argv)

    path = args.path
    if args.recall:
        entry = recall(args.recall, path)
        if entry:
            print(entry["reflection"])
        else:
            print("No entry for that date.")
    elif args.search:
        field, value = args.search
        if field == "trait":
            for e in search_trait(value, path):
                print(f"{e['timestamp']}: {e['reflection']}")
        else:
            print("Unsupported search field.")
    elif args.summary:
        print(generate_summary(path))
    else:
        parser.print_help()


if __name__ == "__main__":  # pragma: no cover - CLI entry
    main()
