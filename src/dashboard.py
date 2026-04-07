#!/usr/bin/env python3
"""
Robot Dashboard - Web interface for debugging robot vision.
Serves on port 8080.

Shows:
- Live camera feed (auto-refreshes)
- Reflex state and sensor values
- What the robot "sees" (obstacle detection visualization)
"""
import os
import sys
import time
import json
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path

# Paths
PROJECT_ROOT = Path(__file__).parent.parent
TMP_DIR = Path("/tmp")
CAM_PATTERN = TMP_DIR / "cam_%04d.jpg"
STATE_FILE = TMP_DIR / "robot_state.json"
LATEST_FRAME = TMP_DIR / "latest_frame.jpg"


def get_latest_frame():
    """Get the most recent camera frame."""
    try:
        frames = list(TMP_DIR.glob("cam_*.jpg"))
        if not frames:
            return None, None
        latest = max(frames, key=lambda p: p.stat().st_mtime)
        frame_age = time.time() - latest.stat().st_mtime
        return latest, frame_age
    except:
        return None, None


def read_robot_state():
    """Read state from file written by robot_agent."""
    try:
        if STATE_FILE.exists():
            with open(STATE_FILE, 'r') as f:
                return json.load(f)
    except:
        pass
    return None


class DashboardHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass  # Suppress noisy logging
    
    def do_GET(self):
        if self.path == "/" or self.path == "/index.html":
            self.send_html()
        elif self.path == "/frame.jpg" or self.path == "/frame":
            self.send_frame()
        elif self.path == "/state.json":
            self.send_state()
        elif self.path == "/debug":
            self.send_debug()
        else:
            self.send_error(404)
    
    def send_html(self):
        state = read_robot_state()
        frame, frame_age = get_latest_frame()
        
        # Build state display
        reflex_state = state.get('reflex_state', 'unknown') if state else 'unknown'
        reflex_action = state.get('reflex_action', 'none') if state else 'none'
        floor_brightness = state.get('floor_brightness', 0) if state else 0
        obstacle_score = state.get('obstacle_score', 0.0) if state else 0.0
        stuck_counter = state.get('stuck_counter', 0) if state else 0
        iteration = state.get('iteration', 0) if state else 0
        
        state_class = 'unknown'
        if reflex_state == 'danger':
            state_class = 'danger'
        elif reflex_state == 'caution':
            state_class = 'caution'
        elif reflex_state == 'normal':
            state_class = 'clear'
        
        obstacle_class = 'normal'
        if obstacle_score > 0.5:
            obstacle_class = 'danger'
        elif obstacle_score > 0.25:
            obstacle_class = 'caution'
        
        html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Robot Dashboard</title>
    <meta http-equiv="refresh" content="1">
    <style>
        * {{ box-sizing: border-box; }}
        body {{ 
            font-family: 'Courier New', monospace; 
            margin: 0; 
            padding: 20px;
            background: #0f0f1a;
            color: #eee;
        }}
        h1 {{ 
            margin: 0 0 20px 0;
            color: #00d9ff;
            font-size: 24px;
        }}
        .container {{ 
            display: flex; 
            gap: 20px;
            flex-wrap: wrap;
            max-width: 1400px;
        }}
        .panel {{
            background: #1a1a2e;
            border-radius: 8px;
            padding: 15px;
            border: 1px solid #333;
        }}
        .camera {{ 
            flex: 2;
            min-width: 400px;
        }}
        .debug {{ 
            flex: 1;
            min-width: 280px;
        }}
        h2 {{ 
            margin: 0 0 15px 0;
            color: #00d9ff;
            font-size: 16px;
            border-bottom: 1px solid #333;
            padding-bottom: 10px;
        }}
        .state-row {{
            display: flex;
            justify-content: space-between;
            padding: 8px 0;
            border-bottom: 1px solid #2a2a3e;
        }}
        .state-label {{ color: #888; font-size: 13px; }}
        .state-value {{ font-weight: bold; font-size: 14px; }}
        .danger {{ color: #ff4757; }}
        .caution {{ color: #ffa502; }}
        .clear {{ color: #2ed573; }}
        .unknown {{ color: #888; }}
        .normal {{ color: #7f8c8d; }}
        .status-badge {{
            display: inline-block;
            padding: 4px 12px;
            border-radius: 4px;
            font-weight: bold;
            text-transform: uppercase;
            font-size: 12px;
        }}
        .badge-danger {{ background: #ff4757; color: white; }}
        .badge-caution {{ background: #ffa502; color: black; }}
        .badge-clear {{ background: #2ed573; color: black; }}
        .badge-unknown {{ background: #444; color: #888; }}
        
        .camera img {{ 
            width: 100%;
            max-width: 640px;
            border-radius: 4px;
            border: 2px solid #333;
            background: #000;
        }}
        .no-camera {{
            width: 100%;
            max-width: 640px;
            height: 360px;
            background: #1a1a1a;
            border-radius: 4px;
            border: 2px solid #333;
            display: flex;
            align-items: center;
            justify-content: center;
            color: #555;
        }}
        .stuck-warning {{
            background: #ff4757;
            color: white;
            padding: 12px;
            border-radius: 4px;
            margin-top: 15px;
            display: none;
            font-weight: bold;
            text-align: center;
        }}
        .stuck-warning.visible {{ display: block; }}
        
        .timestamp {{
            color: #555;
            font-size: 11px;
            margin-top: 10px;
        }}
        
        .sensor-grid {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 10px;
            margin-top: 15px;
        }}
        .sensor-box {{
            background: #16213e;
            padding: 10px;
            border-radius: 4px;
            text-align: center;
        }}
        .sensor-value {{
            font-size: 24px;
            font-weight: bold;
            color: #00d9ff;
        }}
        .sensor-label {{
            font-size: 11px;
            color: #666;
            margin-top: 4px;
        }}
    </style>
</head>
<body>
    <h1>🤖 Robot Dashboard</h1>
    <div class="container">
        <div class="panel camera">
            <h2>📷 Camera Feed</h2>
            <div id="camera-container">
                <img src="/frame.jpg?t={int(time.time())}" alt="Camera" 
                     onerror="this.style.display='none'; document.getElementById('no-cam').style.display='flex';">
                <div id="no-cam" class="no-camera" style="display:none">No camera feed</div>
            </div>
            <div class="timestamp">Frame age: {frame_age:.1f}s | Updated: {time.strftime('%H:%M:%S')}</div>
        </div>
        <div class="panel debug">
            <h2>📊 Reflex State</h2>
            <div class="state-row">
                <span class="state-label">Status</span>
                <span class="state-value">
                    <span class="status-badge badge-{state_class}">{reflex_state}</span>
                </span>
            </div>
            <div class="state-row">
                <span class="state-label">Last Action</span>
                <span class="state-value">{reflex_action}</span>
            </div>
            <div class="state-row">
                <span class="state-label">Stuck Count</span>
                <span class="state-value {('danger' if stuck_counter > 0 else '')}">{stuck_counter}/4</span>
            </div>
            <div class="state-row">
                <span class="state-label">Iteration</span>
                <span class="state-value">{iteration}</span>
            </div>
            
            <div class="sensor-grid">
                <div class="sensor-box">
                    <div class="sensor-value {state_class}">{floor_brightness:.0f}</div>
                    <div class="sensor-label">Floor Brightness</div>
                </div>
                <div class="sensor-box">
                    <div class="sensor-value {obstacle_class}">{obstacle_score:.3f}</div>
                    <div class="sensor-label">Obstacle Score</div>
                </div>
            </div>
            
            <div id="stuck-warning" class="stuck-warning">
                🚨 STUCK DETECTED! Escape maneuver in progress...
            </div>
        </div>
    </div>
    
    <script>
        // Update stuck warning visibility
        const stuckCounter = {stuck_counter};
        if (stuckCounter >= 4) {{
            document.getElementById('stuck-warning').classList.add('visible');
        }}
        
        // Auto-refresh every 500ms for smoother updates
        setTimeout(() => {{
            location.reload();
        }}, 1000);
    </script>
</body>
</html>"""
        
        self.send_response(200)
        self.send_header('Content-Type', 'text/html')
        self.end_headers()
        self.wfile.write(html.encode())
    
    def send_frame(self):
        """Send latest camera frame as JPEG."""
        frame_path, _ = get_latest_frame()
        if frame_path and frame_path.exists():
            try:
                self.send_response(200)
                self.send_header('Content-Type', 'image/jpeg')
                self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
                self.send_header('Pragma', 'no-cache')
                self.send_header('Expires', '0')
                self.end_headers()
                with open(frame_path, 'rb') as f:
                    self.wfile.write(f.read())
            except Exception as e:
                self.send_error(500, str(e))
        else:
            # Send placeholder - 1x1 red GIF (no camera)
            self.send_response(200)
            self.send_header('Content-Type', 'image/gif')
            self.end_headers()
            # 1x1 red dot GIF
            self.wfile.write(b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x80\x00\x00\xff\x00\x00\x00\x00\x21\xf9\x04\x01\x00\x00\x00\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02\x00\x01\x00\x3b')
    
    def send_state(self):
        """Send current robot state as JSON."""
        state = read_robot_state()
        frame, frame_age = get_latest_frame()
        
        state_data = state or {
            'reflex_state': 'unknown',
            'reflex_action': 'none',
            'floor_brightness': 0,
            'obstacle_score': 0.0,
            'stuck_counter': 0,
            'iteration': 0,
        }
        state_data['frame_age_ms'] = frame_age * 1000 if frame_age else 999
        state_data['timestamp'] = time.time()
        state_data['frame_count'] = len(list(TMP_DIR.glob("cam_*.jpg")))
        
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Cache-Control', 'no-cache')
        self.end_headers()
        self.wfile.write(json.dumps(state_data).encode())
    
    def send_debug(self):
        """Send detailed debug info."""
        frame, frame_age = get_latest_frame()
        debug = {
            'tmp_dir': str(TMP_DIR),
            'frame_count': len(list(TMP_DIR.glob("cam_*.jpg"))),
            'latest_frame': str(frame) if frame else None,
            'frame_age': frame_age,
            'state_file_exists': STATE_FILE.exists(),
            'python_version': sys.version,
        }
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(debug, indent=2).encode())


def run_server(port=8080):
    """Run the dashboard server."""
    print(f"🤖 Robot Dashboard")
    print(f"   Dashboard: http://localhost:{port}")
    print(f"   Camera:    http://localhost:{port}/frame.jpg")
    print(f"   State:     http://localhost:{port}/state.json")
    server = HTTPServer(('0.0.0.0', port), DashboardHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nDashboard stopped.")
        server.shutdown()


if __name__ == '__main__':
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8080
    run_server(port)
