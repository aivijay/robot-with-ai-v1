# Robot v2 Build Checklist — VEVOR 1:24 Crawler Chassis

> **Status:** CHASSIS ORDERED — arriving ~weekend of April 5-6, 2026  
> **Last Updated:** 2026-04-05

---

## Phase 0: Pre-Build Research & Planning

### Already Done
- [x] Chassis selected: VEVOR 1:24 (Model 2428), red, 4WD, brushed motor
- [x] TB6612FNG motor driver confirmed (from v1, ready to reuse)
- [x] Pi Zero 2 W with aluminum heatsink case (on desk, ready)
- [x] VEVOR.com order placed — ~$65 with new customer code VVBING5
- [x] Research docs created: `docs/rc-crawler-research.md`, `docs/jiabaile-rc-crawlers-research.md`
- [x] Corrected earlier misinformation: Jiabaile DOES have servo-controlled steering (not fixed)
- [x] Goobay UC-501 USB camera noted as smaller alternative for tight builds

### Research Tasks (Pending)
- [ ] Identify exact motor connector type (likely 3.5mm bullet connectors — verify when chassis arrives)
- [ ] Document stock ESC/receiver wiring (for reference before removal)
- [ ] Find 2S LiPo battery options (< $30, 1000-2000mAh, with Dean-T or XT30 connector)
- [ ] BEC/step-down converter selection for 5V Pi power from 7.4V battery
- [ ] Heat shrink tubing (560-piece kit, 5 colors, 12 sizes, 2:1 ratio — from earlier research)

---

## Phase 1: Chassis Arrival & Inventory

### Upon Arrival
- [ ] Take photo of box contents, stock wiring, motor locations
- [ ] Identify motor type and connector size (measure if needed)
- [ ] Identify steering servo type and connector
- [ ] Locate all PCB boards (ESC, receiver, LED driver)
- [ ] Document stock battery type and connector
- [ ] Measure available mounting space for Pi Zero + heatsink
- [ ] Check ground clearance under chassis

### Initial Tests (Before Modifications)
- [ ] Install batteries and test stock remote control operation
- [ ] Verify motor spins freely, no binding
- [ ] Test steering range and servo operation
- [ ] Note any issues with stock electronics (for warranty reference)

---

## Phase 2: Electronics Removal & Prep

### Strip Down
- [ ] Remove stock receiver/ESC (will be replaced with custom control)
- [ ] Remove or disable stock LED driver (keeping LEDs if possible)
- [ ] Identify motor wire colors: typically red (+), black (-)
- [ ] Identify steering servo wires: typically red (+5V), black (GND), white/yellow (signal)

### Motor Controller Prep
- [ ] Verify TB6612FNG is functional (from v1, should be OK)
- [ ] Prepare wiring harness: motor → TB6612FNG → Pi Zero GPIO
- [ ] Prepare servo wiring: steering servo → Pi Zero GPIO (through level shifter if needed)
- [ ] Plan GPIO pin assignments:
  - Motor A: PWM + Direction pins
  - Motor B: PWM + Direction pins
  - Steering servo: PWM pin

---

## Phase 3: Power System

### Power Architecture
```
2S LiPo (7.4V) ──┬──→ Motors (direct, via TB6612FNG)
                 └──→ BEC (5V) ──→ Pi Zero USB-C
```

### Tasks
- [ ] Source 2S LiPo battery (7.4V, 1000-2000mAh, Dean-T or XT30)
- [ ] Source 5V BEC (3A minimum, UBEC-style)
- [ ] Source XT60 or Dean-T connector to wire adapter
- [ ] Plan power switch wiring (should cut motor power, not Pi power)
- [ ] Calculate estimated runtime with chosen battery

---

## Phase 3.5: LED Control Integration

> **NOTE:** VEVOR 1:24 has 9 built-in LEDs: 1 roof, 6 front, 2 tail. Can control via MOSFET after bypassing stock LED driver.

### LED Wiring (Plan)
- [ ] Identify LED power circuit (positive wire from stock LED driver)
- [ ] Cut ground wire (or positive — depends on stock circuit)
- [ ] Splice MOSFET into LED ground path
- [ ] Wire MOSFET gate to Pi GPIO (through 10K resistor)

### Parts Needed
- [ ] N-channel MOSFET (IRL8721 or similar) × 1-2
- [ ] 10KΩ resistors (one per MOSFET gate)
- [ ] Flyback diodes (if LEDs have inductive load — unlikely for simple LEDs)
- [ ] Heat shrink or electrical tape for splices

### GPIO Pin Plan (TBD)
| LED Group | GPIO Pin | Notes |
|----------|---------|-------|
| Front LEDs (6) | TBD | All front lights together |
| Rear LEDs (2) | TBD | Tail lights |
| Roof LED (1) | TBD | Optional — special effects? |

### Control Options
- [ ] Simple ON/OFF (all LEDs together — start simple)
- [ ] Individual groups (front, rear, roof separate)
- [ ] PWM dimming (optional — add if LED brightness control wanted)

### Software Support
- [ ] Add LED control to `common/hardware.py`
- [ ] Add `set_lights(front=True, rear=True)` function
- [ ] Integrate into reflex layer: headlights auto-on in dark
- [ ] Add LED indicators for robot state (green=ok, red=stuck, amber=turning)

---

## Phase 4: Pi Zero 2W Mounting

### Mounting Options
- [ ] Measure available space under body shell
- [ ] Decide: mount inside shell or external frame?
- [ ] Drill/mount heatsink case securely
- [ ] Plan cable routing for:
  - Camera ribbon (if internal)
  - USB power
  - GPIO to motor driver
  - Optional USB webcam (Goobay UC-501)

