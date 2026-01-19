# Round-Robin Team Test

Tests round-robin team execution with terminate tool functionality.

## What it tests
- Round-robin strategy with 3 agents: brainstormer, critic, coordinator
- Built-in terminate tool usage by coordinator agent
- Team conversation control and termination
- Multi-agent collaboration in iterative discussion

## Running
```bash
chainsaw test
```

The test validates that agents can coordinate in round-robin fashion and properly terminate conversations when sufficient progress is made.