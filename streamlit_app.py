from datetime import datetime
import random
import requests
import time
import streamlit as st


st.set_page_config(
    page_title="Daisy's Maths Practice", page_icon="⭐", layout="centered"
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


def save_score_to_bin(new_entry):
  """Appends a new practice session record to JSONBin.io"""
  history = load_score_history()
  history.append(new_entry)
  # Keep the last 1,000 entries for long-term improvement tracking
  history = history[-1000:] 

  payload = {"history": history}
  url = f"https://api.jsonbin.io/v3/b/{BIN_ID}"

  try:
    response = requests.put(url, json=payload, headers=HEADERS)
    # Check if JSONBin rejected it (e.g., rate limit, 403, 429)
    if response.status_code != 200:
      st.error(
          f"🚨 **Upload Failed!** Tell Dad immediately — we might have hit the 10,000 request limit! (Status: {response.status_code})"
      )
      return False
    st.success("Score successfully saved! 🌼")
    return True
  except Exception as e:
    st.error(
        f"🚨 **Network Error:** Tell Dad this happened: `{e}`"
    )
    return False


# --- Title & Header ---
st.title("🌟 Daisy's Maths Practice")
st.write(
    "Test your multiplication and arithmetic skills, Daisy! Try different game modes in top left settings, and try to beat your high score!" )

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
if "start_time" not in st.session_state:
    st.session_state.start_time = None
if "current_save" not in st.session_state:
    st.session_state.current_save = None

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


# Helper function to format seconds into "X min Ys" 
def format_time(seconds):
    mins = int(seconds // 60)
    secs = seconds % 60
    if mins > 0:
        return f"{mins} min {secs:.0f}s"
    return f"{secs:.1f}s"

# --- Helper to calculate minimum coins for UK currency ---
def get_min_coins(target):
  coins = [50, 20, 10, 5, 2, 1]
  count = 0
  remaining = target
  for coin in coins:
    count += remaining // coin
    remaining %= coin
  return count


# --- Sidebar Settings ---
st.sidebar.header("⚙️ Game Settings")
practice_mode = st.sidebar.selectbox(
    "Choose Mode",
    [
        "Multiplication Table (Grid Completion)",
        "Rapid Fire: Multiplication (1-12)",
        "Rapid Fire: Division (÷)",
        "Rapid Fire: Simple Addition",
        "Rapid Fire: Mixed Arithmetic",
        "Coin math",
    ],
)
# Dynamic Sidebar Filters based on mode choice
selected_tables = list(range(1, 13))  # Default fallback
addition_limit = 20  # Default fallback

if practice_mode in [
    "Rapid Fire: Multiplication (1-12)",
    "Rapid Fire: Division (÷)",
    "Rapid Fire: Mixed Arithmetic",
]:
# st.pills with multi-select enabled gives big, easy-to-tap touch targets 
  selected_tables = st.sidebar.pills(
      "Choose Multiples to Practice:",
      options=list(range(1, 13)),
      default=[2,3,4,5,6,7,8,9,11,12],
      selection_mode="multi",
      help="Select multiples to practice.",
  ) 

# Fallback if all are unchecked
  if not selected_tables:
    selected_tables = list(range(1, 13))
 

if practice_mode in [
    "Rapid Fire: Simple Addition",
    "Rapid Fire: Mixed Arithmetic",
]:
  st.sidebar.markdown("---")
  addition_limit = st.sidebar.slider(
      "Maximum Addition Number:",
      min_value=10,
      max_value=500,
      value=20,
      step=5,
      help="Sets the upper limit for the numbers being added.",
  )


# Function to generate a new Rapid Fire question
def generate_question():
  print(selected_tables, flush=True)
  if practice_mode == "Rapid Fire: Multiplication (1-12)":
    a = random.choice(selected_tables)
    b = random.randint(1, 12)
    if random.choice([True, False]):
      st.session_state.num1 = a
      st.session_state.num2 = b
    else:
      st.session_state.num1 = b
      st.session_state.num2 = a
    st.session_state.op = "×"
  elif practice_mode == "Rapid Fire: Division (÷)":
    b = random.choice(selected_tables)
    a = random.randint(1, 12)
    st.session_state.num1 = a * b
    st.session_state.num2 = b
    st.session_state.op = "÷"
  elif practice_mode == "Rapid Fire: Simple Addition":
    st.session_state.num1 = random.randint(1, addition_limit)
    st.session_state.num2 = random.randint(1, addition_limit)
    st.session_state.op = "+"
  elif practice_mode == "Rapid Fire: Mixed Arithmetic":
    op_choice = random.choice(["+", "-", "×", "÷"])
    if op_choice == "÷":
      b = random.choice(selected_tables)
      a = random.randint(1, 12)
      st.session_state.num1 = a * b
      st.session_state.num2 = b
      st.session_state.op = "÷"
    elif op_choice == "×":
      a = random.choice(selected_tables)
      b = random.randint(1, 12)
      st.session_state.op = "×"
      if random.choice([True, False]):
        st.session_state.num1 = a
        st.session_state.num2 = b
      else:
        st.session_state.num1 = b
        st.session_state.num2 = a
    elif op_choice == "+":
      st.session_state.num1 = random.randint(1, addition_limit)
      st.session_state.num2 = random.randint(1, addition_limit)
      st.session_state.op = "+"
    else:
      a = random.randint(1, addition_limit)
      b = random.randint(1, addition_limit)
      if a < b:
        st.session_state.num1 = b
        st.session_state.num2 = a
      else:
        st.session_state.num1 = a
        st.session_state.num2 = b
      st.session_state.op = "-" 


# --- Detect Mode OR Sub-menu Changes ---
current_filter_state = (practice_mode, tuple(selected_tables), addition_limit)

if (
    "prev_filter_state" not in st.session_state
    or st.session_state.prev_filter_state != current_filter_state
):
  st.session_state.prev_filter_state = current_filter_state
  st.session_state.start_time = None
  if practice_mode not in [
      "Multiplication Table (Grid Completion)",
      "Coin math",
  ]:
    generate_question()

if (
    practice_mode not in [
        "Multiplication Table (Grid Completion)",
        "Coin math",
    ]
    and "num1" not in st.session_state
):
  generate_question()


# Addable list of encouraging success calls
daisy_success_messages = [
    "🎉 Well done, Daisy!",
    "⭐ You go girl!",
    "🚀 You know it 👏",
    "🌟 Look at you go, Daisy!",
    "👏 Superstar skills!",
    "🎉 Awesome job Daisy!",
    "⭐ Brilliant work, Daisy!",
    "🚀 You're crushing it!",
    "👏 High five, maths champion!",
    "🌟 Boom! Nailed it, Daisy!",
    "✨ OMG, literally a maths genius!",
    "💎 Literally crushing it, Daisy! 💅",
    "🫵 OMG nailed it!",
    "👑 Your aura is literally sunshine", 
    "👸 This is giving Princess vibes", 
    "💫 Out of this world!", 
    "🧚 Literally unstoppable!", 
    "🌼 Daisy the Superstar!", 
    "🌄 Sunshine and daisies, you're glowing!", 
]



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
  col2.metric("Revealed ⚠️", st.session_state.grid_failed_score)
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
    total_time = time.time() - st.session_state.start_time
    formatted_duration = format_time(total_time)
    avg_time = format_time(total_time / completed_count) 
    st.session_state.current_save = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "mode": practice_mode,
        "total": completed_count,
        "score": st.session_state.grid_correct_score,
        "total_time_seconds": formatted_duration, 
        "avg_time_per_question": avg_time,
    }

    st.balloons()
    st.success(
        f"🎉 Well done, Daisy! You finished the grid in {formatted_duration}!"
    )
    st.write(
        f"**Final Stats:** {st.session_state.grid_correct_score} correct answers"
        f" | {st.session_state.grid_failed_score} revealed squares."
        f" | Time taken: {formatted_duration}"
        f" | Average time per question: {avg_time}"
    )
    if st.button("🔄 Play Again / Reset Grid"):
      st.session_state.grid_completed = {}
      st.session_state.grid_correct_score = 0
      st.session_state.grid_failed_score = 0
      pick_next_grid_target()
      st.session_state.current_save = None
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
      if st.session_state.start_time is None:
        st.session_state.start_time = time.time() 
      if user_answer is None:
        st.warning("Please type an answer first! 😊")
      else:
        if user_answer == correct_answer:
          st.session_state.grid_completed[(r, c)] = "correct"
          st.session_state.grid_correct_score += 1
          elapsed_time = time.time() - st.session_state.start_time
          formatted_duration = format_time(elapsed_time)
          avg_time = format_time(elapsed_time / (completed_count+1)) 
          st.session_state.current_save = {
              "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
              "mode": practice_mode,
              "total": completed_count+1,
              "score": st.session_state.grid_correct_score,
              "total_time_seconds": formatted_duration, 
              "avg_time_per_question": avg_time,
          }

          st.session_state.streak += 1
          st.session_state.last_feedback = (
              "success",
              random.choice(daisy_success_messages),
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
# MODE 3: COIN MATH
# ==========================================
elif practice_mode == "Coin math":
  if "coin_target" not in st.session_state:
    st.session_state.coin_target = random.randint(1, 99)

# Custom CSS to enlarge number inputs and stepper buttons for mobile touch
  st.markdown(
      """
      <style>
      div.stNumberInput input {
          font-size: 18px !important;
          font-weight: bold !important;
          text-align: center;
      }
      /* Make the stepper container / buttons easier to tap */
      div.stNumberInput button {
          transform: scale(1.25);
          margin: 0px 4px;
      }
      </style>
  """,
      unsafe_allow_html=True,
  )

  col1, col2, col3 = st.columns(3, wrap=False)
  col1.metric("Score 🏆", st.session_state.score)
  col2.metric("Answered 📝", st.session_state.total_questions)
  col3.metric("Streak 🔥", st.session_state.streak)

  st.markdown("---")
  st.markdown(f"### 🪙 Make the target amount: **{st.session_state.coin_target}p**")
  st.write("Select how many of each coin you need:")

  with st.form(key="coin_form", clear_on_submit=True):
    # 2-Column Grid Layout to cut vertical length in half!
    c_col1, c_col2 = st.columns(2, wrap=False)

    with c_col1:
      c50 = st.number_input("50p coins", min_value=0, value=0, step=1, format="%d")
      c10 = st.number_input("10p coins", min_value=0, value=0, step=1, format="%d")
      c2 = st.number_input("2p coins", min_value=0, value=0, step=1, format="%d")

    with c_col2:
      c20 = st.number_input("20p coins", min_value=0, value=0, step=1, format="%d")
      c5 = st.number_input("5p coins", min_value=0, value=0, step=1, format="%d")
      c1 = st.number_input("1p coins", min_value=0, value=0, step=1, format="%d")

    submit_coins = st.form_submit_button(label="Check Coins 🚀", use_container_width=True)
 

  if submit_coins:
    if st.session_state.start_time is None:
      st.session_state.start_time = time.time()
    
    total_calculated = (c50 * 50) + (c20 * 20) + (c10 * 10) + (c5 * 5) + (c2 * 2) + (c1 * 1)
    user_total_coins = c50 + c20 + c10 + c5 + c2 + c1
    st.session_state.total_questions += 1

    if total_calculated == st.session_state.coin_target:
      min_possible_coins = get_min_coins(st.session_state.coin_target)

      if user_total_coins == min_possible_coins:
        # Correct amount AND most efficient!
        st.session_state.score += 1
        st.session_state.streak += 1
        elapsed_time = time.time() - st.session_state.start_time
        formatted_duration = format_time(elapsed_time)
        avg_time = format_time(elapsed_time / st.session_state.total_questions)
        st.session_state.current_save = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "mode": practice_mode,
            "total": st.session_state.total_questions,
            "score": st.session_state.score,
            "total_time_seconds": formatted_duration,
            "avg_time_per_question": avg_time,
        }
        st.session_state.last_feedback = ("success", random.choice(daisy_success_messages))
        if st.session_state.streak % 5 == 0:
          st.session_state.trigger_balloons = True
        st.session_state.coin_target = random.randint(1, 99)
        st.rerun()
      else:
        # Right value, but too many coins used!
        st.session_state.streak = 0
        st.session_state.last_feedback = (
            "error",
            f"⚠️ That adds up to **{st.session_state.coin_target}p**, but can you do it with **fewer coins**? (You used {user_total_coins}, perfection is {min_possible_coins}!)",
        )
        st.rerun()
    else:
      st.session_state.streak = 0
      st.session_state.last_feedback = (
          "error",
          f"❌ Not quite! Your coins added up to **{total_calculated}p**, but the target was **{st.session_state.coin_target}p**.",
      )
      st.session_state.coin_target = random.randint(1, 99)
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
    if st.session_state.start_time is None:
      st.session_state.start_time = time.time()
    if user_answer is None:
      st.warning("Please type an answer first! 😊")
    else:
      st.session_state.total_questions += 1
      if user_answer == correct_answer:
        st.session_state.score += 1
        st.session_state.streak += 1

        elapsed_time = time.time() - st.session_state.start_time
        formatted_duration = format_time(elapsed_time)
        avg_time = format_time(elapsed_time / st.session_state.total_questions) 
        st.session_state.current_save = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "mode": practice_mode,
            "total": st.session_state.total_questions,
            "score": st.session_state.score,
            "total_time_seconds": formatted_duration, 
            "avg_time_per_question": avg_time,
        }

        st.session_state.last_feedback = (
            "success",
            random.choice(daisy_success_messages),
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
    if st.session_state.current_save != None:
        save_score_to_bin(st.session_state.current_save)
        st.session_state.current_save = None
    else:
        st.warning("Answer a few questions before saving!")

with col_reset:
  if st.button("🔄 Reset Game", key="reset_game_btn"):
    st.session_state.current_save = None
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
      timestamp = entry.get('timestamp', 'N/A')
      mode = entry.get('mode', 'Unknown')
      score = entry.get('score', 0)
      total = entry.get('total', 0)
      
      # Pull the new timing fields gracefully
      total_time = entry.get('total_time_seconds')
      avg_time = entry.get('avg_time_per_question')
      
      # Build a suffix for time metrics if they exist in the entry
      timing_str = ""
      if total_time and avg_time:
        timing_str = f" | Total: **{total_time}** | Avg: **{avg_time} per question**"
      
      st.write(
          f"- **{timestamp}** | Mode: *{mode}* | "
          f"Score: **{score} / {total}**{timing_str}"
      )
  else:
    st.write("No saved practice sessions yet. Click 'Save Score' after playing!")
