# VAULTFIRE STREAMLIT CORE LOGIC
# Author: ghostkey316.eth
# Version: Launch Flow v1.0

import streamlit as st
from datetime import datetime
import random

st.set_page_config(page_title="Vaultfire Protocol", layout="wide")

# ---------- XP ENGINE ----------
if 'xp' not in st.session_state:
    st.session_state.xp = 0

def gain_xp(amount):
    st.session_state.xp += amount

st.sidebar.title("🔥 Vaultfire XP Engine")
st.sidebar.write(f"Current XP: {st.session_state.xp}")
if st.sidebar.button("Claim Daily Belief Bonus"):
    gain_xp(10)
    st.sidebar.success("Belief registered. +10 XP.")

# ---------- AI MIRROR ----------
st.title("🪞 AI Mirror")
user_emotion = st.text_input("Describe how you're feeling right now:", "")
if user_emotion:
    mirror_response = f"The system reflects back: '{user_emotion}' — seen, logged, and honored."
    st.write(mirror_response)
    gain_xp(5)

# ---------- SIGNAL DASHBOARD ----------
st.header("📡 Signal Dashboard")
st.write("All systems running. Awaiting signals...")

signals = ["Passive Bonus Delivered", "Streak Achieved", "Codex Unlock Detected"]
if st.button("Generate Random Signal"):
    selected_signal = random.choice(signals)
    st.success(f"Signal: {selected_signal}")
    gain_xp(15)
