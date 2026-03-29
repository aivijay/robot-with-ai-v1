# Raspberry Pi Zero 2 W — AI Robot Feasibility Research

**Project:** robot-with-ai-v1  
**Research Date:** 2026-03-28  
**Hardware Context:** Raspberry Pi Zero 2 W (512MB RAM, 1GHz quad-core ARM Cortex-A53) vs Raspberry Pi 4 (up to 8GB RAM, 1.5GHz quad-core Cortex-A72)

---

## 1. Feasibility Analysis

### Can Pi Zero 2 W Run Ollama + LLaVA?

**Short answer: No, not practically.**

LLaVA (Large Language and Vision Assistant) requires:
- **LLaVA 1.5 7B params:** ~7B parameters × 2 bytes (FP16) = **14GB+** just for weights
- Even quantized to Q4: **~4GB**
- Runtime overhead (context, activations, KV cache): **1–2GB+**

The Zero 2 W has **512MB total RAM**. The OS (Raspberry Pi OS Lite) consumes ~150–200MB at idle. That leaves **~300MB for everything else** — not nearly enough for any vision LLM.

**What about smaller vision models?**

| Model | Size (FP16) | Size (Q4) | Min RAM Needed | Zero 2 W Viable? |
|-------|-------------|-----------|----------------|-------------------|
| LLaVA 1.5 7B | ~14GB | ~4GB | ~5GB | ❌ No |
| Phi-3.5 Vision 4B | ~8GB | ~2.5GB | ~3GB | ❌ No |
| Qwen2-VL 2B | ~4GB | ~1.2GB | ~1.5GB | ❌ No |
| Moondream 1.8B | ~3.6GB | ~1GB | ~1.3GB | ❌ No (barely) |
| MobileCLIP (ViT-L) | ~220MB | 220MB | ~400MB | ⚠️ Borderline |
| MobileNetV4-Small | ~10MB | 10MB | ~50MB | ✅ Yes |

**Phi-3 Vision** — Microsoft's Phi-3.5 Vision is 4B parameters. Even Q4 quantized (~2.5GB), it exceeds the Zero 2 W's RAM by ~5×.

**Moondream 1.8B** — An open-source small vision model. FP16 ~3.6GB. Q4 ~1GB. But the 512MB constraint with OS overhead makes even the quantized version very tight — you'd have ~100–150MB for the running process, which is not enough for activations and input processing.

### RAM Requirements — Real Numbers

- **Zero 2 W total RAM:** 512MB LPDDR2
- **OS overhead (Pi OS Lite + ssh + basics):** ~150–200MB
- **Available for ML:** ~300MB
- **MobileNetV4 inference:** ~50–100MB peak
- **Full vision LLM inference:** 1–4GB minimum

**Conclusion:** Vision LLMs (LLaVA, Phi-3 Vision, Qwen2-VL) are not feasible on Zero 2 W alone.

---

## 2. Performance Expectations

### Pi Zero 2 W Benchmark Numbers

| Workload | Performance | Notes |
|----------|-------------|-------|
| CPU (1GHz Cortex-A53) | ~1–2 GFLOPS | Very limited compute |
| MobileNetV3-Small @ 224×224 | **~15–25 FPS** | Image classification |
| MobileNetV4-Small @ 224×224 | **~10–20 FPS** | Image classification |
| MobileCLIP-Score @ 224×224 | **~5–10 FPS** | Zero-shot classification |
| YOLOv8n (640×640) | **~0.3–0.5 FPS** | Object detection, very slow |
| Depth Anything (mobile) | **~0.2–0.4 FPS** | Monocular depth |
| Raspberry Pi Camera (8MP) | 1080p30 / 720p60 capture | Sensor spec, not inference |

### Pi 4 Comparison (for reference)

