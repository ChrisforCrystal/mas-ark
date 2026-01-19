/* Copyright 2025. McKinsey & Company */

package v1alpha1

import (
	metav1 "k8s.io/apimachinery/pkg/apis/meta/v1"
)

// EDIT THIS FILE!  THIS IS SCAFFOLDING FOR YOU TO OWN!
// NOTE: json tags are required.  Any new fields you add must have json tags for the fields to be serialized.

// EvaluatorSpec defines the configuration for an evaluator that can assess query performance.
// This allows query evaluations to be executed by different evaluation frameworks and systems,
// rather than the built-in evaluation engine.
// Evaluators work as services that process evaluation requests for queries and provide
// performance assessments and scoring.
type EvaluatorSpec struct {
	// Address specifies how to reach the evaluator service
	// +kubebuilder:validation:Required
	Address ValueSource `json:"address"`

	// Description provides human-readable information about this evaluator
	Description string `json:"description,omitempty"`

	// Selector configuration for automatic query evaluation
	// +kubebuilder:validation:Optional
	Selector *ResourceSelector `json:"selector,omitempty"`

	// Parameters to pass to evaluation requests
	// +kubebuilder:validation:Optional
	Parameters []Parameter `json:"parameters,omitempty"`
}

type EvaluatorStatus struct {
	// +kubebuilder:validation:Optional
	// LastResolvedAddress contains the actual resolved address value
	LastResolvedAddress string `json:"lastResolvedAddress,omitempty"`
	Phase               string `json:"phase,omitempty"`
	Message             string `json:"message,omitempty"`
}

// +kubebuilder:object:root=true
// +kubebuilder:subresource:status
// +kubebuilder:printcolumn:name="Phase",type=string,JSONPath=`.status.phase`
// +kubebuilder:printcolumn:name="Address",type=string,JSONPath=`.status.lastResolvedAddress`
// +kubebuilder:printcolumn:name="Age",type=date,JSONPath=`.metadata.creationTimestamp`

type Evaluator struct {
	metav1.TypeMeta   `json:",inline"`
	metav1.ObjectMeta `json:"metadata,omitempty"`

	Spec   EvaluatorSpec   `json:"spec,omitempty"`
	Status EvaluatorStatus `json:"status,omitempty"`
}

// +kubebuilder:object:root=true

// EvaluatorList contains a list of Evaluator.
type EvaluatorList struct {
	metav1.TypeMeta `json:",inline"`
	metav1.ListMeta `json:"metadata,omitempty"`
	Items           []Evaluator `json:"items"`
}

func init() {
	SchemeBuilder.Register(&Evaluator{}, &EvaluatorList{})
}
