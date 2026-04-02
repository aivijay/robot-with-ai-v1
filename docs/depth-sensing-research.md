# Depth Sensing Research — Robot with AI v1

*Created: 2026-04-02*

## Overview

Current robot uses 2D camera images for environment awareness (brightness-based floor detection). This limits ability to perceive 3D space and accurately measure distances to obstacles.

Goal: Add depth perception capability to improve obstacle avoidance and spatial awareness.

---

## Option 1: Depth from Single Camera (Monocular)

### Structure from Motion (SfM)
- Take multiple images from different angles
- Reconstruct 3D structure from motion
- **Pros**: Works with existing camera, no extra hardware
- **Cons**: Needs movement, computationally heavy, no real-time depth

### Depth from Focus/Defocus
- Analyze blur level to estimate distance
- Requires controllable aperture (Pi camera doesn't have adjustable aperture)
- **Pros**: Simple hardware
- **Cons**: Limited accuracy, not reliable

### Neural Network Depth Estimation (MiDaS)
- Use machine learning to estimate depth from 2D image
- Runs on Pi Zero (but slow ~1-2 fps)
- **Pros**: Works with existing camera, good accuracy
- **Cons**: Slow, needs powerful model for real-time

**Libraries**: `torch`, `transformers`, MiDaS model

---

## Option 2: Time of Flight (ToF) Camera

### How It Works
- Emits infrared light pulse
- Measures time for light to bounce back
- Calculates distance for each pixel

### Arducam ToF Camera
- **Sensor**: VL53L5CX (8x8 resolution)
- **Interface**: I2C
- **Range**: 0.4m - 4m
- **Price**: ~$40-50
- **Size**: Small (~25mm x 25mm)
- **Pros**: 
  - Real depth data directly
  - Works indoors
  - Low power
  - Easy integration (I2C)
- **Cons**: 
  - Low resolution (8x8 pixels)
  - Limited range
  - No visible light camera (just depth)

### DFRobot 8x8 ToF Sensor
- ~$20-30
- Similar spec to Arducam
- Good for obstacle detection at close range

### Recommended ToF for Pi Zero
- **Arducam ToF Camera** ($40-50)
- Connect via I2C (SDA/SCL pins)
- Can detect obstacles 0.4-4m away
- Good for knowing "something is there" but not detailed 3D

---

## Option 3: Stereo Camera

### How It Works
- Two cameras spaced apart (like human eyes)
- Compare images to calculate depth via parallax
- Creates disparity map → depth map

### Arducam Stereo Camera Kit
- Two 5MP cameras synchronized
- Includes calibration pattern
- **Price**: ~$50-70
- **Size**: Larger, needs wider mounting

### StereoPi (Dedicated)
- Stereo camera board for Raspberry Pi
- **Price**: ~$60-80 (plus cameras)
- **Pros**: 
  - Dedicated hardware for stereo processing
  - Supports Raspberry Pi compute modules
- **Cons**: 
  - Complex setup
  - Pi Zero may be too slow for real-time processing

### DIY Stereo with Two Pi Cameras
- Use two standard Pi v2 cameras
- Mount with known baseline distance (5-10cm)
- Calibrate with OpenCV
- **Pros**: Cheaper if you have cameras
- **Cons**: Complex calibration, heavy processing

### Stereo Camera on Pi Zero - Reality Check
- Stereo depth calculation is **CPU intensive**
- Pi Zero's single-core performance is limited
- Real-time stereo at decent resolution may be **too slow**
- Pi 3/4 recommended for stereo processing

---

## Option 4: Structured Light (Kinect-style)

### How It Works
- Projects known pattern (dots/lines)
- Camera sees pattern deformation
- Calculates depth from distortion

### Intel RealSense (Used)
- RealSense D400 series: ~$80-150
- Active IR projector + two cameras
- Good depth, but high power consumption
- **Too power-hungry for Pi Zero projects**

### Not recommended for mobile robots

---

## Comparison Table

| Method | Cost | Hardware | Speed | Accuracy | Pi Zero Friendly |
|--------|------|----------|-------|----------|------------------|
| Monocular (ML) | Free | Existing cam | Slow | Medium | Marginal |
| ToF Camera | $40-50 | Extra module | Fast | Good (at range) | ✅ Yes |
| Stereo Camera | $50-80 | Two cameras | Slow | Good | ⚠️ Difficult |
| RealSense | $80+ | Complex | Fast | Excellent | ❌ No (power) |

---

## Recommendation for v1

**For obstacle detection (not detailed 3D mapping):**

**Best choice: Arducam ToF Camera (~$40-50)**
- Adds real depth sensing capability
- I2C interface, easy to wire
- Can detect "obstacle at 1.5m ahead" directly
- Runs on Pi Zero without performance issues
- Low power

**Workflow:**
```
if depth < 0.5m: stop or turn
elif depth < 1.0m: slow down
else: full speed
```

---

## Future Enhancement (v2+)

### Stereo Camera Path
- Add two cameras with wider baseline
- Use StereoPi or compute module for processing
- Full 3D mapping possible
- **Wait for Pi 5 or compute module 4** for real-time performance

### Sensor Fusion
Combine multiple sensors:
- ToF for precise distance
- Camera for object classification
- IMU for orientation
- Creates robust perception system

---

## Implementation Ideas

### ToF Integration (Next Step)
1. Buy Arducam VL53L5CX ToF module
2. Wire via I2C to Pi Zero
3. Read distance data in Python
4. Integrate with drive-simple.py:
   - If obstacle < 0.5m: turn away
   - If obstacle < 1.0m: slow down

### Camera Cable Fix
- Reconnect the detached camera cable
- The cable likely just came loose from the connector
- Push firmly until it clicks into place
- Check that the golden contacts are clean

---

## Research Links

- Arducam ToF: https://blog.arducam.com/time-of-flight-camera-raspberry-pi/
- StereoPi: https://stereopi.com/
- Arducam Stereo: https://blog.arducam.com/raspberry-pi-stereo-camera-depth-mapping-arducam-tutorial/
- MiDaS Depth: https://github.com/intel-iot-devkit/MiDaS
- OpenCV Stereo: https://docs.opencv.org/4.x/dd/d53/tutorial_py_depthmap.html

---

## Testing Plan for v1

1. Fix camera cable
2. Re-test floor detection (still works after enclosure)
3. Add basic object detection (color/contrast based)
4. Test ToF sensor for distance-based reactions
5. Validate autonomous navigation in constrained environment