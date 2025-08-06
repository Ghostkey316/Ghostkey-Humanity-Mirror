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

from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict
from .utils import utcnow, read_json, write_json

try:
    import streamlit as st
except ModuleNotFoundError:  # pragma: no cover - used in tests
    class _Stub:
        session_state: dict = {}

        def __getattr__(self, name):
            def _noop(*args, **kwargs):
                return "Dashboard" if name == "radio" else None

            return _noop

    st = _Stub()

# ---------------------------------------------------------------------------
# Configuration

ROOT = Path(__file__).resolve().parent
USERS_FILE = ROOT / "users.json"
SOUL_ARCHIVE = ROOT / "soul_archive.json"
REFLECTIONS_FILE = ROOT / "reflections.json"
RITUALS_FILE = ROOT / "rituals.json"
VAULT_LOG = ROOT / "vaultfire.log"
REACTIONS_FILE = ROOT / "reactions.json"


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

    return read_json(USERS_FILE, {})


def save_users(users: dict) -> None:
    write_json(USERS_FILE, users)


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
        "timestamp": utcnow().isoformat(),
    })
    record.update(updates)
    users[user] = record
    save_users(users)


def load_reflections() -> list:
    """Return the list of stored reflections."""

    return read_json(REFLECTIONS_FILE, [])


def load_rituals() -> List[dict]:
    """Return the list of stored ritual unlocks."""

    return read_json(RITUALS_FILE, [])


def log_ritual(user: str, ritual: str) -> None:
    """Append a ritual unlock entry to ``rituals.json``."""

    rituals = load_rituals()
    rituals.append({
        "user": user,
        "ritual": ritual,
        "timestamp": utcnow().isoformat(),
    })
    write_json(RITUALS_FILE, rituals)


def log_vault_reveal(user: str) -> None:
    """Record a vault reveal in ``vaultfire.log``."""

    with VAULT_LOG.open("a") as fh:
        fh.write(f"{utcnow().isoformat()} - {user} revealed the vault\n")


def save_reflections(reflections: list) -> None:
    write_json(REFLECTIONS_FILE, reflections)


def load_reactions() -> Dict[str, Dict[str, int]]:
    """Load stored reactions keyed by reflection timestamp."""

    return read_json(REACTIONS_FILE, {})


def save_reactions(reactions: Dict[str, Dict[str, int]]) -> None:
    write_json(REACTIONS_FILE, reactions)


def add_reaction(ref_timestamp: str, emoji: str) -> None:
    """Increment a reaction for the given reflection timestamp."""

    reactions = load_reactions()
    entry = reactions.setdefault(ref_timestamp, {"👏": 0, "🔥": 0, "💭": 0})
    if emoji in entry:
        entry[emoji] += 1
    save_reactions(reactions)


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

    # `now` is injected for tests; default to an aware UTC timestamp
    now = now or utcnow()
    # XP is awarded for sufficiently long reflections and for using
    # certain keywords that indicate depth of thought.
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
            pass  # already reflected today
        elif (today - last_date).days == 1:
            streak += 1
            streak_bonus = 25  # reward continuing streaks
        else:
            streak = 1
            streak_bonus = 25  # reset streak but still reward the day
    else:
        streak = 1
        streak_bonus = 25  # first ever reflection

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

    reflections = load_reflections()
    reflections.append(
        {
            "user": user,
            "timestamp": now.isoformat(),
            "content": content,
            "public": public,
            "color": color,
            "xp_gain": total_gain,
            "streak": streak,
        }
    )
    save_reflections(reflections)

    update_user_record(
        user,
        xp,
        streak=streak,
        last_reflection_date=today_iso,
        reflection_dates=dates,
        badges=badges,
    )
    return xp, total_gain


