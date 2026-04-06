# Jiabaile 3601/3602 1:36 Mini 4WD RC Crawler — Research for Robot v2 (Alternative/Future)

> **Current plan:** VEVOR 1:24 first (more build experience) → Jiabaile 1:36 later (lessons learned)
> This doc is kept as reference for the smaller chassis if/when the project progresses to a compact build.

**Date:** 2026-04-04
**Project:** robot-with-ai-v1 (RC Crawler conversion)
**Product Page:** https://bestbuyboxes.com/products/jiabaile-mini-4wd-metal-rc-crawler-3601-3602
**Price:** $55.99 (currently sold out)

---

## Overview

The Jiabaile 3601/3602 is a 1:36 scale micro 4WD RC crawler. It's significantly smaller than the VEVOR 1:24 crawler originally planned — about **75% smaller in each linear dimension**. The chassis is all-metal with a fully proportional throttle, fixed steering, and 4WD drivetrain. Despite its tiny size, the build quality appears excellent (metal frame, metal wheel hubs, universal shafts, full bearings).

---

## Key Specifications

| Spec | Value |
|------|-------|
| Scale | 1:36 |
| Drive | 4WD |
| Motor | 716 Coreless, 3.7V @ 50,000 RPM |
| Battery | 3.7V 200mAh Li-ion (internal, built-in) |
| Gear Ratio | 1:380 |
| Max Speed | ~2 km/h |
| Run Time | Up to 60 minutes |
| Charge Time | 30 minutes |
| Control | 2.4GHz, 20m range |
| Steering | Servo (proportional, front wheel steering via 3602 control board) |
| Throttle | Fully proportional, 3-speed limit selectable |
| Scale Length | ~100mm (estimated, 1:36 of a ~3.6m real car) |

**Note on steering:** This uses "crawler-style" fixed steering where the front and rear axles are both locked straight. Turning is achieved by differential wheel speed (one side forward, one side back for a pivot, or simply reversing direction to change heading). This is actually ideal for a robot — no servo needed, just two motors or differential drive control.

---

## Robot Conversion Analysis

### Size Comparison

| Chassis | Scale | Est. Length |
|---------|-------|-------------|
| VEVOR 2428 (original plan) | 1:24 | ~200mm |
| Jiabaile 3601 | 1:36 | ~100mm |

The Jiabaile is roughly half the size in each dimension. This means:
- ✅ Very compact — fits anywhere, great for indoor navigation
- ✅ Low mass — less damage risk, safer around people/pets
- ✅ Lighter battery requirements
- ⚠️ Limited payload — Pi Zero + HAT + small battery only
- ⚠️ Motor is tiny (716 coreless) — low torque, not for heavy loads

### Drive System

**Original setup:** Single 716 motor driving all 4 wheels via transfer case (similar to the VEVOR).

**Robot conversion options:**

1. **Keep single motor + TB6612FNG (recommended for v1 reuse)**
   - Motor: 716 coreless, 3.7V, very small
   - Current: ~500mA stall (estimate, 716 motors are typically 180mA no-load)
   - Torque: Very low — this motor is optimized for speed, not torque
   - TB6612FNG can handle it easily (1.2A per channel)
   - Power from 3.7V LiPo — need a boost converter for 5V Pi power

2. **Replace motor with larger N20/JGA20 gearmotor (better for robot)**
   - N20 6V 100RPM: ~$3-5 each, much more torque
   - Would need custom mount — not drop-in
   - 4WD becomes complex (4 separate motors)

3. **Keep 4WD, one motor per axle (keep original drivetrain)**
   - Motor is already center-mounted driving front/rear via transfer case
   - For robot: keep motor, use TB6612FNG to control motor speed/direction
   - Steering: use differential speed (slow one side = turn)

### Power Architecture

The original uses a single 3.7V 200mAh internal cell. For robot use:

```
3.7V LiPo (main) ──┬──→ TB6612FNG → 716 motor (3.7V direct)
                   └──→ 3.7V→5V Boost → USB-C → Pi Zero
```

Or for more power, use a 2S (7.4V) battery and step down:
```
2S LiPo (7.4V) ──┬──→ TB6612FNG → motor (via 7.4V or 5V regulator)
                 └──→ 7.4V→5V BEC → USB-C → Pi Zero
```

