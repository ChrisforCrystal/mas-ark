# Query Model Target Test

Tests direct query execution with model as target (bypassing agents).

## What it tests
- Model as direct query target
- Query execution without agent intermediary
- Model response generation and validation
- Token usage tracking for model-direct queries
- Target type validation in query responses

## Running
```bash
chainsaw test
```

Validates that queries can directly target models for simple interactions without requiring agent configuration.