| Model | Zero 2 W | Pi 4 (4GB) | Speedup |
|-------|----------|------------|---------|
| MobileNetV3 | 15–25 FPS | 80–120 FPS | ~5–6× |
| YOLOv8n | 0.3–0.5 FPS | 2–5 FPS | ~6–10× |
| Ollama + llava:latest | N/A (won't fit) | 0.1–0.3 FPS | — |

### Realistic Use Cases on Zero 2 W

**✅ Viable:**
- Simple color-based blob detection
- Line following (classic robotics)
- Basic motion detection
- MobileNetV3-based object classification (limited categories)
- Edge detection / obstacle detection via classical CV
- **Motor control loop** (trivial compute, very feasible)

**⚠️ Stretch (勉强):**
- Tiny YOLO (320×320) for 3–5 object classes at <1 FPS — barely useful for navigation
- MobileCLIP for zero-shot classification — 5–10 FPS but high RAM pressure

**❌ Not viable:**
- Open-set object detection (LLaVA, CogVLM, etc.)
- Scene understanding / natural language navigation commands
- Real-time obstacle classification with broad categories
- Any vision LLM

---

## 3. Optimizations (If Attempting Zero 2 W)

### Model Quantization

| Quantization | Size Reduction | Quality Loss | Notes |
|--------------|----------------|--------------|-------|
| FP32 → FP16 | 2× | Minimal | Halves RAM, halves compute |
| FP16 → INT8 | 2× | Low-Medium | Requires calibration |
| FP16 → Q4_K_M | ~4× | Medium | Best quality/size ratio |
| FP16 → Q2_K | ~6× | High | Only if quality tolerance is high |

**Note:** Even with Q4 quantization, most vision LLMs need 1–4GB. The Zero 2 W's 512MB is a hard ceiling that quantization alone cannot solve.

### Smaller Models That Fit in 512MB

**Vision models that actually fit in 512MB total:**

1. **MobileNetV4-Small** (~10MB) — Image classification, ~15 FPS
2. **EfficientNet-Lite0** (~15MB) — Image classification, ~10 FPS
3. **YOLOv8n** (~6MB) — Object detection at 320×320, ~1–2 FPS
4. **Depth Anything (mobile variant)** (~100MB) — Monocular depth estimation, slow
5. **MobileCLIP** (~220MB) — Zero-shot image classification, 5–10 FPS
6. **RegNet** variants — Various sizes, efficient architectures

**TFLite / ONNX Runtime:** Use TensorFlow Lite or ONNX Runtime (with GPU delegate if possible) for inference. ONNX Runtime on ARM can use the NEON SIMD unit for acceleration.

### Streaming / Chunking Approaches

- **Frame subsampling:** Run inference every 5–10 frames instead of every frame
- **ROI cropping:** Only analyze center region at full resolution
- **Hierarchical detection:** Use fast small model → only run heavy model on detected ROIs
- **Async pipeline:** Capture frame → queue → return immediately → process in background

### Alternative Vision Models

| Model | Size | FPS (Zero 2 W) | Use Case | Fit? |
|-------|------|----------------|----------|------|
| MobileNetV3-Large | 20MB | 10–15 | Classification | ✅ |
| YOLOv8n (320px) | 6MB | 1–2 | Detection | ✅ |
| YOLOv10n | 5MB | 1–3 | Detection, more efficient | ✅ |
| Depth Anything (mobile) | ~100MB | 0.2–0.5 | Depth | ⚠️ Tight |
| FastSAM-tiny | ~30MB | 0.5–1 | Segmentation | ⚠️ Tight |
| MobileCLIP-Score | ~220MB | 5–8 | Zero-shot class | ⚠️ Tight |

---

## 4. Alternative Approaches for Zero 2 W

### Option A: Zero 2 W as Pure Controller (Recommended)

**Architecture:**
```
[Camera] → [Zero 2 W] → [Serial/UART] → [Motor Driver] → [Motors]
                ↓
          [WiFi/Ethernet]
                ↓
    [Pi 4 / Laptop / Phone] = AI Brain
```

- Zero 2 W handles: camera capture, motor PWM control, sensor reading, real-time loop
- Pi 4 or other device handles: vision inference, decision making, path planning
- Communication: REST API over WiFi, WebSocket, or raw TCP socket
- **Latency:** ~50–100ms round-trip on local network (acceptable for slow robots)

**Pros:** Zero 2 W stays within its comfort zone; full AI capability available  
**Cons:** Requires external device; not fully autonomous

### Option B: Edge Computing Pattern (Zero 2 W + Phone/Laptop)

- Robot streams compressed video to a nearby phone/laptop
- Phone runs vision model, sends back navigation commands
- Similar to Option A but with mobile device as brain

**Pros:** Zero compute requirement on robot  
**Cons:** Tethered to phone proximity; latency varies

### Option C: Hybrid Approach (Most Practical)

**Divide vision tasks by complexity:**

| Task | Where It Runs | Model |
|------|--------------|-------|
| Frame capture & pre-processing | Zero 2 W | — |
| Obstacle proximity detection | Zero 2 W | Ultrasound/IR sensors |
| Simple color blob detection | Zero 2 W | OpenCV |
| Object classification (limited) | Zero 2 W | MobileNetV3 |
| Open-set scene understanding | Pi 4 | LLaVA/Ollama |
| Navigation planning | Pi 4 | Custom logic |

This way, the Zero 2 W handles time-critical reactive behaviors locally, while complex reasoning is offloaded.

### Option D: Mistral 7B / Ollama on Pi 4 Only

If you want a fully self-contained robot, **just use the Pi 4**. It's not close.

| | Zero 2 W | Pi 4 (4GB+) |
|-|----------|-------------|
| Vision LLM | ❌ | ✅ Ollama + llava |
| Object detection | ⚠️ YOLO at <1 FPS | ✅ YOLO at 5+ FPS |
| Depth estimation | ⚠️ Slow/borderline | ✅ Real-time |
| Motor control | ✅ | ✅ |
| Power draw | ~0.5–1W idle | ~2–5W idle |
| Cost | $15–25 | $55–80 (board only) |

---

## 5. Recommendations

### Is Zero 2 W Viable?

**For a fully autonomous AI robot with vision LLMs: ❌ NO**

The 512MB RAM is a hard brick wall. No quantization trick or model compression makes a vision LLM fit in 512MB with OS overhead. Even Moondream 1.8B at Q4 (~1GB) is double available memory.

**For a reactive robot with simple vision: ✅ YES**

If the robot only needs:
- Line following
- Obstacle avoidance (using sensors, not vision)
- Simple color-based navigation
- MobileNet classification of a few specific objects

...then Zero 2 W is perfectly capable and very power-efficient.

### Use Cases by Hardware Choice

| Use Case | Hardware | Notes |
|----------|----------|-------|
| "Follow the red ball" | Zero 2 W | Color tracking via OpenCV |
| "Navigate to the kitchen" | Pi 4 | Vision + language |
| "Avoid obstacles" | Zero 2 W + ultrasound | Sensor-based, no vision needed |
| "Detect faces/people" | Zero 2 W | MobileNet face detection, ~5 FPS |
| "Describe what you see" | Pi 4 | LLaVA required |
| "Learn new objects interactively" | Pi 4 | In-context learning needed |
| "Autonomous room mapping" | Pi 4 | Depth + SLAM |

### Specific Recommendation for Vijay

**If you want a low-cost, low-power, fully autonomous robot:**

→ Use **Pi 4 (4GB)** as the main computer + a **Pi Zero 2 W as a peripheral controller**

The Pi 4 runs Ollama/LLaVA for AI, the Zero 2 W handles time-critical motor control and sensor reading off the main CPU's GPIO bus.

**If you want the cheapest possible robot that can do AI vision:**

→ Use **Zero 2 W + WiFi offload to your laptop/phone**. Accept that it's not fully autonomous.

**If you want to build right now with what you have:**

→ **Pi 4 is the clear choice.** The Zero 2 W can still be used for motor control only, running as a headless controller via UART/I2C from the Pi 4.

### Model Recommendations (if using Zero 2 W for vision)

1. **Object Detection:** YOLOv10n (nano) or YOLOv8n at 320×320 — ~1–3 FPS, ~5MB
2. **Classification:** MobileNetV3-Large — ~10–15 FPS, ~20MB
3. **Depth:** Depth Anything Mobile — only if you accept 0.2–0.5 FPS

---

## 6. Cost Breakdown

### Zero 2 W Build

| Component | Price (USD) | Notes |
|-----------|-------------|-------|
| Raspberry Pi Zero 2 W | $15–25 | 512MB, no WiFi (Zero 2 W has WiFi) |
| microSD Card (32GB) | $8–12 | Class 10, for OS |
| Camera Module 3 (8MP) | $10–15 | Or use existing camera |
| Motor Driver (L298N or DRV8833) | $3–8 | Dual H-bridge |
| Motors (2× TT motors) | $5–10 | Gear motors with wheels |
| Power Bank (5V 2A) | $10–20 | Or 3× Li-ion + holder |
| Chassis/Frame | $5–15 | Or 3D print |
| Wires, headers, breadboard | $5–10 | |
| **Total** | **$56–100** | |

### Pi 4 Build (for comparison)

| Component | Price (USD) | Notes |
|-----------|-------------|-------|
| Raspberry Pi 4 (4GB) | $55–80 | |
| microSD Card (64GB) | $10–15 | |
| Camera Module 3 | $10–15 | |
| Motor Driver | $3–8 | |
| Motors + Wheels | $5–10 | |
| Power Supply (USB-C 3A) | $10–15 | Official Pi 4 PSU recommended |
| Chassis | $5–15 | |
| **Total** | **$98–158** | |

**Delta:** ~$40–60 more for Pi 4, but you get a fully functional AI robot brain.

---

## Summary

| Question | Answer |
|----------|--------|
| Can Zero 2 W run Ollama + LLaVA? | ❌ No — 512MB is 8× too small |
| Can Zero 2 W run any vision AI? | ✅ Yes — MobileNet, YOLO, simple classifiers |
| Can Zero 2 W do navigation decisions? | ⚠️ Simple ones only (line follow, avoid-obstacle) |
| Should Vijay use Zero 2 W or Pi 4? | **Pi 4** for AI vision; Zero 2 W as motor controller |
| Best Zero 2 W vision model? | YOLOv10n or MobileNetV3 |
| Fully autonomous AI robot possible on Zero 2 W? | ❌ No — needs offboard AI compute |

**Bottom line:** The Zero 2 W is an excellent, cheap, low-power motor controller and camera capture device. For a genuinely intelligent robot that can understand its environment via AI vision, you'll need the Pi 4 (or an offboard device). The good news: you can use both together, giving you a capable robot at moderate cost.
