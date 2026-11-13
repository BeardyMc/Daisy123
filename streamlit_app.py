import math
import streamlit as st
import random
import time
import requests

st.set_page_config(
    page_title="Math Practice", page_icon="⭐", layout="centered"
)

# --- Title & Header ---
st.title("🌟 Math Practice for Daisy 🌟")
st.write(
    "Test your multiplication and arithmetic skills! Answer correctly to build"
    " your streak and score points!"
)

# --- Initialize Session State ---
if "score" not in st.session_state:
  st.session_state.score = 0
if "total_questions" not in st.session_state:
  st.session_state.total_questions = 0
if "streak" not in st.session_state:
  st.session_state.streak = 0



