import argparse
import datetime
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from mirror_log import log_sample, self_audit_template
from vaultfire import rewards
from memory_graph import update_graph
from moral_alignment import evaluate_entry
from identity.bridge import generate_belief_certificate
from identity.exporter import export_certificate


def get_user_input():
    print("💠 Welcome to Humanity Mirror")
    print("1. Daily Reflection  2. Self-Audit  3. Exit")
    choice = input("Choose (1/2/3): ")

    if choice == "1":
        entry = input("Reflect freely (feelings, choices, doubts):\n")
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        with open("mirror_log/log_sample.md", "a") as f:
            f.write(f"\n## {timestamp}\n{entry}\n")
        update_graph(entry)
        evaluate_entry(entry)
        rewards.calculate(entry)

    elif choice == "2":
        with open("mirror_log/self_audit_template.md", "r") as f:
            print(f.read())
    else:
        print("Goodbye.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Humanity Mirror")
    parser.add_argument(
        "--export", action="store_true", help="generate belief proof and export logs"
    )
    args = parser.parse_args()

    if args.export:
        cert = generate_belief_certificate("ghostkey316.eth", "bpow20.cb.id")
        path = export_certificate(cert)
        print(f"Belief certificate saved to {path}")
        signal = rewards.get_last_signal()
        if signal:
            print(signal)
    else:
        get_user_input()
