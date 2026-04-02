# Autonomous Charging Research — Robot with AI v1

*Created: 2026-04-01*

## Concept Overview

Add autonomous charging capability to the robot car so it can:
1. Detect low battery
2. Navigate to home base
3. Auto-dock and charge
4. Resume operation

---

## Power Architecture

### Current Setup (v1)
- **RPi Zero**: Powered by USB power bank (5V)
- **Motors**: Powered by car's 3.7V LiPo battery via TB6612FNG
- **Problem**: Two separate batteries, manually recharged

### Proposed v2 Architecture
- **Single power bank** (10000mAh USB-C) powers RPi
- **Motors** powered by car's 3.7V LiPo
- OR: Power bank also powers motors via boost converter

### Power Bank Selection
- **Target size**: ~10 x 7 x 1.5 cm
- **Capacity**: 10000mAh (realistic in this size)
- **Runtime estimate**: ~6-7 hours RPi, or 30+ min heavy motor use
- **Example**: Kuulaa 10000mAh MagSafe Power Bank
  - Dimensions: 10.4 x 6.8 x 1.45 cm
  - USB-C output, 5V
  - Digital display
  - ~$20-25

---

## Auto-Charging Strategies

### Option 1: Wired Magnetic Connector (Easiest)
- Magnetic charging cable (like MacBook magsafe)
- Car parks at base, magnets align connector
- Base has charger → battery
- **Pros**: Efficient, reliable
- **Cons**: Requires precise alignment

### Option 2: Wireless Qi Charging (Cooler)
- Qi receiver coil on car bottom
- Qi transmitter pad at home base
- Car parks on pad, coils align inductively
- **Pros**: No physical connection needed
- **Cons**: ~70-80% efficiency, alignment critical

### Qi Receiver Options

| Module | Output | Current | Size | Price |
|--------|--------|---------|------|-------|
| Adafruit Qi Receiver | 5V | 500mA | Small | $7.50 |
| JH-QS-RX-V2 | 5V | 2A (10W) | Medium | $5-10 |
| Ultra-Thin Android Qi | 5V | 500-800mA | Very thin | $5-8 |

**Recommendation**: 2A module for headroom during charging + RPi load

### Option 3: Contact Charging (Simplest)
- Two metal contacts on car bottom
- Car drives into dock, contacts touch rails
- Like Roomba's charging dock
- **Pros**: Simple, efficient
- **Cons**: Requires good alignment

---

## GPS Navigation Ideas (Future Enhancement)

### Vijay's Vision
1. **Home base has GPS coordinate**
2. **Robot knows its GPS position**
3. **Robot calculates shortest path home**
4. **Learns routes over time**
5. **Can go outside and return**

### GPS Module Options

| Module | Type | Accuracy | Cost |
|--------|------|----------|------|
| NEO-6M (GPS) | UART | ~2.5m | $10-15 |
| NEO-8M | UART | ~2.5m | $15-20 |
| RTK GPS | RTK | ~1-2cm | $100+ |

**For indoor**: GPS doesn't work well indoors. Alternative:
- **Vision-based** positioning (track landmarks)
- **IMU dead reckoning** (drifts over time)
- **Floor markers** (QR codes, lines, RFID)

**For outdoor**: GPS becomes viable
- NEO-6M is good starter module
- Requires clear sky view

### Path Planning Ideas
- **A* or Dijkstra** for shortest path
- **SLAM** (Simultaneous Localization and Mapping) for learning environment
- **Beacon-based** navigation (IR/Radio beacons at known positions)

---

## Auto-Dock Flow (Proposed)

```
1. Battery low detected (voltage threshold)
2. Get GPS of home base (stored position)
3. Calculate path to home base
4. Navigate following path
5. Detect dock (infrared sensor / camera / bump switch)
6. Align and dock (using magnets or guide rails)
7. Start charging
8. Monitor battery level
9. When full: resume autonomous operation
```

---

## Next Steps

- [ ] Finalize power bank selection
- [ ] Choose charging method (wired vs wireless)
- [ ] Design home base dock
- [ ] Research GPS modules for outdoor capability
- [ ] Test low-battery detection

---

## Research Links

- Adafruit Qi Receiver: https://www.adafruit.com/product/1901
- Qi 2A Receiver Module: https://www.wirelesschargingcoil.com/10w-fast-wireless-charging-receiver-module/
- LiPoPi (LiPo + Pi power): https://github.com/NeonHorizon/lipopi
