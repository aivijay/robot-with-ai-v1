# ACAMMZAR 1:24 RC Drift Car - Hacking Notes

## Overview
Hacking the ACAMMZAR 1:24 RC drift car for autonomous AI control using:
- Raspberry Pi Zero W + Camera
- Ollama (LLM/VLM on laptop)
- TB6612FNG Dual Motor Driver (×2 for 4WD)
- Custom motor controller replacement

**Status: Planning phase** - only have product images, no physical car yet.

---

## Car Details

### Scale
- **1:24 scale** - larger than 1:64, good platform for internal components

### Drive Type
- **TRUE 4WD** - 4 individual motors (one per wheel), confirmed from product images
- Not like the 1:32 which is advertised as 4WD but only has 2 motors (1 front, 1 back)

### Battery
- **7.4V** (2× 3.7V LiPo in series)
- This is a higher voltage than the 1:64's 3.7V single cell
- More power available for motors

### Motor Specs (Estimated)
- Likely 3-6V motors given the 7.4V battery (with voltage regulation)
- 4× small brushed DC motors (one per wheel)
- Individual motor control possible with 4-channel setup

### Internal Components (from images)
- Custom PCB with motor driver ICs
- 4 motor connectors (one per wheel)
- Central PCB visible in bottom view
- TX/RX test points visible on PCB (UART debug?)
- Suspension visible at all 4 corners

---

## Motor Driver Decision

### Question: Replace controller OR hack existing PCB?

**Option A: Replace with TB6612FNG (External)**
- Use 2× TB6612FNG boards (each handles 2 motors = 4 total)
- Remove or bypass existing PCB
- Known, documented approach

**Option B: Hack existing PCB**
- Use the existing 4-channel H-bridge on the car's PCB
- Figure out control signals from limited images
- Unknown pinout, voltage levels, control protocol

### Decision: **Use TB6612FNG (External Controller)**

**Rationale:**
1. **Unknown PCB** - only 1 image of the bottom, can't identify chips/traces/pinout
2. **No hardware access** - can't probe with multimeter or oscilloscope
3. **Risk** - wrong signals could fry the existing PCB
4. **Known approach** - TB6612FNG is documented, we understand it
5. **Flexibility** - can debug and modify easily with known wiring
6. **Safety** - if something goes wrong, we haven't damaged the car PCB

**Cons of hacking existing PCB:**
- Don't know if it needs 3.3V or 5V logic
- Don't know PWM frequency requirements
- Don't know direction control (1-wire vs 2-wire H-bridge)
- Can't test without physical hardware
- Reverse-engineering would require multiple iterations

---

## Proposed Wiring Architecture

### Power Distribution
```
Car Battery (7.4V)
     │
     ├──► TB6612FNG #1 ──► Front Left Motor
     │                        Front Right Motor
     │
     ├──► TB6612FNG #2 ──► Rear Left Motor
     │                        Rear Right Motor
     │
     └──► Step-Down (7.4V → 5V) ──► Pi Zero W + Camera
```

**Note:** The TB6612FNG can handle up to 13.5V VMOTOR, so 7.4V is well within spec. The Pi needs 5V, so a step-down converter is required.

### TB6612FNG Pinout (per board)
```
┌────────────────────────────────────────┐
│  VMOTOR (+) ─── Battery + (7.4V)      │
│  VMOTOR (-) ─── Battery - (GND)       │
│                                        │
│  VCC  ─────────── Pi 3.3V             │
│  GND  ─────────── Pi GND              │
│                                        │
│  PWMA  ────────── GPIO (PWM)          │
│  AIN1  ────────── GPIO (DIR)          │
│  AIN2  ────────── GPIO (DIR)          │
│  AOUT1 ────────── Motor +             │
│  AOUT2 ────────── Motor -             │
│                                        │
│  PWMB  ────────── GPIO (PWM)          │
│  BIN1  ────────── GPIO (DIR)          │
│  BIN2  ────────── GPIO (DIR)           │
│  BOUT1 ────────── Motor +             │
│  BOUT2 ────────── Motor -             │
│                                        │
│  STBY  ────────── Pi GPIO (HIGH)      │
└────────────────────────────────────────┘
```

