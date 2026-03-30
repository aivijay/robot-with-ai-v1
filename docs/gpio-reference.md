# GPIO Reference — ACAMMZAR 1:24 4WD

> Pi Zero W pin assignments for 2× TB6612FNG motor drivers, 4 motors total.
> Use **BCM numbering** (GPIO numbers, not physical pin numbers).

---

## Quick Reference Table

| BCM GPIO | Function                | Board | TB6612FNG Pin | Motor           |
|----------|-------------------------|-------|---------------|-----------------|
| GPIO 17  | Motor A Direction 1     | 1     | AIN1          | Front Left      |
| GPIO 18  | Motor A Speed (PWM)     | 1     | PWMA          | Front Left      |
| GPIO 27  | Motor A Direction 2    | 1     | AIN2          | Front Left      |
| GPIO 22  | Motor B Direction 1     | 1     | BIN1          | Front Right     |
| GPIO 23  | Motor B Speed (PWM)    | 1     | PWMB          | Front Right     |
| GPIO 24  | Motor B Direction 2    | 1     | BIN2          | Front Right     |
| GPIO 10  | Motor C Direction 1     | 2     | AIN1          | Rear Left       |
| GPIO 9   | Motor C Speed (PWM)     | 2     | PWMA          | Rear Left       |
| GPIO 11  | Motor C Direction 2    | 2     | AIN2          | Rear Left       |
| GPIO 8   | Motor D Direction 1     | 2     | BIN1          | Rear Right      |
| GPIO 7   | Motor D Speed (PWM)     | 2     | PWMB          | Rear Right      |
| GPIO 25  | Motor D Direction 2     | 2     | BIN2          | Rear Right      |
| GPIO 5   | Standby Enable          | 1     | STBY          | — (Board 1)     |
| GPIO 6   | Standby Enable          | 2     | STBY          | — (Board 2)     |
| 3.3V     | Logic Power             | both  | VCC           | —               |
| GND      | Ground                  | both  | GND           | —               |
| 5V       | Pi Power Input          | —     | LM2596 OUT    | Pi Zero W       |
| —        | Battery Power           | both  | VMOTOR        | 7.4V direct     |

---

## Board 1 — Front Motors (TB6612FNG #1)

```
Pi Zero W                          TB6612FNG #1
─────────────────                  ──────────────────────────
GPIO 17  ────────────────────────── AIN1   (Motor A Dir 1)
GPIO 18  ────────────────────────── PWMA   (Motor A Speed/PWM)
GPIO 27  ────────────────────────── AIN2   (Motor A Dir 2)
                                       │
                                       ├── AOUT1 ──► Front Left Motor (+)
                                       └── AOUT2 ──► Front Left Motor (-)

GPIO 22  ────────────────────────── BIN1   (Motor B Dir 1)
GPIO 23  ────────────────────────── PWMB   (Motor B Speed/PWM)
GPIO 24  ────────────────────────── BIN2   (Motor B Dir 2)
                                       │
                                       ├── BOUT1 ──► Front Right Motor (+)
                                       └── BOUT2 ──► Front Right Motor (-)

GPIO 5   ────────────────────────── STBY   (HIGH = enabled)

3.3V     ────────────────────────── VCC    (logic power)
GND      ────────────────────────── GND    (ground)
VMOTOR ──────────────────────────── VMOTOR (7.4V battery — direct)
```

---

## Board 2 — Rear Motors (TB6612FNG #2)

```
Pi Zero W                          TB6612FNG #2
─────────────────                  ──────────────────────────
GPIO 10  ────────────────────────── AIN1   (Motor C Dir 1)
GPIO 9   ────────────────────────── PWMA   (Motor C Speed/PWM)
GPIO 11  ────────────────────────── AIN2   (Motor C Dir 2)
                                       │
                                       ├── AOUT1 ──► Rear Left Motor (+)
                                       └── AOUT2 ──► Rear Left Motor (-)

GPIO 8   ────────────────────────── BIN1   (Motor D Dir 1)
GPIO 7   ────────────────────────── PWMB   (Motor D Speed/PWM)
GPIO 25  ────────────────────────── BIN2   (Motor D Dir 2)
                                       │
                                       ├── BOUT1 ──► Rear Right Motor (+)
                                       └── BOUT2 ──► Rear Right Motor (-)

GPIO 6   ────────────────────────── STBY   (HIGH = enabled)

3.3V     ────────────────────────── VCC    (logic power)
GND      ────────────────────────── GND    (ground)
VMOTOR ──────────────────────────── VMOTOR (7.4V battery — direct)
```

---

## Power Rails

