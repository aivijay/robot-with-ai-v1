# Robot Car Setup Troubleshooting Guide

## Python/pip Issues

### pip not found
```bash
sudo apt update && sudo apt install python3-pip -y
```

### Install OpenCV
```bash
pip3 install opencv-python --break-system-packages
```

### OpenCV missing system libraries
If you get errors about missing `.so` files (libopenblas, libwebp, libopenjp2, libavcodec, etc.), install all OpenCV dependencies at once:
```bash
sudo apt install libopenblas-dev libwebp-dev libopenjp2-7 libavcodec-dev libavformat-dev libswscale-dev libjpeg-dev libtiff-dev libpng-dev -y
```

### pip install failing with "No space left on device"
The build process uses /tmp which may be small (tmpfs). Use a larger directory:
```bash
mkdir -p ~/tmp && TMPDIR=~/tmp pip3 install <package> --break-system-packages
```

### av (FFmpeg) package compilation is very slow on Pi Zero
The `av` package compiles from source and can take 20+ minutes on Pi Zero. Be patient — it's not hung, just slow.

If you want to skip video features and avoid the long build:
```bash
TMPDIR=~/tmp pip3 install picamera2 --break-system-packages --no-deps
pip3 install picamera2 --break-system-packages  # basic without av
```

## Camera Issues

### Camera not detected
```bash
# Enable camera
sudo raspi-config
# Navigate: Interface Options → Camera → Enable
reboot

# Or check if already enabled
vcgencmd get_camera
```

### Dark images from camera
- Enable auto-exposure in code
- Or use `rpicam-awt` for better default settings

## Motor Driver Issues

### TB6612FNG Getting Hot
- **CAUSE**: Reversed VCC and GND will fry the chip!
- **FIX**: NEVER connect 3.3V/GND backwards. The chip will get hot and die immediately.
- **SOLUTION**: Replace with a new TB6612FNG board

### Motor not spinning despite correct signals
- Check ALL ground connections (logic GND + motor GND must both be connected)
- Verify motor leads are on AO1/AO2 (not some other pins)
- Some boards label pins differently - check your specific board's pinout
- Try swapping to a different motor driver board if available

### Motor runs intermittently (randomly starts/stops)
- **CAUSE**: Loose connection or bad solder joint
- **FIX**: Check solder joints on motor leads, try re-soldering
- **TEST**: Hold wires steady while running - if it works when held, it's loose

### GPIO signals correct but AOUT shows 0V
- Motor driver chip may be damaged
- Try a different TB6612FNG board

## Network Issues

### WiFi soft-blocked
```bash
sudo rfkill unblock wifi
```

### wpa_supplicant issues
- Don't use process substitution (`/etc/wpa_supplicant/wlan0.conf < <(...)`)
- Create the config file directly:
```bash
cat > /etc/wpa_supplicant/wlan0.conf << 'EOF'
ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
update_config=1
country=US
network={
    ssid="your-ssid"
    psk="your-password"
}
EOF
```

### Static IP not persisting
- Edit `/etc/dhcpcd.conf` directly
- Add:
```
interface wlan0
    static ip_address=192.168.1.50/24
    static routers=192.168.1.1
    static domain_name_servers=192.168.1.1
```

### Create WiFi systemd service for persistence
```bash
sudo nano /etc/systemd/system/wifi-manager.service
```
Content:
```
[Unit]
Description=WiFi Manager
After=network.target

[Service]
Type=oneshot
ExecStart=/sbin/wpa_supplicant -c /etc/wpa_supplicant/wlan0.conf -i wlan0
RemainAfterExit=yes

[Install]
WantedBy=multi-user.target
```
Enable:
```bash
sudo systemctl enable wifi-manager
```

## General

### Check 3.3V rail stability
If GPIO signals are unstable, disconnect all wiring and reconnect one at a time to find the shorted wire.

### Multimeter basics
- Red probe on signal pin
- Black probe on GND (use the GND near VCC, not VMOTOR GND)
- Should read ~3.3V for active GPIO HIGH signal
