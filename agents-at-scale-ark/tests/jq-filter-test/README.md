# JQ Filter Test

Tests jq expression filtering functionality in agent tools.

## What it tests
- Agent tool function filtering with jq expressions
- Proper JSON filtering and response transformation
- Comparison between filtered and unfiltered tool responses

## Running
```bash
chainsaw test
```

Validates that jq expressions correctly filter tool responses when specified in agent tool functions.

Test skipped, reason - to be fixed:
- Sometimes doesn't return the sentiment field
- Sometimes phase ends in error
