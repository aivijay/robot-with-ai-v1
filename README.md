# robot-with-ai-v1

**Build an autonomous AI robot on a budget.** The robot is a WiFi "thin client" — it just streams camera images and runs motor commands. All AI runs on your laptop via Ollama.

Inspired by the [YouTube video "I Gave Claude a Body"](https://www.youtube.com/watch?v=jBpQiv-ZlVM) but simplified for ~$30–100.

---

## Architecture

```
┌─────────────────────────┐        WiFi         ┌──────────────────────────┐
│         LAPTOP          │ ◄────────────────── │         ROBOT            │
│                         │                      │                          │
│  Ollama (vision model)  │  HTTP POST /api/frame│  Camera (CSI or USB)     │
│         +               │ ──────────────────► │  Motors + driver         │
│  FastAPI server         │                      │  WiFi client             │
│  (receives frames,      │ ◄────────────────── │  Lightweight Python      │
│   calls AI, returns     │   HTTP GET /api/cmd  │   or Arduino (ESP32)     │
│   commands)             │                      │                          │
└─────────────────────────┘                      └──────────────────────────┘
```

**The robot runs zero AI models.** Your laptop does all the thinking.

---

## Quick Start

### 1. Laptop Setup (once)

```bash
# Install dependencies
pip install fastapi uvicorn requests pillow streamlit openai

# Install a vision model in Ollama
ollama pull moondream:1.8b     # fast, ~1GB, good enough for navigation
# or for better quality:
ollama pull llava:latest       # slower, ~4.7GB
# or:
ollama pull qwen2.5vl:3b       # ~2.3GB

# Start the server
python src/laptop/laptop_server.py

# In another terminal, start the dashboard
streamlit run src/laptop/dashboard.py --server.port 8501
```

### 2. Robot Setup

**Option A — Pi Zero 2 W or Pi 4** (recommended, ~$25–65 new):
```bash
# SSH into your Pi, then:
sudo apt install python3-pip
pip install picamera2 gpiozero requests

# Set your laptop IP (change 192.168.1.100 to your actual laptop IP)
export LAPTOP_IP=192.168.1.100

# Run the thin client
python3 src/robot/robot_client.py --laptop $LAPTOP_IP --port 8000
```

**Option B — ESP32-CAM** (cheapest, ~$8–10 + parts):
- Flash `src/robot/robot_client_esp32/robot_client_esp32.ino` using Arduino IDE
- Set your WiFi SSID/password and laptop IP in the sketch
- The ESP32-CAM streams directly to the laptop

### 3. Test It

Dashboard at `http://localhost:8501`:
- **Manual mode**: Click direction buttons to drive
- **AI mode**: Click "Run AI Step" or toggle "Auto-navigate"
- Watch the robot respond to what it sees

---

## Parts List

| Option | Robot Brain | New Cost | Notes |
|--------|-------------|----------|-------|
| **A** | ESP32-CAM | $30–40 | Ultra-cheap, Arduino code |
| **B** | Pi Zero 2 W + camera | $55–65 | Full Pi OS, Python |
| **C** | Pi 4 (you own) + camera | $65–75 | Zero incremental SBC cost |

See [docs/parts-list.md](docs/parts-list.md) for specific products and links.

---

## Project Structure

```
robot-with-ai-v1/
├── docs/
│   ├── architecture.md      # Architecture overview (start here)
│   ├── parts-list.md        # Specific products with prices
│   ├── detailed-research.md # Original detailed research
│   ├── pi-zero-2-research.md # Zero 2 W feasibility (now viable!)
│   └── research-v1.md        # Original research notes
├── src/
│   ├── robot/
│   │   ├── robot_client.py              # Python thin client (Pi)
│   │   └── robot_client_esp32/
│   │       └── robot_client_esp32.ino    # Arduino sketch (ESP32-CAM)
│   └── laptop/
│       ├── laptop_server.py   # FastAPI + Ollama brain
│       └── dashboard.py        # Streamlit dashboard
└── tests/
```

---

## How It Works

1. **Robot captures** a camera frame (640×480 JPEG)
2. **Robot sends** the frame to laptop via `POST /api/frame`
3. **Laptop receives** the frame and sends it to Ollama vision model
4. **Ollama returns** a text decision: `forward`, `left`, `right`, `stop`
5. **Robot polls** `GET /api/command` and executes the motor command
6. **Loop** repeats at ~1–5 FPS

---

## Key Design Decisions

| Decision | Choice | Why |
|----------|--------|-----|
| AI location | Laptop | No powerful hardware needed on robot |
| Robot OS | Pi OS or Arduino | Simple, well-documented |
| Protocol | HTTP REST | No special libraries needed |
| Vision model | moondream:1.8b | Fastest, smallest, good enough |
| Motor driver | DRV8833 | Cheap, 2 channels, 1.5A |

---

## Troubleshooting

**"Ollama not reachable"**
```bash
# Make sure Ollama is running on laptop
ollama serve

# Or check the host URL
curl http://localhost:11434/api/tags
```

**Robot not connecting to laptop**
- Check both are on the same WiFi network
- Verify laptop firewall allows port 8000
- Check laptop IP: `ip addr show wlan0 | grep inet`

**Slow AI responses**
- Use `moondream:1.8b` instead of `llava`
- Reduce frame resolution
- Use Ethernet instead of WiFi if possible
