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
    "Test your multiplication skills, Daisy! Answer correctly to build your streak, and score points. We can even save scores to compare. Try different modes like division for a challenge! Get 5 in a row!"
)

from datetime import datetime
import random
import requests
import streamlit as st

st.set_page_config(
    page_title="Daisy's Math Practice", page_icon="⭐", layout="centered"
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
  history = history[-50:]  # Keep last 50 entries

  payload = {"history": history}
  url = f"https://api.jsonbin.io/v3/b/{BIN_ID}"
  try:
    requests.put(url, json=payload, headers=HEADERS)
  except Exception:
    pass


# --- Title & Header ---
st.title("🌟 Daisy's Maths Practice")
st.write(
    "Test your multiplication and arithmetic skills! Answer correctly to build"
    " your streak and score points."
)

# --- Initialize Session State ---
if "score" not in st.session_state:
  st.session_state.score = 0
if "total_questions" not in st.session_state:
  st.session_state.total_questions = 0
if "streak" not in st.session_state:
  st.session_state.streak = 0
if "last_feedback" not in st.session_state:
  st.session_state.last_feedback = None
if "trigger_balloons" not in st.session_state:
  st.session_state.trigger_balloons = False

# Grid Mode State Initialization
if "table_row" not in st.session_state:
  st.session_state.table_row = random.randint(1, 12)
if "table_col" not in st.session_state:
  st.session_state.table_col = random.randint(1, 12)
if "table_attempts" not in st.session_state:
  st.session_state.table_attempts = 0


# --- Sidebar Settings ---
st.sidebar.header("⚙️ Game Settings")
practice_mode = st.sidebar.selectbox(
    "Choose Mode",
    [
        "Rapid Fire: Multiplication (1-12)",
        "Rapid Fire: Division (÷)",
        "Rapid Fire: Easy Addition",
        "Rapid Fire: Mixed Arithmetic",
        "Multiplication Table (Grid)",
    ],
)


# Function to generate a new Rapid Fire question
def generate_question():
  if practice_mode == "Rapid Fire: Multiplication (1-12)":
    st.session_state.num1 = random.randint(1, 12)
    st.session_state.num2 = random.randint(1, 12)
    st.session_state.op = "×"
  elif practice_mode == "Rapid Fire: Division (÷)":
    a = random.randint(1, 12)
    b = random.randint(1, 12)
    st.session_state.num1 = a * b
    st.session_state.num2 = b
    st.session_state.op = "÷"
  elif practice_mode == "Rapid Fire: Easy Addition":
    st.session_state.num1 = random.randint(1, 20)
    st.session_state.num2 = random.randint(1, 20)
    st.session_state.op = "+"
  else:  # Mixed Arithmetic
    op_choice = random.choice(["+", "-", "×", "÷"])
    if op_choice == "÷":
      a = random.randint(1, 12)
      b = random.randint(1, 12)
      st.session_state.num1 = a * b
      st.session_state.num2 = b
      st.session_state.op = "÷"
    elif op_choice == "×":
      st.session_state.num1 = random.randint(1, 12)
      st.session_state.num2 = random.randint(1, 12)
      st.session_state.op = "×"
    elif op_choice == "+":
      st.session_state.num1 = random.randint(1, 20)
      st.session_state.num2 = random.randint(1, 20)
      st.session_state.op = "+"
    else:
      st.session_state.num1 = random.randint(1, 20)
      st.session_state.num2 = random.randint(1, 20)
      if st.session_state.num1 < st.session_state.num2:
        st.session_state.num1, st.session_state.num2 = (
            st.session_state.num2,
            st.session_state.num1,
        )
      st.session_state.op = "-"


# Function to generate a new target square for the Grid mode
def generate_table_target():
  st.session_state.table_row = random.randint(1, 12)
  st.session_state.table_col = random.randint(1, 12)
  st.session_state.table_attempts = 0


# Detect if mode changed in sidebar and update accordingly
if (
    "prev_practice_mode" not in st.session_state
    or st.session_state.prev_practice_mode != practice_mode
):
  st.session_state.prev_practice_mode = practice_mode
  if practice_mode == "Multiplication Table (Grid)":
    generate_table_target()
  else:
    generate_question()

# Fallback first load check
if (
    practice_mode != "Multiplication Table (Grid)"
    and "num1" not in st.session_state
):
  generate_question()


# --- Scoreboard Display ---
col1, col2, col3 = st.columns(3, wrap=False)
col1.metric("Score 🏆", st.session_state.score)
col2.metric("Answered 📝", st.session_state.total_questions)
col3.metric("Streak 🔥", st.session_state.streak)

st.markdown("---")


# ==========================================
# MODE 1: MULTIPLICATION TABLE (GRID)
# ==========================================
if practice_mode == "Multiplication Table (Grid)":
  st.markdown(
      "### 🗺️ Multiplication Table Challenge"
  )
  st.write(
      "Find the highlighted square on the 12×12 grid and type the correct"
      " product!"
  )

  r = st.session_state.table_row
  c = st.session_state.table_col
  correct_answer = r * c

  # Render 12x12 HTML Grid with highlighted cell
  grid_html = "<div style='overflow-x:auto;'><table style='width:100%; border-collapse: collapse; font-family: sans-serif; font-size: 0.9em;'>"
  grid_html += "<tr><th style='border: 1px solid rgba(150,150,150,0.4); padding: 6px; background: rgba(150,150,150,0.1);'>×</th>"
  for col_idx in range(1, 13):
    grid_html += f"<th style='border: 1px solid rgba(150,150,150,0.4); padding: 6px; background: rgba(150,150,150,0.1);'>{col_idx}</th>"
  grid_html += "</tr>"

  for row_idx in range(1, 13):
    grid_html += f"<tr><th style='border: 1px solid rgba(150,150,150,0.4); padding: 6px; background: rgba(150,150,150,0.1);'>{row_idx}</th>"
    for col_idx in range(1, 13):
      is_highlighted = (row_idx == r) and (col_idx == c)
      if is_highlighted:
        grid_html += "<td style='border: 2px solid #ff4b4b; background-color: #ffeb3b; color: #000000; text-align: center; font-weight: bold; font-size: 1.2em; padding: 6px;'>?</td>"
      else:
        grid_html += f"<td style='border: 1px solid rgba(150,150,150,0.2); text-align: center; padding: 6px; color: inherit;'>{row_idx * col_idx}</td>"
    grid_html += "</tr>"
  grid_html += "</table></div><br>"

  st.markdown(grid_html, unsafe_allow_html=True)
  st.markdown(
      f"#### What is **{r} × {c}**? (Highlighted yellow square on the grid above)"
  )

  with st.form(key="grid_form", clear_on_submit=True):
    user_answer = st.number_input(
        "Type your answer here:",
        value=None,
        step=1,
        format="%d",
        placeholder="Type answer...",
    )
    submit_button = st.form_submit_button(label="Submit Answer 🚀")

  if submit_button:
    if user_answer is None:
      st.warning("Please type an answer first! 😊")
    else:
      st.session_state.total_questions += 1
      if user_answer == correct_answer:
        st.session_state.score += 1
        st.session_state.streak += 1
        st.session_state.last_feedback = (
            "success",
            random.choice(
                [
                    "🎉 Awesome job!",
                    "⭐ Correct! You found the right square!",
                    "🚀 Nailed it!",
                    "👏 Brilliant!",
                ]
            ),
        )
        if st.session_state.streak % 5 == 0:
          st.session_state.trigger_balloons = True
        else:
          st.session_state.trigger_balloons = False
        generate_table_target()
        st.rerun()
      else:
        # Incorrect attempt logic with 1 second chance
        if st.session_state.table_attempts == 0:
          st.session_state.table_attempts += 1
          st.session_state.last_feedback = (
              "error",
              "❌ Not quite! You have **1 more chance** to try again for this"
              " square. Look closely at row "
              f"{r} and column {c}!",
          )
          st.session_state.trigger_balloons = False
          st.rerun()
        else:
          # Second wrong attempt -> reveal answer and move on
          st.session_state.streak = 0
          st.session_state.last_feedback = (
              "error",
              f"❌ Still not quite! The correct answer for **{r} × {c}** was"
              f" **{correct_answer}**. Moving to a new square!",
          )
          st.session_state.trigger_balloons = False
          generate_table_target()
          st.rerun()


# ==========================================
# MODE 2: RAPID FIRE MODES
# ==========================================
else:
  n1 = st.session_state.num1
  n2 = st.session_state.num2
  op = st.session_state.op

  st.markdown(f"### What is **{n1} {op} {n2}** ?")

  # Calculate correct answer
  if op == "+":
    correct_answer = n1 + n2
  elif op == "-":
    correct_answer = n1 - n2
  elif op == "×":
    correct_answer = n1 * n2
  elif op == "÷":
    correct_answer = n1 // n2

  with st.form(key="math_form", clear_on_submit=True):
    user_answer = st.number_input(
        "Type your answer here:",
        value=None,
        step=1,
        format="%d",
        placeholder="Type your answer...",
    )
    submit_button = st.form_submit_button(label="Submit Answer 🚀")

  if submit_button:
    if user_answer is None:
      st.warning("Please type an answer first! 😊")
    else:
      st.session_state.total_questions += 1
      if user_answer == correct_answer:
        st.session_state.score += 1
        st.session_state.streak += 1
        st.session_state.last_feedback = (
            "success",
            random.choice(
                [
                    "🎉 Awesome job!",
                    "⭐ Correct! You're a math superstar!",
                    "🚀 Nailed it!",
                    "👏 Brilliant!",
                ]
            ),
        )
        if st.session_state.streak % 5 == 0:
          st.session_state.trigger_balloons = True
        else:
          st.session_state.trigger_balloons = False
      else:
        st.session_state.streak = 0
        st.session_state.last_feedback = (
            "error",
            f"❌ Not quite! The correct answer was **{correct_answer}**. Keep"
            " going!",
        )
        st.session_state.trigger_balloons = False

      generate_question()
      st.rerun()


# --- Display Feedback & Balloons ---
if st.session_state.last_feedback:
  f_type, f_msg = st.session_state.last_feedback
  if f_type == "success":
    st.success(f_msg)
  elif f_type == "error":
    st.error(f_msg)
  st.session_state.last_feedback = None

if st.session_state.trigger_balloons:
  st.balloons()
  st.session_state.trigger_balloons = False


# --- Save Session Score Button ---
st.markdown("---")
col_save, col_reset = st.columns(2, wrap=False)

with col_save:
  if st.button("💾 Save Score to Cloud", key="save_cloud_btn"):
    if st.session_state.total_questions > 0:
      save_score_to_bin(
          st.session_state.score, st.session_state.total_questions, practice_mode
      )
      st.success("Score successfully saved to the cloud! 🌟")
    else:
      st.warning("Answer a few questions before saving!")

with col_reset:
  if st.button("🔄 Reset Game", key="reset_game_btn"):
    st.session_state.score = 0
    st.session_state.total_questions = 0
    st.session_state.streak = 0
    if practice_mode == "Multiplication Table (Grid)":
      generate_table_target()
    else:
      generate_question()
    st.rerun()

# --- Parent / History Dashboard ---
with st.expander("📊 Past Practice History (Cloud Log)"):
  history = load_score_history()
  if history:
    for entry in reversed(history[-10:]):
      st.write(
          f"- **{entry.get('timestamp')}** | Mode: *{entry.get('mode')}* |"
          f" Score: **{entry.get('score')} / {entry.get('total')}**"
      )
  else:
    st.write("No saved practice sessions yet. Click 'Save Score' after playing!")




