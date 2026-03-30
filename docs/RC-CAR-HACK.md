# RC Car Hacking - Project Notes

## Overview
Hacking a cheap 1:64 RC car for autonomous AI control using:
- Raspberry Pi Zero W + Camera
- Ollama (LLM/VLM on laptop)
- TB6612FNG motor driver
- Differential steering

---

## Car Details

### Scale
- **1:64 scale** - very small RC car (not ideal for carpet, but hackable!)

### Motor Specs
- **Motor Model:** JGB-370-12400-B4WD
- **Voltage:** DC 3-6V
- **RPM:** ~15000 (at 3V estimate)
- **Type:** DC brush motor with gearbox
- **Quantity:** 2 motors (front + rear)

### Battery
- **Model:** 802025
- **Voltage:** 3.7V nominal (4.2V fully charged, 3.0V discharged)
- **Capacity:** 250mAh
- **Connector:** 2-pin

### Steering
- **Type:** Differential steering
- **Front Motor:** drives front axle
- **Rear Motor:** drives rear axle
- **Turning:** spin motors in opposite directions to turn

---

## Motor Driver Board

### Original Chip
- **Chip:** GZ405 (dual H-bridge motor driver)
- **Location:** Small PCB with labeled motor wires

### Wire Labels (from photos)
- FRONT MOTOR +/-
- REAR MOTOR +/-
- Each motor has 2 wires (4 wires total)

### Motor Connector Pins
```
┌─────────────────────────────────┐
│  FRONT MOTOR +   [RED]         │
│  FRONT MOTOR -   [BLUE]        │
│  REAR MOTOR +    [BLUE]        │
│  REAR MOTOR -    [RED]         │
└─────────────────────────────────┘
```

---

## Hacking Plan

### Goal
Replace the car's RC receiver + motor driver with our own DRV8833 and Pi Zero.

### Wiring Diagram
```
┌──────────────────────────────────────────────────────┐
│                                                      │
│   3.7V Battery (802025 250mAh)                      │
│       │ (+)                                           │
│       │                                               │
│       └────────┬──────────────┐                      │
│                │              │                      │
│                ▼              │                      │
│         ┌─────────────┐      │                      │
│         │   DRV8833    │      │                      │
│         │ Motor Driver │      │                      │
│         │             │      │                      │
│         │ Channel A ──┼──────┼──► Front Motor       │
│         │ Channel B ──┼──────┼──► Rear Motor        │
│         │             │      │                      │
│         └──────┬──────┘      │                      │
│                │              │                      │
│                ▼              │                      │
│         ┌─────────────┐       │                      │
│         │   Pi Zero   │◄──────┘                      │
│         │   W + Cam   │       │                      │
│         │             │       │                      │
│         │ GPIO pins ──┘       │                      │
│         └─────────────┘       │                      │
│                                                      │
└──────────────────────────────────────────────────────┘
```

### GPIO to TB6612FNG Mapping
| GPIO Pin | Function       | TB6612FNG Pin |
|----------|---------------|---------------|
| GPIO 17  | Motor A Direction | AIN1       |
| GPIO 18  | Motor A Speed    | PWMA        |
| GPIO 22  | Motor B Direction | BIN1       |
| GPIO 23  | Motor B Speed    | PWMB         |
| GPIO 25  | Motor Enable     | STBY        |
| GND      | Ground          | GND          |

### TB6612FNG Pinout
```
┌─────────────────────────────┐
│  VMOTOR (+) ─── Battery +   │
│  VMOTOR (-) ─── Battery -   │
│                             │
│  AOUT1 ─── Front Motor +    │
│  AOUT2 ─── Front Motor -    │
│  BOUT1 ─── Rear Motor +     │
│  BOUT2 ─── Rear Motor -     │
│                             │
│  VCC ─────── Pi 3.3V        │
│  GND ─────── Pi GND        │
│  PWMA ────── GPIO 18       │
│  AIN1 ────── GPIO 17       │
│  AIN2 ────── GND (or GPIO) │
│  BIN1 ────── GPIO 22       │
│  BIN2 ────── GND (or GPIO) │
│  PWMB ────── GPIO 23       │
│  STBY ────── GPIO 25 (HIGH)│
└─────────────────────────────┘
```