| Source          | Destination            | Wire Gauge | Notes                          |
|-----------------|------------------------|------------|--------------------------------|
| 7.4V Battery +  | VMOTOR (Board 1)       | 18 AWG     | Thick wire — motor current     |
| 7.4V Battery -  | GND (Board 1)          | 18 AWG     | Thick wire — motor current     |
| 7.4V Battery +  | VMOTOR (Board 2)       | 18 AWG     | Thick wire — motor current     |
| 7.4V Battery -  | GND (Board 2)          | 18 AWG     | Thick wire — motor current     |
| 7.4V Battery +  | LM2596 IN+             | 18 AWG     | Buck converter input            |
| 7.4V Battery -  | LM2596 IN-             | 18 AWG     | Buck converter input           |
| LM2596 OUT+     | Pi Zero W 5V pin       | 22 AWG     | Set LM2596 to 5V first!        |
| LM2596 OUT-     | Pi Zero W GND pin      | 22 AWG     |                                |
| Pi 3.3V pin     | VCC (Board 1 + 2)      | 24 AWG     | Logic power for TB6612FNG      |
| Pi GND pin      | GND (Board 1 + 2)      | 24 AWG     |                                |
| Pi 5V pin       | Camera (if powered)    | 24 AWG     |                                |

---

## STBY (Standby) Notes

- **GPIO 5 → STBY on Board 1** — Drive HIGH to enable front motor board
- **GPIO 6 → STBY on Board 2** — Drive HIGH to enable rear motor board
- Both STBY pins default to **LOW (disabled)** until the Pi sets them HIGH
- In Python: `GPIO.setup(5, GPIO.OUT)` then `GPIO.output(5, GPIO.HIGH)`

---

## Physical Pinout — Pi Zero W GPIO Header

```
        ╔═══╗
   5V   ║ 1 ║  5V
  GPIO  ║ 2 ║  5V
  GPIO  ║ 3 ║  GND
  GPIO  ║ 4 ║  TXD
  GND   ║ 5 ║  RXD
  GPIO  ║ 6 ║  GPIO [STBY Board 2 = GPIO 6]
  GPIO  ║ 7 ║  GPIO
  GPIO  ║ 8 ║  GND
  GPIO  ║ 9 ║  GPIO
  GPIO  ║10 ║  GPIO
  GPIO  ║11 ║  GPIO
  GND   ║12 ║  GPIO
  GPIO  ║13 ║  3.3V
  GPIO  ║14 ║  GND
  GPIO  ║15 ║  GPIO [MOTOR A DIR 2 = GPIO 27]
  GPIO  ║16 ║  GPIO
  3.3V  ║17 ║  3.3V [VCC both boards]
  GPIO  ║18 ║  GPIO [MOTOR A PWM = GPIO 18]
  GND   ║19 ║  GPIO
  GPIO  ║20 ║  GND
  GPIO  ║21 ║  GPIO
  GPIO  ║22 ║  GPIO [MOTOR B DIR 1 = GPIO 22]
  GPIO  ║23 ║  GPIO [MOTOR B PWM = GPIO 23]
  GND   ║24 ║  GPIO
  GPIO  ║25 ║  GPIO [MOTOR D DIR 2 = GPIO 25]
  GPIO  ║26 ║  GPIO
        ╚═══╝

  Side with notches = top (away from board edge)
  BCM numbers are shown
```

---

## PWM Frequency Note

The Python module (`tb6612fng.py`) uses **1000 Hz** PWM frequency by default (`PWM_FREQ_HZ = 1000`). This is a safe default for small DC motors. You can adjust it in the `TB6612FNGMotor` class if needed. Higher frequencies (>5kHz) may reduce motor hum but increase switching losses on the TB6612FNG.

---

## All BCM GPIO Pins Used — Summary

```
GPIO 5   — STBY Board 1
GPIO 6   — STBY Board 2
GPIO 7   — Rear Right Motor Speed (PWMB)
GPIO 8   — Rear Right Motor Direction 1 (BIN1)
GPIO 9   — Rear Left Motor Speed (PWMA)
GPIO 10  — Rear Left Motor Direction 1 (AIN1)
GPIO 11  — Rear Left Motor Direction 2 (AIN2)
GPIO 17  — Front Left Motor Direction 1 (AIN1)
GPIO 18  — Front Left Motor Speed (PWMA)
GPIO 22  — Front Right Motor Direction 1 (BIN1)
GPIO 23  — Front Right Motor Speed (PWMB)
GPIO 24  — Front Right Motor Direction 2 (BIN2)
GPIO 25  — Rear Right Motor Direction 2 (BIN2)
GPIO 27  — Front Left Motor Direction 2 (AIN2)

Total GPIO pins used: 14
Pins available on Pi Zero W: ~28 (excluding special-function pins)
```

---

## Color Code Suggestion for Jumper Wires

| Wire Color | Suggested Use                  |
|------------|-------------------------------|
| Red        | 3.3V logic power (VCC)        |
| Black      | GND (all grounds)            |
| Yellow     | Motor A direction (AIN1/AIN2) |
| White      | Motor B direction (BIN1/BIN2) |
| Green      | PWMA / PWMB (PWM signals)    |
| Blue       | STBY enable lines            |
| Orange     | Motor output AOUT/BOUT +     |
| Brown      | Motor output AOUT/BOUT -     |
