# Depth Sensing Research — Robot v2

*Updated: 2026-04-05*

## Overview

Goal: Add depth perception so the robot can navigate without hitting obstacles. Current brightness-based floor detection is 2D and limited. We need to perceive 3D space and measure distances to objects.

---

## Option 1: Monocular Depth Estimation (ML-Based)

### How It Works
- Single RGB camera image → neural network → depth map
- Network learns visual cues (perspective, size, texture gradients) to estimate depth
- Outputs relative depth (not absolute meters unless calibrated)

### State of the Art (2025-2026)
**MiDaS v3.0** (Intel ISL) — current best-in-class for monocular depth
- Multiple model sizes: Large (384px), Base, Small, Tiny
- Works zero-shot across datasets
- Relative depth output (relative distances, not absolute unless calibrated)

**Smaller variants for edge:**
- `midas_v21_small_256` — optimized for mobile/edge, ~5-10 FPS on Pi Zero possible
- `dpt_swin2_tiny_256` — SwinTransformer-based, better accuracy but heavier

### Quantized Models Available
| Model | Format | Size | Pi Zero Viability |
|-------|--------|------|-------------------|
| MiDaS v2.1 Small | TFLite INT8 | ~25MB | ✅ Marginal (5-10 FPS) |
| MiDaS v2.1 Small | ONNX Quantized | ~25MB | ⚠️ Needs benchmarking |
| MiDaS v3 Small | PyTorch | ~50MB | ❌ Too heavy |

### Pros
- Works with existing camera (no extra hardware)
- No baseline calibration needed
- Active research area, improving rapidly

### Cons
- **No absolute scale** — only relative depth (object A is closer than B)
- Slow on Pi Zero (~0.5-2 FPS on full model)
- Quantized models still heavy for real-time navigation
- Needs calibration to convert to real-world meters

### Implementation Reality
```python
# Pseudocode for MiDaS on Pi Zero
import tflite_runtime.interpreter as tflite

interpreter = tflite.Interpreter('midas_v21_small_256.tflite')
interpreter.allocate_tensors()

# For each camera frame:
input_data = preprocess(frame, 256, 256)  # resize
interpreter.set_tensor(input_details[0]['index'], input_data)
interpreter.invoke()
depth_map = interpreter.get_tensor(output_details[0]['index'])
```

**Realistic FPS on Pi Zero:** 0.5-2 FPS with small quantized model
**Verdict:** Too slow for real-time robot navigation. Better for mapping or infrequent checks.

---

## Option 2: Time of Flight (ToF) Camera

### How It Works
- Emits infrared light pulse
- Measures time for light to bounce back
- Outputs distance per pixel (like LiDAR but short range)

### Arducam VL53L5CX
- **Resolution:** 8×8 pixels
- **Range:** 0.4m - 4m
- **Interface:** I2C (SDA/SCL)
- **Price:** ~$40-50
- **Size:** ~25mm × 25mm
- **Power:** Low (~100mW)

### Pros
- Direct depth measurement (absolute distance in meters)
- Real-time (30+ FPS)
- Works indoors
- I2C = only 4 wires to Pi
- Low power, small size

### Cons
- 8×8 is very low resolution (basically a heat map)
- Can't detect small obstacles
- Limited to 4m range
- No color/texture info

### What It Can Do
- "Something at 1.5m ahead" — good enough to trigger turn
- "Closest obstacle in 8 regions" — works for navigation
- Not good enough for detailed mapping or small object detection

### Verdict: **RECOMMENDED for v2**
Simple, reliable, real-time distance data for obstacle avoidance. Not detailed 3D, but enough for "stop before hitting."

### Workflow
```python
import board
import busio
import adafruit_vl53l5cx

i2c = busio.I2C(board.SCL, board.SDA)
sensor = adafruit_vl53l5cx.VL53L5CX(i2c)
sensor.start_ranging()

while True:
    distance = sensor.distance  # 8x8 array in mm
    if distance.min() < 500:  # 50cm
        robot.stop()
```

---

## Option 3: Stereo Camera

### How It Works
- Two cameras spaced apart (human-eye baseline ~6-8cm)
- Compare left/right images → disparity map → depth map
- Triangulation gives absolute depth

### Options
| Product | Price | Cameras | Pi Zero Support |
|---------|-------|---------|-----------------|
| Arducam Stereo | ~$50-70 | 2× 5MP synced | ⚠️ Hard (heavy processing) |
| StereoPi | ~$60-80 | Your own | ⚠️ Needs CM4 (heavy) |
| Dual Pi v2 (DIY) | ~$40-60 | 2× 8MP | ❌ Too heavy |

### Reality on Pi Zero
- Stereo depth calculation is **CPU intensive**
- Even with optimized OpenCV, real-time stereo at useful resolution is **too slow**
- Pi 3/4 minimum for stereo processing
- **StereoPi with Compute Module 4** could work but adds cost/complexity

### Verdict: **Not for v2** — deferred to v3 if Pi 5 or CM4 used

