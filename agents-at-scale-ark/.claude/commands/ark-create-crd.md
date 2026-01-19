# ARK CRD Generator

You are an expert Kubernetes CRD developer working on the ARK project. Your task is to generate a new Custom Resource Definition following ARK's established patterns and design guidelines.

## Pre-Task Checklist
1. **Review CRD Design Guidelines** at `/docs/content/concepts/crd-design-guide.mdx`
2. **Examine existing CRDs** in `/ark/api/v1alpha1/` for pattern consistency
3. **Check common types** in `/ark/api/v1alpha1/common_types.go` for reusable patterns
4. **Create a todo list** using TodoWrite for tracking CRD generation subtasks

## CRD Generation Workflow
- [ ] Analyze the requested resource type and requirements
- [ ] Determine appropriate naming following ARK conventions
- [ ] Design the Spec structure using common patterns
- [ ] Design the Status structure with appropriate phases
- [ ] Add proper kubebuilder annotations
- [ ] Generate the complete types file
- [ ] Create sample YAML manifestation
- [ ] Generate basic controller scaffold (if requested)
- [ ] Generate admission webhook scaffold (if requested)
- [ ] Update relevant documentation

## ARK CRD Design Principles

### Core Patterns to Follow
1. **ValueSource Pattern**: Use for all configuration values that may contain secrets
2. **Parameter Pattern**: Include `[]Parameter` for template processing
3. **TTL Pattern**: Add `TTL *metav1.Duration` with default "720h"
4. **TokenUsage Pattern**: Include `TokenUsage *TokenUsage` for AI operations
5. **Owner References**: Use for parent-child relationships in controller, not as CRD field

### Naming Conventions
- **`...Ref`**: For references to other CRDs (e.g., `AgentModelRef`)
- **`...Config`**: For embedded configuration structs (e.g., `ModelConfig`)
- **`...Spec`**: For resource desired state (e.g., `AgentSpec`)
- **`...Status`**: For resource observed state (e.g., `AgentStatus`)

### Required Kubebuilder Annotations
```go
// +kubebuilder:object:root=true
// +kubebuilder:subresource:status
// +kubebuilder:printcolumn:name="Phase",type=string,JSONPath=`.status.phase`
// +kubebuilder:printcolumn:name="Age",type=date,JSONPath=`.metadata.creationTimestamp`
```

### Standard Status Structure
```go
type ResourceStatus struct {
    // +kubebuilder:validation:Optional
    // +kubebuilder:validation:Enum=pending;running;ready;error
    Phase string `json:"phase,omitempty"`
    // +kubebuilder:validation:Optional
    Message string `json:"message,omitempty"`
}
```

### Standard Spec Structure
```go
type ResourceSpec struct {
    // +kubebuilder:validation:Required
    Config ResourceConfig `json:"config"`
    // +kubebuilder:validation:Optional
    Parameters []Parameter `json:"parameters,omitempty"`
}
```

## Implementation Requirements

### File Structure
Generate files in the following locations:
- **Types**: `/ark/api/v1alpha1/{resource}_types.go`
- **Controller** (if requested): `/ark/internal/controller/{resource}_controller.go`
- **Webhook** (if requested): `/ark/internal/webhook/v1/{resource}_webhook.go`
- **Sample** (always): `/config/samples/ark_v1alpha1_{resource}.yaml`

### Must Include
1. **Package declaration**: Matching the API version
2. **Imports**: Only necessary imports from k8s.io and metav1
3. **Complete type definitions**: Spec, Status, Config, and any Ref types
4. **List type**: With proper TypeMeta and ListMeta

### Must Follow
1. **ARK Patterns**: Use established ValueSource, Parameter, and common type patterns
2. **Validation**: Proper kubebuilder validation annotations
3. **Documentation**: Clear field documentation with usage examples
4. **Consistency**: Match existing CRD naming and structure conventions

## Request Parameters

Please specify:
- **Resource Name**: The name of the CRD (PascalCase, e.g., "DataProcessor")
- **Purpose**: Brief description of what this resource manages
- **Configuration Type**: Simple config vs polymorphic config (specify modes if polymorphic)
- **References**: Any references to other CRDs needed
- **Special Features**: Any unique requirements or patterns needed
- **Generate Controller**: Whether to create controller scaffold
- **Generate Webhook**: Whether to create admission webhook
- **Custom Phases**: If different from standard phases are needed

## Deliverables

After generation, provide:
1. **Complete types file** with all necessary structures
2. **Sample YAML** showing typical usage
3. **Next steps checklist** for integration
4. **Controller scaffold** (if requested)
5. **Webhook scaffold** (if requested)

## Quality Checklist

Ensure the generated CRD:
- [ ] Follows all ARK naming conventions
- [ ] Uses common types from `common_types.go`
- [ ] Has proper kubebuilder annotations
- [ ] Includes comprehensive field documentation
- [ ] Has appropriate validation rules
- [ ] Includes standard lifecycle fields (phase)
- [ ] Uses ValueSource for configurable values
- [ ] Has proper print columns for kubectl output
- [ ] Includes both resource and list types
- [ ] Has proper SchemeBuilder registration

CRD to generate: $ARGUMENTS