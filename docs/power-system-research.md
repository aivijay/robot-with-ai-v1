# Robot v2 Power System — Single Battery Architecture

> **Status:** Research complete — needs parts sourcing  
> **Last Updated:** 2026-04-06

---

## Problem Statement

v1 uses two separate batteries:
- **Power bank** (~200g) → Pi Zero
- **4000mAh LiPo** (~50g) → motors

This is heavy and awkward for a small 1:24 crawler. Need to consolidate to ONE lightweight battery while keeping Pi power stable during motor load spikes.

---

## Solution: Single 3.7V LiPo Architecture

```
┌──────────────────────────────────────────────────┐
│              3.7V LiPo (4000mAh)                  │
│                        │                         │
│          ┌─────────────┼─────────────┐          │
│          │             │             │          │
│          ▼             ▼             ▼          │
│    ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│    │  Motors  │  │   Buck   │  │ Capacitor│   │
│    │  (direct │  │ Converter│  │  Buffer  │   │
│    │ via FETs)│  │   5V/3A  │  │ 1000µF   │   │
│    └──────────┘  └────┬─────┘  └──────────┘   │
│                       │                         │
│                       ▼                         │
│                 ┌──────────┐                   │
│                 │   Pi     │                    │
│                 │ Zero 2W │                    │
│                 └──────────┘                   │
└──────────────────────────────────────────────────┘
```

**Why this works:**
- Motors draw directly from battery — big current spikes stay on that rail
- Buck converter isolates Pi from motor noise
- Capacitor near Pi buffers any transient dips during sudden motor load
- Both systems share the same battery but are electrically separated at the converter

---

## Components Required

### 1. Battery

**Option A: Budget**
| Item | Price | Weight | Specs |
|------|-------|--------|-------|
| Generic 4000mAh 3.7V LiPo (JST PH2.0) | ~$12-15 | ~50g | 1C charge, 25C discharge — **LIMITED** |
| Turnigy 1000mAh 3S (if upgrading later) | ~$12 | ~80g | 25C discharge |

**Option B: Recommended**
| Item | Price | Weight | Specs |
|------|-------|--------|-------|
| GNB 1300mAh 3.7V LiPo (HV plug) | ~$18-22 | ~35g | 80C discharge, 5C charge |
| CNHL 2200mAh 3.7V LiPo | ~$20 | ~60g | 90C discharge |

**Option C: High Performance**
| Item | Price | Weight | Specs |
|------|-------|--------|-------|
| CNHL 4000mAh 3.7V LiPo | ~$30 | ~95g | 90C discharge |

**Selection rationale:** The 4000mAh gives plenty of run time (3-4 hours idle, 60-90 min motors) while keeping weight reasonable. The "budget" generic 4000mAh will work but its low discharge rating (25C) means it can't deliver current for high motor loads sustainably. Get at least 60C+ rated battery.

### 2. Buck Converter

**The critical piece — bad buck = Pi restarts**

| Item | Price | Quality | Notes |
|------|-------|---------|-------|
| MT3608 Mini DC-DC | ~$0.50 | ⚠️ Poor | Cheap, high ripple, can glitch Pi |
| LM2596s ADJ Module | ~$2-3 | ✅ OK | Adjustable, decent regulation, 2A max |
| RT8293H Buck Module | ~$4-6 | ✅✅ Great | 3A, low ripple, built for Pi projects |
| Pololu 5V Step-Down (D24V10F5) | ~$10 | ✅✅✅ Excellent | Ultra-low ripple, 3.5-36V in, 1A out, Pololu reputation |

**Recommendation:** The RT8293H module is the sweet spot — cheap enough to risk, good enough to work reliably. The Pololu is overkill for cost but if you want "just works" with zero hassle, it's solid.

**Critical specs needed:**
- Input: 3.7V-5V (our single LiPo)
- Output: 5V / 2-3A minimum
- Low ripple (< 100mV preferred, < 50mV ideal)

### 3. Capacitor

| Item | Price | Specs |
|------|-------|-------|
| Electrolytic 1000µF 10V | ~$0.50 | 105°C rated, low ESR preferred |
| Capacitor kit (assorted) | ~$8 | Has various values for future projects |

**Mounting:** Solder directly to Pi's 5V/GND test points or USB-C power lines. Place as close to Pi as possible.

### 4. Power Switch

| Item | Price | Notes |
|------|-------|-------|
| Breadboard power switch module | ~$1 | Simple slide switch + USB connectors |
| Rocker switch (6A) + panel mount | ~$2 | Cleaner install, recommended |

**Wiring note:** Switch should cut power to **motors only** — Pi should stay powered for safe shutdown. Or use a 2-circuit switch that cuts both motor and Pi power.

### 5. Wiring

| Item | Price | Notes |
|------|-------|-------|
| 22AWG silicone wire (various) | ~$8 | Flexible, heat resistant, good for robot |
| 26AWG silicone wire | ~$6 | For signal lines, lighter |
| JST PH2.0 connectors | ~$2 | For battery connection |
| 3.5mm bullet connectors | ~$3 | For motor connections (if needed) |

**Wire gauge guide:**
- Motor leads: 18-22AWG depending on current
- Pi power: 22-24AWG sufficient
- Signal lines (GPIO): 26AWG fine

---

## Power Budget

| Component | Current Draw | Notes |
|-----------|-------------|-------|
| Pi Zero 2W (idle) | ~250mA @ 5V | 1.25W |
| Pi Zero 2W (camera + WiFi) | ~500mA @ 5V | 2.5W |
| Motors (normal load) | ~500mA-1A @ 3.7V | Variable |
| Motors (stall) | ~3-5A @ 3.7V | Will sag battery |

