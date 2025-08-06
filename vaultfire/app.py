# Vaultfire Streamlit App with Multi-User XP Leaderboard
# Author: ghostkey316.eth

"""Streamlit interface for the Vaultfire XP system.

This version adds a simple identity layer and a persistent leaderboard so
multiple users can accumulate XP. User data is stored in ``users.json`` at the
repository root and contains the XP, rank and the time it was last updated.
When a user reaches the top rank (``Ghostkey Master``) they can claim a role
which logs the achievement in ``soul_archive.json`` and grants a one time
bonus.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import List

import streamlit as st

# ---------------------------------------------------------------------------
# Configuration

ROOT = Path(__file__).resolve().parent.parent
USERS_FILE = ROOT / "users.json"
SOUL_ARCHIVE = ROOT / "soul_archive.json"
REFLECTIONS_FILE = ROOT / "reflections.json"
RITUALS_FILE = ROOT / "rituals.json"
VAULT_LOG = ROOT / "vaultfire.log"


# Rank structure
RANKS = [
    {"min_xp": 0, "max_xp": 99, "rank": "Moral Novice", "badge": "🧠"},
    {"min_xp": 100, "max_xp": 199, "rank": "Seeker", "badge": "🔎"},
    {"min_xp": 200, "max_xp": 399, "rank": "Code Aligned", "badge": "🧬"},
    {"min_xp": 400, "max_xp": 699, "rank": "Flamekeeper", "badge": "🔥"},
    {"min_xp": 700, "max_xp": 999, "rank": "Belief Architect", "badge": "🛠️"},
    {"min_xp": 1000, "max_xp": 9999, "rank": "Ghostkey Master", "badge": "👻🗝️"},
]


# ---------------------------------------------------------------------------
# Helpers for rank and persistence

def load_users() -> dict:
    """Return the persisted user table."""

    if USERS_FILE.exists():
        try:
            return json.loads(USERS_FILE.read_text())
        except json.JSONDecodeError:
            return {}
    return {}


def save_users(users: dict) -> None:
    USERS_FILE.write_text(json.dumps(users, indent=2))


def get_rank(xp: int) -> tuple[str, str]:
    """Return the rank label and badge for a given XP amount."""

    for rank in RANKS:
        if rank["min_xp"] <= xp <= rank["max_xp"]:
            return rank["rank"], rank["badge"]
    return "Unknown", "❓"


def get_rank_info(xp: int):
    """Return the current rank structure and the next one if available."""

    for i, r in enumerate(RANKS):
        if r["min_xp"] <= xp <= r["max_xp"]:
            next_rank = RANKS[i + 1] if i + 1 < len(RANKS) else None
            return r, next_rank
    return RANKS[-1], None


def progress_within_rank(xp: int) -> float:
    """Return progress (0..1) within the current rank."""

    r, _ = get_rank_info(xp)
    span = r["max_xp"] - r["min_xp"]
    if span == 0:
        return 1.0
    return (xp - r["min_xp"]) / span


def update_user_record(user: str, xp: int, **updates) -> None:
    """Persist the given user's XP, rank and timestamp.

    Extra keyword fields are merged into the stored record so other
    properties like streaks or badges survive multiple updates.
    """

    rank_label, _ = get_rank(xp)
    users = load_users()
    record = users.get(user, {})
    record.update({
        "xp": xp,
        "rank": rank_label,
        "timestamp": datetime.utcnow().isoformat(),
    })
    record.update(updates)
    users[user] = record
    save_users(users)


def load_reflections() -> list:
    """Return the list of stored reflections."""

    if REFLECTIONS_FILE.exists():
        try:
            return json.loads(REFLECTIONS_FILE.read_text())
        except json.JSONDecodeError:
            return []
    return []


def load_rituals() -> List[dict]:
    """Return the list of stored ritual unlocks."""

    if RITUALS_FILE.exists():
        try:
            return json.loads(RITUALS_FILE.read_text())
        except json.JSONDecodeError:
            return []
    return []


def log_ritual(user: str, ritual: str) -> None:
    """Append a ritual unlock entry to ``rituals.json``."""

    rituals = load_rituals()
    rituals.append({
        "user": user,
        "ritual": ritual,
        "timestamp": datetime.utcnow().isoformat(),
    })
    RITUALS_FILE.write_text(json.dumps(rituals, indent=2))


def log_vault_reveal(user: str) -> None:
    """Record a vault reveal in ``vaultfire.log``."""

    with VAULT_LOG.open("a") as fh:
        fh.write(f"{datetime.utcnow().isoformat()} - {user} revealed the vault\n")


def save_reflections(reflections: list) -> None:
    REFLECTIONS_FILE.write_text(json.dumps(reflections, indent=2))


KEYWORDS = {"hope", "sacrifice", "truth", "trust"}

RITUAL_MEANINGS = {
    "Ritual of Fire": "Seven reflections forged the flame",
    "Eyes Opened": "First public signal",
    "Chainbreaker": "Top 3 on leaderboard",
}


def process_reflection(user: str, content: str, public: bool, color: str, now: datetime | None = None):
    """Record a reflection and update XP/streak information.

    Returns the user's new XP total and the XP gained from this reflection.
    """

    now = now or datetime.utcnow()
    reflections = load_reflections()
    reflections.append({
        "user": user,
        "timestamp": now.isoformat(),
        "content": content,
        "public": public,
        "color": color,
    })
    save_reflections(reflections)

    word_count = len(content.split())
    base_gain = 50 if word_count > 30 else 0
    keyword_gain = 10 if any(k in content.lower() for k in KEYWORDS) else 0
    xp_gain = base_gain + keyword_gain

    users = load_users()
    record = users.get(user, {})
    xp = record.get("xp", 0)

    today = now.date()
    last_date_str = record.get("last_reflection_date")
    streak = record.get("streak", 0)
    streak_bonus = 0
    if last_date_str:
        last_date = datetime.fromisoformat(last_date_str).date()
        if last_date == today:
            pass
        elif (today - last_date).days == 1:
            streak += 1
            streak_bonus = 25
        else:
            streak = 1
            streak_bonus = 25
    else:
        streak = 1
        streak_bonus = 25

    dates = record.get("reflection_dates", [])
    today_iso = today.isoformat()
    if today_iso not in dates:
        dates.append(today_iso)

    badges = record.get("badges", [])
    if streak >= 7 and "7-Day Streak" not in badges:
        badges.append("7-Day Streak")
    if streak >= 30 and "30-Day Streak" not in badges:
        badges.append("30-Day Streak")

    total_gain = xp_gain + streak_bonus
    xp += total_gain

    update_user_record(
        user,
        xp,
        streak=streak,
        last_reflection_date=today_iso,
        reflection_dates=dates,
        badges=badges,
    )
    return xp, total_gain


def check_and_unlock_rituals(user: str, *, public_signal: bool = False, top3: bool = False) -> List[str]:
    """Check milestone conditions and unlock rituals as needed.

    Returns a list of newly unlocked ritual names.
    """

    users = load_users()
    record = users.get(user, {})
    rituals: List[str] = record.get("rituals", [])
    unlocked: List[str] = []

    reflections = [r for r in load_reflections() if r["user"] == user]

    def unlock(name: str):
        if name not in rituals:
            rituals.append(name)
            unlocked.append(name)
            log_ritual(user, name)
            st.balloons()
            st.markdown(f"**{name} unlocked!** ✨")
            st.caption(RITUAL_MEANINGS.get(name, ""))

    if len(reflections) >= 7:
        unlock("Ritual of Fire")

    if public_signal:
        unlock("Eyes Opened")

    if top3:
        unlock("Chainbreaker")

    if record.get("streak", 0) > 30 and not record.get("vault_revealed"):
        st.markdown("## 🔓 The Vault Reveals Itself!")
        log_vault_reveal(user)
        record["vault_revealed"] = True

    if unlocked or record.get("vault_revealed"):
        update_user_record(
            user,
            record.get("xp", 0),
            rituals=rituals,
            vault_revealed=record.get("vault_revealed", False),
        )
    return unlocked


def log_role_claim(user: str, rank_label: str) -> None:
    """Append the role claim to ``soul_archive.json``."""

    archive = []
    if SOUL_ARCHIVE.exists():
        try:
            archive = json.loads(SOUL_ARCHIVE.read_text())
        except json.JSONDecodeError:
            archive = []
    archive.append({
        "user": user,
        "rank": rank_label,
        "timestamp": datetime.utcnow().isoformat(),
    })
    SOUL_ARCHIVE.write_text(json.dumps(archive, indent=2))


def render_signal_map(record: dict) -> None:
    """Display the user's milestones as a graph."""

    from graphviz import Digraph

    g = Digraph()
    colors = {"XP": "lightblue", "Reflection": "lightgreen", "Ritual": "orange"}

    first_ref_done = bool(record.get("reflection_dates"))
    streak7 = record.get("streak", 0) >= 7
    is_master = record.get("rank") == "Ghostkey Master"

    g.node("First Reflection", style="filled", fillcolor=colors["Reflection"] if first_ref_done else "lightgrey")
    g.node("Streak 7", style="filled", fillcolor=colors["Reflection"] if streak7 else "lightgrey")
    g.node("Ghostkey Master", style="filled", fillcolor=colors["XP"] if is_master else "lightgrey")

    g.edge("First Reflection", "Streak 7")
    g.edge("Streak 7", "Ghostkey Master")

    for ritual in record.get("rituals", []):
        g.node(ritual, style="filled", fillcolor=colors["Ritual"])
        if ritual == "Ritual of Fire":
            g.edge("Streak 7", ritual)
        elif ritual == "Eyes Opened":
            g.edge("First Reflection", ritual)
        else:
            g.edge("Ghostkey Master", ritual)

    st.graphviz_chart(g)
