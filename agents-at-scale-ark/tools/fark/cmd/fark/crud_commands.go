package main

import (
	"encoding/json"
	"fmt"
	"k8s.io/apimachinery/pkg/apis/meta/v1/unstructured"
	"k8s.io/apimachinery/pkg/runtime/schema"
	"sigs.k8s.io/yaml"
)

// runGetResourceCommand gets a specific resource by name
func runGetResourceCommand(config *Config, resourceType, resourceName, namespace string, jsonOutput bool) error {
	id := &ResourceIdentifier{
		Config:    config,
		Type:      getResourceTypeFromString(resourceType),
		Name:      resourceName,
		Namespace: namespace,
	}

	return id.Get(jsonOutput)
}

// runDeleteResourceCommand deletes a resource
func runDeleteResourceCommand(config *Config, resourceType, resourceName, namespace string) error {
	id := &ResourceIdentifier{
		Config:    config,
		Type:      getResourceTypeFromString(resourceType),
		Name:      resourceName,
		Namespace: namespace,
	}

	return id.Delete()
}

// Helper functions

func getResourceTypeFromString(resourceType string) ResourceType {
	switch resourceType {
	case "agent":
		return ResourceAgent
	case "team":
		return ResourceTeam
	case "model":
		return ResourceModel
	case "tool":
		return ResourceTool
	case "query":
		return ResourceQuery
	default:
		return ""
	}
}

func getGVRFromString(resourceType string) *schema.GroupVersionResource {
	switch resourceType {
	case "agent":
		gvr := GetGVR(ResourceAgent)
		return &gvr
	case "team":
		gvr := GetGVR(ResourceTeam)
		return &gvr
	case "model":
		gvr := GetGVR(ResourceModel)
		return &gvr
	case "tool":
		gvr := GetGVR(ResourceTool)
		return &gvr
	case "query":
		gvr := GetGVR(ResourceQuery)
		return &gvr
	default:
		return nil
	}
}

func printResourceJSON(resource *unstructured.Unstructured) error {
	jsonData, err := json.MarshalIndent(resource.Object, "", "  ")
	if err != nil {
		return fmt.Errorf("failed to marshal resource to JSON: %v", err)
	}
	fmt.Println(string(jsonData))
	return nil
}

func printResourceYAML(resource *unstructured.Unstructured) error {
	// Create a clean version without technical metadata
	cleanResource := make(map[string]interface{})

	// Keep essential fields
	cleanResource["apiVersion"] = resource.Object["apiVersion"]
	cleanResource["kind"] = resource.Object["kind"]

	// Simplified metadata with only name and namespace
	metadata := make(map[string]interface{})
	if originalMeta, found := resource.Object["metadata"]; found {
		if metaMap, ok := originalMeta.(map[string]interface{}); ok {
			if name, exists := metaMap["name"]; exists {
				metadata["name"] = name
			}
			if namespace, exists := metaMap["namespace"]; exists {
				metadata["namespace"] = namespace
			}
			if creationTimestamp, exists := metaMap["creationTimestamp"]; exists {
				metadata["creationTimestamp"] = creationTimestamp
			}
		}
	}
	cleanResource["metadata"] = metadata

	// Keep spec as-is
	if spec, found := resource.Object["spec"]; found {
		cleanResource["spec"] = spec
	}

	// Keep status if present
	if status, found := resource.Object["status"]; found {
		cleanResource["status"] = status
	}

	yamlData, err := yaml.Marshal(cleanResource)
	if err != nil {
		return fmt.Errorf("failed to marshal resource to YAML: %v", err)
	}
	fmt.Print(string(yamlData))
	return nil
}

func getNestedString(obj map[string]any, fields ...string) string {
	value, found, _ := unstructured.NestedString(obj, fields...)
	if !found {
		return ""
	}
	return value
}

func getResourceStatus(resource map[string]any) string {
	// Try to get status phase
	if phase, found, _ := unstructured.NestedString(resource, "status", "phase"); found {
		return phase
	}

	// Default status
	return "Unknown"
}
