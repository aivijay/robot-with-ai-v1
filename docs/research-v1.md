# Robot with AI v1 - Research Project

## Overview
Build a low-cost, simple autonomous robot inspired by the YouTube video "I Gave Claude a Body" (https://www.youtube.com/watch?v=jBpQiv-ZlVM)

**Goal:** Create a smaller, affordable version of an AI-powered autonomous vehicle that can:
- Navigate and explore its environment
- Use vision for autonomous movement
- Connect to an AI brain (Claude/Ollama)
- Process depth/distance information

## Original Video Project (Reference)
The creator spent ~$1100+ on:
- Traxxas Maxx RC car ($1100)
- Raspberry Pi 5
- 16MP camera module with wide-angle lens
- 4G LTE hat
- PCA9685 servo driver board
- Apple Depth Pro ML model for depth estimation
- Custom 3D printed "crab" body

**Key Features Implemented:**
1. Servo steering control via PCA9685
2. Motor control via ESC (Electronic Speed Controller)
3. MCP server connecting Claude to hardware
4. Vision-based navigation with image prompts
5. Journey Grid (6-image collage for temporal context)
6. Voice output
7. Web-based command center/dashboard
8. Depth estimation

## Vijay's Requirements for v1
- **CHEAP** - Minimize cost
- **Simple** - Easier than the original
- **Smaller scale** - Not the massive RC car
- **Similar functions** - Core autonomous navigation and vision

## Design Constraints
1. Budget target: TBD (aim for under $100-200?)
2. Simpler mechanics than full RC car
3. Should work indoors or in controlled environments
4. AI runs locally (Ollama) not cloud

## Suggested Research Areas

### 1. Platform Options (Low-Cost Alternatives)
- **Raspberry Pi + L298N Motor Driver** - Very cheap, simple DC motors
- **ESP32-based robot** - Cheap WiFi, but limited AI processing
- **Arduino + Raspberry Pi combo** - Arduino for motors, Pi for AI
- **Cheap RC car chassis** - $20-30 on Amazon
- **Track/robot car kits** - Under $50

### 2. Vision System
- **Raspberry Pi Camera Module v2** (8MP) - ~$25
- **USB webcam** - $10-20
- **Wide-angle camera** - Needed for navigation
- **Depth sensing alternatives:**
  - Stereo camera (two cameras)
  - LIDAR (expensive, $100+)
  - Ultrasonic sensors for basic obstacle detection
  - Intel RealSense (used, ~$100)

### 3. AI/Computing
- **Local:** Ollama on Raspberry Pi 5 or laptop
- **Perception:** 
  - Ollama for image analysis
  - Depth anything model for depth estimation
  - Or simpler: just vision-based prompts

### 4. Motor Control
- **Servo-based steering** (like original) - PCA9685 + servos
- **DC motor with L298N** - Cheaper, simpler
- **ESC** - For variable speed control

### 5. Connectivity
- Local WiFi (no 4G needed for indoor/small scale)
- SSH for debugging
- Web dashboard similar to original

### 6. Power
- LiPo battery (small, 3.7V or 7.4V)
- Power bank for Raspberry Pi
- Need to power motors separately

## Suggested Minimum V1 Parts
1. Raspberry Pi 4 or 5 (~$35-80)
2. Raspberry Pi Camera v2 (~$25)
3. L298N Motor Driver (~$5)
4. Small robot car chassis with 2 DC motors (~$20-30)
5. USB WiFi adapter (if needed)
6. Power bank/batteries (~$15-20)
7. Jumper wires, breadboard (~$5)

**Estimated Total: $100-150** (vs $1100+ original)

## Open Questions
1. What budget does Vijay have in mind?
2. Indoor or outdoor use?
3. Size constraints?
4. Does Vijay have any existing hardware?
5. Single function (just drive) or multi-function?

## Next Steps
- [ ] Define budget constraints
- [ ] Determine indoor/outdoor usage
- [ ] Decide on hardware platform
- [ ] Research specific components
- [ ] Order parts

---

**Delegating to Clawe's team for detailed research:**
- Component selection with pricing
- Alternative architectures
- Software stack recommendations
- Step-by-step build guide outline