**Issue:** The 716 motor is rated for 3.7V. Running at 7.4V would overrev and likely burn it out. If keeping this motor, must use 3.7V supply.

### Space Constraints

At 1:36 scale, the chassis is very small. Estimated chassis dimensions:
- Length: ~100mm
- Width: ~50mm
- Height: ~30mm

**Pi Zero + TB6612FNG footprint:**
- Pi Zero: 65×30mm
- TB6612FNG (12-pin DIP): ~20×8mm + heat spreader
- Stacked or side-by-side: ~65×50mm total

This fits on the chassis but is tight. **Vijay's soldering plan is excellent** — removing jumper headers saves significant space. Direct soldering of motor wires and GPIO leads to the TB6612FNG and Pi headers would reduce the footprint considerably.

**Soldering approach recommended:**
- Solder motor leads directly to TB6612FNG output pins (no header)
- Solder TB6612FNG logic pins (direct wire to specific GPIO)
- Solder 5V power wires directly to Pi Zero test pads (PP1/PP6)
- Use a small custom PCB or deadbug wiring for clean layout

---

## Full Parts List (from product page explosion diagram)

### Chassis & Frame
| Part # | Description | Qty |
|--------|-------------|-----|
| 3601 | Chassis Frame (with motor mount) | 1 |
| 3601-821 | Metal Chassis (lower frame) | 1 |
| 3601-820 | Metal Main Frame (upper) | 1 |
| 3601-815 | Upper Wishbone A | 2 |
| 3601-813 | Lower Wishbone B | 2 |
| 3601-816 | Front Steering Knuckle | 1 |
| 3601-817 | Rear Steering Knuckle | 1 |

### Drivetrain
| Part # | Description | Qty |
|--------|-------------|-----|
| 3601-826 | Motor 716 (3.7V coreless) | 1 |
| 3601-829 | Motor Gear | 1 |
| 3601-828 | Drive Gear | 1 |
| 3601-827 | Universal Shaft | 1 |
| 3601-807A | Axle Shaft (rear, L+R) | 2 |
| 3601-807B | Axle Shaft (front, L+R) | 2 |
| 3601-806A | Front Axle | 1 |
| 3601-806B | Rear Axle | 1 |

### Wheels & Suspension
| Part # | Description | Qty |
|--------|-------------|-----|
| 3601-811 | Wheels | 4 |
| 3601-812 | Tires (rubber) | 4 |
| 3601-810 | Wheel Hub (metal) | 4 |
| 3601-801 | Spring Shock Absorber | 4 |

### Hardware & Fasteners
| Part # | Description | Qty |
|--------|-------------|-----|
| 3601-837 | M1.4×4 Screw | 4 |
| 3601-838 | M1.6×6 Screw | 6 |
| 3601-839 | M1.6×7 Screw | 2 |
| 3601-840 | M2×5 Screw | 2 |
| 3601-841 | M2×10 Screw | 4 |
| 3601-842 | M2.5×4 Screw | 4 |
| 3601-843 | M2.5×8 Screw | 2 |
| 3601-844 | M2.5×10 Screw | 2 |
| 3601-845 | M3×4 Set Screw | 2 |
| 3601-846 | M3×6 Set Screw | 1 |
| 3601-847 | Nut M1.4 | 4 |
| 3601-848 | Nut M2 | 2 |
| 3601-849 | Nut M3 | 1 |
| 3601-850 | O-ring 3×1.5 | 1 |
| 3601-851 | O-ring 5×1.5 | 1 |
| 3601-852 | O-ring 6×1.5 | 1 |

### Bearings & Bushings
| Part # | Description | Qty |
|--------|-------------|-----|
| 3601-825 | Bearing 3×7×3 | 4 |
| 3601-824 | Bearing 4×8×3 | 2 |

### Electronics & Battery
| Part # | Description | Qty |
|--------|-------------|-----|
| 3601-830 | Battery Case (2-pin connector) | 1 |
| 3601-3602 | 3-Speed Throttle Board (with motor driver) | 1 |
| 3601-823 | Power Switch | 1 |
| 3601-822 | 2.4G RX Board | 1 |
| 3601-3602-TX | 2.4G TX Module (on tx board) | 1 |
| 3601-834 | USB Cable (for charging) | 1 |

