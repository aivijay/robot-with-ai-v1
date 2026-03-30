# ACAMMZAR 1:24 — 4WD Wiring Diagram

> **Components:** 2× TB6612FNG (each drives 2 motors) | 7.4V LiPo battery | LM2596 step-down → 5V for Pi Zero W | Raspberry Pi Zero W

---

## 1. Power Distribution

```
┌─────────────────────────────────────────────────────────────┐
│                     7.4V LiPo Battery                        │
│                        (+ red, - black)                      │
└──────────────────────┬──────────────┬───────────────────────┘
                       │              │
                       │              │   ┌──────────────────┐
                       │              └──►│ LM2596 Buck      │
                       │                  │ Module           │
                       │                  │ IN+ ──► 7.4V     │
                       │                  │ IN- ──► GND      │
                       │                  │ OUT+ ──► 5V ────┼──► Pi Zero W (5V pin)
                       │                  │ OUT- ──► GND ───┼──► Pi Zero W (GND pin)
                       │                  └──────────────────┘
                       │
           ┌───────────┴───────────┐
           │                       │
           ▼                       ▼
   ┌───────────────┐       ┌───────────────┐
   │  TB6612FNG #1  │       │  TB6612FNG #2  │
   │  (Front Motors)│       │  (Rear Motors) │
   │  VMOTOR = 7.4V │       │  VMOTOR = 7.4V │
   │  VCC  = 3.3V   │       │  VCC  = 3.3V   │
   │  GND  = GND    │       │  GND  = GND    │
   └───────┬───────┘       └───────┬───────┘
           │                       │
           ▼                       ▼
   ┌───────────────┐       ┌───────────────┐
   │ Front Left    │       │ Rear Left     │
   │ Motor (FL)    │       │ Motor (RL)    │
   └───────────────┘       └───────────────┘
   ┌───────────────┐       ┌───────────────┐
   │ Front Right   │       │ Rear Right    │
   │ Motor (FR)    │       │ Motor (RR)    │
   └───────────────┘       └───────────────┘
```

**Notes:**
- TB6612FNG VMOTOR supports up to 13.5V — 7.4V is safe
- TB6612FNG VCC (logic power) = 3.3V from Pi Zero — do NOT power with 5V
- LM2596 module must be adjusted to 5V output BEFORE connecting to Pi

---

## 2. TB6612FNG Pinout (per board — annotated)

```
    ┌────────────────────────────────────────────────────────┐
    │                                                        │
    │   VMOTOR  ●━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━● +7.4V   │
    │   GND     ●━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━● GND       │
    │                                                        │
    │   VCC     ●━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━● 3.3V    │
    │   GND     ●━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━● GND      │
    │                                                        │
    │   STBY    ●━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━● GPIO 5  │
    │           (Board 1)   or   GPIO 6 (Board 2)            │
    │                                                        │
    │   ─── CHANNEL A (Motor A) ────                         │
    │   PWMA    ●━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━● GPIO 18  │
    │   AIN1    ●━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━● GPIO 17  │
    │   AIN2    ●━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━● GPIO 27  │
    │   AOUT1   ●━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━● Motor A +│
    │   AOUT2   ●━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━● Motor A -│
    │                                                        │
    │   ─── CHANNEL B (Motor B) ────                         │
    │   PWMB    ●━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━● GPIO 23  │
    │   BIN1    ●━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━● GPIO 22  │
    │   BIN2    ●━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━● GPIO 24  │
    │   BOUT1   ●━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━● Motor B +│
    │   BOUT2   ●━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━● Motor B -│
    │                                                        │
    └────────────────────────────────────────────────────────┘
```

### STBY (Standby) — One per board
- Drive HIGH (3.3V) to enable the board
- Drive LOW to disable all motors (coast stop)
- Each board needs its own STBY GPIO (GPIO 5 for Board 1, GPIO 6 for Board 2)

---

## 3. Full GPIO to Motor Wiring Map

