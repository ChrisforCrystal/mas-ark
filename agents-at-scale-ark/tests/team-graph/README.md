# Team Graph Strategy Test

Tests graph team strategy with directed workflow execution through predefined edges.

## What it tests
- Graph team strategy creates directed workflow between team members
- Team members execute in order defined by graph edges (researcher → analyzer → reviewer → writer)
- All team members participate in the workflow execution
- Query completes successfully with responses from all agents

## Running
```bash
chainsaw test
```

Successful completion validates that graph teams execute agents in directed workflow order according to defined edges.