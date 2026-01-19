package main

import (
	"context"
	"encoding/json"
	"fmt"
	"strings"

	metav1 "k8s.io/apimachinery/pkg/apis/meta/v1"
	"k8s.io/apimachinery/pkg/apis/meta/v1/unstructured"
)

func validateToolParameters(config *Config, toolName, namespace, input string) error {
	toolGVR := GetGVR(ResourceTool)
	toolResource, err := config.DynamicClient.Resource(toolGVR).Namespace(namespace).Get(
		context.TODO(),
		toolName,
		metav1.GetOptions{},
	)
	if err != nil {
		return fmt.Errorf("failed to get tool %s: %v", toolName, err)
	}

	inputSchemaRaw, found, err := unstructured.NestedMap(toolResource.Object, "spec", "inputSchema")
	if err != nil {
		return fmt.Errorf("failed to get input schema: %v", err)
	}
	if !found {
		return nil
	}

	requiredFields, found, err := unstructured.NestedStringSlice(inputSchemaRaw, "required")
	if err != nil {
		return fmt.Errorf("failed to get required fields: %v", err)
	}
	if !found || len(requiredFields) == 0 {
		return nil
	}

	var inputData map[string]interface{}
	if err := json.Unmarshal([]byte(input), &inputData); err != nil {
		return fmt.Errorf("tool input must be valid JSON when tool has required parameters")
	}

	var missingFields []string
	for _, field := range requiredFields {
		if _, exists := inputData[field]; !exists {
			missingFields = append(missingFields, field)
		}
	}

	if len(missingFields) > 0 {
		parameterInfo := buildParameterInfo(inputSchemaRaw)
		return fmt.Errorf("missing required parameters: %s\n\nTool Parameters:\n%s",
			strings.Join(missingFields, ", "), parameterInfo)
	}

	return nil
}

func buildParameterInfo(schema map[string]interface{}) string {
	var info strings.Builder

	properties, found, err := unstructured.NestedMap(schema, "properties")
	if err != nil || !found {
		return "No parameter information available"
	}

	requiredFields, _, _ := unstructured.NestedStringSlice(schema, "required")
	requiredSet := make(map[string]bool)
	for _, field := range requiredFields {
		requiredSet[field] = true
	}

	for paramName, paramDef := range properties {
		paramMap, ok := paramDef.(map[string]any)
		if !ok {
			continue
		}

		required := ""
		if requiredSet[paramName] {
			required = " (required)"
		}

		paramType, _, _ := unstructured.NestedString(paramMap, "type")
		description, _, _ := unstructured.NestedString(paramMap, "description")

		info.WriteString(fmt.Sprintf("  %s%s", paramName, required))
		if paramType != "" {
			info.WriteString(fmt.Sprintf(" [%s]", paramType))
		}
		if description != "" {
			info.WriteString(fmt.Sprintf(": %s", description))
		}

		enumValues, found, _ := unstructured.NestedSlice(paramMap, "enum")
		if found && len(enumValues) > 0 {
			var enumStrings []string
			for _, val := range enumValues {
				if str, ok := val.(string); ok {
					enumStrings = append(enumStrings, str)
				}
			}
			if len(enumStrings) > 0 {
				info.WriteString(fmt.Sprintf(" (options: %s)", strings.Join(enumStrings, ", ")))
			}
		}

		info.WriteString("\n")
	}

	return info.String()
}
