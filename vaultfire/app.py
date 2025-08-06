# Vaultfire Streamlit App with Rank-Based XP System
# Author: ghostkey316.eth

import streamlit as st

# Load rank structure
RANKS = [
    {"min_xp": 0, "max_xp": 99, "rank": "Moral Novice", "badge": "🧠"},
    {"min_xp": 100, "max_xp": 199, "rank": "Seeker", "badge": "🔎"},
    {"min_xp": 200, "max_xp": 399, "rank": "Code Aligned", "badge": "🧬"},
    {"min_xp": 400, "max_xp": 699, "rank": "Flamekeeper", "badge": "🔥"},
    {"min_xp": 700, "max_xp": 999, "rank": "Belief Architect", "badge": "🛠️"},
    {"min_xp": 1000, "max_xp": 9999, "rank": "Ghostkey Master", "badge": "👻🗝️"},
]

# Get user XP (or start fresh)
if "xp" not in st.session_state:
    st.session_state["xp"] = 0

xp = st.session_state["xp"]


def get_rank(xp: int):
    """Return the rank label and badge for a given XP amount."""
    for rank in RANKS:
        if rank["min_xp"] <= xp <= rank["max_xp"]:
            return rank["rank"], rank["badge"]
    return "Unknown", "❓"


rank, badge = get_rank(xp)

# Display XP + Rank
st.title("🔥 Vaultfire XP System")
st.markdown(f"### 🏅 Your Rank: {badge} **{rank}**")
st.markdown(f"**XP:** `{xp}`")

# Simulate XP gain
if st.button("Do Loyalty Action"):
    st.session_state["xp"] += 50
    st.experimental_rerun()

# Special reward
if rank == "Ghostkey Master":
    st.success("💎 You’ve reached Ghostkey Master.")
    st.balloons()
    if st.button("Claim Ghost Signal"):
        st.session_state["xp"] += 100
        st.markdown("👻 Signal claimed: +100 XP")
        st.experimental_rerun()