---

## Decision Points for Vijay

### Should You Buy This?

**Buy this chassis if:**
- You want a very compact, high-quality metal chassis for indoor robot experiments
- You don't need to carry heavy payloads (Pi Zero + small battery only)
- You're okay with a single-motor 4WD drivetrain
- You can work with the tiny 716 motor (low torque but sufficient for smooth indoor floors)
- You want to practice direct-solder wiring for minimal footprint

**Stick with VEVOR 1:24 if:**
- You need higher torque for outdoor/rough terrain
- You want more payload capacity (larger SBC, ToF sensor, etc.)
- You prefer a more standard steering servo setup
- Size isn't a constraint

### For the Robot v2 Build (if buying this)

**Power:**
- 1× 3.7V 1000-1500mAh LiPo (small single-cell) for motor
- 1× 5V boost converter for Pi
- Or: 1× 2S LiPo + dual 5V BEC — but motor must be replaced for 7.4V operation

**Motor control:**
- Keep TB6612FNG from v1 ✅ (way overkill for this tiny motor, but reusable)
- Or use a tiny DRV8833 dual motor driver board (much smaller footprint)

**Soldering plan (Vijay's idea — excellent):**
1. Remove all jumper headers from Pi Zero GPIO
2. Solder motor wires directly to TB6612FNG output pins
3. Solder twisted-pair GPIO wires directly to TB6612FNG logic inputs
4. Solder 5V power wires directly to Pi Zero test pads (PP1/PP6)
5. Use heat-shrink to insulate all joints
6. Mount TB6612FNG directly below Pi Zero (standoff mount)

**Camera:**
- The chassis is too small for the standard Pi Camera v2 with ribbon — consider the Goobay UC-501 USB camera (small, ~$10) or a small Arducam MIPI module

**Navigation:**
- No room for ToF sensor on the tiny chassis — wall-following via camera is more realistic
- Cliff detection via downward-facing LDR or small IR sensor is feasible

---

## Action Items (for Jiabaile 1:36 — Phase 2)

- [ ] **Phase 1 first**: Build VEVOR 1:24, learn lessons
- [ ] Later: Consider Jiabaile 1:36 as Phase 2 compact build
- [ ] Plan direct-solder wiring layout for minimal footprint (from VEVOR lessons)
- [ ] Order Goobay UC-501 USB camera or Arducam B0390 (mini) for compact build
- [ ] Order heat shrink kit (~560pcs, 5 colors, 12 sizes)

---

## Hardware / Tools / Consumables for Build

### Heat Shrink Tubing
For insulating solder joints on motor wires, GPIO leads, and power connections.

**Recommended kit:**
- **560-piece heat shrink assortment** — 5 colors (black, red, blue, yellow, green), 12 sizes (1mm–13mm), 2:1 ratio
  - ~$12–15 on Amazon
  - Get the one with multiple smaller sizes (1mm, 1.5mm, 2mm) — you'll need these for GPIO wires and motor leads
  - 2:1 ratio = shrinks to half diameter when heated (standard, reliable)

**Buy links:**
- Amazon: https://www.amazon.com/560PCS-Heat-Shrink-Tubing-Electrical/dp/B0G5K6SNWX
- Walmart: https://www.walmart.com/ip/16954111463
- Search: "560pcs heat shrink assortment kit 5 colors" (many sellers ~$10–15)

**Tip:** Get a pack with multiple SMALL sizes. The 1mm, 1.5mm, 2mm tubes are the ones you'll use most on a Pi Zero / motor controller build. Larger sizes (8mm, 10mm, 13mm) are for power wiring.

### Other Consumables
- **Soldering iron tip cleaner** — brass wool or tip tinner
- **Rosin core solder** — 0.8mm or 1.0mm diameter for electronics work
- **Kapton tape** — high-temp insulation for securing wires to chassis
- **Zip ties** — small nylon ties for cable management

---

## Links

- Product: https://bestbuyboxes.com/products/jiabaile-mini-4wd-metal-rc-crawler-3601-3602
- Reference image: `docs/images/jiabaile-rc-crawlers.jpg` (790×18561px full explosion diagram)