---

## Option 4: Structured Light (Kinect-style)

### How It Works
- Projects known pattern (dots/lines) onto scene
- Camera sees pattern deformation → calculates depth
- Like how iPhone FaceID works

### Intel RealSense D400 Series
- **Price:** $80-150
- **Power:** 2.5W — too much for small mobile robot
- **Not recommended** for battery-powered mobile

---

## Option 5: Ultrasonic/Radar (Simple Distance)

### How It Works
- Emit ultrasonic pulse → measure time to return
- Simple distance to nearest obstacle

### HC-SR04 Ultrasonic Sensor
- **Price:** ~$2-3
- **Range:** 2cm - 4m
- **Interface:** GPIO (trigger + echo)
- **Accuracy:** ~3mm (but slow refresh)

### Multiple Mounting Options
```
Front-facing: 1-2 sensors for forward obstacle detection
Panoramic: servo-mounted sensor sweeps 180°
Corner: 3 sensors at 60° intervals
```

### Pros
- Dirt cheap ($2-3 each)
- Simple wiring (GPIO)
- Provides absolute distance in cm
- Fast refresh rate

### Cons
- Limited to ~4m max
- Small objects hard to detect
- Multiple sensors = more GPIO pins needed
- Can't build full depth map (only point measurements)

### Verdict: **Good supplement for v2** — cheap and reliable for specific directions

---

## Recommended Architecture for v2

### Layered Approach (Best Value)

```
┌─────────────────────────────────────────┐
│  PRIMARY: Arducam VL53L5CX ToF (I2C)    │
│  - 8x8 grid of distances               │
│  - Real-time obstacle detection         │
│  - Trigger: stop at <50cm, slow at <1m │
└─────────────────────────────────────────┘
         +
┌─────────────────────────────────────────┐
│  SUPPLEMENTAL: HC-SR04 Ultrasonic (×3) │
│  - Front-facing for precise forward    │
│  - Backup to ToF for edge cases        │
└─────────────────────────────────────────┘
         +
┌─────────────────────────────────────────┐
│  FUTURE: MiDaS Monocular (v3 upgrade)  │
│  - Full depth map for mapping          │
│  - Runs on Pi 5 / compute module      │
│  - Not for real-time navigation       │
└─────────────────────────────────────────┘
```

### Why This Works
1. **ToF gives real-time 8-direction obstacle data** — enough for basic navigation
2. **Ultrasonics fill gaps** — precise front-facing distance when ToF misses
3. **Monocular ML is mapping-only** — too slow for real-time, but useful for building maps post-hoc

---

## Distance Sensor Comparison

| Method | Cost | Abs Distance | Real-Time | Pi Zero | Resolution |
|--------|------|-------------|-----------|---------|------------|
| ToF (VL53L5CX) | $40-50 | ✅ m | ✅ 30fps | ✅ | 8×8 |
| Ultrasonic (HC-SR04) | $2-3 | ✅ cm | ✅ 10Hz | ✅ | 1 point |
| Monocular (MiDaS) | Free | ❌ relative | ⚠️ 0.5-2fps | ⚠️ marginal | full |
| Stereo | $50-80 | ✅ m | ❌ slow | ❌ no | good |

---

## v2 Implementation Plan

### Phase 1 (v2 Build — Recommended)
1. **Add Arducam VL53L5CX ToF** — $40-50
   - I2C wiring to Pi Zero
   - Read 8×8 distance grid
   - Integrate with reflex layer: turn away if closest < 50cm

2. **Add 1-2 HC-SR04 Ultrasonics** — $2-6
   - Front-facing, detects precise front obstacle
   - Complements ToF
   - Both sensors used = redundant safety

### Phase 2 (v3 — If Needed)
1. **Upgrade to stereo camera** — Pi 5 or Compute Module 4 required
2. **Or: Full MiDaS depth map** — if running on stronger hardware

---

## Parts List (v2 Recommended)

| Item | Price | Purpose |
|------|-------|---------|
| Arducam VL53L5CX | ~$40-50 | Primary ToF depth sensor |
| HC-SR04 × 2-3 | ~$4-9 | Ultrasonic backup |
| Jumper wires | ~$2 | Wiring |

---

## Reference Links

- MiDaS: https://github.com/isl-org/MiDaS
- MiDaS TFLite Small: https://models.luxonis.com/luxonis/midas-v2-1/be09b09e-053d-4330-a0fc-0c9d16aac007
- Arducam VL53L5CX: https://www.arducam.com/laser-ranging-camera/
- HC-SR04: Amazon ~$2-3

---

## Historical Notes

Original research (2026-04-02) suggested ToF as best for Pi Zero. This update adds:
- Updated MiDaS research (v3.0 state-of-art, but still too heavy for Pi Zero)
- Quantized TFLite models available but marginal FPS
- Stereo camera confirmed too heavy for Pi Zero
- Layered approach recommended (ToF + Ultrasonics)