# Robot with AI v1 — Architecture Overview

## Agent Architecture

The robot is controlled by a multi-agent system running on the laptop. Each agent has a specific responsibility:

### Core Agents

| Agent | Responsibility | Latency | Technology |
|-------|---------------|---------|------------|
| **Brain Agent** | LLM decision making, reasoning, planning | Seconds | Ollama (LLM) |
| **CNS Agent** | Message routing between agents, coordination | Milliseconds | OpenClaw |
| **Vision Agent** | Frame capture, preprocessing, scene analysis | Hundreds of ms | Vision model (llava/qwen2.5-vl) |
| **Hearing Agent** | Audio capture, speech recognition (future) | Hundreds of ms | Whisper |
| **Motion Agent** | Motor control, speed, steering commands | Milliseconds | Classical (PID/IK) |
| **Reaction Agent** | Fast reflex responses, emergency stop | Microseconds | Reactive code (NO LLM) |
| **Speaking Agent** | Text-to-speech, verbal responses | Hundreds of ms | Piper TTS |

### Safety-Critical Note: Motion + Reaction must be Classical

LLMs think in seconds, but motors need milliseconds. **Motion Agent** and **Reaction Agent** must use classical control systems — never route through an LLM for safety-critical paths.

```
Reaction Agent ← Direct signal ← Safety sensors (NO LLM IN PATH)
Motion Agent ← PID controller ← Movement commands (NO LLM IN PATH for emergency)
```

### Agent Communication Flow

```
[Camera] ──frame──► [Vision Agent] ──analysis──► [Brain Agent]
                                                         │
                                                         ▼
[Sensors] ──data──► [CNS Agent] ◄───coordination───► [Brain Agent]
                │                                            │
                ▼                                            ▼
         [Motion Agent] ◄────────commands───────── [Brain Agent]
                │
                ▼
         [Motors via UART/GPIO]
```

### Future Agents (TBD)

- **Safety Agent** — battery monitoring, temperature limits, current protection
- **Memory Agent** — learned patterns, maps, object recognition cache
- **Navigation Agent** — SLAM, path planning, obstacle avoidance

---

## The Key Insight

**All AI runs on the laptop. The robot is just a "thin client"** — it captures camera frames, streams them over WiFi, and executes motor commands it receives back. No AI models run on the robot itself.

This dramatically cuts hardware requirements and cost — the robot just needs WiFi + GPIO + camera interface, nothing more.

## MCP Communication Layer

The laptop-to-robot communication uses **MCP (Model Context Protocol)** — OpenClaw agents call robot tools via MCP:

```
┌──────────────────────────────────────────────────────────────┐
│                         LAPTOP                                 │
│                                                              │
│   ┌──────────────┐    ┌──────────────────┐   ┌───────────┐  │
│   │  Ollama      │    │  Robot MCP Server │   │  Vision   │  │
│   │              │◄───│  (robot_mcp_     │◄──│  Model    │  │
│   │              │    │   server.py)      │   │           │  │
│   └──────────────┘    └────────┬───────────┘   └───────────┘  │
│                               │                               │
│                    MCP (stdio) │ HTTP                         │
│                               │                               │
└───────────────────────────────┼───────────────────────────────┘
                                │
                     ┌──────────▼──────────┐
                     │      ROBOT (Pi)     │
                     │                      │
                     │  robot_client.py     │
                     │  (thin client)      │
                     │  Camera + Motors     │
                     └──────────────────────┘
```

### MCP Tools Exposed

| Tool | Agent | Description |
|------|-------|-------------|
| `robot_move` | Motion Agent | Direction + speed control |
| `robot_camera` | Vision Agent | Capture current frame |
| `robot_status` | CNS Agent | Connection health |
| `robot_stop` | Reaction Agent | Emergency motor halt |

