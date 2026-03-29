# Robot with AI v1 - Detailed Build Research

**Project:** Low-cost autonomous robot with AI vision  
**Inspired by:** "I Gave Claude a Body" (Traxxas Maxx + Claude + MCP)  
**Goal:** Build a cheap, simple, small-scale version for ~$50–150  
** Vijay's assets:** Raspberry Pi 4, basic tools, programming skills

---

## Table of Contents

1. [Original Project Reference](#original-project-reference)
2. [Hardware Selection](#hardware-selection)
3. [Component Alternatives with Pricing](#component-alternatives-with-pricing)
4. [Software Architecture](#software-architecture)
5. [Simplified Build Steps](#simplified-build-steps)
6. [Minimum Viable Product Options](#minimum-viable-product-options)
7. [Recommended MVP Configuration](#recommended-mvp-configuration)

---

## Original Project Reference

The YouTube video built an AI-powered autonomous RC car with:

| Component | Cost |
|-----------|------|
| Traxxas Maxx RC car | ~$1,100 |
| Raspberry Pi 5 | ~$80 |
| 16MP camera + wide-angle lens | ~$60 |
| 4G LTE hat | ~$50 |
| PCA9685 servo driver | ~$15 |
| Apple Depth Pro (ML depth estimation) | Free |
| Custom 3D printed body | ~$30 |
| **Total** | **~$1,335+** |

Key software concepts to preserve:
- **MCP server** bridging AI brain ↔ hardware control
- **Vision pipeline** capturing images and prompting AI for navigation decisions
- **Web dashboard** for remote viewing and control
- **Journey Grid** (6-image collage) for temporal context

Key simplifications for our build:
- WiFi instead of 4G LTE (indoor/small outdoor use)
- No depth estimation model (use simpler obstacle detection)
- No ESC — use basic DC motor driver instead
- Smaller chassis, not full RC car scale
- Raspberry Pi 4 ( already owned) instead of Pi 5

---

## Hardware Selection

### 2.1 Single-Board Computer

** Already available: Raspberry Pi 4 (4GB)** — this is the primary compute.

| Option | Pi 4 (4GB) | Pi 5 (4GB) | Jetson Nano |
|--------|-----------|-----------|-------------|
| Cost | ~$0 (owned) | ~$80 | ~$150+ |
| AI inference speed | Moderate | Faster | GPU-accelerated |
| WiFi | Built-in | Built-in | Optional |
| Power draw | 5V/3A | 5V/5A | 5V/2A |
| Camera support | CSI + USB | CSI + USB | CSI only |
| Verdict | ✅ Use what you have | Future upgrade | Overkill + expensive |

**Recommendation:** Start with the **Raspberry Pi 4**. Ollama runs fine on it for image captioning and basic reasoning tasks. If inference is too slow, consider Pi 5 as a future upgrade.

---

### 2.2 Motor Driver

The original used a PCA9685 servo driver + ESC for precision steering. We need something simpler and cheaper.

| Driver | Cost | Current | Channels | Use Case | Verdict |
|--------|------|---------|----------|----------|---------|
| **L298N Dual H-Bridge** | ~$5–8 | 2A per channel | 2 (2 motors) | DC motors, simple | ✅ Budget choice |
| **L293D Motor Shield** | ~$10–15 | 600mA | 4 (2 motors) | Arduino shields | ⚠️ Underpowered for bigger motors |
| **TB6612FNG** | ~$8–12 | 3A per channel | 2 (2 motors) | DC motors, efficient | ✅ Better than L298N |
| **PCA9685 + Servos** | ~$10–15 | 25mA per channel | 16 | Precision steering | ⚠️ Need servos + ESC equivalent |
| **DRV8833** | ~$5 | 1.5A | 2 (2 motors) | Small motors | ✅ Ultra-cheap for tiny bots |

**Recommendation:** **L298N** for budget builds (works with 2 motors, handles 5–35V). **TB6612FNG** if you want better efficiency and less heat. Both are widely available and well-documented.

---

### 2.3 Robot Chassis / Platform

This is where most of the cost lives. Here are options from cheapest to most capable:

| Option | Type | Cost | Motors | Drive | Notes |
|--------|------|------|--------|-------|-------|
| **2WD Smart Car Kit** (generic) | Kit | ~$15–20 | 2× DC gear motors | Differential | Most popular for Pi robots |
| **4WD Smart Car Kit** | Kit | ~$25–35 | 4× DC gear motors | Differential | Better traction |
| **Tank/Track Kit** (Tamiya or generic) | Kit | ~$30–50 | 2× DC motors | Tank tread | Great off-road, complex |
| **Buggy Robot Kit** (Adeept) | Kit | ~$40–55 | 2× DC + servo | Ackermann-ish | Looks like a real car |
| **Cheap RC car chassis** (Traxxas clones) | Used/cheap | ~$20–40 | Brushed DC + ESC | Shaft drive | Needs ESC, more complex |
| **Custom 3D printed / acrylic** | DIY | ~$15–25 | 2× N20 motors | Differential | Flexible but needs fabrication |

**Recommendation:** Start with a **2WD or 4WD Smart Car Kit** (~$18–25 on Amazon/AliExpress). These come with motor mounts, wheels, and chassis plates — everything you need in one box. The 4WD version handles indoor carpet better.

---

### 2.4 Camera

| Camera | Cost | Resolution | Interface | FOV | Notes |
|--------|------|-----------|-----------|-----|-------|
| **Raspberry Pi Camera v2** | ~$25–30 | 8MP | CSI (native) | 62.2° | ✅ Native Pi support, great quality |
| **Raspberry Pi Camera v3** | ~$35–40 | 12MP | CSI | 78° (wide) | Auto-focus, HDR — worth the ~$10 extra |
| **PiCamera Module 3 (NoIR)** | ~$40 | 12MP | CSI | 78° | No IR filter = night vision with IR LEDs |
| **USB Webcam (Logitech C270)** | ~$20–30 | 720p | USB | 55° | Easier to mount, less flexible |
| **Wide-angle USB webcam** | ~$15–25 | 1080p | USB | 110–170° | Good coverage but lower quality |
| **OAK-D Lite** | ~$120 | 12MP + depth | USB-C | 120° | Depth sensing, overkill for this project |

**Recommendation:** **Raspberry Pi Camera v3** (~$35) with a wide-angle lens attachment (~$8) — gives you auto-focus, 12MP, and native CSI connection with no USB overhead. If budget is tight, v2 at ~$25 is excellent. Avoid cheap USB webcams on Pi 4 — they compete for USB bandwidth.

---

### 2.5 Power Supply

Power is often overlooked and causes frustration. Here's what you need:

| Solution | Cost | Capacity | Notes |
|----------|------|----------|-------|
| **Power bank (20,000mAh, 5V/3A)** | ~$15–20 | Powers Pi only | Simple, but doesn't power motors |
| **LiPo 2S (7.4V) + UBEC** | ~$15–20 | Powers all | Need UBEC to step down to 5V for Pi |
| **LiPo 3S (11.1V) + UBEC** | ~$20 | Motors + Pi | More headroom, needs 12V input driver |
| **AA battery pack (8× AA)** | ~$8–12 | Short life | Cheap but heavy, no recharge |
| **18650 Li-Ion pack (2S2P)** | ~$12–18 | Good capacity | Rechargeable, good current delivery |

**Recommendation:** **LiPo 2S (7.4V) 1000–2000mAh + UBEC** (~$15) — this gives you 7.4V for the motor driver (L298N/TB6612 can handle this directly) and 5V/3A regulated output for the Pi via the UBEC. Add a USB power bank for Pi only if you want separation.

---

### 2.6 Connectivity

- **WiFi:** Pi 4 has built-in WiFi — use it. Make sure the Pi is on the same network as the machine running Ollama (or run Ollama on the Pi itself for standalone operation).
- **No 4G needed** — we're targeting indoor/small outdoor use.
- Optional: **ESP32-CAM** for a secondary wireless camera feed (~$8, adds complexity).

---

## Component Alternatives with Pricing

### Option A: Ultra-Cheap (~**$50**)

| Component | Specific Product | Price |
|-----------|-----------------|-------|
| Chassis | 2WD Smart Car Kit (AliExpress/Amazon basics) | $12–15 |
| Motor Driver | L298N (generic) | $5 |
| Camera | Raspberry Pi Camera v2 (or use phonecam) | $25 |
| Power | 8× AA battery holder | $5 |
| Wires/Breadboard | Jumper wires + mini breadboard | $5 |
| **Total** | | **$52–55** |

*Note: Uses existing Raspberry Pi 4. Assumes you already have a phone/computer running Ollama.*

### Option B: Mid-Range (~**$100**)

| Component | Specific Product | Price |
|-----------|-----------------|-------|
| Chassis | 4WD Smart Car Kit (SunFounder or similar) | $28–35 |
| Motor Driver | TB6612FNG (better than L298N) | $10 |
| Camera | Raspberry Pi Camera v3 | $35 |
| Power | LiPo 2S (1000mAh) + UBEC | $15 |
| Misc | Jumper wires, breadboard, zip ties | $5 |
| **Total** | | **$93–105** |

### Option C: Full-Featured (~**$150**)

| Component | Specific Product | Price |
|-----------|-----------------|-------|
| SBC | Raspberry Pi 5 (if upgrading from Pi 4) | ~$80 |
| Chassis | 4WD Tank Track Kit or Buggy Kit | $40–50 |
| Motor Driver | TB6612FNG + PCA9685 (for servo) | $20 |
| Camera | Pi Camera v3 Wide-angle | $35 + $8 lens |
| Power | LiPo 3S (1500mAh) + UBEC | $22 |
| IMU | MPU6050 gyroscope (optional) | $5 |
| Misc | Wires, mounts, breadboard | $8 |
| **Total** | | **$175–205** |

*Note: Option C pushes past $150 if including Pi 5. Skip the Pi 5 upgrade to stay within budget — Pi 4 is sufficient.*

---

## Software Architecture

### Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                      USER / WEB DASHBOARD                       │
│                  (Streamlit or Flask + Browser)                 │
└───────────────────────────┬─────────────────────────────────────┘
                            │ HTTP / WebSocket
┌───────────────────────────▼─────────────────────────────────────┐
│                     FLASK / FASTAPI SERVER                       │
│                  (Runs on Raspberry Pi 4)                        │
│  ┌──────────────┐  ┌──────────────┐  ┌────────────────────────┐ │
│  │  Camera      │  │  Motor       │  │  Ollama Client         │ │
│  │  Capture     │  │  Controller  │  │  (image + text prompt) │ │
│  │  Service     │  │  Service     │  │  Service               │ │
│  └──────────────┘  └──────────────┘  └────────────────────────┘ │
└───────────────────────────┬─────────────────────────────────────┘
                            │ calls
┌───────────────────────────▼─────────────────────────────────────┐
│                     OLLAMA (Local AI)                            │
│                  (llava or llama3.2 vision)                      │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  Image → Caption/Analysis → Navigation Decision           │   │
│  │  Prompt: "What direction should the robot go? forward,   │   │
│  │          left, right, or stop?"                           │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                            │
┌───────────────────────────▼─────────────────────────────────────┐
│                     MOTOR DRIVER (L298N / TB6612)                │
│                  GPIO Pins → Motor signals                       │
└─────────────────────────────────────────────────────────────────┘
```

---

### 4.1 Ollama Integration

**Why Ollama:** Free, local, privacy-friendly. Runs on the Pi 4 (using quantized models).

**Recommended Models:**

| Model | Size | Use Case | Pi 4 Feasibility |
|-------|------|----------|-----------------|
| **llava:latest** | 4.7GB | Vision + language | ✅ Best choice — designed for images |
| **llama3.2-vision:11b** | ~7.9GB | Vision + reasoning | ⚠️ Heavy, slow on Pi 4 |
| **llama3.2:3b** | 2.0GB | Text-only reasoning | ✅ Fast, combine with llava |
| **phi3.5-vision:3.8b** | ~2.5GB | Lightweight vision | ✅ Good alternative |

**Setup on Pi 4:**
```bash
# Install Ollama on Pi
curl -fsSL https://ollama.com/install.sh | sh

# Pull vision model
ollama pull llava:latest

# Or lightweight alternative
ollama pull phi3.5-vision:3.8b

# Run server (default port 11434)
ollama serve
```

**Prompting strategy for navigation:**
```
System: You are a small robot. Analyze the image and respond with ONLY 
one word: "forward", "left", "right", or "stop". Consider obstacles, 
boundaries, and safety.

User: [attached image]
```

---

### 4.2 MCP Server Design

The MCP (Model Context Protocol) server bridges the AI model to hardware. Here's the architecture:

```python
# Simplified MCP Server (Python)
# Runs on Pi alongside Flask server

import json
import serial
import gpiozero
from mcp.server.fastmcp import FastMCP

# Initialize MCP server
mcp = FastMCP("robot-control")

# Hardware resources
class MotorController:
    def __init__(self, driver="tb6612"):
        if driver == "tb6612":
            # TB6612 pins: AIN1, AIN2, PWMA, BIN1, BIN2, PWMB
            self.left_motor = Motor(22, 23, 13)  # GPIO pins
            self.right_motor = Motor(24, 25, 12)
    
    def forward(self, speed=0.5):
        self.left_motor.forward(speed)
        self.right_motor.forward(speed)
    
    def left(self, speed=0.5):
        self.left_motor.reverse(speed)
        self.right_motor.forward(speed)
    
    def right(self, speed=0.5):
        self.left_motor.forward(speed)
        self.right_motor.reverse(speed)
    
    def stop(self):
        self.left_motor.stop()
        self.right_motor.stop()

motor_ctrl = MotorController()

# MCP Tools (exposed to AI model)
@mcp.tool()
def move_forward(distance_meters: float = 0.5):
    """Move the robot forward by specified distance."""
    motor_ctrl.forward(speed=0.6)
    time.sleep(distance_meters / 0.3)  # rough speed estimate
    motor_ctrl.stop()
    return {"status": "moved_forward", "distance": distance_meters}

@mcp.tool()
def turn(direction: str):
    """Turn robot left or right 90 degrees."""
    if direction == "left":
        motor_ctrl.left(speed=0.5)
        time.sleep(0.8)  # calibrate turn time
    else:
        motor_ctrl.right(speed=0.5)
        time.sleep(0.8)
    motor_ctrl.stop()
    return {"status": "turned", "direction": direction}

@mcp.tool()
def stop():
    """Emergency stop - halt all motors immediately."""
    motor_ctrl.stop()
    return {"status": "stopped"}

@mcp.tool()
def capture_image() -> str:
    """Capture image from camera and return base64 for vision analysis."""
    # libcamera-still or OpenCV capture
    # Return path to saved image
    return "/tmp/robot_capture.jpg"

@mcp.tool()
def read_sensors() -> dict:
    """Read ultrasonic sensor distance."""
    # HC-SR04 reading
    return {"distance_cm": 45.2}
```

**Alternative — No MCP, Direct API:**
If MCP setup is too complex, use a simple Flask REST API:

```python
# Simple alternative - Flask API instead of full MCP
from flask import Flask, jsonify, request
import subprocess

app = Flask(__name__)

@app.route('/api/image', methods=['GET'])
def get_image():
    # Capture image, return path or base64
    return jsonify({"image_path": "/tmp/robot_capture.jpg"})

@app.route('/api/analyze', methods=['POST'])
def analyze():
    image_path = request.json.get('image_path')
    # Call Ollama with image
    result = subprocess.run([
        'ollama', 'run', 'llava:latest',
        f"Analyze this image. What should a robot do? "
        f"Respond with ONLY one word: forward, left, right, or stop."
        f"<image>"
    ], capture_output=True, text=True)
    return jsonify({"decision": result.stdout.strip()})

@app.route('/api/move', methods=['POST'])
def move():
    direction = request.json.get('direction')
    # Execute motor command
    return jsonify({"status": "ok", "moved": direction})
```

---

### 4.3 Vision Processing Pipeline

**Step-by-step flow:**

```
1. Capture Frame
   ├─ libcamera-still -o /tmp/frame.jpg --width 640 --height 480
   └─ Or: OpenCV cv2.VideoCapture(0) + cv2.imwrite()

2. Pre-process Image
   ├─ Resize to 640×480 (smaller = faster AI inference)
   ├─ Optionally crop for forward-facing perspective
   └─ Compress to JPEG if needed

3. AI Analysis (Ollama)
   ├─ Send image + text prompt to llava model
   ├─ Prompt: "What direction should this robot go? Options: forward, 
   │          left, right, stop. Look for obstacles and path clarity."
   └─ Parse response: extract one word (forward/left/right/stop)

4. Decision & Action
   ├─ Map AI response to motor command
   ├─ Execute movement (with timeout)
   └─ Add safety check: if ultrasonic sensor < 10cm → STOP

5. Loop
   └─ Repeat at ~0.5–1 Hz (every 1–2 seconds)
```

**Frame rate considerations:**
- Pi 4 can handle ~0.5–1 image analysis per second with llava
- For faster response, use smaller model (phi3.5-vision) or lower resolution
- Don't try to match the original project's real-time video — 1 FPS is fine for autonomous wandering

---

### 4.4 Web Dashboard

**Simple approach — Streamlit (recommended):**

```python
# dashboard.py - Run on Pi, access via browser
import streamlit as st
import requests
import cv2
from PIL import Image
import io

st.set_page_config(page_title="Robot Control Center")
st.title("🤖 AI Robot Dashboard")

# Live camera feed
frame = requests.get("http://localhost:5000/video_feed")
if frame.ok:
    st.image(frame.content, channels="RGB", width=640)

# Control buttons
col1, col2, col3, col4 = st.columns(4)
with col1:
    if st.button("⬆️ Forward"):
        requests.post("http://localhost:5000/api/move", json={"direction": "forward"})
with col2:
    if st.button("⬅️ Left"):
        requests.post("http://localhost:5000/api/move", json={"direction": "left"})
with col3:
    if st.button("➡️ Right"):
        requests.post("http://localhost:5000/api/move", json={"direction": "right"})
with col4:
    if st.button("⏹️ Stop"):
        requests.post("http://localhost:5000/api/move", json={"direction": "stop"})

# AI Mode toggle
if st.toggle("🤖 AI Autonomous Mode"):
    st.info("AI is navigating autonomously...")
    # Trigger continuous AI loop
    response = requests.post("http://localhost:5000/api/ai_step")
    st.write(f"AI Decision: {response.json().get('decision')}")

# Console log
st.text_area("Log", value="System ready...\n", height=200)
```

**Start with:**
```bash
pip install streamlit
streamlit run dashboard.py --server.port 8501
```

Access at `http://<pi-ip>:8501`

---

## Simplified Build Steps

### Week 1: Hardware Assembly (~3–4 hours)

**Step 1: Unbox and assemble the chassis**
- Follow kit instructions to attach motors, wheels, and chassis plate
- For 2WD: left motor + right motor only
- Leave room on the chassis for the Pi and camera

**Step 2: Wire the motor driver**
```
L298N / TB6612 connections to Raspberry Pi 4:
  - Motor A (left):  IN1 → GPIO 23, IN2 → GPIO 24, ENA → GPIO 13 (PWM)
  - Motor B (right): IN3 → GPIO 25, IN4 → GPIO 16, ENB → GPIO 12 (PWM)
  - GND → Pi GND (pin 6)
  - VCC → 7.4V LiPo (direct from battery, for motors)
  - 5V regulator → powers logic (or use separate 5V supply)
  - 3.3V/5V from Pi → VCC logic side of driver
```

**Step 3: Connect the camera**
- Pi Camera v2/v3: CSI ribbon cable to Pi CSI port
- Route camera cable through chassis to face forward
- Secure with zip ties or tape

**Step 4: Set up power**
- LiPo battery → XT60 or JST connector → UBEC (if using) → 5V microUSB for Pi
- Or: LiPo → L298N 5V output → microUSB cable to Pi
- **Important:** Never power motors from the Pi's 5V rail — use external battery

**Step 5: Initial test**
```bash
# SSH into Pi
ssh pi@raspberrypi.local

# Test motor driver with Python
python3 << 'EOF'
import gpiozero
from gpiozero import Motor

motor = Motor(23, 24)  # Test one motor
motor.forward()
import time; time.sleep(2)
motor.stop()
print("Motor test OK")
EOF
```

---

### Week 2: Software Setup (~2–3 hours)

**Step 6: Install Ollama on Pi 4**
```bash
curl -fsSL https://ollama.com/install.sh | sh
ollama pull llava:latest
ollama serve
```

**Step 7: Install project dependencies**
```bash
pip install flask opencv-python gpiozero picamera2 requests
```

**Step 8: Set up the Flask API server**
- Create `/home/pi/robot/api.py` with camera capture, motor control, Ollama client
- Test each endpoint individually

**Step 9: Set up the web dashboard**
```bash
pip install streamlit
streamlit run /home/pi/robot/dashboard.py
```

---

### Week 3: Integration & Autonomous Mode (~3–4 hours)

**Step 10: Wire ultrasonic sensor (HC-SR04)**
```
HC-SR04 → Pi 4:
  - VCC → 5V
  - GND → GND
  - TRIG → GPIO 18
  - ECHO → GPIO 17 (via 1kΩ resistor)
```

**Step 11: Write the autonomous loop**
```python
# autonomous_loop.py
import time
import requests
import cv2
from picamera2 import Picamera2

picam = Picamera2()
picam.start()

def autonomous_step():
    # 1. Capture
    frame = picam.capture_array()
    cv2.imwrite('/tmp/frame.jpg', frame)
    
    # 2. Safety check
    distance = read_ultrasonic()  # your sensor function
    if distance < 10:  # cm
        move("stop")
        return "stop"
    
    # 3. AI decision
    response = requests.post("http://localhost:5000/api/ai_decide", 
                            files={"image": open('/tmp/frame.jpg', 'rb')})
    decision = response.json().get('decision', 'stop')
    
    # 4. Execute
    move(decision)
    return decision

while True:
    decision = autonomous_step()
    print(f"Decision: {decision}")
    time.sleep(2)  # Wait between decisions
```

**Step 12: Tune and calibrate**
- Adjust motor speeds (PWM values)
- Calibrate turn duration (test how long "left" needs to be for 90°)
- Tune ultrasonic threshold
- Adjust AI prompting for better decisions

---

## Minimum Viable Product Options

### MVP Option A: Ultra-Cheap (~$50)

**Goal:** Just prove the concept — basic autonomous movement with vision.

| Part | Product | Price |
|------|---------|-------|
| Chassis | 2WD Smart Car Kit (AliExpress) | $12 |
| Motor Driver | L298N | $5 |
| Camera | USB webcam (old phone camera or $10) | $0–10 |
| Power | 8× AA battery holder | $5 |
| Wires | Jumper wires | $3 |
| **Total** | | **$35–40** (plus existing Pi 4) |

**What you get:** A robot that drives forward until it sees something, then stops or turns. Basic line-of-sight manual control via web UI. Ollama vision on a remote machine (laptop) since Pi 4 might be slow with webcam.

**Limitations:** No depth sensing, slow AI response, no indoor carpet handling.

---

### MVP Option B: Mid-Range (~$100) — **Recommended**

**Goal:** Fully functional indoor autonomous robot with vision and safety sensors.

| Part | Product | Price |
|------|---------|-------|
| Chassis | 4WD Smart Car Kit (SunFounder or Adeept) | $30 |
| Motor Driver | TB6612FNG (or stick with L298N) | $10 |
| Camera | Raspberry Pi Camera v3 | $35 |
| Ultrasonic | HC-SR04 (×3 for front/sides) | $6 |
| Power | LiPo 2S (1000mAh) + UBEC | $15 |
| Misc | Wires, breadboard, mounts | $5 |
| **Total** | | **~$101** |

**What you get:** 
- 4WD for carpet/indoor surfaces
- Vision-based autonomous navigation via Ollama
- Ultrasonic safety stops (stops before hitting walls)
- Web dashboard with live camera feed
- Runs AI locally on Pi 4
- Can operate in autonomous wander mode or manual control

**This is the sweet spot.** Under $110, fully functional, and actually fun to use.

---

### MVP Option C: Full-Featured (~$150)

**Goal:** Near-reference implementation with better hardware.

| Part | Product | Price |
|------|---------|-------|
| Chassis | Tank/Track Kit or Buggy Kit | $45–55 |
| Motor Driver | TB6612FNG + PCA9685 (for future servo) | $22 |
| Camera | Pi Camera v3 + wide-angle lens | $43 |
| Ultrasonic | HC-SR04 × 3 | $6 |
| Power | LiPo 3S (1500mAh) + UBEC | $22 |
| IMU | MPU6050 (optional) | $5 |
| **Total** | | **~$143–153** |

**What you get:**
- Tank tracks for outdoor/rough terrain
- Future upgrade path: add servo steering with PCA9685
- Wide-angle camera for better navigation visibility
- IMU for orientation tracking
- All the indoor capabilities of Option B, plus outdoor use

**Trade-off:** Pushing past $150. If you already have a Pi 4, Option B + skip Pi 5 keeps you under $110.

---

## Recommended MVP Configuration

Based on Vijay's existing hardware (Pi 4), skills, and budget constraints, here's the recommended build:

### Recommended Parts List

```
Already owned:
✅ Raspberry Pi 4 (4GB)
✅ Basic tools (soldering iron, multimeter, etc.)
✅ MicroSD card (16GB+)
✅ WiFi network

To purchase (~$95–105):
1. 4WD Smart Car Chassis Kit .......... $30–35
   (SunFounder Smart Robot Car Kit or similar on Amazon)
   → Includes: chassis, 4 motors, wheels, encoders

2. Raspberry Pi Camera v3 ............. $35
   (official Raspberry Pi Camera v3, 12MP, auto-focus)

3. TB6612FNG Motor Driver Module ...... $10
   (dual motor driver, much better than L298N)

4. HC-SR04 Ultrasonic Sensors ......... $6
   (×3: front + left + right coverage)

5. LiPo Battery 2S (1000mAh) + UBEC .. $15
   (7.4V for motors, regulated 5V for Pi)

6. Jumper wires + Mini Breadboard .... $5
   (for prototyping sensor connections)

TOTAL: ~$95–101
```

### Software Stack

| Layer | Technology | Notes |
|-------|-----------|-------|
| AI Brain | Ollama + llava:latest | Vision + reasoning, runs on Pi 4 |
| API Server | Flask | Handles camera, motor, AI calls |
| Web Dashboard | Streamlit | Live video + controls |
| Motor Control | gpiozero + TB6612FNG | Simple Python GPIO |
| Camera | picamera2 | Native Pi camera library |
| Safety | HC-SR04 via gpiozero | Ultrasonic collision avoidance |

### Build Priority Order

1. **Phase 1** — Manual control: Wire motors, test via SSH commands
2. **Phase 2** — Camera + web feed: Get live video working
3. **Phase 3** — Web dashboard: Add manual control buttons
4. **Phase 4** — Ollama integration: Test image analysis
5. **Phase 5** — Autonomous loop: Connect AI decisions to motor commands
6. **Phase 6** — Safety sensors: Add ultrasonic stops

### Key Differences from Original Video

| Feature | Original ($1,100) | Our Build (~$100) |
|---------|------------------|-------------------|
| Chassis | $1,100 Traxxas Maxx | $30 4WD kit |
| SBC | Pi 5 | Pi 4 (already owned) |
| Camera | 16MP + wide-angle ($60) | Pi Camera v3 ($35) |
| Connectivity | 4G LTE | WiFi only |
| Steering | Servo + ESC | Differential (tank-style) |
| Depth | Apple Depth Pro ML | Ultrasonic sensors only |
| AI | Claude via cloud | Ollama (local, free) |
| Dashboard | Custom web app | Streamlit (faster dev) |

---

## Risks & Mitigations

| Risk | Likelihood | Mitigation |
|------|-----------|------------|
| Pi 4 too slow for Ollama | Medium | Run Ollama on laptop; Pi as controller only |
| Motors draw too much current | Medium | Use separate battery for motors; never from Pi 5V rail |
| Camera cable disconnects | Low | Secure with cable clips or tape |
| Robot gets stuck | High | Use ultrasonic + boundary setup (test in a room first) |
| WiFi latency for control | Low | Use hardcoded fallback delays; test range first |

---

## Next Steps for Vijay

1. **Order parts** — Aim for Option B (~$100) as recommended
2. **Set up Pi 4** — Fresh Raspberry Pi OS install + SSH enabled
3. **Install Ollama** on the Pi and test with a sample image
4. **Assemble chassis** — Follow kit instructions
5. **Wire motor driver** — Double-check GPIO pin assignments
6. **Test manual control** — Make the robot drive via SSH commands
7. **Add camera** — Get live feed working
8. **Build dashboard** — Streamlit web UI
9. **Integrate AI** — Connect vision pipeline to motor control
10. **Add safety sensors** — Ultrasonic collision avoidance
11. **Tune autonomous behavior** — Adjust prompting, speeds, thresholds

---

*Document version: 1.0 | Based on "I Gave Claude a Body" video analysis and low-cost alternatives research*
