# Model Properties Test

Tests model configuration with custom properties like temperature, max_tokens, and penalties.

## What it tests
- Model creation with custom properties configuration
- Temperature setting (0.1) for deterministic output
- Max tokens limitation (100) for response length control
- Top_p nucleus sampling parameter (0.9)
- Frequency penalty (0.5) and presence penalty (0.3)
- Seed value (42) for reproducible results
- Property validation in model spec
- Agent execution with custom model properties

## Running
```bash
chainsaw test
```

Validates that models accept and apply custom properties that influence generation behavior and output characteristics.