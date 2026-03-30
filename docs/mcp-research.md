# MCP Server Research — Robot Control

**Date:** 2026-03-30
**Status:** Research completed, stub implemented

## Problem Statement

We need a reliable communication mechanism between OpenClaw (running on laptop) and the robot (running on Pi Zero 2 W). The robot is a "thin client" — it captures camera frames and executes motor commands. OpenClaw agents need to invoke robot capabilities like tools.

## Options Considered

### 1. Direct HTTP (Current Approach — `laptop_server.py`)
- Robot exposes REST API, agents call via `requests`
- **Pros:** Simple, well-understood, works today
- **Cons:** Polling-based (robot polls for commands), no standardized tool interface, agents must handle HTTP boilerplate

### 2. WebSocket (Real-time Bidirectional)
- Persistent connection for streaming frames + commands
- **Pros:** Low latency, bidirectional, natural for streaming
- **Cons:** More complex server implementation, connection management, not standardized for agents

### 3. MCP (Model Context Protocol) ⭐ **Selected**
- OpenClaw natively supports MCP as a client
- Robot exposes tools via MCP server (stdio or HTTP)
- **Pros:** 
  - Native OpenClaw integration (agents call tools directly)
  - Standardized tool interface (JSON schema for inputs/outputs)
  - OpenClaw handles transport, retries, session management
  - Tool discovery via `list_tools`
- **Cons:** Newer protocol, Python `mcp` package required on laptop

### 4. gRPC
- High-performance RPC with protocol buffers
- **Pros:** Fast, typed interfaces, streaming support
- **Cons:** More boilerplate, not natively supported by OpenClaw, overkill for this use case

## Why MCP Wins for This Use Case

1. **OpenClaw native support** — No custom integration code needed
2. **Tool-based interface** — Robot capabilities map naturally to tools (`robot_move`, `robot_camera`)
3. **Agent workflow** — Agents can use tools without knowing HTTP details
4. **Inspectability** — MCP Inspector (`npx mcp dev`) lets us test tools interactively
5. **Future-proof** — MCP is becoming a standard for AI tool use

## MCP Architecture Decision: Stdio vs HTTP

MCP supports two transport modes:

### Stdio (Selected for Robot)
```
Agent → stdio → robot_mcp_server.py → HTTP → robot_client.py → Robot
```
- Server runs as subprocess
- Simple, no network needed between laptop and server
- Server can run locally on laptop
- Robot accessed via HTTP to Pi IP

**Best for:** Local MCP server that communicates with robot over HTTP

### HTTP/SSE (Alternative)
```
Agent → HTTP → robot_mcp_server.py (network accessible)
```
- Server runs as network service
- Could run on Pi directly
- More complex setup (TLS, auth)

**Best for:** Cloud deployments, multi-robot scenarios

## Implementation: `robot_mcp_server.py`

**Location:** `src/robot/mcp_server/robot_mcp_server.py`

**Tools exposed:**
| Tool | Input | Output |
|------|-------|--------|
| `robot_move` | `{direction: enum, speed?: number}` | `{ok: boolean, ...}` |
| `robot_camera` | `{}` | `{image: base64, size: number}` |
| `robot_status` | `{}` | `{connected: boolean, ...}` |
| `robot_stop` | `{}` | `{ok: boolean}` |

**Communication flow:**
1. OpenClaw starts MCP server as subprocess (via plugin config)
2. Agent calls `robot_move` → MCP → server → HTTP POST to robot
3. Robot executes command, returns response
4. MCP response bubbles back to agent

## OpenClaw MCP Registration

Add to `~/.openclaw/openclaw.json`:
```json
{
  "plugins": {
    "entries": {
      "robot": {
        "command": "python",
        "args": ["/path/to/robot_mcp_server.py", "--robot-host", "<PI_IP>"]
      }
    }
  }
}
```

Or via CLI:
```bash
openclaw mcp add robot python /path/to/robot_mcp_server.py
```

## Future Enhancements

1. **Streaming camera** — Add WebSocket endpoint on robot, expose as MCP streaming tool
2. **Multi-robot** — Run multiple MCP servers, one per robot
3. **Tool callbacks** — Robot sends notifications back to agent (robot → agent events)
4. **Sensor streaming** — Battery, IMU data as continuous tool streams

## References

- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)
- [MCP Protocol Spec](https://modelcontextprotocol.io/)
- [OpenClaw MCP Support](https://docs.openclaw.ai/)