def main() -> None:
    """Run the Streamlit interface."""

    # ---------------------------------------------------------------------------
    # Identity input

    users = load_users()
    user_input = st.text_input(
        "Enter your identity (name, ENS, or wallet alias)",
        st.session_state.get("user_id", ""),
    )

    if not user_input:
        st.title("🔥 Vaultfire XP System")
        st.info("Please enter your identity to begin earning XP.")
        st.stop()

    user_id = user_input.strip()
    st.session_state["user_id"] = user_id

    # Load or initialize XP for this user
    user_record = users.get(user_id, {"xp": 0})
    if st.session_state.get("xp_user") != user_id:
        st.session_state["xp"] = user_record.get("xp", 0)
        st.session_state["xp_user"] = user_id

    xp = st.session_state.get("xp", 0)

    # ---------------------------------------------------------------------------
    # Sidebar / status

    rank_struct, next_rank = get_rank_info(xp)
    rank_label, badge = rank_struct["rank"], rank_struct["badge"]

    with st.sidebar:
        page = st.radio("Page", ["Dashboard", "Signal Map"])
        st.header("Your Status")
        st.markdown(f"{badge} **{rank_label}**")
        st.markdown(f"XP: `{xp}`")
        st.progress(progress_within_rank(xp))
        if next_rank:
            remaining = next_rank["min_xp"] - xp
            st.caption(f"{remaining} XP to {next_rank['rank']}")
        else:
            st.caption("Max rank achieved")
        if user_record.get("badges"):
            st.markdown("**Badges:** " + ", ".join(user_record.get("badges", [])))

        if user_record.get("rituals"):
            st.subheader("Rituals")
            for r in user_record.get("rituals", []):
                meaning = RITUAL_MEANINGS.get(r, "")
                st.markdown(f"<span title='{meaning}'>{r}</span>", unsafe_allow_html=True)

        st.subheader("Recent Reflections")
        recent_refs = [r for r in load_reflections() if r["user"] == user_id][-7:]
        for ref in reversed(recent_refs):
            st.caption(ref["timestamp"])
            st.markdown(ref["content"])
            st.markdown(
                f"<div style='background-color:{ref.get('color', '#ccc')};height:5px;'></div>",
                unsafe_allow_html=True,
            )

    # ---------------------------------------------------------------------------
    # Main panel - actions and display

    if page == "Dashboard":
        st.title("🔥 Vaultfire XP System")
        st.markdown(f"### 🏅 Your Rank: {badge} **{rank_label}**")
        st.markdown(f"**XP:** `{xp}`")

        st.subheader("Reflection Journal")
        reflection_text = st.text_area("What did you believe in today?")
        public_signal = st.checkbox("Public Signal")
        emotion_color = st.color_picker("Emotion color", "#cccccc")
        if st.button("Submit Reflection"):
            if reflection_text.strip():
                xp, gain = process_reflection(
                    user_id, reflection_text.strip(), public_signal, emotion_color
                )
                st.session_state["xp"] = xp
                check_and_unlock_rituals(user_id, public_signal=public_signal)
                st.success(f"Reflection recorded! +{gain} XP")
                st.experimental_rerun()
            else:
                st.warning("Please enter a reflection before submitting.")

        if st.button("Do Loyalty Action"):
            xp += 50
            st.session_state["xp"] = xp
            update_user_record(user_id, xp)
            st.experimental_rerun()

        # Claim Ghostkey Role if master
        if rank_label == "Ghostkey Master":
            st.success("💎 You’ve reached Ghostkey Master.")
            if not st.session_state.get("claimed_master"):
                if st.button("Claim Ghostkey Role"):
                    log_role_claim(user_id, rank_label)
                    xp += 250
                    st.session_state["xp"] = xp
                    st.session_state["claimed_master"] = True
                    update_user_record(user_id, xp)
                    st.markdown(
                        "<span style='font-size:40px'>✨👻✨</span>", unsafe_allow_html=True
                    )
                    st.experimental_rerun()

        # ---------------------------------------------------------------------------
        # Leaderboard

        st.header("🏆 Leaderboard")
        users = load_users()
        sorted_users = sorted(
            users.items(), key=lambda item: item[1].get("xp", 0), reverse=True
        )

        for position, (uid, data) in enumerate(sorted_users, start=1):
            u_rank, u_badge = get_rank(data.get("xp", 0))
            st.markdown(f"**{position}. {u_badge} {uid}** - {data.get('xp', 0)} XP")
            st.progress(progress_within_rank(data.get("xp", 0)))
            if uid == user_id and position <= 3:
                check_and_unlock_rituals(user_id, top3=True)

        st.subheader("Public Signals")
        public_refs = [r for r in load_reflections() if r.get("public")]
        for ref in reversed(public_refs[-10:]):
            st.markdown(f"_{ref['content']}_")
            st.caption(ref["timestamp"])
            st.markdown(
                f"<div style='background-color:{ref.get('color', '#ccc')};height:5px;'></div>",
                unsafe_allow_html=True,
            )

    else:
        st.title("🌐 Signal Map")
        render_signal_map(user_record)

    # Ensure current user's data is persisted
    latest = load_users().get(user_id, {})
    update_user_record(
        user_id,
        xp,
        rituals=latest.get("rituals", []),
        vault_revealed=latest.get("vault_revealed", False),
    )


if __name__ == "__main__":
    main()

