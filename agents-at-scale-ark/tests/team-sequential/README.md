# Sequential Team Test

Tests sequential team execution with multi-agent workflow.

## What it tests
- Sequential strategy with 3 agents: researcher → analyst → summarizer
- Agent handoff and data flow between team members
- Ordered execution and response chaining
- Complex multi-step workflows

## Running
```bash
chainsaw test
```

The test validates that agents execute in proper sequence and build upon each other's work to complete complex tasks.