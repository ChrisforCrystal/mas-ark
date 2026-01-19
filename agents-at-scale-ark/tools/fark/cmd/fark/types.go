package main

import (
	"fmt"
	"strings"

	"go.uber.org/zap"
	"k8s.io/apimachinery/pkg/runtime/schema"
	"k8s.io/client-go/dynamic"
)

type Config struct {
	DynamicClient dynamic.Interface
	Namespace     string
	Port          string
	Logger        *zap.Logger
}

type ResourceType string

const (
	ResourceQuery ResourceType = "queries"
	ResourceAgent ResourceType = "agents"
	ResourceTeam  ResourceType = "teams"
	ResourceModel ResourceType = "models"
	ResourceTool  ResourceType = "tools"
	ResourceEvent ResourceType = "events"
)

var resourceGVRMap = map[ResourceType]schema.GroupVersionResource{
	ResourceQuery: {Group: "ark.mckinsey.com", Version: "v1alpha1", Resource: "queries"},
	ResourceAgent: {Group: "ark.mckinsey.com", Version: "v1alpha1", Resource: "agents"},
	ResourceTeam:  {Group: "ark.mckinsey.com", Version: "v1alpha1", Resource: "teams"},
	ResourceModel: {Group: "ark.mckinsey.com", Version: "v1alpha1", Resource: "models"},
	ResourceTool:  {Group: "ark.mckinsey.com", Version: "v1alpha1", Resource: "tools"},
	ResourceEvent: {Group: "", Version: "v1", Resource: "events"},
}

func GetGVR(resourceType ResourceType) schema.GroupVersionResource {
	return resourceGVRMap[resourceType]
}

// OutputOptions groups output formatting parameters
type OutputOptions struct {
	OutputMode string // "text" or "json"
	Verbose    bool   // Show detailed events and logs
	Quiet      bool   // Suppress events and progress indicators
}

// AgentSpec groups agent creation and update parameters
type AgentSpec struct {
	Prompt      string
	ModelRef    string
	Description string
	Tools       []string
}

// ResourceRequest groups parameters for resource operations
type ResourceRequest struct {
	Config    *Config
	Type      string
	Name      string
	Namespace string
	Filename  string
	AgentSpec *AgentSpec
}

// Update updates the resource using either file or flags
func (r *ResourceRequest) Update() error {
	id := &ResourceIdentifier{
		Config:    r.Config,
		Type:      getResourceTypeFromString(r.Type),
		Name:      r.Name,
		Namespace: r.Namespace,
	}

	if r.Filename != "" {
		return id.UpdateFromFile(r.Filename)
	}

	return id.UpdateFromFlags(r.AgentSpec)
}

// Create creates the resource using either file or flags
func (r *ResourceRequest) Create() error {
	id := &ResourceIdentifier{
		Config:    r.Config,
		Type:      getResourceTypeFromString(r.Type),
		Name:      r.Name,
		Namespace: r.Namespace,
	}

	if r.Filename != "" {
		return id.CreateFromFile(r.Filename)
	}

	return id.CreateFromFlags(r.AgentSpec)
}

// InputResolver groups input resolution parameters
type InputResolver struct {
	Input     string
	InputFile string
	Args      []string
	Required  bool
}

// Resolve resolves input from various sources
func (r *InputResolver) Resolve() (string, error) {
	if r.Input != "" && r.InputFile != "" {
		return "", fmt.Errorf("cannot use both --input and --file flags")
	}
	if (r.Input != "" || r.InputFile != "") && len(r.Args) > 0 {
		return "", fmt.Errorf("cannot provide input text as both flags and arguments")
	}

	if r.InputFile != "" {
		content, err := readInputFile(r.InputFile)
		if err != nil {
			return "", fmt.Errorf("failed to read input file: %v", err)
		}
		return content, nil
	}

	if r.Input != "" {
		return r.Input, nil
	}

	if len(r.Args) > 0 {
		return strings.Join(r.Args, " "), nil
	}

	if r.Required {
		return "", fmt.Errorf("query input required - provide as argument or use --file (-f) flag")
	}
	return "", nil
}
