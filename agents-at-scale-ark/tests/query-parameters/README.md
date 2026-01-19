# Query Parameters Test

Tests query parameter templating and injection.

## What it tests
- Query input parameter templating
- Parameter resolution from ConfigMaps and Secrets
- Dynamic query configuration
- Template substitution in query inputs

## Running
```bash
chainsaw test
```

Validates that queries can dynamically resolve parameters from external sources.