# Agent Parameters Test

Tests agent parameter injection from ConfigMaps and Secrets.

## What it tests
- Template parameter resolution in agent prompts
- ConfigMap and Secret parameter references
- Dynamic agent configuration
- Parameter substitution validation

## Running
```bash
chainsaw test
```

Validates that agents can dynamically resolve parameters from external sources.