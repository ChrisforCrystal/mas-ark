# Team Selector Strategy Test

Tests AI-driven participant selection in team coordination using selector strategy.

## What it tests
- **Selector Strategy**: AI model intelligently chooses next participant
- **Dynamic Participant Selection**: Context-aware team member selection
- **Template-based Selection**: Uses conversation history and role descriptions
- **Turn-based Constraints**: `maxTurns: 6` prevents infinite selection loops
- **Intelligent Sequencing**: AI-driven coordination vs fixed order execution

## Team Configuration
- **Strategy**: `selector` with AI model making selection decisions
- **Selector Model**: Uses `test-model` for participant selection
- **Selection Prompt**: Template with `{{.Roles}}`, `{{.History}}`, `{{.Participants}}`
- **Team Members**:
  - `researcher` - Research and data analysis specialist
  - `analyst` - Strategic analysis and insights expert  
  - `coordinator` - Project coordination with terminate capability

## Selection Process
1. AI model analyzes conversation history and context
2. Evaluates available participants and their expertise
3. Selects most appropriate member for next response
4. Prevents consecutive selection of same participant
5. Continues until task completion or maxTurns limit

## Running
```bash
chainsaw test
```

Validates AI-driven team coordination where participant selection is based on contextual intelligence rather than predetermined sequences.