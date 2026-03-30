# Robot MCP Server Skill

## Overview

The robot MCP server exposes the RC car robot as an MCP tool server, allowing OpenClaw agents to control the robot via tool calls.

## Architecture

```
OpenClaw (MCP Client) → robot_mcp_server.py (MCP Server) → robot_client.py (HTTP) → Robot (Pi)
```

## Quick Start

### 1. Start the Robot (on Pi)
```bash
cd ~/robot-with-ai-v1
python3 src/robot/robot_client.py --laptop <YOUR_LAPTOP_IP>
```

### 2. Start the MCP Server (on Laptop)
```bash
cd ~/robot-with-ai-v1
python3 src/robot/mcp_server/robot_mcp_server.py --robot-host <PI_IP>
```

### 3. Configure OpenClaw

Add to `openclaw.json` under `plugins.entries`:

```json
{
  "robot-mcp": {
    "command": "node",
    "args": ["/home/vijay/projects/robot-with-ai-v1/src/robot/mcp_server/robot_mcp_server.py"],
    "cwd": "/home/vijay/projects/robot-with-ai-v1",
    "env": {
      "PYTHONIOENCODING": "utf-8"
    }
  }
}
```

Or use the OpenClaw MCP registration:
```
openclaw mcp add robot python /home/vijay/projects/robot-with-ai-v1/src/robot/mcp_server/robot_mcp_server.py
```

## Available Tools

| Tool | Description |
|------|-------------|
| `robot_move` | Move in direction (forward, backward, left, right, stop) |
| `robot_camera` | Get current camera frame |
| `robot_status` | Check robot connection status |
| `robot_stop` | Emergency stop |

## Example Usage

```
You: Ask the robot to move forward and see what's in front of it.

Agent calls:
1. robot_move(direction="forward", speed=0.6)
2. robot_camera() → analyze frame
3. Based on analysis: decide next action
```

## Troubleshooting

### Robot not connecting
- Check robot is running: `curl http://<PI_IP>:8000/`
- Check firewall: `sudo ufw allow 8000`

### MCP server not starting
- Verify Python deps: `pip install mcp fastapi uvicorn requests pillow`
- Test HTTP directly: `curl http://<PI_IP>:8000/api/command -X POST -d '{"direction":"stop"}'`

## Agent Integration

The MCP server enables the 7-agent architecture:

- **Motion Agent** → calls `robot_move`
- **Vision Agent** → calls `robot_camera`  
- **Reaction Agent** → calls `robot_stop` (emergency only)
- **CNS Agent** → routes all tool calls
- **Brain Agent** → orchestrates based on vision + context
