# Query Tool Target Test

Tests direct query execution targeting tools without agents.

## What it tests
- Direct tool execution bypassing agent layer
- Tool response content generation from fetcher
- Query response structure with tool targets
- Tool target validation and resolution
- Fetcher URL template execution with input parameters

## Running
```bash
chainsaw test
```

Validates tool-direct query execution for direct API integration and tool testing.