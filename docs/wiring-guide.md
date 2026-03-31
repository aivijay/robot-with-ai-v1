# Robot Car Wiring — Clear Guide

## Your 3 Questions, Answered

### 1. Motor Wires → Motor Controller

The motor has **2 wires**: `+` and `-`

These connect to the **TB6612FNG** at:
- **Motor A (front wheel)**: `AOUT1` and `AOUT2` pins
- **Motor B (rear wheel)**: `BOUT1` and `BOUT2` pins

**It doesn't matter which wire goes to which pin** — swap them to reverse direction.

---

### 2. Power Flow for Motors

```
Car Battery (3.7V LiPo)
        │
        ├──(+)──→ VMOTOR pin on TB6612FNG
        │
        ├──(-)──→ GND pin on TB6612FNG
```

**NOT from Pi.** The Pi only sends control signals (GPIO). Motor power comes directly from the car battery.

---

### 3. Pi Zero GPIO Pinout

Here are the actual pins on Pi Zero W you'll use:

```
        ┌──────────────┐
        │   Pi Zero    │
        │              │
  ┌─────┤  3.3V  ●  5V ├─────┐
  │     │         ●       │     │
  │     │  GPIO  ●  GND   │     │
  │     │  17 ●───●  18   │     │  ← PWMA
  │     │  27 ●───●  22   │     │  ← BIN1
  │     │  23 ●───●  24   │     │  ← BIN2
  │     │  GPIO ●  GND    │     │
  │     │   5 ●───●  21   │     │  ← STBY
  └─────┤  GND  ●  GPIO   ├─────┘
        │              │
        └──────────────┘
```

**Your actual connections:**

| Pi Pin | Wire Color (suggestion) | Connects to TB6612FNG |
|--------|------------------------|----------------------|
| GPIO 5 | (any) | STBY |
| GPIO 17 | (any) | AIN1 |
| GPIO 18 | (any) | PWMA (PWM speed) |
| GPIO 27 | (any) | AIN2 |
| GPIO 22 | (any) | BIN1 |
| GPIO 24 | (any) | BIN2 |
| GPIO 23 | (any) | PWMB (PWM speed) |
| 3.3V | Red | VCC |
| GND | Black | GND |

---

## TB6612FNG Board Layout

```
    ┌─────────────────────────────┐
    │  TB6612FNG                  │
    │                             │
    │  VCC ◄─── 3.3V (from Pi)   │
    │  GND ◄─── GND (from Pi)    │
    │  STBY ◄── GPIO 5          │
    │                             │
    │  AIN1 ◄── GPIO 17          │
    │  AIN2 ◄── GPIO 27          │
    │  PWMA ◄── GPIO 18          │
    │                             │
    │  BIN1 ◄── GPIO 22          │
    │  BIN2 ◄── GPIO 24          │
    │  PWMB ◄── GPIO 23          │
    │                             │
    │  VMOTOR ◄── 3.7V (car battery +) │
    │  GND ◄──── 3.7V (car battery -)  │
    │                             │
    │  AOUT1 ───┬── Motor A (+)  │
    │  AOUT2 ───┤                │
    │           └── Motor A (-)  │
    │                             │
    │  BOUT1 ───┬── Motor B (+)  │
    │  BOUT2 ───┤                │
    │           └── Motor B (-)  │
    └─────────────────────────────┘
```

---

## Simple Wiring Order

**Step 1:** Power off everything first!

**Step 2:** Connect Pi to TB6612FNG (logic):
   - Pi 3.3V → TB6612FNG VCC
   - Pi GND → TB6612FNG GND
   - Pi GPIO 5 → TB6612FNG STBY
   - Pi GPIO 17 → TB6612FNG AIN1
   - Pi GPIO 27 → TB6612FNG AIN2
   - Pi GPIO 18 → TB6612FNG PWMA
   - Pi GPIO 22 → TB6612FNG BIN1
   - Pi GPIO 24 → TB6612FNG BIN2
   - Pi GPIO 23 → TB6612FNG PWMB

**Step 3:** Connect motors to TB6612FNG:
   - Front motor wires → AOUT1 and AOUT2 (either way)
   - Rear motor wires → BOUT1 and BOUT2 (either way)

**Step 4:** Connect motor power:
   - Car battery + → TB6612FNG VMOTOR
   - Car battery - → TB6612FNG GND

**Step 5:** Power on Pi (power bank) and test!

---

## What's NOT Connected

- No motor power from Pi (Pi only runs on power bank)
- No buck converter needed
- You don't use the Pi's 5V pin for motors

The Pi and motors have SEPARATE power supplies. They only share ground (GND) and GPIO signals.
