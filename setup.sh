#!/bin/bash
# setup.sh — First-time setup for robot-with-ai-v1
set -e

echo "=== Robot-with-AI-v1 Setup ==="
echo ""

# ── Detect what we're on ────────────────────────────────────────────────────

ON_LAPTOP=true
ON_PI=false
UNAME_M=$(uname -m)
if [[ "$UNAME_M" == *"arm"* ]] || [[ "$UNAME_M" == *"aarch64"* ]]; then
    if grep -q "Raspberry" /proc/cpuinfo 2>/dev/null || \
       [[ -f /etc/rpi-issue ]] || \
       [[ -d /sys/class/gpio/gpio22 ]]; then
        ON_PI=true
        ON_LAPTOP=false
    fi
fi

echo "Detected: $(uname -n) ($(uname -m))"
echo ""

# ── Laptop setup ────────────────────────────────────────────────────────────

setup_laptop() {
    echo "📦 Setting up LAPTOP side..."
    echo ""

    echo "  Installing Python packages..."
    pip install fastapi uvicorn requests pillow streamlit openai httpx --quiet

    echo "  Checking Ollama..."
    if command -v ollama &>/dev/null; then
        echo "  ✅ Ollama found: $(ollama --version 2>/dev/null || echo 'unknown version')"

        echo ""
        echo "  Checking vision models..."
        AVAILABLE=$(ollama list 2>/dev/null | grep -iE "llava|moondream|phi.*vision|qwen.*vl" || true)
        if [[ -n "$AVAILABLE" ]]; then
            echo "  ✅ Vision models found:"
            echo "$AVAILABLE" | sed 's/^/     /'
        else
            echo "  ⚠️  No vision models found. Install one:"
            echo ""
            echo "     # Fastest (recommended first):"
            echo "     ollama pull moondream:1.8b"
            echo ""
            echo "     # Better quality:"
            echo "     ollama pull llava:latest"
            echo "     ollama pull qwen2.5vl:3b"
        fi
    else
        echo "  ⚠️  Ollama not found. Install from: https://ollama.com"
        echo "     Then run: ollama pull moondream:1.8b"
    fi

    echo ""
    echo "  Getting laptop IP on WiFi..."
    WIFI_IP=$(ip addr show 2>/dev/null | grep "inet " | grep -v "127.0.0.1" | awk '{print $2}' | head -1 || echo "unknown")
    echo "  → Laptop IP: $WIFI_IP"
    echo "  → Use this IP when starting robot_client.py"
    echo ""

    echo "  To start the AI brain server:"
    echo "    cd $(dirname "$0")"
    echo "    python src/laptop/laptop_server.py --host 0.0.0.0 --port 8000"
    echo ""
    echo "  To start the dashboard (in another terminal):"
    echo "    streamlit run src/laptop/dashboard.py --server.port 8501"
    echo ""
    echo "  Dashboard will be at: http://\$WIFI_IP:8501"
}

# ── Robot setup (Pi Zero 2 W / Pi 3 / Pi 4) ──────────────────────────────────

setup_pi() {
    echo "🤖 Setting up ROBOT side (Raspberry Pi)..."
    echo ""

    echo "  Installing Python packages..."
    sudo apt-get update -qq
    sudo apt-get install -y -qq python3-pip python3-gpiozero python3-picamera2 || true
    pip install requests --quiet

    echo ""
    echo "  Detecting camera..."
    if command -v libcamera-still &>/dev/null; then
        echo "  ✅ libcamera available"
    fi

    echo ""
    echo "  What's your laptop's IP on WiFi?"
    echo "  (Run 'hostname -I' on your laptop to find it)"
    read -p "  Laptop IP: " LAPTOP_IP
    if [[ -z "$LAPTOP_IP" ]]; then
        echo "  ⚠️  No IP entered. You'll need to pass --laptop manually."
    else
        echo "  → You'll connect to: http://$LAPTOP_IP:8000"
    fi
    echo ""

    echo "  To start the robot thin client:"
    echo "    cd $(dirname "$0")"
    echo "    python3 src/robot/robot_client.py --laptop $LAPTOP_IP --port 8000"
    echo ""
}

# ── ESP32 setup ─────────────────────────────────────────────────────────────

setup_esp32() {
    echo "📟 Setting up ESP32-CAM..."
    echo ""
    echo "  1. Open src/robot/robot_client_esp32/robot_client_esp32.ino"
    echo "     in Arduino IDE (install ESP32 board support first)"
    echo ""
    echo "  2. Edit these lines with your WiFi and laptop IP:"
    echo "     const char* WIFI_SSID = \"YourWiFiName\";"
    echo "     const char* WIFI_PASS = \"YourWiFiPassword\";"
    echo "     const char* LAPTOP_HOST = \"192.168.1.100\";"
    echo ""
    echo "  3. Flash the sketch to your ESP32-CAM"
    echo ""
    echo "  4. The ESP32-CAM will auto-connect and start streaming"
    echo ""
}

# ── Menu ─────────────────────────────────────────────────────────────────────

echo "What are you setting up?"
echo ""
echo "  [1] Laptop (AI brain + dashboard)"
echo "  [2] Raspberry Pi (robot thin client)"
echo "  [3] ESP32-CAM (robot thin client)"
echo "  [4] Full diagram + all options"
echo ""

if [[ "$ON_PI" == "true" ]]; then
    echo "  → Detected Pi, defaulting to option 2"
    CHOICE="2"
else
    read -p "  Choice [1]: " CHOICE
    CHOICE="${CHOICE:-1}"
fi

case "$CHOICE" in
    1) setup_laptop ;;
    2) setup_pi ;;
    3) setup_esp32 ;;
    4) echo "See docs/architecture.md for full diagram" ;;
    *) echo "Invalid choice" ;;
esac

echo ""
echo "=== Setup complete ==="
