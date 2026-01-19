# Team Round-Robin Max Turns Test

Tests round-robin team execution with maxTurns constraint validation.

## What it tests
- Round-robin team strategy with turn-based execution limits
- **Max Turns Configuration**: `maxTurns: 2` prevents infinite cycling
- Team member cycling through brainstormer → critic → coordinator
- Turn-based execution termination at configured limit
- Response generation within turn constraints
- Team response length validation with constrained execution

## Running
```bash
chainsaw test
```

Validates maxTurns prevents infinite round-robin cycling and constrains team execution to defined iteration limits.