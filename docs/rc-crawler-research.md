# RC Crawler Research for Robot Project

**Date:** 2026-04-03
**Purpose:** Find a hackable RC crawler chassis for Vijay's robot project (robot-with-ai-v1)

---

## Requirements Summary
- **Scale:** 1:24 preferred, also 1:20 models
- **Dimensions:** L × W × H needed
- **Price:** $100 max (can stretch to ~$125, slightly above OK if exceptional)
- **Must be:** Sturdy, hackable, good ground clearance
- **Motors:** Check for 4 independent motor drives OR upgradeable to 4WD
- **Additional needs:** Strong chassis for electronics (Pi Zero, battery, motor controller)

---

## Crawler Options

### 1. RACENT RCS24 1/24 — **TOP PICK** ⭐

| Spec | Value |
|------|-------|
| **Scale** | 1:24 |
| **Dimensions** | 228 × ~100 × 103 mm |
| **Price** | ~$70-90 |
| **Motor** | Brushed 180 size (single motor, 4WD via transmission) |
| **Chassis** | Full metal alloy |
| **Suspension** | Multi-link coil spring |
| **Ground Clearance** | ~20-30mm estimated |
| **Battery** | 7.4V 380mAh Li-ion (included) |
| **LED Lights** | Yes (headlights, taillights) |
| **Water Resistance** | Splashproof |
| **Hackability** | ★★★★☆ Standard servo+ESC setup, popular platform |

**Notes:**
- Metal chassis = sturdy, can hold electronics
- 180 motor is standard size, easy to upgrade
- Single motor with 4WD (not 4 independent motors) - standard for this price
- Very popular in RC community = spare parts available
- Actual real-world car at 1:24 = ~5.5m long, so 228mm is accurate scale

**Link:** Amazon, Banggood, fpvbuildsrc.com

---

### 2. WPL C24 1/16 — Upgrade Pick

| Spec | Value |
|------|-------|
| **Scale** | 1:16 |
| **Dimensions** | 310 × 113 × 140 mm |
| **Price** | ~$80-110 |
| **Motor** | Brushed 180 size |
| **Chassis** | Metal frame + plastic body |
| **Drive** | 4WD |
| **Servo** | 17g included |
| **Battery** | 7.4V 500mAh (included) |
| **LED Lights** | Yes |
| **Hackability** | ★★★★★ Most popular budget crawler, HUGE aftermarket |

**Notes:**
- Larger = more room for electronics
- Excellent upgrade path (metal shafts, better motors, etc.)
- WPL ecosystem = tons of spare parts
- 4WD with single motor is standard
- Great for robot project - well-documented

**Link:** WPL official store, Amazon, rcmotoworks.com

---

### 3. FLYCOLOR / Generic 1/24 Rock Crawler

| Spec | Value |
|------|-------|
| **Scale** | 1:24 |
| **Dimensions** | ~220-240mm length (similar to RACENT) |
| **Price** | ~$50-70 |
| **Motor** | Brushed |
| **Chassis** | Metal alloy |
| **Drive** | 4WD |
| **Battery** | 7.4V (included) |
| **LED Lights** | Yes |
| **Hackability** | ★★★☆☆ Cheaper components |

**Notes:**
- Budget option, similar to RACENT
- Lower price = potentially lower quality components
- Still hackable but fewer upgrade parts

---

## 4-Motor Question

**Short answer: No budget crawler has 4 independent motors.** Here's why:

- **Standard RC crawlers** use 1 motor + transfer case → drives all 4 wheels via differentials
- **4WD** means all wheels get power, not 4 independent motors
- **True 4-motor (hub motors)** adds significant cost ($150+ just for motors)

**However**, for differential steering (turning), you can control left vs right side independently with:
- **2 motors + 2 ESCs** (replaces single motor setup) = ~$30-50
- Allows true tank steering = better robot control
- Most 4WD crawlers can be converted to 2-motor dual-ESC setup

**Recommendation:** Get a standard 4WD crawler (single motor), then upgrade to dual-motor setup later if you want independent wheel control.

---

## Missing Requirements I Added

1. **Ground clearance** - Need enough to not scrape on indoor floors/rugs
2. **Battery voltage** - 7.4V is standard, easy to find chargers
3. **Weight capacity** - Metal chassis crawlers can handle 200-300g of added electronics
4. **舵机 (Servo) compatibility** - Standard S接口 for external microcontroller control
5. **External control option** - Look for "hobby-grade" with separate receiver, NOT integrated Rx

---

## Recommendation for Vijay

### If you want 1:24 (smaller, fits more places):
**Buy: RACENT RCS24** (~80-90)
- Metal chassis = holds Pi Zero + electronics
- Small enough for indoor/outdoor
- Well-documented, community support
- Spare parts available

### If you want more room for electronics (1:16):
**Buy: WPL C24** (~80-100)
- Bigger = easier to mount things
- Best upgrade ecosystem
- Great documentation

---

## Additional Things to Buy

| Item | Price | Purpose |
|------|-------|---------|
| Spare battery (2x) | ~$15-20 | Longer runtime |
| LiPo charger | ~$10-15 | Recharge batteries |
| 2S LiPo battery (upgraded) | ~$15-20 | More voltage for motors |
| Aluminum wheel hubs | ~$10 | Better durability |

---

## Key Specs Needed for Vijay's Project

Current robot parts that need to fit:
- Pi Zero W
- TB6612FNG motor driver
- 5MP camera with cable
- Power bank (or LiPo)
- Servo for potential arm

**Recommendation:** Go with **WPL C24 1:16** - more room for mounting electronics, excellent community support for hacks/upgrades.
