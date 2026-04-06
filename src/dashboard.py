#!/usr/bin/env python3
"""
Robot Dashboard - Web interface for debugging robot vision.
Serves on port 8080.

Shows:
- Live camera feed
- Reflex state and sensor values
- What the robot "sees" (obstacle detection visualization)
"""
import os
import sys
import time
import json
import threading
import subprocess
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path

# Paths
PROJECT_ROOT = Path(__file__).parent.parent
TMP_DIR = Path("/tmp")
CAM_PATTERN = TMP_DIR / "cam_%04d.jpg"
LATEST_FRAME = TMP_DIR / "latest_frame.jpg"

# Shared state (updated by robot_agent or we'll poll directly)
class RobotState:
    reflex_state = "unknown"
    reflex_action = "none"
    floor_brightness = 0
    obstacle_score = 0.0
    stuck_counter = 0
    iteration = 0
    last_update = 0

state = RobotState()

def get_latest_frame():
    """Get the most recent camera frame."""
    try:
        # Find latest cam_XXXX.jpg
        frames = list(TMP_DIR.glob("cam_*.jpg"))
        if not frames:
            return None
        latest = max(frames, key=lambda p: p.stat().st_mtime)
        return latest
    except:
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
        html = """<!DOCTYPE html>
<html>
<head>
    <title>Robot Dashboard</title>
    <meta http-equiv="refresh" content="0.5">
    <style>
        body { 
            font-family: monospace; 
            margin: 20px; 
            background: #1a1a2e;
            color: #eee;
        }
        .container { 
            display: flex; 
            gap: 20px;
            flex-wrap: wrap;
        }
        .panel {
            background: #16213e;
            border-radius: 8px;
            padding: 15px;
        }
        .camera { 
            flex: 2;
            min-width: 300px;
        }
        .camera img { 
            width: 100%;
            border-radius: 4px;
        }
        .debug { 
            flex: 1;
            min-width: 250px;
        }
        h2 { 
            margin-top: 0;
            color: #00d9ff;
        }
        .state-row {
            display: flex;
            justify-content: space-between;
            padding: 5px 0;
            border-bottom: 1px solid #333;
        }
        .state-label { color: #888; }
        .state-value { font-weight: bold; }
        .danger { color: #ff4757; }
        .caution { color: #ffa502; }
        .clear { color: #2ed573; }
        .unknown { color: #888; }
        .status-badge {
            display: inline-block;
            padding: 4px 12px;
            border-radius: 4px;
            font-weight: bold;
            text-transform: uppercase;
        }
        .stuck-warning {
            background: #ff4757;
            color: white;
            padding: 10px;
            border-radius: 4px;
            margin-top: 10px;
            display: none;
        }
        .stuck-warning.visible { display: block; }
    </style>
</head>
<body>
    <h1>🤖 Robot Dashboard</h1>
    <div class="container">
        <div class="panel camera">
            <h2>Camera Feed</h2>
            <img src="/frame.jpg?t=""" + str(int(time.time())) + """" alt="Camera">
        </div>
        <div class="panel debug">
            <h2>Reflex State</h2>
            <div id="reflex-info">Loading...</div>
        </div>
    </div>
    <div id="stuck-warning" class="stuck-warning">
        🚨 STUCK DETECTED! Escape maneuver in progress...
    </div>
    <script>
        async function updateState() {
            try {
                const res = await fetch('/state.json');
                const data = await res.json();
                
                const reflexEl = document.getElementById('reflex-info');
                const stateClass = data.reflex_state === 'danger' ? 'danger' : 
                                   data.reflex_state === 'caution' ? 'caution' : 
                                   data.reflex_state === 'clear' ? 'clear' : 'unknown';
                
                reflexEl.innerHTML = `
                    <div class="state-row">
                        <span class="state-label">Status</span>
                        <span class="state-value ${stateClass}">
                            <span class="status-badge ${stateClass}">${data.reflex_state}</span>
                        </span>
                    </div>
                    <div class="state-row">
                        <span class="state-label">Action</span>
                        <span class="state-value">${data.reflex_action}</span>
                    </div>
                    <div class="state-row">
                        <span class="state-label">Floor Brightness</span>
                        <span class="state-value">${data.floor_brightness.toFixed(1)}</span>
                    </div>
                    <div class="state-row">
                        <span class="state-label">Obstacle Score</span>
                        <span class="state-value ${data.obstacle_score > 0.25 ? 'danger' : ''}">${data.obstacle_score.toFixed(3)}</span>
                    </div>
                    <div class="state-row">
                        <span class="state-label">Iteration</span>
                        <span class="state-value">${data.iteration}</span>
                    </div>
                    <div class="state-row">
                        <span class="state-label">Stuck Count</span>
                        <span class="state-value ${data.stuck_counter > 0 ? 'danger' : ''}">${data.stuck_counter}/4</span>
                    </div>
                `;
                
                // Show stuck warning
                const stuckEl = document.getElementById('stuck-warning');
                if (data.stuck_counter >= 4) {
                    stuckEl.classList.add('visible');
                } else {
                    stuckEl.classList.remove('visible');
                }
            } catch (e) {
                console.error('State fetch failed:', e);
            }
        }
        // Update every 200ms
        updateState();
        setInterval(updateState, 200);
    </script>
</body>
</html>"""
        
        self.send_response(200)
        self.send_header('Content-Type', 'text/html')
        self.end_headers()
        self.wfile.write(html.encode())
    
    def send_frame(self):
        """Send latest camera frame as JPEG."""
        frame_path = get_latest_frame()
        if frame_path and frame_path.exists():
            try:
                # Copy to latest_frame.jpg for consistent URL
                import shutil
                shutil.copy(frame_path, LATEST_FRAME)
                
                self.send_response(200)
                self.send_header('Content-Type', 'image/jpeg')
                self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
                self.end_headers()
                with open(LATEST_FRAME, 'rb') as f:
                    self.wfile.write(f.read())
            except Exception as e:
                self.send_error(500, str(e))
        else:
            # Send placeholder
            self.send_response(200)
            self.send_header('Content-Type', 'image/jpeg')
            self.end_headers()
            # 1x1 transparent GIF
            self.wfile.write(b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x80\x00\x00\xff\xff\xff\x00\x00\x00\x21\xf9\x04\x01\x00\x00\x00\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02\x44\x01\x00\x3b')
    
    def send_state(self):
        """Send current robot state as JSON."""
        # Try to read from robot_agent's shared state if available
        # Otherwise return mock state
        frame = get_latest_frame()
        frame_age = time.time() - frame.stat().st_mtime if frame else 999
        
        state_data = {
            'reflex_state': 'unknown',
            'reflex_action': 'none',
            'floor_brightness': 0,
            'obstacle_score': 0.0,
            'stuck_counter': 0,
            'iteration': 0,
            'frame_age_ms': frame_age * 1000,
            'timestamp': time.time()
        }
        
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Cache-Control', 'no-cache')
        self.end_headers()
        self.wfile.write(json.dumps(state_data).encode())
    
    def send_debug(self):
        """Send detailed debug info."""
        debug = {
            'project_root': str(PROJECT_ROOT),
            'tmp_dir': str(TMP_DIR),
            'frames': len(list(TMP_DIR.glob("cam_*.jpg"))),
            'python_version': sys.version,
        }
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(debug, indent=2).encode())


def run_server(port=8080):
    """Run the dashboard server."""
    server = HTTPServer(('0.0.0.0', port), DashboardHandler)
    print(f"🤖 Robot Dashboard running at http://localhost:{port}")
    print(f"   - Camera feed: http://localhost:{port}/frame.jpg")
    print(f"   - State JSON: http://localhost:{port}/state.json")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nDashboard stopped.")
        server.shutdown()


if __name__ == '__main__':
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8080
    run_server(port)