```
┌──────────────────────────────────────────────────────────────┐
│                         LAPTOP                                 │
│                                                              │
│   ┌──────────────┐    ┌──────────────┐   ┌───────────────┐  │
│   │  Ollama      │    │  FastAPI     │   │  Vision Model │  │
│   │  (running)   │◄───│  Server      │◄──│  (llava,      │  │
│   │              │    │  localhost   │   │   qwen2.5-vl) │  │
│   └──────────────┘    └──────┬───────┘   └───────────────┘  │
│                              ▲                                 │
│                    HTTP/REST over WiFi                        │
│                              │                                 │
└──────────────────────────────┼────────────────────────────────┘
                               │
                    ┌──────────▼──────────┐
                    │      ROBOT          │
                    │                      │
                    │  ┌────────────────┐  │
                    │  │ Camera (CSI)   │──┼── captures frames
                    │  │ ESP32-CAM or   │  │
                    │  │ Pi Camera      │  │
                    │  └────────────────┘  │
                    │  ┌────────────────┐   │
                    │  │ Motor Driver   │◄──┼── receives commands
                    │  │ (DRV8833/L298N)│   │
                    │  └────────────────┘   │
                    │  ┌────────────────┐   │
                    │  │ WiFi (client)  │───┼── streams to laptop
                    │  └────────────────┘   │
                    │  ┌────────────────┐   │
                    │  │ Microcontroller│   │
                    │  │ ESP32 or Pi   │   │
                    │  │ Zero 2 W      │   │
                    │  └────────────────┘   │
                    └───────────────────────┘
```

## Communication Protocol

### Robot → Laptop (image stream)
```
POST /api/frame
Body: multipart/form-data with image file (JPEG, max 640x480)
Response: {"received": true}
```

### Laptop → Robot (motor commands)
```
POST /api/command
Body: {"direction": "forward" | "left" | "right" | "stop", "speed": 0.0-1.0}
Response: {"executed": true, "direction": "forward"}
```

### Optional: WebSocket for real-time video
```
WS /ws/video
Robot streams JPEG frames continuously at ~5-10 FPS
```

## Hardware Options (Cheapest to Most Capable)

| Rank | Robot Brain | Cost | Camera | WiFi | GPIO | Notes |
|------|-------------|------|--------|------|------|-------|
| 1 | **ESP32-CAM** | $8–10 | Built-in | ✅ | Limited | Ultra-cheap, streams over WiFi directly |
| 2 | **Pi Zero 2 W** | $20–25 | CSI (v3) | ✅ | ✅ | Full Pi OS, GPIO, camera port |
| 3 | **Pi Zero W** | $15 | CSI | ✅ | ✅ | Slower but still works |
| 4 | **Pi 3A+** | $25–30 | CSI | ✅ | ✅ | More headroom, faster |
| 5 | **Pi 4** | $0 (own) | CSI | ✅ | ✅ | Already owned — most powerful option |

**Recommendation for Vijay (absolute cheapest):** Start with **ESP32-CAM** as robot brain (~$8–10) + any external motor driver. If ESP32-CAM GPIO is too limiting, fall back to **Pi Zero 2 W** (~$25 total).

## Software Stack

### Laptop Side
- **Ollama** — serves vision model
- **FastAPI server** — receives images, calls Ollama, returns decisions
- **Optional:** Streamlit dashboard for manual override

### Robot Side
- **MicroPython (ESP32)** or **Python (Pi)** — handles camera + WiFi + motors
- Minimal dependencies — no ML libraries needed

## Why This Architecture Wins

1. **No model on robot** — AI model lives on laptop (unlimited compute)
2. **No thermal issues** — laptop has fans, robot doesn't overheat
3. **Easy iteration** — swap vision models without touching robot
4. **Remote debugging** — all logs on laptop, easy to fix
5. **Battery life** — robot uses pennies of power, no heavy compute

## Model Recommendations for Laptop

| Model | Size | Speed | Quality | Install Command |
|-------|------|-------|---------|-----------------|
| `llava:latest` | 4.7GB | Slow on CPU | Good | `ollama pull llava` |
| `qwen2.5vl:3b` | 2.3GB | Usable | Good | `ollama pull qwen2.5vl:3b` |
| `phi3.5-vision:3.8b` | 2.5GB | Usable | Good | `ollama pull phi3.5-vision` |
| `moondream:1.8b` | ~1GB | Fast | OK | `ollama pull moondream` |

**On laptop (x86_64):** All models run at reasonable speed.
**Recommended first try:** `ollama pull moondream` — smallest, fastest, good enough for navigation.