### Heat Management
- [ ] Pi Zero 2 W with heatsink should handle ambient
- [ ] Monitor temps during first tests
- [ ] Consider thermal pads if needed

---

## Phase 5: Camera Integration

### Options for v2
- [ ] **Option A:** Continue with current 8MP Pi Camera v2 (uses ribbon cable)
- [ ] **Option B:** Switch to Goobay UC-501 USB camera (15×15mm, plug-and-play, less fragile)
- [ ] Plan camera mount angle (0.08 radians ≈ 4.6° down for floor visibility, same as v1)
- [ ] Route camera cable safely (avoid moving parts)

---

## Phase 6: Software Architecture

### Multi-Layer Design (from v1 learnings)
```
src/
├── robot/camera.py      # MJPEG streaming + frame analysis
├── robot/motors.py      # GPIO PWM motor + servo control
├── robot/reflex.py      # Safety reflexes + skill layer (cerebellum)
├── agent/brain.py       # LLM orchestrator (prefrontal cortex)
├── common/hardware.py   # Config (speeds, thresholds, GPIO pins)
├── robot_agent.py       # Main entry point
└── memory/robot_memory.py # Persistent JSON memory
```

### Implement for v2
- [ ] Copy/refactor v1 code as baseline
- [ ] Add wheel-slip detection (if wheels spin but robot doesn't move → reverse immediately)
- [ ] Improve stuck detection (v1 got stuck between boxes for extended period)
- [ ] Adapt floor detection algorithm (v1 worked well)
- [ ] Add camera angle control via servo
- [ ] Add battery voltage monitoring

### Reflex Layer (Priority)
- [ ] Cliff detection (already working in v1)
- [ ] Obstacle detection via floor brightness (already working in v1)
- [ ] Wheel-slip detection (NEW for v2)
- [ ] Stuck/escape behavior (improved from v1)
- [ ] Auto-dock (already working in v1)

---

## Phase 7: Testing & Calibration

### Calibration Tasks
- [ ] Motor speed vs PWM duty cycle mapping
- [ ] Steering servo center point and range
- [ ] Camera angle for optimal floor visibility
- [ ] Cliff detection threshold tuning
- [ ] Obstacle detection sensitivity
- [ ] LLM brain prompt tuning

### Test Sequence
1. [ ] Manual remote control (GPIO buttons or wired)
2. [ ] Motor forward/backward at low speed
3. [ ] Steering full range
4. [ ] Autonomous wander mode (basic)
5. [ ] Cliff detection + auto-stop
6. [ ] Floor brightness obstacle avoidance
7. [ ] Stuck detection + escape
8. [ ] LLM navigation commands
9. [ ] Long-duration autonomous run (30+ min)

---

## Phase 8: Field Testing & Iteration

### Porch/Outdoor Testing
- [ ] Test on different floor surfaces
- [ ] Test cliff detection on stairs
- [ ] Test obstacle avoidance with varied objects
- [ ] Battery life measurement
- [ ] WiFi range test (Pi Zero to host laptop)

### Documentation
- [ ] Update MEMORY.md with final v2 config
- [ ] Document any issues and fixes
- [ ] Photo document build process

---

## Issues to Watch (from v1 learnings)

| Issue | Mitigation |
|-------|-----------|
| Cozmo falls asleep mid-session | Keep battery charged during testing |
| Robot gets stuck between objects | Improve stuck detection, add wheel-slip |
| Camera ribbon cable loose | Reseat firmly, secure with tape |
| Motor driver fried (v1) | NEVER reverse VCC/GND on TB6612FNG |
| Low battery = sluggish | Monitor voltage, auto-dock before critical |
| Multiple rpicam-vid processes | Kill all before starting fresh |

---

## Future: Jiabaile 1:36 (Phase 2)

> Defer until v2 with VEVOR is complete and lessons learned.

- [ ] Jiabaile 3601/3602 research complete (has servo steering, 716 motor, 3.7V)
- [ ] Smaller scale = tighter space constraints
- [ ] Goobay UC-501 USB camera more appropriate for compact build
- [ ] Power from single 3.7V battery (no 2S needed)

---

## Hardware Inventory (v2)

| Item | Status | Notes |
|------|--------|-------|
| VEVOR 1:24 Chassis (red) | ON ORDER | Arriving ~weekend |
| Pi Zero 2 W + heatsink case | READY | On desk |
| TB6612FNG motor driver | READY | From v1 |
| 8MP Pi Camera v2 | READY | From v1 |
| Goobay UC-501 USB | PENDING | Alternative camera option |
| 2S LiPo battery | PENDING | Need to source |
| 5V BEC | PENDING | Need to source |
| Heat shrink kit | PENDING | From earlier research |
| N-channel MOSFET (IRL8721) | PENDING | LED control, ~$1-2 |
| 10KΩ resistors | PENDING | LED gate pull-down |
| Flyback diodes | PENDING | Optional — likely not needed for LEDs |

---

## Reference Documents

- `/home/vijay/projects/robot-with-ai-v1/docs/rc-crawler-research.md`
- `/home/vijay/projects/robot-with-ai-v1/docs/jiabaile-rc-crawlers-research.md`
- `/home/vijay/projects/robot-with-ai-v1/docs/autonomous-charging-research.md`
- `/home/vijay/projects/robot-with-ai-v1/docs/depth-sensing-research.md`
- `/home/vijay/.openclaw/agents/main/MEMORY.md` (current robot state)