#!/usr/bin/env python3
"""
laptop_server.py — AI brain for robot-with-ai-v1
Runs on laptop. Receives images from robot, runs vision AI, returns motor commands.

Requirements:
    pip install fastapi uvicorn requests pillow openai

Usage:
    python laptop_server.py [--model MODEL] [--host HOST] [--port PORT]

Models tested with Ollama:
    - moondream:1.8b     (fastest, ~1GB)
    - llava:latest       (~4.7GB)
    - qwen2.5vl:3b       (~2.3GB)
    - phi3.5-vision:3.8b (~2.5GB)
"""

import argparse
import io
import logging
import os
import time
import json
import threading
from pathlib import Path
from typing import Optional

import requests
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from PIL import Image
import uvicorn

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
log = logging.getLogger(__name__)

# --- Ollama config ---
DEFAULT_OLLAMA_HOST = "http://localhost:11434"
DEFAULT_MODEL = "moondream:1.8b"

# Navigation prompt — keep simple for reliability
NAVIGATION_PROMPT = (
    "You are a robot. Look at this image from your camera. "
    "What should you do? Reply with exactly ONE word: "
    "forward, left, right, backward, or stop. "
    "Consider: obstacles, walls, clear paths, and safety."
)

# --- App ---
app = FastAPI(title="Robot AI Brain", version="1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global state
latest_frame: Optional[bytes] = None
latest_decision: str = "stop"
last_decision_time: float = 0
lock = threading.Lock()

# Config
cfg = {
    "ollama_host": DEFAULT_OLLAMA_HOST,
    "model": DEFAULT_MODEL,
    "last_command": {"direction": "stop", "speed": None},
}


# ── Ollama helpers ───────────────────────────────────────────────────────────

def check_ollama() -> bool:
    """Check if Ollama is reachable."""
    try:
        resp = requests.get(f"{cfg['ollama_host']}/api/tags", timeout=5)
        return resp.status_code == 200
    except Exception:
        return False


def get_ollama_model() -> str:
    """Get which vision model to use. Try several known names."""
    try:
        resp = requests.get(f"{cfg['ollama_host']}/api/tags", timeout=5)
        models = resp.json().get("models", [])
        available = [m["name"] for m in models]

        # Prefer known vision model names
        candidates = [
            "moondream:latest", "moondream:1.8b",
            "llava:latest",
            "qwen2.5vl:latest", "qwen2.5vl:3b",
            "phi3.5-vision:latest", "phi3.5-vision:3.8b",
        ]
        for c in candidates:
            for a in available:
                if c.split(":")[0] in a.lower():
                    return a

        # Fall back to any vision model in list
        for a in available:
            name = a.lower()
            if any(x in name for x in ["vision", "llava", "moondream", "phi3", "qwen2.5vl"]):
                return a

        return available[0] if available else DEFAULT_MODEL
    except Exception as e:
        log.warning(f"Could not list Ollama models: {e}")
        return DEFAULT_MODEL


def ollama_vision(image_bytes: bytes, prompt: str, model: str) -> str:
    """Send image to Ollama vision model and get text response."""
    try:
        # Build multipart form data like `curl` does
        url = f"{cfg['ollama_host']}/api/chat"
        files = {
            "image": ("frame.jpg", io.BytesIO(image_bytes), "image/jpeg")
        }
        # For chat completions with image, use the /api/chat endpoint
        # with a vision-capable model
        payload = {
            "model": model,
            "messages": [
                {"role": "user", "content": prompt, "images": [image_bytes]}
            ],
            "stream": False,
        }
        resp = requests.post(url, json=payload, timeout=120)
        if resp.status_code == 200:
            data = resp.json()
            return data.get("message", {}).get("content", "").strip().lower()
        else:
            log.error(f"Ollama error {resp.status_code}: {resp.text[:200]}")
            return "stop"
    except Exception as e:
        log.error(f"Ollama call failed: {e}")
        return "stop"


def extract_direction(text: str) -> str:
    """Parse a direction word from AI response."""
    text = text.lower()
    words = {"forward", "backward", "left", "right", "stop"}
    for w in words:
        if w in text:
            return w
    return "stop"


# ── Routes ────────────────────────────────────────────────────────────────────

@app.on_event("startup")
def startup():
    if check_ollama():
        model = get_ollama_model()
        cfg["model"] = model
        log.info(f"Ollama connected. Using model: {model}")
    else:
        log.warning(
            "⚠️  Ollama not reachable at %s — AI decisions will return 'stop' "
            "until it connects.", cfg["ollama_host"]
        )
    log.info(f"Server running on http://{args.host}:{args.port}")


@app.get("/")
def index():
    return {
        "status": "ok",
        "model": cfg["model"],
        "ollama": cfg["ollama_host"],
        "last_decision": latest_decision,
    }


@app.post("/api/frame")
async def receive_frame(file: UploadFile = File(...)):
    """Robot sends a JPEG frame here."""
    global latest_frame
    try:
        data = await file.read()
        with lock:
            latest_frame = data
        return JSONResponse({"received": True, "size": len(data)})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/command")
def get_command():
    """Robot polls here to get the current motor command."""
    with lock:
        return cfg["last_command"]


@app.post("/api/command")
def post_command(data: dict):
    """Manual override: set a motor command (e.g. from dashboard)."""
    direction = data.get("direction", "stop")
    speed = data.get("speed")
    with lock:
        cfg["last_command"] = {"direction": direction, "speed": speed}
    log.info(f"Manual command set: {direction} @ {speed}")
    return {"ok": True}


@app.get("/api/frame/latest.jpg")
def latest_jpg():
    """Streaming endpoint: return the most recent frame as JPEG."""
    with lock:
        if latest_frame is None:
            raise HTTPException(status_code=204, detail="No frame yet")
        return JSONResponse(
            content=latest_frame,
            media_type="image/jpeg"
        )


@app.post("/api/ai_decide")
def ai_decide():
    """
    Trigger an AI decision on the latest frame.
    Returns the decision directly (synchronous, blocking).
    """
    global latest_decision, last_decision_time

    with lock:
        frame = latest_frame

    if frame is None:
        return JSONResponse({"decision": "stop", "reason": "no frame"})

    log.info(f"Analyzing frame ({len(frame)} bytes) with {cfg['model']}...")
    start = time.time()

    response_text = ollama_vision(frame, NAVIGATION_PROMPT, cfg["model"])
    direction = extract_direction(response_text)
    elapsed = time.time() - start

    log.info(f"AI decision: {direction!r} ({elapsed:.1f}s) — raw: {response_text[:80]!r}")

    with lock:
        latest_decision = direction
        last_decision_time = time.time()
        cfg["last_command"] = {"direction": direction, "speed": None}

    return JSONResponse({
        "decision": direction,
        "raw": response_text,
        "model": cfg["model"],
        "elapsed_s": round(elapsed, 2),
    })


@app.post("/api/autonomous_loop")
def autonomous_loop():
    """
    Single step of the autonomous loop:
    - Take latest frame
    - Run AI decision
    - Return command
    Use from the dashboard to trigger steps manually.
    """
    return ai_decide()


# ── CLI ───────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Robot AI brain server")
    parser.add_argument("--host", default="0.0.0.0", help="Bind host")
    parser.add_argument("--port", type=int, default=8000, help="Port")
    parser.add_argument("--ollama", default=DEFAULT_OLLAMA_HOST, help="Ollama host URL")
    parser.add_argument("--model", default=None, help="Vision model name")
    args = parser.parse_args()

    cfg["ollama_host"] = args.ollama
    if args.model:
        cfg["model"] = args.model

    uvicorn.run(app, host=args.host, port=args.port, log_level="info")
