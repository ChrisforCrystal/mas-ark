# Agent Structured Output Test

## Overview

This test validates the structured output functionality for agents using JSON schema. It verifies that when an agent is configured with an `outputSchema`, the LLM responses conform to the specified JSON structure.

## Test Scenario

1. **Agent Configuration**: Creates an agent with a JSON schema defining structured output format
2. **Query Execution**: Sends a query to the agent requesting data extraction
3. **Response Validation**: Verifies the response follows the exact JSON schema structure

## JSON Schema Definition

The test agent uses a schema that defines:
- `summary`: A brief summary of the input text
- `entities`: Array of named entities with name and type
- `sentiment`: Overall sentiment classification

## Expected Behavior

- Agent responds with valid JSON matching the schema exactly
- Response includes all required fields
- Field types and constraints are enforced
- Additional properties are not allowed

## Prerequisites

- Azure OpenAI API key and base URL configured
- gpt-4.1-mini model access
- ARK controller running with webhook validation

## Test Resources

- **Model**: Azure OpenAI gpt-4.1-mini
- **Agent**: Configured with JSON schema for structured output
- **Query**: Text analysis request with specific input

## Validation Points

1. Agent creation succeeds with valid schema
2. Query execution completes without errors
3. Response content is valid JSON
4. Response structure matches schema requirements
5. All required fields are present
6. Field types conform to schema constraints