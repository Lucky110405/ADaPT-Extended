import streamlit as st
import json
from datetime import datetime
import time
from logger import log_event
from logger import get_events, clear_events
from main import main_agent

# ----------------------------
# SESSION STATE INIT
# ----------------------------
# ----------------------------
# SESSION STATE INIT (REQUIRED)
# ----------------------------
if "events" not in st.session_state:
    st.session_state.events = get_events()

if "memory" not in st.session_state:
    st.session_state.memory = {}

if "answers" not in st.session_state:
    st.session_state.answers = {}



# ----------------------------
# UI CONFIG
# ----------------------------
st.set_page_config(page_title="AI Agent Dashboard", layout="wide")

st.title("🧠 Autonomous AI Agent Dashboard")

# ----------------------------
# SIDEBAR
# ----------------------------
st.sidebar.header("⚙️ Controls")

task = st.sidebar.text_input("Enter Task")
run = st.sidebar.button("Run Agent")
if st.sidebar.button("Clear Events"):
    clear_events()
    st.rerun()

# ----------------------------
# RUN AGENT
# ----------------------------
if run and task:
    st.session_state.events = []  # reset events for new run
    given_task = task
    log_event("process", "Calling LLM")

    response = main_agent.invoke(given_task)

    log_event("result", "LLM response", response)

if "pending_question" in st.session_state:
    question = st.session_state.pending_question

    answer = st.text_input("Answer:", key="answer_input")

    if st.button("Submit Answer"):

        # ✅ store answer
        st.session_state.answers[question] = answer

        log_event("answer", answer)

        del st.session_state.pending_question

        st.rerun()

# ----------------------------
# MAIN LAYOUT
# ----------------------------
col1, col2 = st.columns([2, 1])

# ----------------------------
# 🧠 TIMELINE PANEL
# ----------------------------
with col1:
    st.subheader("🧠 Agent Timeline")

    events = get_events()

    for event in events:
        time_str = event["time"]

        if event["type"] == "process":
            st.info(f"[{time_str}] ⚙️ {event['message']}")

        elif event["type"] == "tool":
            st.warning(f"[{time_str}] 🛠️ {event['message']}")
            st.json(event["data"])

        elif event["type"] == "result":
            st.success(f"[{time_str}] 📊 {event['message']}")
            st.write(event["data"])

        elif event["type"] == "question":
            st.error(f"[{time_str}] ❓ {event['data']}")

        elif event["type"] == "answer":
            st.success(f"[{time_str}] 💬 {event['data']}")

        elif event["type"] == "execution":
            st.write(f"[{time_str}] 🚀 {event['message']}")

# ----------------------------
# 💬 CHAT PANEL
# ----------------------------
with col1:
    st.subheader("💬 Interaction")

    for event in events:
        if event["type"] == "question":
            with st.chat_message("assistant"):
                st.write(event["data"])

        elif event["type"] == "answer":
            with st.chat_message("user"):
                st.write(event["data"])

# ----------------------------
# 🛠️ TOOL PANEL
# ----------------------------
with col2:
    st.subheader("🛠️ Tools Used")

    for event in events:
        if event["type"] == "tool":
            st.write("🔧", event["message"])
            st.json(event["data"])

# ----------------------------
# 💾 MEMORY PANEL
# ----------------------------
with col2:
    st.subheader("💾 Memory")

    if st.session_state.memory:
        st.json(st.session_state.memory)
    else:
        st.info("No memory yet")

# ----------------------------
# STATUS
# ----------------------------
st.subheader("📊 Status")

if st.session_state.events:
    st.success("✅ Task Completed")
else:
    st.warning("⏳ Waiting for task...")