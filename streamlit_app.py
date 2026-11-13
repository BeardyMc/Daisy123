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
    "Test your multiplication and arithmetic skills! Fill the grid to reach"
    " 100% completion!"
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
if "grid_completed" not in st.session_state:
  st.session_state.grid_completed = {}  # {(r, c): "correct" or "revealed"}
if "grid_correct_score" not in st.session_state:
  st.session_state.grid_correct_score = 0
if "grid_failed_score" not in st.session_state:
  st.session_state.grid_failed_score = 0
if "grid_target" not in st.session_state:
  st.session_state.grid_target = None
if "grid_attempts" not in st.session_state:
  st.session_state.grid_attempts = 0


def pick_next_grid_target():
  """Selects a random unfilled cell on the 12x12 grid"""
  unfilled = []
  for r in range(1, 13):
    for c in range(1, 13):
      if (r, c) not in st.session_state.grid_completed:
        unfilled.append((r, c))
  if unfilled:
    st.session_state.grid_target = random.choice(unfilled)
    st.session_state.grid_attempts = 0
  else:
    st.session_state.grid_target = None


# Initialize target if none set
if st.session_state.grid_target is None and len(
    st.session_state.grid_completed
) < 144:
  pick_next_grid_target()


# --- Sidebar Settings ---
st.sidebar.header("⚙️ Game Settings")
practice_mode = st.sidebar.selectbox(
    "Choose Mode",
    [
        "Multiplication Table (Grid Completion)",
        "Rapid Fire: Multiplication (1-12)",
        "Rapid Fire: Division (÷)",
        "Rapid Fire: Easy Addition",
        "Rapid Fire: Mixed Arithmetic",
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


# Detect if mode changed in sidebar and update accordingly
if (
    "prev_practice_mode" not in st.session_state
    or st.session_state.prev_practice_mode != practice_mode
):
  st.session_state.prev_practice_mode = practice_mode
  if practice_mode != "Multiplication Table (Grid Completion)":
    generate_question()

if (
    practice_mode != "Multiplication Table (Grid Completion)"
    and "num1" not in st.session_state
):
  generate_question()


# ==========================================
# MODE 1: MULTIPLICATION TABLE (GRID COMPLETION)
# ==========================================
if practice_mode == "Multiplication Table (Grid Completion)":
  st.markdown("### 🗺️ Multiplication Table Completion Challenge")

  completed_count = len(st.session_state.grid_completed)
  progress_pct = completed_count / 144.0

  # Progress Bar & Metrics
  st.progress(
      progress_pct,
      text=(
          f"Grid Completion: {completed_count} / 144 cells"
          f" ({progress_pct * 100:.1f}%)"
      ),
  )

  col1, col2, col3 = st.columns(3, wrap=False)
  col1.metric("Correct Answers ⭐", st.session_state.grid_correct_score)
  col2.metric("Revealed / Failed ⚠️", st.session_state.grid_failed_score)
  col3.metric("Completed 🗺️", f"{completed_count}/144")

  st.markdown("---")

  # Render 12x12 HTML Grid
  grid_html = "<div style='overflow-x:auto;'><table style='width:100%; border-collapse: collapse; font-family: sans-serif; font-size: 0.9em;'>"
  grid_html += "<tr><th style='border: 1px solid rgba(150,150,150,0.4); padding: 6px; background: rgba(150,150,150,0.1);'>×</th>"
  for col_idx in range(1, 13):
    grid_html += f"<th style='border: 1px solid rgba(150,150,150,0.4); padding: 6px; background: rgba(150,150,150,0.1);'>{col_idx}</th>"
  grid_html += "</tr>"

  for row_idx in range(1, 13):
    grid_html += f"<tr><th style='border: 1px solid rgba(150,150,150,0.4); padding: 6px; background: rgba(150,150,150,0.1);'>{row_idx}</th>"
    for col_idx in range(1, 13):
      cell_key = (row_idx, col_idx)
      is_target = (
          st.session_state.grid_target
          and st.session_state.grid_target == cell_key
      )

      if cell_key in st.session_state.grid_completed:
        status = st.session_state.grid_completed[cell_key]
        if status == "correct":
          # Greenish for correct
          grid_html += f"<td style='border: 1px solid rgba(150,150,150,0.2); background-color: rgba(40, 167, 69, 0.15); text-align: center; padding: 6px; font-weight: bold; color: inherit;'>{row_idx * col_idx}</td>"
        else:
          # Orange-yellow for revealed after 2 failed attempts
          grid_html += f"<td style='border: 1px solid rgba(150,150,150,0.2); background-color: rgba(255, 193, 7, 0.2); text-align: center; padding: 6px; font-weight: bold; color: inherit;'>{row_idx * col_idx}</td>"
      elif is_target:
        grid_html += "<td style='border: 2px solid #ff4b4b; background-color: #ffeb3b; color: #000000; text-align: center; font-weight: bold; font-size: 1.2em; padding: 6px;'>?</td>"
      else:
        grid_html += "<td style='border: 1px solid rgba(150,150,150,0.2); text-align: center; padding: 6px; color: rgba(150,150,150,0.4);'>·</td>"
    grid_html += "</tr>"
  grid_html += "</table></div><br>"

  st.markdown(grid_html, unsafe_allow_html=True)

  # Check if grid is fully completed
  if completed_count >= 144:
    st.balloons()
    st.success(
        "🎉 Incredible! You've reached 100% completion on the entire grid!"
    )
    st.write(
        f"**Final Stats:** {st.session_state.grid_correct_score} correct answers"
        f" | {st.session_state.grid_failed_score} revealed squares."
    )
    if st.button("🔄 Play Again / Reset Grid"):
      st.session_state.grid_completed = {}
      st.session_state.grid_correct_score = 0
      st.session_state.grid_failed_score = 0
      pick_next_grid_target()
      st.rerun()
  else:
    r, c = st.session_state.grid_target
    correct_answer = r * c

    st.markdown(
        f"#### What is **{r} × {c}**? (Highlighted yellow square on the grid"
        " above)"
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
        if user_answer == correct_answer:
          st.session_state.grid_completed[(r, c)] = "correct"
          st.session_state.grid_correct_score += 1
          st.session_state.streak += 1
          st.session_state.last_feedback = (
              "success",
              random.choice(
                  [
                      "🎉 Awesome job!",
                      "⭐ Correct! Square filled in!",
                      "🚀 Nailed it!",
                      "👏 Brilliant!",
                  ]
              ),
          )
          if st.session_state.streak % 5 == 0:
            st.session_state.trigger_balloons = True
          else:
            st.session_state.trigger_balloons = False
          pick_next_grid_target()
          st.rerun()
        else:
          if st.session_state.grid_attempts == 0:
            st.session_state.grid_attempts += 1
            st.session_state.last_feedback = (
                "error",
                "❌ Not quite! You have **1 more chance** to try again for this"
                f" square ({r} × {c}).",
            )
            st.session_state.trigger_balloons = False
            st.rerun()
          else:
            # Second wrong attempt -> fill in as revealed
            st.session_state.grid_completed[(r, c)] = "revealed"
            st.session_state.grid_failed_score += 1
            st.session_state.streak = 0
            st.session_state.last_feedback = (
                "error",
                f"❌ Still not quite! The correct answer for **{r} × {c}** was"
                f" **{correct_answer}**. It has been filled in for you.",
            )
            st.session_state.trigger_balloons = False
            pick_next_grid_target()
            st.rerun()


# ==========================================
# MODE 2: RAPID FIRE MODES
# ==========================================
else:
  # Scoreboard Display for Rapid Fire
  col1, col2, col3 = st.columns(3, wrap=False)
  col1.metric("Score 🏆", st.session_state.score)
  col2.metric("Answered 📝", st.session_state.total_questions)
  col3.metric("Streak 🔥", st.session_state.streak)

  st.markdown("---")

  n1 = st.session_state.num1
  n2 = st.session_state.num2
  op = st.session_state.op

  st.markdown(f"### What is **{n1} {op} {n2}** ?")

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
    if (
        practice_mode == "Multiplication Table (Grid Completion)"
        and (
            st.session_state.grid_correct_score > 0
            or st.session_state.grid_failed_score > 0
        )
    ):
      total_grid_attempts = (
          st.session_state.grid_correct_score
          + st.session_state.grid_failed_score
      )
      save_score_to_bin(
          st.session_state.grid_correct_score,
          total_grid_attempts,
          practice_mode,
      )
      st.success("Score successfully saved to the cloud! 🌟")
    elif (
        practice_mode != "Multiplication Table (Grid Completion)"
        and st.session_state.total_questions > 0
    ):
      save_score_to_bin(
          st.session_state.score, st.session_state.total_questions, practice_mode
      )
      st.success("Score successfully saved to the cloud! 🌟")
    else:
      st.warning("Answer a few questions before saving!")

with col_reset:
  if st.button("🔄 Reset Game", key="reset_game_btn"):
    if practice_mode == "Multiplication Table (Grid Completion)":
      st.session_state.grid_completed = {}
      st.session_state.grid_correct_score = 0
      st.session_state.grid_failed_score = 0
      pick_next_grid_target()
    else:
      st.session_state.score = 0
      st.session_state.total_questions = 0
      st.session_state.streak = 0
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
