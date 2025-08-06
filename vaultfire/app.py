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

import streamlit as st

# ---------------------------------------------------------------------------
# Configuration

ROOT = Path(__file__).resolve().parent.parent
USERS_FILE = ROOT / "users.json"
SOUL_ARCHIVE = ROOT / "soul_archive.json"
REFLECTIONS_FILE = ROOT / "reflections.json"


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


def save_reflections(reflections: list) -> None:
    REFLECTIONS_FILE.write_text(json.dumps(reflections, indent=2))


KEYWORDS = {"hope", "sacrifice", "truth", "trust"}


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

    st.subheader("Public Signals")
    public_refs = [r for r in load_reflections() if r.get("public")]
    for ref in reversed(public_refs[-10:]):
        st.markdown(f"_{ref['content']}_")
        st.caption(ref["timestamp"])
        st.markdown(
            f"<div style='background-color:{ref.get('color', '#ccc')};height:5px;'></div>",
            unsafe_allow_html=True,
        )

    # Ensure current user's data is persisted
    update_user_record(user_id, xp)


if __name__ == "__main__":
    main()

