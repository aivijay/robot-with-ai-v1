# Robot Car Project - Memory

## Last Session (2026-03-31 ~00:45 CDT)
Vijay went to sleep. We had just gotten the camera working on Pi Zero.

## Pi Zero Setup (COMPLETED)
- WiFi: Connected, IP is now 192.168.1.50 (updated from earlier)
- SSH: Working
- Camera: rpicam-still works, captures 2592x1944 (5MP)
- rpicam-apps installed

## Hardware
- Pi Zero W
- 5MP Camera v2 (OV5647 sensor) - WORKING
- TB6612FNG motor driver (only 1 needed for 2WD)
- 2 motors: front + rear (2WD, NOT 4WD)
- 3.7V LiPo battery, Power bank

## Motor Wiring (PENDING)
- GPIO: 17/27/18 (Motor A), 22/24/23 (Motor B), GPIO 5 (STBY)
- Docs: docs/wiring-diagram-2wd.md

## Next Steps (Priority Order)
1. Wire motors to TB6612FNG
2. Test motor control with Python
3. Write autonomous driving code

## Key Insight (from multi-agent research)
Motor control should use CLASSICAL control systems (PID) NOT LLMs. LLMs think in seconds, motors need milliseconds.
Architecture: LLM as "brain" delegating to classical controllers as "reflexes"