### GPIO Mapping (Pi Zero W)

**TB6612FNG #1 (Front motors):**
| GPIO | Function       | TB6612FNG Pin |
|------|---------------|---------------|
| GPIO 17 | Motor A Direction | AIN1 |
| GPIO 18 | Motor A Speed    | PWMA |
| GPIO 27 | Motor A Direction 2 | AIN2 |
| GPIO 22 | Motor B Direction | BIN1 |
| GPIO 23 | Motor B Speed    | PWMB |
| GPIO 24 | Motor B Direction 2 | BIN2 |

**TB6612FNG #2 (Rear motors):**
| GPIO | Function       | TB6612FNG Pin |
|------|---------------|---------------|
| GPIO 10 | Motor C Direction | AIN1 |
| GPIO 9  | Motor C Speed    | PWMA |
| GPIO 11 | Motor C Direction 2 | AIN2 |
| GPIO 8  | Motor D Direction | BIN1 |
| GPIO 7  | Motor D Speed    | PWMB |
| GPIO 25 | Motor D Direction 2 | BIN2 |

**Common:**
| GPIO | Function       | TB6612FNG Pin |
|------|---------------|---------------|
| GPIO 5 | Enable Board 1 | STBY (board 1) |
| GPIO 6 | Enable Board 2 | STBY (board 2) |
| GND | Ground | GND (both boards) |

---

## 4WD Steering Logic

### Motor Layout (4WD)
```
     [FL]           [FR]
       \             /
        \___________/
        |           |
        |___________|
       /             \
     [RL]           [RR]
```

### Differential Steering (4WD)

**Note:** With 4WD, you can do true tank steering or try to mimic Ackerman steering.

**Tank Steering (simpler):**
| FL | FR | RL | RR | Action |
|----|----|----|----|--------|
| + | + | + | + | Forward |
| - | - | - | - | Backward |
| + | - | + | - | Spin left (tank) |
| - | + | - | + | Spin right (tank) |
| 0 | + | 0 | + | Turn right |
| + | 0 | + | 0 | Turn left |

**4WD Ackerman-like (more realistic):**
For a drift car, you might want:
- Front wheels: steering angle
- Rear wheels: driving force

This would require:
- Front motors: variable speed for steering
- Rear motors: equal speed for driving

### Simpler Approach: 2-Wheel Control

Since we're replacing the stock electronics anyway, we could simplify:
- **Connect front-left + rear-left** to same driver channel (both on left side)
- **Connect front-right + rear-right** to same driver channel (both on right side)
- This gives standard differential steering with 2 TB6612FNG instead of needing 4

This is a reasonable simplification for an RC drift car - the rear wheels can be synchronized.

---

## Parts Needed

### Already Have
- Raspberry Pi Zero W ✅
- Pi Camera v2 (8MP) ✅
- USB Power Bank (for Pi) ✅

### Need to Order

| Item | Purpose | Quantity | Status |
|------|---------|----------|--------|
| TB6612FNG Dual Motor Driver | Control 2 motors each | 2 boards | Need to order |
| Jumper Wires (F/F) | GPIO to driver connections | 40pcs | Need to order |
| LM2596 DC-DC Buck Converter | 7.4V → 5V for Pi | 1 | Need to order |
| 2×20 Male Header | Solder to Pi Zero GPIO | 1 | Need to order |
| Prototype PCB / Perfboard | Mount TB6612FNG boards | 1 | Need to order |

### Estimated Cost
- TB6612FNG (2-pack): ~$8-12
- Jumper wires: ~$5-8
- LM2596 module: ~$2-3
- Headers + perfboard: ~$5

**Total: ~$20-30**

---

## Physical Mounting Considerations

### Space in 1:24 Car
- 1:24 scale car has more internal space than 1:64
- Should fit: Pi Zero W, 2× TB6612FNG, step-down converter
- Battery already in car (7.4V LiPo)
- May need to remove some internal plastic

### Mounting Strategy
1. Remove stock PCB (keep motor driver section or replace entirely)
2. Mount Pi Zero with adhesive standoffs or double-sided tape
3. Mount TB6612FNG boards with standoffs or hot glue
4. Route wires cleanly, use zip ties for management

