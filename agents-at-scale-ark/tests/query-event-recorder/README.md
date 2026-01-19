# Query Event Recorder Test

Tests comprehensive query event recording during execution lifecycle.

## What it tests
- Query lifecycle event recording with detailed timing
- **Event Types Validated:**
  - `QueryResolveStart` - Query execution initiation
  - `AgentExecutionStart` - Agent processing begins
  - `LLMCallStart` - LLM API call initiation  
  - `LLMCallComplete` - LLM API call completion with token usage
  - `AgentExecutionComplete` - Agent processing completion
  - `TargetExecutionComplete` - Target execution completion
  - `QueryResolveComplete` - Query execution completion
- Event message content with structured JSON data
- Event association with query resources
- Event retrieval and validation
- Performance timing and token usage tracking

## Running
```bash
chainsaw test
```

Validates comprehensive event recording for query execution observability, debugging, and performance monitoring.