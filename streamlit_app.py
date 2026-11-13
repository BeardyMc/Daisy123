import math
import streamlit as st
import random
import time
import requests

st.set_page_config(
    page_title="Math Practice", page_icon="⭐", layout="centered"
)

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
col1, col2, col3 = st.columns(3)
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
if st.button("🔄 Reset Game"):
  st.session_state.score = 0
  st.session_state.total_questions = 0
  st.session_state.streak = 0
  generate_question()
  st.rerun()