### Future Upgrades
- Could add IMU (MPU6050) for odometry
- Could add encoder disks to motors for precise speed control
- Could add ultrasonic sensors for obstacle avoidance

---

## Comparison: 1:64 vs 1:32 vs 1:24

| Feature | 1:64 (current) | 1:32 | 1:24 (this car) |
|---------|----------------|------|-----------------|
| Size | Tiny | Medium | Large |
| Motors | 2 (fake 4WD) | 2 (fake 4WD) | 4 (true 4WD) |
| Battery | 3.7V 250mAh | 3.7V 600mAh | 7.4V (unknown mAh) |
| Pi fits inside | No | Maybe | Yes |
| Power bank fits | No | No | Yes |
| Carpet performance | Poor | Medium | Good |
| Hacking potential | Limited | Medium | High |

---

## References

### Photos (in ./docs/images/ACAMMZAR-RC-Drift-Car-1-24/)
- `71c5KvCr02L._AC_SL1500_.jpg` - Bottom view (PCB visible, 4 motor positions)
- `71mEo3ZUmfL._AC_SL1500_.jpg` - Front view (front motor visible)
- `71w394T5rrL._AC_SL1500_.jpg` - Side/bottom view (motor connector visible)

### Project Location
`/home/vijay/projects/robot-with-ai-v1/`

---

## Next Steps

1. [ ] Acquire the ACAMMZAR 1:24 car (order if not already done)
2. [ ] Take detailed internal photos once received
3. [ ] Identify motor specs (measure or look up)
4. [ ] Order TB6612FNG boards (2×)
5. [ ] Order other components (jumpers, step-down, headers)
6. [ ] Design wiring diagram in detail
7. [ ] Solder male headers to Pi Zero GPIO
8. [ ] Wire up test circuit on bench
9. [ ] Test motor control before installing in car
10. [ ] Install in car and test

---

## Future Upgrades / Backlog

### Voice and Hearing (TTS + STT)

**Goal:** Add speakers and microphone so the robot can hear commands and respond with voice.

**Use cases:**
- Voice commands ("come here", "stop", "follow me")
- Text-to-speech responses ("I'm stuck", "I see an obstacle")
- Conversational AI interaction
- Audio feedback for robot state

**Options considered:**

1. **Respeaker USB Mic Array**
   - 4-microphone array, good for voice capture
   - Built-in voice processing
   - USB connection (easy to set up)
   - Has speaker output
   - CONS: Larger, more expensive (~$40)

2. **Adafruit MEMS Microphone (MAX4466) + Speaker HAT**
   - Small, fits in 1:24 car
   - I2S MEMS mic for good quality
   - Speaker HAT for audio output
   - CONS: Requires separate amp for speakers

3. **ReSpeaker 2-Mic Pi HAT**
   - Designed for Pi Zero
   - 2-microphone array
   - Built-in 3W speaker driver
   - GPIO pins for connection
   - CONS: Size might be tight in 1:24

4. **USB Sound Card + Cheap Mic + Speaker**
   - Small USB sound card (~$$5)
   - Clip-on mic or small MEMS
   - Small 4Ω speaker
   - CONS: Multiple components to mount

**Design considerations:**
- Pi Zero has limited USB ports (1 OTG)
- Need to consider audio latency for real-time interaction
- Wake word detection (like "Hey Pi") would be nice
- Could use Whisper for local STT, or cloud API
- For TTS: can use gTTS, Coqui, or cloud TTS

**Recommended approach (TBD):**
- Research ReSpeaker 2-Mic HAT for form factor
- Consider separate USB sound card if tight on space
- Keep the mic close to front of car for better voice pickup
- Speaker can mount in the car body (hollow section)

**Status:** 🟡 Backlog - pending design decision

---

## Decision Summary

**Date:** 2026-03-29

**Decision:** Use external TB6612FNG motor controllers (2× boards for 4WD)

**Reasoning:** 
- Only have product images, no physical access to car
- Existing PCB is unknown/unverified
- TB6612FNG approach is documented and safe
- Can debug easily without risk to car electronics

**Alternative considered:** Hack existing PCB
- Rejected due to insufficient information and lack of physical access

---

*Document created: 2026-03-29*
