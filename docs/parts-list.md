# Parts List & Pricing — Thin Client Robot

**Goal:** Absolute minimum cost for a robot that can see and move based on AI decisions running on laptop.

---

## Option A: Ultra-Cheap — ESP32-CAM ($30–40)

Best for: If you want the cheapest possible thing that actually works.

| Part | Specific Product | Price | Link/Notes |
|------|-----------------|-------|------------|
| Microcontroller + Camera | ESP32-CAM (AI-Thinker) | $8–10 | Amazon, AliExpress |
| Motor Driver | DRV8833 Dual Motor Driver | $4 | Amazon, 2 channels, 1.5A |
| Motors + Wheels | TT Gear Motors (2x) + wheel set | $6–8 | AliExpress, "TT motor 3-6V" |
| Chassis | Acrylic sheet + motor mounts (DIY) | $5–8 | Or buy a cheap 2WD kit |
| Power | 3.7V LiPo 1S (or 2x 18650) | $5 | Any 3.7V battery |
| **TOTAL** | | **$28–35** | |

### ESP32-CAM Limitations
- Only 2 GPIO pins exposed after camera usage (limited PWM channels)
- Requires external motor driver (DRV8833 works)
- Programming requires FTDI USB-serial adapter (~$5, one-time)
- WiFi streaming works out of the box with Arduino IDE / ESP-IDF
- No CSI camera port — built-in OV2640 is the only option

### ESP32-CAM Schematic
```
ESP32-CAM          DRV8833
─────────          ───────
3.3V ────────────── VCC (logic)
GND ─────────────── GND
GPIO 4 ──────────── AIN1 (Motor A)
GPIO 2 ──────────── AIN2 (Motor A)
GPIO 12 ─────────── BIN1 (Motor B)
GPIO 13 ─────────── BIN2 (Motor B)
                    VMOT ──── Battery 3.7V
```

### ESP32-CAM Code Path
- Arduino sketch: WiFi server + camera capture + motor PWM
- Receives HTTP commands from laptop: `/forward`, `/left`, `/right`, `/stop`
- Laptop polls or uses WebSocket for frame streaming

---

## Option B: Pi Zero 2 W — Most Practical Cheap Option ($55–65)

Best for: Full Pi OS, GPIO, camera port, WiFi, easier to program.

| Part | Specific Product | Price | Link/Notes |
|------|-----------------|-------|------------|
| SBC | Raspberry Pi Zero 2 W (512MB) | $20–25 | pi.io/z2w |
| Camera | Raspberry Pi Camera v3 (8MP) | $25–30 | Or Camera v2 ~$25 |
| Camera Cable | Zero 2 W compatible (short) | $3–5 | Amazon, "Pi Zero camera cable" |
| Motor Driver | DRV8833 Dual Motor Driver | $4 | Amazon |
| Motors + Wheels | TT Gear Motors (2x) + wheel set | $6–8 | AliExpress |
| Power | 3.7V LiPo 1S or USB power bank | $5 | |
| microSD Card | 16GB (already have) | $0 | |
| **TOTAL** | | **~$63–77** | |

### Pi Zero 2 W Advantages
- Full Raspberry Pi OS support
- Native CSI camera port
- Python + gpiozero for easy motor control
- SSH headless setup
- Can run Flask/MicroPython for the thin client
- **The Pi Zero 2 W can handle the WiFi + camera + motor loop easily** — no heavy compute needed

### Pi Zero 2 W Pinout (used)
```
GPIO 22 ─── AIN1 (Motor A forward)
GPIO 23 ─── AIN2 (Motor A reverse)
GPIO 24 ─── BIN1 (Motor B forward)
GPIO 25 ─── BIN2 (Motor B reverse)
GND ─────── DRV8833 GND
5V ──────── DRV8833 VCC (logic)
VMOT ────── External battery (3.7-6V)
```

### Zero 2 W Shell Cost (if starting fresh)
- Pi Zero 2 W board only: **$25**
- Camera v3 + short cable: **~$30**
- Motor driver + motors + chassis: **~$20**
- Power: **$5**
- **Total new: ~$80** — still cheaper than a Pi 4 ($55+) + same everything else

