#!/usr/bin/env python3
"""
robot_mcp_server.py — MCP server for robot-with-ai-v1

Runs on the laptop. Exposes robot capabilities as MCP tools to OpenClaw.
OpenClaw connects as an MCP client and can call tools like:
  - get_camera_frame() → image analysis
  - move(direction, speed) → motor commands
  - get_status() → robot health

The robot itself is a thin client running robot_client.py on the Pi.
Communication: MCP (OpenClaw) → HTTP (this server) → HTTP (robot)

Requirements:
    pip install fastapi uvicorn requests mcp[cli]

Usage:
    python robot_mcp_server.py [--robot-host ROBOT_IP] [--robot-port 8000]

MCP Inspector for testing:
    npx mcp dev src/robot/mcp_server/robot_mcp_server.py
"""

import argparse
import io
import logging
import time
import threading
from pathlib import Path
from typing import Optional

import requests
from PIL import Image

# MCP imports
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent
from mcp import Kit

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
log = logging.getLogger(__name__)

# ── Config ────────────────────────────────────────────────────────────────────

DEFAULT_ROBOT_HOST = "192.168.1.100"  # Update with actual robot IP
DEFAULT_ROBOT_PORT = 8000

# ── Robot Communication ──────────────────────────────────────────────────────

class RobotConnection:
    """HTTP client for talking to robot_client.py on the Pi."""

    def __init__(self, host: str, port: int):
        self.base_url = f"http://{host}:{port}"
        self.last_frame: Optional[bytes] = None
        self.lock = threading.Lock()

    def is_connected(self) -> bool:
        try:
            resp = requests.get(f"{self.base_url}/", timeout=2)
            return resp.status_code == 200
        except:
            return False

    def move(self, direction: str, speed: float = 0.6) -> dict:
        """Send motor command to robot."""
        try:
            resp = requests.post(
                f"{self.base_url}/api/command",
                json={"direction": direction, "speed": speed},
                timeout=5
            )
            return {"ok": True, "direction": direction, "speed": speed}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def get_last_frame(self) -> Optional[bytes]:
        """Get the most recent camera frame from robot."""
        try:
            resp = requests.get(f"{self.base_url}/api/frame/latest.jpg", timeout=5)
            if resp.status_code == 200:
                return resp.content
        except:
            pass
        return None

    def get_status(self) -> dict:
        """Get robot status."""
        try:
            resp = requests.get(f"{self.base_url}/", timeout=2)
            return resp.json()
        except Exception as e:
            return {"connected": False, "error": str(e)}


# ── MCP Server ────────────────────────────────────────────────────────────────

app = Server("robot-with-ai-v1")

# Global robot connection
robot: Optional[RobotConnection] = None


@app.list_tools()
async def list_tools() -> list[Tool]:
    """Expose robot capabilities as MCP tools."""
    return [
        Tool(
            name="robot_move",
            description="Move the robot in a direction. Use this to navigate the robot around.",
            inputSchema={
                "type": "object",
                "properties": {
                    "direction": {
                        "type": "string",
                        "enum": ["forward", "backward", "left", "right", "stop"],
                        "description": "Direction to move"
                    },
                    "speed": {
                        "type": "number",
                        "default": 0.6,
                        "minimum": 0.0,
                        "maximum": 1.0,
                        "description": "Speed from 0.0 to 1.0"
                    }
                },
                "required": ["direction"]
            }
        ),
        Tool(
            name="robot_camera",
            description="Capture and return the current camera frame from the robot. Use this to see what the robot sees.",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="robot_status",
            description="Get the current status of the robot including connection health and last decision.",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="robot_stop",
            description="Emergency stop — immediately halt all motors.",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict) -> TextContent:
    """Handle tool calls from MCP clients (OpenClaw)."""
    global robot

    if robot is None:
        return TextContent(
            text="Robot not connected. Initialize with robot_status first."
        )

    if name == "robot_move":
        direction = arguments.get("direction", "stop")
        speed = arguments.get("speed", 0.6)
        result = robot.move(direction, speed)
        return TextContent(text=f"Moved {direction} @ speed {speed}. Result: {result}")

    elif name == "robot_camera":
        frame = robot.get_last_frame()
        if frame:
            # Return image as base64 for vision models
            import base64
            b64 = base64.b64encode(frame).decode()
            return TextContent(
                text=f"Camera frame captured ({len(frame)} bytes). Image: data:image/jpeg;base64,{b64[:100]}...[truncated]"
            )
        else:
            return TextContent(text="No camera frame available")

    elif name == "robot_status":
        status = robot.get_status()
        return TextContent(text=f"Robot status: {status}")

    elif name == "robot_stop":
        result = robot.move("stop", 0)
        return TextContent(text=f"Emergency stop executed. Result: {result}")

    else:
        return TextContent(text=f"Unknown tool: {name}")


# ── Main ──────────────────────────────────────────────────────────────────────

async def main():
    global robot

    parser = argparse.ArgumentParser(description="Robot MCP Server")
    parser.add_argument("--robot-host", default=DEFAULT_ROBOT_HOST, help="Robot IP")
    parser.add_argument("--robot-port", type=int, default=DEFAULT_ROBOT_PORT, help="Robot port")
    args = parser.parse_args()

    robot = RobotConnection(args.robot_host, args.robot_port)

    log.info(f"Robot MCP Server starting, robot at {args.robot_host}:{args.robot_port}")

    # Test connection
    if robot.is_connected():
        log.info("✓ Robot connected")
    else:
        log.warning("⚠ Robot not reachable — will retry on tool calls")

    # Run MCP server over stdio
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
