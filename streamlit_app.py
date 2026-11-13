from datetime import datetime
import math
import streamlit as st
import random
import time
import requests

st.set_page_config(
    page_title="Math Practice", page_icon="⭐", layout="centered"
)


# --- JSONBin Configuration from Secrets ---
API_KEY = st.secrets["JSONBIN_API_KEY"]
BIN_ID = st.secrets["BIN_ID"]
HEADERS = {"Content-Type": "application/json", "X-Master-Key": API_KEY}


def load_score_history():
  """Fetches past practice records from JSONBin.io"""
  url = f"https://api.jsonbin.io/v3/b/{BIN_ID}/latest"
  try:
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
      data = response.json().get("record", {})
      return data.get("history", [])
  except Exception:
    pass
  return []


def save_score_to_bin(score, total, mode):
  """Appends a new practice session record to JSONBin.io"""
  history = load_score_history()
  new_entry = {
      "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
      "score": score,
      "total": total,
      "mode": mode,
  }
  history.append(new_entry)

  # Keep only the last 50 entries to avoid bloating the bin
  history = history[-50:]

  payload = {"history": history}
  url = f"https://api.jsonbin.io/v3/b/{BIN_ID}"
  try:
    requests.put(url, json=payload, headers=HEADERS)
  except Exception:
    pass



# --- Title & Header ---
st.title("🌟 Daisy's Maths Practice")
st.write(
    "Test your multiplication skills! Answer correctly to build your streak, and score points."
)

# --- Initialize Session State ---
if "score" not in st.session_state:
  st.session_state.score = 0
if "total_questions" not in st.session_state:
  st.session_state.total_questions = 0
if "streak" not in st.session_state:
  st.session_state.streak = 0

# Generate a question if one doesn't exist yet
if "num1" not in st.session_state:
  st.session_state.num1 = random.randint(1, 12)
  st.session_state.num2 = random.randint(1, 12)
  st.session_state.op = "×"


# --- Sidebar Settings ---
st.sidebar.header("⚙️ Game Settings")
practice_mode = st.sidebar.selectbox(
    "Choose Mode",
    ["Multiplication Only (1-12)", "Mixed Arithmetic (+, -, ×)", "Easy Addition"],
)


# Function to generate a new question based on the selected mode
def generate_question():
  if practice_mode == "Multiplication Only (1-12)":
    st.session_state.num1 = random.randint(1, 12)
    st.session_state.num2 = random.randint(1, 12)
    st.session_state.op = "×"
  elif practice_mode == "Easy Addition":
    st.session_state.num1 = random.randint(1, 20)
    st.session_state.num2 = random.randint(1, 20)
    st.session_state.op = "+"
  else:  # Mixed Arithmetic
    st.session_state.num1 = random.randint(1, 12)
    st.session_state.num2 = random.randint(1, 12)
    st.session_state.op = random.choice(["+", "-", "×"])

    # Prevent negative results for subtraction in mixed mode
    if (
        st.session_state.op == "-"
        and st.session_state.num1 < st.session_state.num2
    ):
      st.session_state.num1, st.session_state.num2 = (
          st.session_state.num2,
          st.session_state.num1,
      )


# --- Scoreboard Display ---
col1, col2, col3 = st.columns(3, wrap=False)
col1.metric("Score 🏆", st.session_state.score)
col2.metric("Answered 📝", st.session_state.total_questions)
col3.metric("Streak 🔥", st.session_state.streak)

st.markdown("---")

# --- Current Question Display ---
n1 = st.session_state.num1
n2 = st.session_state.num2
op = st.session_state.op

st.markdown(f"### What is **{n1} {op} {n2}** ?")

# Calculate the correct answer
if op == "+":
  correct_answer = n1 + n2
elif op == "-":
  correct_answer = n1 - n2
elif op == "×":
  correct_answer = n1 * n2

# --- Answer Form ---
with st.form(key="math_form", clear_on_submit=True):
  user_answer = st.number_input(
      "Type your answer here:", value=0, step=1, format="%d"
  )
  submit_button = st.form_submit_button(label="Submit Answer 🚀")

if submit_button:
  st.session_state.total_questions += 1
  if user_answer == correct_answer:
    st.session_state.score += 1
    st.session_state.streak += 1
    st.success(
        random.choice(
            [
                "🎉 Awesome job!",
                "⭐ Correct! You're a math superstar!",
                "🚀 Nailed it!",
                "👏 Brilliant!",
            ]
        )
    )
    # Trigger celebratory balloons every 5 streak wins!
    if st.session_state.streak % 5 == 0:
      st.balloons()
  else:
    st.session_state.streak = 0
    st.error(
        f"❌ Not quite! The correct answer was **{correct_answer}**. Keep going!"
    )

  # Generate the next question and refresh view
  generate_question()
  st.rerun()

# --- Reset Button ---
st.markdown("---") 

# --- Save Session Score Button ---
st.markdown("---")
col_save, col_reset = st.columns(2, wrap=False)

with col_save:
  if st.button("💾 Save Score to Cloud"):
    if st.session_state.total_questions > 0:
      save_score_to_bin(
          st.session_state.score, st.session_state.total_questions, practice_mode
      )
      st.success("Score successfully saved to the cloud! 🌟")
    else:
      st.warning("Answer a few questions before saving!")

with col_reset:
  if st.button("🔄 Reset Game"):
    st.session_state.score = 0
    st.session_state.total_questions = 0
    st.session_state.streak = 0
    generate_question()
    st.rerun()

# --- Parent / History Dashboard ---
with st.expander("📊 Past Practice History (Cloud Log)"):
  history = load_score_history()
  if history:
    for entry in reversed(history[-10:]):  # Show last 10 entries
      st.write(
          f"- **{entry.get('timestamp')}** | Mode: *{entry.get('mode')}* |"
          f" Score: **{entry.get('score')} / {entry.get('total')}**"
      )
  else:
    st.write("No saved practice sessions yet. Click 'Save Score' after playing!")