---

## Option C: Pi 4 (Already Owned) — Zero Incremental Cost ($0)

Best for: Using what you already have. Full power, most capable.

Vijay already owns a Raspberry Pi 4. This is the best option if cost is not a factor and he wants the most straightforward build.

| Part | Already Owned | Price |
|------|--------------|-------|
| Raspberry Pi 4 (4GB) | ✅ | $0 |
| microSD Card | ✅ | $0 |
| **New only:** | | |
| Motor Driver | DRV8833 / L298N | $4–5 |
| Motors + Wheels | TT motors + wheels | $6–8 |
| Chassis | 2WD kit | $15 |
| Camera | Pi Camera v3 | $30–35 |
| Power | USB power bank | $10–15 |
| **Total new:** | | **~$65–75** |

### Why Pi 4 is Great
- Already owned = free
- Fast enough for local Ollama if desired
- More GPIO pins, more USB, more everything
- Well-documented, large community

---

## Comparison Table

| | ESP32-CAM | Pi Zero 2 W | Pi 4 (own) |
|-|-----------|-------------|-----------|
| **Incremental Cost** | $28–35 | $63–77 | $65–75 |
| **Camera** | Built-in OV2640 | Add $25+ | Add $30+ |
| **GPIO for motors** | Limited (2 pins) | Full GPIO | Full GPIO |
| **WiFi** | ✅ 802.11n | ✅ 802.11n | ✅ 802.11ac |
| **Programming** | Arduino/C++ | Python | Python |
| **Difficulty** | Medium | Easy | Easy |
| **Power draw** | ~0.25W | ~0.5–1W | ~2–5W |
| **Streaming FPS** | ~5-10 FPS | ~10-20 FPS | ~10-20 FPS |
| **Reliability** | Good | Very good | Excellent |

---

## Specific Products with Prices

### Amazon (Prime, fast shipping)

**ESP32-CAM:**
- "ESP32-CAM Module" by DIYmall or equivalent — **$8.99–12.99**

**Motor Driver:**
- "DRV8833 Dual Motor Driver Module" — **$4.49–6.99**

**TT Motors:**
- "DC 3-6V TT Gear Motor with Wheel" 2-pack — **$6.99–9.99**

**Chassis options:**
- Option 1: Buy a cheap 2WD robot car kit — **$12.99–18.99** (SunFounder, Adeept)
- Option 2: DIY acrylic + motor mounts — ~$5 in materials

**Pi Camera v3:**
- "Raspberry Pi Camera Module 3" — **$34.99** (official, Amazon)

**Pi Zero 2 W:**
- "Raspberry Pi Zero 2 W" — **$24.99–29.99** (Canakit, Amazon)

### AliExpress (2-4 week delivery, cheaper)

**ESP32-CAM:**
- "ESP32-CAM AI-Thinker" 2-pack — **$12–16** (~$6–8 each)

**Pi Zero 2 W:**
- "Raspberry Pi Zero 2 W" — **$18–22**

**Pi Camera v3:**
- "Raspberry Pi Camera Module 3" — **$23–28**

**TT Motors + Wheels:**
- "TT DC 3-6V Gear Motor" 4-pack + wheels — **$8–12**

**DRV8833:**
- "DRV8833 Dual Motor Driver" — **$3–5**

---

## Vijay's Decision Matrix

| Priority | Choose |
|----------|--------|
| Absolute cheapest, willing to solder/DIY | **ESP32-CAM** ($30) |
| Cheapest that "just works" with Pi ecosystem | **Pi Zero 2 W** ($63) |
| Use what I have, easiest path | **Pi 4** ($65 new parts) |

**Recommendation:** Start with **Option C (Pi 4)** since it's already owned. Add a $15 chassis + $4 motor driver + $6 motors = **~$25 in new parts**. If that works and you want a dedicated robot, buy a second SD card and use the Pi 4 exclusively for the robot, or buy a Pi Zero 2 W for the robot and keep Pi 4 for something else.
