# ACAMMZAR — 2WD Wiring Diagram (Simplified)

> **Components:** 1× TB6612FNG (drives 2 motors) | Car's internal 3.7V LiPo (motors) | External 5V power bank (Pi Zero) | Raspberry Pi Zero W | 2 motors (front + rear)

---

## 1. System Overview

```
┌─────────────────┐          ┌─────────────────┐          ┌─────────────────┐
│  POWER BANK     │          │   PI ZERO W     │          │   TB6612FNG     │
│  (5V USB)       │          │                 │          │                 │
│                 │          │  3.3V ──────────┼──────────┼──► VCC         │
│  USB ───────────┼──────────► Micro USB       │          │  GND ───────────┼──► GND
│                 │          │                 │          │  STBY ◄────────┼─── GPIO 5
│                 │          │  GPIO 17 ──────┼──────────┼──► AIN1         │
│                 │          │  GPIO 18 ──────┼──────────┼──► PWMA (PWM)  │
│                 │          │  GPIO 27 ──────┼──────────┼──► AIN2         │
│                 │          │  GPIO 22 ──────┼──────────┼──► BIN1         │
│                 │          │  GPIO 23 ──────┼──────────┼──► PWMB (PWM)  │
│                 │          │  GPIO 24 ──────┼──────────┼──► BIN2         │
└─────────────────┘          └─────────────────┘          └────────┬────────┘
                                                                    │
                                                                    │ AOUT1/AOUT2
                                                                    ▼
                                                            ┌───────────────┐
                                                            │ FRONT MOTOR   │
                                                            │   (Motor A)   │
                                                            └───────────────┘

                                                            ┌───────────────┐
                                                            │ REAR MOTOR    │
                                                            │   (Motor B)   │
                                                            └───────────────┘
                                                                    ▲
                                                                    │ BOUT1/BOUT2
┌─────────────────┐          ┌─────────────────┐          ┌────────┴────────┐
│  3.7V LiPo     │          │                 │          │                 │
│  (car battery)  │          │                 │          │                 │
│                 │          │                 │          │                 │
│  + (red) ───────┼──────────┼─────────────────┼──────────┼──► VMOTOR      │
│  - (black) ─────┼──────────┼─────────────────┼──────────┼──► GND         │
└─────────────────┘          └─────────────────┘          └─────────────────┘
```

**Power flow:**
- Power bank → Pi Zero (USB)
- Pi 3.3V + GND → TB6612FNG VCC + GND (logic power)
- Pi GPIO → TB6612FNG (control signals)
- Car LiPo → TB6612FNG VMOTOR + GND (motor power)

---

## 2. Power Domains (IMPORTANT — NO SHARED POWER)

```
┌─────────────────────────────────────────────────────────────────┐
│                    POWER BANK (5V USB)                         │
│                          │                                      │
│                          │ USB / microUSB                        │
│                          ▼                                      │
│                   ┌──────────────┐                              │
│                   │  Pi Zero W   │                              │
│                   │  5V pin      │                              │
│                   │  GND pin     │                              │
│                   └──────┬───────┘                              │
│                          │ 3.3V, GND, GPIO                      │
│                          │ 3 separate connections               │
└──────────────────────────┼──────────────────────────────────────┘
                           │
            ┌──────────────┼──────────────┐
            ▼              ▼              ▼
     ┌───────────┐  ┌───────────┐  ┌────────────┐
     │   VCC     │  │   GND     │  │   STBY      │
     │  (3.3V)   │  │           │  │  (GPIO 5)   │
     └───────────┘  └───────────┘  └────────────┘
                           │
                           ▼
              ┌────────────────────────┐
              │      TB6612FNG         │
              │                        │
              │ VMOTOR ◄── 3.7V LiPo   │
              │ GND    ◄── LiPo GND   │
              └────────────────────────┘
                           │
                           ▼
              ┌────────────────────────┐
              │   MOTORS              │
              │   Front (A)            │
              │   Rear (B)            │
              └────────────────────────┘
```

**Key rule:** Pi gets power from power bank. Motors get power from car LiPo. They only share ground (GND) and logic signals — no common power rails between them.

---

## 3. TB6612FNG Connections (Single Board)

| Pi Zero W | TB6612FNG | Function |
|-----------|-----------|----------|
| GPIO 17 | AIN1 | Motor A direction 1 |
| GPIO 27 | AIN2 | Motor A direction 2 |
| GPIO 18 | PWMA | Motor A speed (PWM) |
| GPIO 22 | BIN1 | Motor B direction 1 |
| GPIO 24 | BIN2 | Motor B direction 2 |
| GPIO 23 | PWMB | Motor B speed (PWM) |
| GPIO 5 | STBY | Enable (HIGH = on) |
| 3.3V | VCC | Logic power (from Pi) |
| GND | GND | Shared ground |

**Motor power:**
- TB6612FNG VMOTOR → 3.7V LiPo (+) 
- TB6612FNG GND → 3.7V LiPo (-)
- AOUT1/AOUT2 → front motor
- BOUT1/BOUT2 → rear motor

---

## 4. Motor Direction Truth Table

| AIN1 | AIN2 | PWMA | Result |
|------|------|------|--------|
| HIGH | LOW  | PWM  | Forward |
| LOW  | HIGH | PWM  | Backward |
| LOW  | LOW  | PWM  | Brake |
| HIGH | HIGH | PWM  | Brake |

Same logic applies to BIN1/BIN2/PWMB for Motor B (rear motor).

**Note:** With only 3.7V instead of 7.4V, motors will run slower but still work fine.

---

## 5. Unused GPIO Pins (free for other use)

| GPIO | Would be used for (4WD) |
|------|------------------------|
| GPIO 6 | STBY Board 2 |
| GPIO 7 | Rear Right Speed |
| GPIO 8 | Rear Right Dir 1 |
| GPIO 9 | Rear Left Speed |
| GPIO 10 | Rear Left Dir 1 |
| GPIO 11 | Rear Left Dir 2 |
| GPIO 25 | Rear Right Dir 2 |

---

## 6. Connection Order

1. **Power off everything** before wiring
2. **Connect Pi to power bank** via USB/microUSB — verify Pi boots
3. **Connect Pi 3.3V + GND** to TB6612FNG VCC + GND
4. **Connect GPIO wires**: 17, 18, 27, 22, 23, 24, 5
5. **Connect motor leads** to AOUT1/AOUT2 (front) and BOUT1/BOUT2 (rear)
6. **Connect 3.7V LiPo** to TB6612FNG VMOTOR + GND (from car — no buck converter needed!)
7. Test motors

**Note:** No LM2596 needed with this setup — car battery (3.7V) goes directly to TB6612FNG VMOTOR. The Pi is powered separately by the power bank.

---

## 7. Why Two Power Sources?

| Component | Power Source | Voltage |
|-----------|-------------|---------|
| Pi Zero W | Power bank | 5V USB |
| TB6612FNG logic (VCC) | Pi 3.3V | 3.3V |
| Motors | Car LiPo | 3.7V |

This keeps things simple — no buck converter needed, and you can power off the Pi independently without affecting motor control.
