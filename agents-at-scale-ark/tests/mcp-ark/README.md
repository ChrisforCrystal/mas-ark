# MCP ARK Integration Test

Tests ARK MCP server deployment and basic tool functionality.

## What it tests
- ARK MCP server deployment via Helm chart
- MCP server pod readiness and health check
- Tool registration and basic tool call execution
- `list_agents` tool with deterministic response structure

## Running
```bash
chainsaw test tests/mcp-ark/
```

Successful completion validates that the ARK MCP server can deploy and respond to basic tool calls.