**Note:** STBY must be pulled HIGH (3.3V) for motors to operate. Set GPIO 25 HIGH before using motors.

### Differential Steering Logic
| Left Motor | Right Motor | Action      |
|------------|-------------|-------------|
| Forward    | Forward     | Go forward  |
| Backward   | Backward    | Go backward |
| Forward    | Backward    | Spin right  |
| Backward   | Forward     | Spin left   |
| Stop       | Forward     | Turn right  |
| Forward    | Stop        | Turn left   |

---

## Parts Needed (CONFIRMED 2026-03-29)

### 1. TB6612FNG Motor Driver Module
- **Purpose:** Controls 2 motors with PWM speed control (better than DRV8833)
- **Spec:** Dual H-bridge, 1A per channel, built-in flyback diodes, 100kHz PWM support
- **Quantity:** 2-pack (order one, get one spare)
- **Search:** `DAOKAI TB6612FNG High Performance DRV8833 Microcontroller`
- **Status:** ❌ Need to order

### 2. Jumper Wires
- **Purpose:** Connect Pi Zero GPIO to TB6612FNG, and driver to motors
- **Type:** Female-to-Female (F/F) jumper wires
- **Quantity:** 40-piece bundle
- **Search:** "jumper wires female to female 40pcs"
- **Status:** ❌ Need to order

### 3. 2×20 Male Header
- **Purpose:** Solder onto Pi Zero GPIO pins for jumper wire connections
- **Search:** "2x20 male header raspberry pi"
- **Status:** ❌ Need to order

### 4. Arducam Pi Zero Camera Cable Set
- **Purpose:** Connect Pi Camera v2 (8MP) to Pi Zero W CSI port
- **Spec:** 22-pin to 15-pin CSI cable, multiple lengths (38mm, 73mm, 150mm)
- **Search:** "Arducam pi zero camera ribbon cable set"
- **Status:** ❌ Need to order

### 5. USB Power Bank (5V 2.4A, 5000mAh)
- **Purpose:** Power Pi Zero W + Camera
- **Status:** ✅ Already have

### 6. Raspberry Pi Zero W
- **Status:** ✅ Already have

### 7. Pi Camera v2 (8MP)
- **Status:** ✅ Already have

---

## Issues & Solutions

### Issue: Car Too Small for Carpet
**Problem:** 1:64 scale is designed for smooth indoor surfaces, not carpet
**Solution:** Test on smooth floors first (hardwood, tile). Upgrade to larger car (1:18) later.

### Issue: Unknown Motor Current
**Problem:** Don't know exact stall current for JGB-370 motors
**Solution:** DRV8833 can handle 1.5A per channel, motors likely under 1A. Start with low PWM values.

### Issue: Small Battery (250mAh)
**Problem:** Battery might drain quickly under motor load
**Solution:** Monitor during testing. Upgrade to larger Li-ion (18650-based) if needed.

---

## V2 Power Supply Upgrade (Future)

Currently (V1), the Pi Zero is powered by an external USB power bank. This works, but it's not clean — a cable dangling off the car. Here are options for a fully integrated internal power supply.

### Option 1: Pimoroni LiPo Shim (Simplest Integration)

Sits directly on the Pi Zero GPIO pins. Has a LiPo battery connector and built-in 5V regulation + charging.