**Total estimated:** ~4-6W average during operation

**Battery life (4000mAh @ 3.7V):**
- Pi only: ~20+ hours
- Motors only: ~2-3 hours continuous
- Combined (typical): ~1.5-2 hours

---

## Safety Notes

⚠️ **LiPo safety:**
- Use a LiPo bag when charging
- Don't discharge below 3.0V per cell
- Don't puncture battery
- Watch for swelling — dispose safely

⚠️ **Motor stall current:**
- If robot gets stuck and wheels lock, motor draws stall current (~3-5A)
- This can sag battery voltage and reset Pi if capacitor isn't big enough
- Consider adding motor fuse (2A polyfuse) or current limiting in software

⚠️ **Power path sequencing:**
- Battery → Buck → Pi (soft start via converter)
- Motor → direct from battery (no soft start, immediate power)
- Capacitor on Pi rail absorbs motor transients

---

## Wiring Diagram

```
BATTERY (3.7V LiPo, JST PH2.0)
    │
    ├──[Red/Black 18AWG]────────────────────┐
    │                                        │
    │    ┌─────────────────────────────┐     │
    │    │   BUCK CONVERTER (5V/3A)    │     │
    │    │   Input: 3.7-5V             │     │
    │    │   Output: 5V ───────────────┼─────┤
    │    └─────────────────────────────┘     │  │
    │                                        │  │ 22AWG
    │                                        │  │
    │    ┌─────────────────────────────┐     │  │
    │    │   ELECTROLYTIC CAPACITOR   │     │  │
    │    │   1000µF 10V (polarized!)  │◄────┘  │
    │    │   + to 5V line             │        │
    │    │   - to GND                 │        │
    │    └─────────────────────────────┘        │
    │                                             │
    │    ┌─────────────────────────────┐         │
    │    │   USB-C Cable to Pi Zero   │◄────────┘
    │    └─────────────────────────────┘
    │
    │
    ├──[Red/Black 18AWG]──────────────────────────────┐
    │                                                 │
    │    ┌─────────────────────────────┐              │
    │    │   TB6612FNG MOTOR DRIVER   │              │
    │    │   VM: battery+             │◄─────────────┘
    │    │   GND: battery-             │
    │    │                             │
    │    │   A01, A02 ──► Motor L      │
    │    │   B01, B02 ──► Motor R     │
    │    │   PWMA,AIN1,AIN2 ◄── GPIO  │
    │    │   PWMB,BIN1,BIN2 ◄── GPIO  │
    │    │   STBY ◄── GPIO            │
    │    └─────────────────────────────┘
    │
    └──[Red/Black to]───────────────────────────────
         STEERING SERVO
         (if separate power needed)
```

---

## Module Shopping List

### Minimum Viable (~$35-40)
| Item | Price | Link (approx) |
|------|-------|---------------|
| CNHL 4000mAh 3.7V LiPo (90C) | ~$30 | Amazon B08F4F8JZH |
| RT8293H Buck Module | ~$4 | Amazon B07ripL3CN |
| 1000µF Electrolytic Cap | ~$1 | Amazon |
| JST PH2.0 connector | ~$2 | Amazon |
| 18AWG wire (silicon) | ~$8 | Amazon B073RBGM3Q |
| **TOTAL** | **~$45** | |

### Recommended (~$50-55)
| Item | Price | Link (approx) |
|------|-------|---------------|
| CNHL 4000mAh 3.7V LiPo (90C) | ~$30 | Amazon |
| Pololu 5V Step-Down D24V10F5 | ~$10 | Pololu.com |
| 1000µF Capacitor | ~$1 | Amazon |
| Rocker switch + mount | ~$3 | Amazon |
| JST PH2.0 + wire kit | ~$8 | Amazon |
| **TOTAL** | **~$52** | |

### Premium (~$65)
| Item | Price | Link (approx) |
|------|-------|---------------|
| GNB 1300mAh HV LiPo (80C) × 2 | ~$36 | getfpv.com |
| Pololu 5V/3A Regulator | ~$10 | Pololu.com |
| Premium wiring kit | ~$15 | Amazon |
| **TOTAL** | **~$61** | (lighter overall) |

---

## Runtime Expectations

With 4000mAh battery at 3.7V (nominal):

| Mode | Current | Runtime |
|------|---------|---------|
| Pi idle only | ~250mA @ 5V | ~16 hours |
| Pi + camera + WiFi | ~500mA @ 5V | ~8 hours |
| Motors (light load) | ~0.5A @ 3.7V | ~8 hours |
| Motors (medium load) | ~1A @ 3.7V | ~4 hours |
| **Combined typical** | **~1.5A @ 3.7V** | **~2.5 hours** |
| Motors + Pi (heavy) | ~2A @ 3.7V | ~2 hours |

With 2000mAh battery: halve the above  
With 1300mAh battery: ~40% of above

---

## Open Questions / To Verify

1. **Steering servo power:** Does VEVOR servo need 5V or 6V? Need to check if it can run from 3.7V or needs separate regulator
2. **Motor stall current:** Actual stall amps when wheels locked — may need to add polyfuse protection
3. **Battery discharge cutoff:** Add voltage monitoring to auto-dock before battery gets too low
4. **Charging:** USB LiPo charger (balanced) needed — ~$10-15

---

## Related Documents

- `v2-build-checklist.md` — Overall build plan
- `autonomous-charging-research.md` — Charging dock ideas (v2 feature)
- `rc-crawler-research.md` — Chassis details
