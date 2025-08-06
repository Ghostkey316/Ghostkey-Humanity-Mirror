from mirror_log import log_sample, self_audit_template
from vaultfire import rewards
from memory_graph import update_graph
from moral_alignment import evaluate_entry
import datetime


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
    get_user_input()