**Specs:**
- Output: 5V/1A via GPIO (load-sharing)
- Battery: JST connector for LiPo (500mAh–2000mAh)
- Charging: Micro USB (5V/1A charge rate)
- Size: Very slim (doesn't add much height)
- Price: ~$12–15

**Why it's good:**
- Clean GPIO connection (no USB cable)
- Runs while charging (UPS mode)
- Compact form factor
- Well-documented by Pimoroni

**Search:** `Pimoroni LiPo Shim for Pi Zero`

---

### Option 2: Adafruit PowerBoost 1000C + LiPo Battery (Most Flexible)

A dedicated 5V boost converter with integrated LiPo charger. Pair with any LiPo battery.

**Specs:**
- Output: 5.2V/1A (boosted from 3.7V LiPo)
- Input: 3.7V–5V via micro USB or battery
- Battery: Any LiPo (1000mAh–5000mAh)
- Features: Load-sharing, low-battery LED, 1A charger
- Price: ~$10–15 (board) + battery ~$5–15

**Why it's good:**
- Works with any LiPo battery size
- Higher capacity options available (5000mAh+)
- Can charge while running (UPS mode)
- Well-documented by Adafruit

**Search:** `Adafruit PowerBoost 1000C`

---

### Option 3: Dedicated Pi Zero UPS HAT (All-in-One)

A HAT designed specifically as a UPS (Uninterruptible Power Supply) for Pi Zero.

**Specs:**
- Built-in 18650 Li-ion battery holder
- Output: 5V/2A via GPIO
- Charging: USB-C or Micro USB
- Features: On/off button, battery indicator LEDs
- Price: ~$15–25

**Why it's good:**
- All-in-one solution
- Swappable 18650 cells (high capacity)
- Professional look
- No separate components to wire

**Search:** `Pi Zero UPS HAT 18650`

---

### Recommended V2 Build

**For easiest integration:**
1. **Pimoroni LiPo Shim** (~$12–15)
2. **LiPo battery** — any 500mAh–1500mAh with JST connector (~$5–10)
3. Keep the **car's battery for motors only** (via TB6612FNG)

**Wiring for V2:**
```
Car Battery (3.7V) ──→ TB6612FNG ──→ Motors
                                          
LiPo Shim (on GPIO) ──→ Pi Zero W + Camera
```

This gives you:
- Separate power domains (motors vs. computing)
- Pi runs for 5–10 hours on LiPo
- Motors use car battery (250mAh is small but ok for short runs)
- No external cables except optional USB charging

---

### When to Upgrade

V1 (current build) is fine for testing and development. Upgrade to V2 power when:
- You want the robot to be fully self-contained
- Cable management becomes annoying
- You need longer runtime than the USB power bank provides
- You're ready to make the build more permanent

---

## Single Power Bank for Everything

Instead of separate batteries for Pi and motors, you could use one large power bank to power both. This simplifies charging (one thing to charge) and can provide very long runtime.

### Power Budget Analysis

| Component | Voltage | Typical Current | Peak Current |
|-----------|---------|----------------|--------------|
| Pi Zero W + Camera | 5V | 1-1.5A | 2A |
| Motors (JGB-370) | 3.7V | 200-500mA | 1-2A (stall) |
| **Total** | 5V | **1.2-2A** | **3-4A** |

**Problem:** Most USB power banks are rated 5V/2.4A max. That's cutting it close when Pi + motors both run.

---

### Option A: High-Capacity Power Bank + Step-Down Converter

Use a large USB power bank (10,000-20,000mAh) with **two outputs**, or a single output with a USB splitter.

**Wiring:**
```
Power Bank (5V USB) ──→ USB Splitter (optional)
                              │
              ┌───────────────┴───────────────┐
              │                               │
              ▼                               ▼
       Pi Zero W (USB micro)         Step-Down Converter (5V → 3.7V)
                                              │
                                              ▼
                                       TB6612FNG (VMOTOR)
                                              │
                                              ▼
                                        Motors
```

**Required parts:**
- USB power bank (10,000mAh+, 2+ USB outputs)
- USB to 5.5x2.1mm DC cable (~$2)
- **LM2596 DC-DC buck converter** ($3-5) — adjust to 3.7V output

**Pros:**
- One battery to charge
- Very long runtime (10-20 hours Pi, 5-10 hours motors)
- Can use off-the-shelf power bank

**Cons:**
- Power bank current limit (2.4A) shared between Pi and motors
- Heavy for a small car (power banks are ~200-300g for 10,000mAh)
- Needs step-down converter wiring

---

### Option B: Power Bank for Pi + Separate Motor Battery

Keep things separated but upgrade motor battery to something bigger than the tiny 250mAh stock battery.

**Power architecture:**
| Component | Power Source |
|-----------|-------------|
| Pi Zero + Camera | USB power bank (5V, any capacity) |
| Motors | Upgrade to 18650 LiPo pack (3.7V, 2000-5000mAh) |

**This is actually the best practical approach for V1/V2:**

- Power bank for Pi: Easy, proven, 10,000mAh = 8-10 hours
- Motors: Use a **18650 LiPo battery** ($5-10) instead of the tiny 250mAh stock battery
  - 18650 cells are 2000-3500mAh each
  - 1 cell = 3.7V, 2 cells in series = 7.4V → step down to 5V for Pi OR use TB6612FNG directly at 3.7V

---

### Option C: 1:24 Scale Car (Recommended for Future)

The 1:64 car is too small for a power bank inside. **1:24 scale** changes everything:

- Fits a 10,000mAh power bank easily
- Room for Pi Zero + TB6612FNG + full wiring
- Bigger motors = more torque = works on carpet
- More stable platform for AI vision

**1:24 upgrade benefits:**
- Space for full-size power bank (10,000-20,000mAh)
- Larger motors = more torque = works on carpet
- More stable for camera vision
- Still affordable ($20-40 for the car itself)

**Suggested 1:24 build:**
1. 1:24 RC car (traxxas-like or similar)
2. Raspberry Pi Zero W + Camera v2
3. TB6612FNG motor driver
4. 10,000mAh USB power bank (for Pi)
5. 2x 18650 battery pack (for motors) OR run motors off power bank + step-down

---

### Recommendation Summary

| Build | Power Setup | Effort | Runtime |
|-------|------------|--------|---------|
| V1 (current 1:64) | USB bank (Pi) + stock battery (motors) | Low | Medium |
| V2 (1:64 with hat) | LiPo Shim (Pi) + stock battery (motors) | Medium | Medium |
| V2+ (1:64 full) | Power bank (Pi) + 18650 pack (motors) | Medium | Long |
| V3 (1:24) | Large power bank (everything) | High | Very Long |

**For now:** Stick with V1 (separate banks). It's simpler to debug.
**For longer runs:** Upgrade motor battery to 18650.
**For clean build:** Consider 1:24 scale with single power bank.

---

## Scale Comparison

| Scale | Car Size (approx) | Fits Inside | Recommended Power |
|-------|------------------|-------------|------------------|
| 1:64 | 7cm × 3cm × 2cm | Nothing | External only |
| 1:32 | 14cm × 6cm × 4cm | Small LiPo only | LiPo for Pi |
| 1:24 | 18cm × 8cm × 6cm | Power bank + HAT | Full internal |

---

## References

### Photos (in ./docs/images/)
- 20260329_011620.jpg - Front motor assembly
- 20260329_011637.jpg - Rear motor assembly  
- 20260329_012309.jpg - Motor back (JGB-370 label visible)
- 20260329_012324.jpg - Motor back angle 2
- 20260329_014358.jpg - Motor driver PCB
- 20260329_014415.jpg - Motor driver PCB angle 2
- 20260329_021741.jpg - Battery (802025 3.7V 250mAh)

### Motor Specs (from label)
- Model: JGB-370-12400-B4WD
- DC 3-6V
- Other markings: "KFF-030SH" (可能是另一个电机标记)

---

## Next Steps

1. [ ] Order TB6612FNG (2-pack)
2. [ ] Order Jumper wires (F/F, 40pcs)
3. [ ] Order 2×20 Male header
4. [ ] Order Arducam Pi Zero camera cable set
5. [ ] Solder male header to Pi Zero GPIO
6. [ ] Wire motors to TB6612FNG
7. [ ] Wire Pi Zero GPIO to TB6612FNG
8. [ ] Test motor control with Python (PWM speed control)
9. [ ] Integrate with AI vision code (robot_client.py)
10. [ ] Test on smooth floor

---

## Date: 2026-03-29
Document created: Initial RC car hack analysis