def evaluate_chain_rituals(now: datetime | None = None) -> List[str]:
    """Check for a chain ritual and award participants.

    Returns the list of participants if a ritual was triggered.
    """

    # Use an aware timestamp to avoid naive/aware warnings
    now = now or utcnow()
    window_start = now - timedelta(minutes=30)
    reflections = [
        r
        for r in load_reflections()
        if r.get("public") and datetime.fromisoformat(r["timestamp"]) >= window_start
    ]
    participants = sorted({r["user"] for r in reflections})
    if len(participants) < 3:
        return []

    rituals = load_rituals()
    for event in rituals:
        if event.get("type") == "ChainRitual":
            event_time = datetime.fromisoformat(event["timestamp"])
            # avoid double-counting the same participant set within the window
            if event_time >= window_start and set(event.get("participants", [])) == set(
                participants
            ):
                return []

    rituals.append(
        {
            "type": "ChainRitual",
            "participants": participants,
            "timestamp": now.isoformat(),
        }
    )
    write_json(RITUALS_FILE, rituals)

    users = load_users()
    for p in participants:
        record = users.get(p, {})
        xp = record.get("xp", 0) + 150
        chain_count = record.get("chain_rituals", 0) + 1
        week_start = now - timedelta(days=7)
        recent_events = [
            e
            for e in rituals
            if e.get("type") == "ChainRitual"
            and p in e.get("participants", [])
            and datetime.fromisoformat(e["timestamp"]) >= week_start
        ]
        title = record.get("title")
        if len(recent_events) >= 3:
            title = "Signal Architect"  # title after three chains in a week
        update_user_record(p, xp, chain_rituals=chain_count, title=title)
    return participants


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
            # persist the ritual, celebrate, and show its meaning
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

    archive = read_json(SOUL_ARCHIVE, [])
    archive.append({
        "user": user,
        "rank": rank_label,
        "timestamp": utcnow().isoformat(),
    })
    write_json(SOUL_ARCHIVE, archive)


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
        page = st.radio("Page", ["Dashboard", "Signal Map", "Signalboard"])
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
                participants = evaluate_chain_rituals()
                check_and_unlock_rituals(user_id, public_signal=public_signal)
                latest_xp = load_users().get(user_id, {}).get("xp", xp)
                st.session_state["xp"] = latest_xp
                if user_id in participants:
                    st.balloons()
                    st.success("Chain Ritual! +150 XP")
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
            line = f"**{position}. {u_badge} {uid}**"
            if data.get("title"):
                line += f" ({data['title']})"
            if data.get("chain_rituals", 0) >= 2:
                line += " 🔥 Chain Ritualist"
            line += f" - {data.get('xp', 0)} XP"
            st.markdown(line)
            st.progress(progress_within_rank(data.get("xp", 0)))
            if uid == user_id and position <= 3:
                check_and_unlock_rituals(user_id, top3=True)

        st.subheader("Public Signals")
        public_refs = [r for r in load_reflections() if r.get("public")]
        reactions = load_reactions()
        for ref in reversed(public_refs[-10:]):
            st.markdown(f"_{ref['content']}_")
            counts = reactions.get(ref["timestamp"], {})
            bubble = " ".join(
                f"{e} {counts.get(e,0)}" for e in ["👏", "🔥", "💭"] if counts.get(e, 0)
            )
            st.caption(f"{ref['timestamp']} {bubble}".strip())
            st.markdown(
                f"<div style='background-color:{ref.get('color', '#ccc')};height:5px;'></div>",
                unsafe_allow_html=True,
            )

    elif page == "Signal Map":
        st.title("🌐 Signal Map")
        render_signal_map(user_record)
    else:
        st.title("📡 Signalboard")
        public_refs = [r for r in load_reflections() if r.get("public")]
        sort_by = st.selectbox("Sort by", ["Newest", "Highest XP", "Streak Position"])
        if sort_by == "Newest":
            public_refs.sort(key=lambda r: r["timestamp"], reverse=True)
        elif sort_by == "Highest XP":
            public_refs.sort(key=lambda r: r.get("xp_gain", 0), reverse=True)
        else:
            public_refs.sort(key=lambda r: r.get("streak", 0), reverse=True)

        reactions = load_reactions()
        users_data = load_users()
        for ref in public_refs:
            badge = get_rank(users_data.get(ref["user"], {}).get("xp", 0))[1]
            st.markdown(f"{badge} _{ref['content']}_")
            st.caption(f"{ref['timestamp']} · +{ref.get('xp_gain',0)} XP")
            st.markdown(
                f"<div style='background-color:{ref.get('color', '#ccc')};height:5px;'></div>",
                unsafe_allow_html=True,
            )
            counts = reactions.get(ref["timestamp"], {})
            cols = st.columns(3)
            for emoji, col in zip(["👏", "🔥", "💭"], cols):
                label = f"{emoji} {counts.get(emoji,0)}"
                if col.button(label, key=f"{emoji}-{ref['timestamp']}"):
                    add_reaction(ref["timestamp"], emoji)
                    st.experimental_rerun()

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