```
                         ┌──────────────────────────┐
                         │    Raspberry Pi Zero W   │
                         │                          │
                         │  GPIO 17 ────────────────●────── AIN1 (Board 1)
                         │  GPIO 18 ────────────────●────── PWMA (Board 1)
                         │  GPIO 27 ────────────────●────── AIN2 (Board 1)
                         │  GPIO 22 ────────────────●────── BIN1 (Board 1)
                         │  GPIO 23 ────────────────●────── PWMB (Board 1)
                         │  GPIO 24 ────────────────●────── BIN2 (Board 1)
                         │  GPIO 10 ────────────────●────── AIN1 (Board 2)
                         │  GPIO 9  ────────────────●────── PWMA (Board 2)
                         │  GPIO 11 ────────────────●────── AIN2 (Board 2)
                         │  GPIO 8  ────────────────●────── BIN1 (Board 2)
                         │  GPIO 7  ────────────────●────── PWMB (Board 2)
                         │  GPIO 25 ────────────────●────── BIN2 (Board 2)
                         │  GPIO 5  ────────────────●────── STBY  (Board 1)
                         │  GPIO 6  ────────────────●────── STBY  (Board 2)
                         │  3.3V   ────────────────●────── VCC   (both boards)
                         │  GND    ────────────────●────── GND   (both boards)
                         │  5V     ────────────────●────── Pi camera
                         │                          │
                         └──────────────────────────┘


    ┌─────────────────────────────────┐    ┌─────────────────────────────────┐
    │     TB6612FNG #1 (FRONT)        │    │     TB6612FNG #2 (REAR)         │
    │                                 │    │                                 │
    │  AIN1 ◄── GPIO 17               │    │  AIN1 ◄── GPIO 10               │
    │  PWMA ◄── GPIO 18  (PWM)        │    │  PWMA ◄── GPIO 9   (PWM)       │
    │  AIN2 ◄── GPIO 27               │    │  AIN2 ◄── GPIO 11               │
    │  AOUT1 ──► Front Left Motor +   │    │  AOUT1 ──► Rear Left Motor +    │
    │  AOUT2 ──► Front Left Motor -   │    │  AOUT2 ──► Rear Left Motor -    │
    │                                 │    │                                 │
    │  BIN1 ◄── GPIO 22               │    │  BIN1 ◄── GPIO 8                │
    │  PWMB ◄── GPIO 23  (PWM)        │    │  PWMB ◄── GPIO 7   (PWM)       │
    │  BIN2 ◄── GPIO 24               │    │  BIN2 ◄── GPIO 25               │
    │  BOUT1 ──► Front Right Motor +  │    │  BOUT1 ──► Rear Right Motor +   │
    │  BOUT2 ──► Front Right Motor - │    │  BOUT2 ──► Rear Right Motor -   │
    │                                 │    │                                 │
    │  STBY  ◄── GPIO 5   (HIGH=ON)  │    │  STBY  ◄── GPIO 6   (HIGH=ON)   │
    │  VCC   ◄── 3.3V                 │    │  VCC   ◄── 3.3V                 │
    │  GND   ◄── GND                  │    │  GND   ◄── GND                  │
    │  VMOTOR ◄── +7.4V battery       │    │  VMOTOR ◄── +7.4V battery       │
    └─────────────────────────────────┘    └─────────────────────────────────┘
              │                                       │
              ▼                                       ▼
      ┌───────────────┐                      ┌───────────────┐
      │ Front Left    │                      │ Rear Left     │
      │ Motor (FL)    │                      │ Motor (RL)    │
      │ + = AOUT1     │                      │ + = AOUT1     │
      │ - = AOUT2     │                      │ - = AOUT2     │
      └───────────────┘                      └───────────────┘
      ┌───────────────┐                      ┌───────────────┐
      │ Front Right   │                      │ Rear Right    │
      │ Motor (FR)    │                      │ Motor (RR)    │
      │ + = BOUT1     │                      │ + = BOUT1     │
      │ - = BOUT2     │                      │ - = BOUT2     │
      └───────────────┘                      └───────────────┘
```

---

## 4. Motor Direction Truth Table

| AIN1 | AIN2 | PWMA | Result         |
|------|------|------|----------------|
| HIGH | LOW  | PWM  | Forward        |
| LOW  | HIGH | PWM  | Backward       |
| LOW  | LOW  | PWM  | Brake (fast)   |
| HIGH | HIGH | PWM  | Brake (fast)   |
| X    | X    | LOW  | Coast (motor off) |

The same logic applies to BIN1/BIN2/PWMB for Motor B.

**Tip:** Always set direction pins FIRST, then set the PWM duty cycle. Changing direction while PWM is active can cause brief cross-conduct in the H-bridge.

---

## 5. Standby Control

| STBY Pin | State | Motors |
|----------|-------|--------|
| HIGH (3.3V) | Active | Enabled, respond to PWM |
| LOW (GND) | Standby | Disabled, coast |

- Use a separate GPIO for each board's STBY so they can be independently enabled/disabled
- Default: drive HIGH to enable both boards at startup

---

## 6. Bill of Materials for Wiring

| Item | Connection From | Connection To | Wire Type |
|------|----------------|---------------|-----------|
| Battery + | 7.4V Battery + | VMOTOR (both boards) | 16-20 AWG |
| Battery - | 7.4V Battery - | GND (both boards) | 16-20 AWG |
| 3.3V | Pi 3.3V pin | VCC (both boards) | 24+ AWG |
| GND | Pi GND pin | GND (both boards) | 24+ AWG |
| GPIO wires | Pi GPIO | AIN1, AIN2, PWMA, BIN1, BIN2, PWMB, STBY | 24 AWG jumper |
| Motor wires | AOUT1/AOUT2 | Motor leads | 22 AWG |
| 5V supply | LM2596 OUT+ | Pi 5V pin | 22 AWG |
| GND supply | LM2596 OUT- | Pi GND pin | 22 AWG |

**Warning:** Double-check polarity on the LM2596 module before connecting to the Pi. Wrong 5V can fry the Pi Zero W.

---

## 7. Quick-Start Connection Order

1. **Power off everything** before wiring
2. Connect **battery leads** to both TB6612FNG VMOTOR/GND
3. Connect **Pi 3.3V + GND** to both TB6612FNG VCC + GND
4. Connect **all GPIO wires** (see GPIO reference table)
5. Connect **motor leads** to AOUT/BOUT terminals
6. Connect **LM2596** output to Pi 5V + GND (set to 5V first!)
7. Power battery → verify TB6612FNG boards get warm (not hot)
8. SSH into Pi → run test code
