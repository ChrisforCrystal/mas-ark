# Query Model Token Usage Test

Tests token usage tracking for direct model target queries.

## What it tests
- Token counting for model target type queries
- Validation that model targets generate token usage metrics
- Comparison of token usage between agent and model targets

## Running
```bash
chainsaw test tests/query-model-token-usage/
```

Validates that direct model queries properly track and report token usage.