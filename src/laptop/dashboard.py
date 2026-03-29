#!/usr/bin/env python3
"""
dashboard.py — Streamlit dashboard for robot-with-ai-v1
Run on laptop alongside laptop_server.py

Usage:
    streamlit run dashboard.py --server.port 8501

Access: http://localhost:8501
"""

import streamlit as st
import requests
import json
from PIL import Image
import io

st.set_page_config(
    page_title="🤖 Robot AI Control Center",
    page_icon="🤖",
    layout="wide",
)

# ── Config ────────────────────────────────────────────────────────────────────

LAPTOP_HOST = "http://localhost:8000"
REFRESH_INTERVAL = 3  # seconds

# ── State ─────────────────────────────────────────────────────────────────────

if "auto_mode" not in st.session_state:
    st.session_state.auto_mode = False
if "last_decision" not in st.session_state:
    st.session_state.last_decision = "stop"
if "last_frame" not in st.session_state:
    st.session_state.last_frame = None

# ── Helpers ───────────────────────────────────────────────────────────────────

def get(url: str):
    try:
        return requests.get(f"{LAPTOP_HOST}{url}", timeout=5)
    except Exception as e:
        return None

def post(url: str, data=None):
    try:
        return requests.post(f"{LAPTOP_HOST}{url}", json=data, timeout=30)
    except Exception as e:
        return None

def poll_frame():
    """Fetch latest frame as JPEG bytes."""
    resp = get("/api/frame/latest.jpg")
    if resp and resp.status_code == 200:
        return resp.content
    return None

# ── Sidebar ───────────────────────────────────────────────────────────────────

with st.sidebar:
    st.title("🤖 Robot Status")

    # System status
    info = get("/")
    if info:
        data = info.json()
        st.success("🟢 Server Online")
        st.caption(f"Model: `{data.get('model', 'unknown')}`")
        st.caption(f"Ollama: {data.get('ollama', '')}")
    else:
        st.error("🔴 Server Offline")
        st.caption("Is laptop_server.py running?")
        st.stop()

    st.divider()

    # Manual command buttons
    st.subheader("🎮 Manual Control")
    col1, col2 = st.columns(2)
    directions = {
        "forward": "⬆️ Fwd",
        "backward": "⬇️ Back",
        "left": "⬅️ Left",
        "right": "➡️ Right",
        "stop": "⏹️ Stop",
    }

    for direction, label in directions.items():
        if st.button(label, use_container_width=True):
            post("/api/command", {"direction": direction})
            st.session_state.last_decision = direction
            st.rerun()

    st.divider()

    # AI settings
    st.subheader("🧠 AI Mode")
    st.session_state.auto_mode = st.toggle("Auto-navigate", value=st.session_state.auto_mode)

    if st.button("🪄 Run AI Step", use_container_width=True):
        with st.spinner("Running AI..."):
            resp = post("/api/autonomous_loop")
            if resp and resp.status_code == 200:
                result = resp.json()
                st.session_state.last_decision = result.get("decision", "?")
                st.success(f"Decision: **{st.session_state.last_decision}**")
                st.caption(f"({result.get('elapsed_s', '?')}s)")
            else:
                st.error("AI step failed")

    st.divider()

    # Current state
    st.subheader("📊 Current State")
    cmd = get("/api/command")
    if cmd:
        st.write(f"**Command:** `{cmd.json().get('direction', '?')}`")
        speed = cmd.json().get("speed")
        if speed:
            st.write(f"**Speed:** {speed}")

    if st.session_state.last_decision:
        st.write(f"**Last AI:** `{st.session_state.last_decision}`")

# ── Main area ─────────────────────────────────────────────────────────────────

st.title("🤖 Robot AI Control Center")

# Live camera feed
col_video, col_status = st.columns([2, 1])

with col_video:
    frame_bytes = poll_frame()
    if frame_bytes:
        img = Image.open(io.BytesIO(frame_bytes))
        st.image(img, channels="RGB", width=640, caption="Robot Camera Feed")
    else:
        st.info("No camera feed yet. Is the robot streaming?")

with col_status:
    st.subheader("📋 Decision Log")
    st.code(st.session_state.last_decision or "—", language=None)

    # Quick stats
    info = get("/").json() if get("/") else {}
    if info:
        st.markdown(f"**Model:** `{info.get('model', '?')}`")

        # Show raw Ollama info if available
        tags = get("/api/tags")
        if tags:
            models = [m["name"] for m in tags.json().get("models", [])]
            st.markdown(f"**Available models:** {len(models)}")

# ── Auto-refresh ───────────────────────────────────────────────────────────────

if st.session_state.auto_mode:
    st.info("🟡 Auto mode active — robot is navigating autonomously")
    # Use experimental fragments for partial rerun
    st_autorefresh = st
else:
    st.caption("Toggle Auto-navigate in the sidebar to enable continuous AI navigation")

# ── Code reference ───────────────────────────────────────────────────────────

with st.expander("📡 API Reference"):
    st.markdown(f"""
    **Endpoints:**
    - `GET /` — Server status
    - `POST /api/frame` — Upload JPEG from robot
    - `GET /api/command` — Robot polls for current command
    - `POST /api/command` — Manual override
    - `POST /api/ai_decide` — Trigger AI decision on latest frame
    - `POST /api/autonomous_loop` — One autonomous step
    - `GET /api/frame/latest.jpg` — Latest frame as JPEG

    **Test with curl:**
    ```bash
    # See server status
    curl {LAPTOP_HOST}/

    # Set manual command
    curl -X POST {LAPTOP_HOST}/api/command -H "Content-Type: application/json" \\
      -d '{{"direction": "forward"}}'

    # Trigger AI decision
    curl -X POST {LAPTOP_HOST}/api/ai_decide
    ```
    """)
