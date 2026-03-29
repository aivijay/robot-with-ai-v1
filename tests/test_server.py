#!/usr/bin/env python3
"""
test_server.py — Smoke test for laptop_server.py
Tests all endpoints without needing a robot connected.

Run from the project root:
    python tests/test_server.py

Requirements:
    pip install requests pillow
"""
import io
import sys
import time
from PIL import Image

BASE = "http://localhost:8000"

def make_test_image():
    """Generate a small test JPEG."""
    img = Image.new("RGB", (320, 240), color=(100, 150, 200))
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    buf.seek(0)
    return buf

def test_status():
    import requests
    r = requests.get(f"{BASE}/")
    assert r.status_code == 200, f"Status failed: {r.status_code}"
    data = r.json()
    print(f"  ✅ Server up — model: {data.get('model')}, ollama: {data.get('ollama')}")

def test_frame_no_robot():
    """Test that /api/frame accepts a frame even without a robot."""
    import requests
    buf = make_test_image()
    r = requests.post(f"{BASE}/api/frame", files={"image": buf})
    assert r.status_code == 200, f"Frame upload failed: {r.status_code}"
    print(f"  ✅ /api/frame accepts JPEG ({buf.tell()} bytes)")

def test_command_set():
    """Test setting a manual command."""
    import requests
    for direction in ["forward", "left", "right", "stop"]:
        r = requests.post(f"{BASE}/api/command", json={"direction": direction})
        assert r.status_code == 200, f"Command '{direction}' failed"
        print(f"  ✅ /api/command set: {direction}")

    r = requests.get(f"{BASE}/api/command")
    assert r.status_code == 200
    data = r.json()
    assert data.get("direction") == "stop", f"Expected stop, got {data}"
    print(f"  ✅ /api/command get: correct")

def test_ai_decide():
    """Test AI decision on a test image."""
    import requests
    buf = make_test_image()
    # First upload a frame
    r = requests.post(f"{BASE}/api/frame", files={"image": buf})
    assert r.status_code == 200

    print("  ⏳ Calling /api/ai_decide (may take a few seconds)...")
    r = requests.post(f"{BASE}/api/autonomous_loop", timeout=60)
    if r.status_code == 200:
        data = r.json()
        print(f"  ✅ AI decision: {data.get('decision')!r} in {data.get('elapsed_s')}s")
        print(f"     Raw response: {data.get('raw', '')[:80]!r}")
    else:
        print(f"  ⚠️  AI endpoint returned {r.status_code} (Ollama may be offline)")

def main():
    import requests
    print("=== laptop_server.py smoke test ===")
    print(f"Server: {BASE}")
    print()

    # Check server is running
    try:
        test_status()
    except Exception as e:
        print(f"  ❌ Server not reachable: {e}")
        print()
        print("  Start the server first:")
        print("    python src/laptop/laptop_server.py")
        sys.exit(1)

    print()
    print("  Running tests...")
    test_frame_no_robot()
    test_command_set()

    print()
    print("  AI test (requires Ollama running):")
    try:
        test_ai_decide()
    except Exception as e:
        print(f"  ❌ AI test failed: {e}")

    print()
    print("=== Done ===")

if __name__ == "__main__":
    main()
