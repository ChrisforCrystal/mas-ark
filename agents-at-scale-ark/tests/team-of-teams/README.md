# Team of Teams Test

Tests hierarchical team structures with teams containing other teams as members.

## What it tests
- **Hierarchical Team Structure**: Parent team coordinating multiple sub-teams
- **Nested Team Execution**: Teams as members of other teams
- **Multi-Level Coordination**: 
  - Parent team (sequential strategy)
  - Research sub-team (researcher → analyst)
  - Synthesis sub-team (synthesizer → coordinator)
- **Sequential Workflow**: Sub-teams execute in defined order
- **Comprehensive Response Generation**: Multiple levels of team collaboration

## Team Architecture
```
parent-team (sequential)
├── research-team (sequential)
│   ├── researcher
│   └── analyst
└── synthesis-team (sequential)
    ├── synthesizer
    └── coordinator
```

## Running
```bash
chainsaw test
```

Validates hierarchical team coordination for complex multi-level workflow orchestration and organizational team structures.