# Autonomous Charging Research — Robot v2

*Updated: 2026-04-05*

## Current Status

**CHARGING ARCHITECTURE DECIDED — Implementation pending chassis arrival**

---

## Power Architecture (v2 Final)

### Robot Power Budget
- **Pi Zero 2 W**: 5V/0.5-1A (2.5-5W)
- **Motors**: 3.7V nominal, stall ~2A per motor
- **Camera + misc**: 5V/0.2A

### Battery Setup (v2)
| Component | Battery | Connector | Notes |
|-----------|---------|-----------|-------|
| Pi + Electronics | USB Power Bank (external) | USB-C | 10000mAh, separate circuit |
| Motors | 3.7V LiPo (4000mAh) | JST PH2.0 | Internal, powers motors via TB6612FNG |

---

## Charging Architecture (Decided)

```
┌─────────────────────────────────────────┐
│         MAGNETIC DOCK (single point)   │
│              on robot chassis            │
└──────────────────┬──────────────────────┘
                   │ Magnetic connector (self-aligning)
                   ▼
        ┌──────────────────┐
        │  1-to-2 Splitter │
        │  (USB-C F → 2M)  │
        └───────┬──────────┘
                │
       ┌────────┴────────┐
       ▼                 ▼
  ┌─────────┐      ┌──────────────┐
  │Power Bank│     │ LiPo Charger  │
  │(USB-C)  │     │ (USB-C →      │
  │         │     │  JST PH2.0)   │
  └─────────┘     └──────┬───────┘
                          ▼
                   ┌──────────────┐
                   │ 3.7V LiPo    │
                   │ 4000mAh      │
                   │ (motors)     │
                   └──────────────┘
```

### Parts List
| Item | Approx Cost | Notes |
|------|-------------|-------|
| Magnetic USB-C connector (pair) | $5-10 | Male on robot, female on dock cable |
| USB-C 1-to-2 splitter (passive) | $8-12 | Like the 3-way you found, or simpler 2-way |
| TP4056 LiPo charger module | $1-2 | Basic, 1A max charge rate |
| 3.7V/4000mAh LiPo battery | ~$15 | Already have |
| USB power bank | Already have | Powers Pi Zero |

### Charging Behavior
- **Slow charging only** — passive splitter limits PD negotiation
- Both power bank and LiPo fall back to 5V/2A shared
- Power bank: ~10W fast charge capable, gets ~5W through splitter
- LiPo: TP4056 maxes at 1A (~5W), charges in ~4-5 hours
- **Sufficient for overnight docked charging**

---

## Magnetic Dock Design

### Requirements
1. Single dock point on robot (magnetic self-aligning)
2. Cable from dock runs to charger / power source
3. Robot can approach from any angle, magnet pulls it into alignment
4. Enough strength to hold robot during charging

### Approach
- **Magnetic "landing pad"** — flat surface with embedded USB-C female or magnetic adapter
- **Magnet pair** — one on robot body, one on dock — creates "snap" alignment
- Robot drives onto pad, parks, magnet engages, charging begins

### Implementation
1. Mount a small **neodymium magnet** on robot chassis bottom/rear
2. Corresponding **metal plate or magnet** on charging dock
3. USB-C magnetic adapter cable plugs into dock, magnetic tip on robot side
4. Alternative: magnetic ring around USB-C connector (MagSafe-like)

### Commercial Options
- **USB-C Magnetic Adapter** (search "magnetic USB-C adapter 3-pack") — $6-10
- **MagSafe to USB-C converter** — works with Apple's magnetic ecosystem

---

## Why Slow Charging Is Acceptable

1. **Robot is docked for long periods** — overnight, during work, etc.
2. **No urgency** — unlike a phone, it doesn't need 0→100% in 30 min
3. **Simple architecture** — no PD negotiation, no active circuits in splitter
4. **Proven pattern** — Roomba docks and charges slowly over hours

### Charge Time Estimates
| Battery | Capacity | Charge Rate | Time |
|---------|----------|-------------|------|
| Power bank | 10000mAh | ~5W (splitter) | ~20 hours (!) — too slow |
| LiPo (motors) | 4000mAh | ~5W (TP4056 @ 1A) | ~4-5 hours |

**NOTE:** Power bank charge time through passive splitter is terrible (~20 hours). Consider:
- Power bank charges via its own USB-C port (separate, not through splitter)
- Only LiPo goes through splitter

### Revised Architecture (Better)
```
Magnetic Dock
    │
    ├── USB-C → Power bank (direct, fast charge)
    └── USB-C → LiPo charger → 3.7V battery
```

This way power bank charges at full speed (18W+), only the LiPo suffers slow charge.

**Or simpler:** Just plug power bank directly to charger when needed — power bank isn't the bottleneck for v2 since it powers only the Pi (low consumption).

---

## Future Fast Charging Options

### When Needed (v3+)
1. **Active power sharing module** (IP2368-based, ~$12)
   - USB-C PD input, intelligent split
   - 5A+ charge current possible
   - Adds complexity and cost

2. **Battery swap station**
   - Two batteries, one always charging
   - Robot swaps depleted → charged in seconds
   - Requires mechanical swap mechanism (door, latch, alignment)

3. **2S LiPo (7.4V) upgrade**
   - Same physical size as 1S, double voltage
   - More efficient for motors, same runtime
   - Need 2S-capable charger

### Larger Battery Option (v2 Upgrade Path)
- **10,000mAh at 3.7V is feasible** in 1:24 scale — Vijay says there's enough room
- Current: 4,000mAh/3.7V (already purchased, use for now)
- Upgrade path: Swap to 10,000mAh if longer runs are needed
- 2S/7.4V alternative: Double voltage = more efficient for motors, same runtime in smaller package
- Upgrade note: Larger battery = longer charge time; slow charging setup can accommodate

---

## GPS Navigation (Deferred — Future)

- Indoor: GPS doesn't work, use vision/IMU/floor markers
- Outdoor: NEO-6M GPS module (~$12)
- Home base GPS coordinate stored
- Shortest path calculation
- Path learning over time

**Not a v2 priority** — focus on getting robot driving first.

---

## Implementation Tasks

### Charging System (v2)
- [ ] Source magnetic USB-C adapter pair
- [ ] Source 2-way USB-C splitter (or use power bank direct + LiPo charger)
- [ ] Mount magnet on robot chassis
- [ ] Build/buy dock platform
- [ ] Test alignment and charging
- [ ] Verify LiPo charges while robot is parked

### Safety
- [ ] LiPo charging protection (TP4056 has basic protection)
- [ ] No overcharge — charger board handles this
- [ ] Thermal monitoring if fast charging later

---

## Old Research (Superseded)

The original autonomous-charging-research.md (April 1) covered:
- Qi wireless charging options
- 2S LiPo architecture
- GPS navigation ideas

Much of that was conceptual. This doc reflects **actual decisions made for v2**.

---

## Reference Links

- TP4056 module: ~$0.50-2 (Amazon, AliExpress)
- IP2368 fast charger: ~$10-15 (AliExpress)
- Magnetic USB-C adapter: ~$6-10 (Amazon)
- USB-C 2-way splitter: ~$8-12 (Amazon)
- Neodymium magnets: ~$5-10 for a set (Amazon)