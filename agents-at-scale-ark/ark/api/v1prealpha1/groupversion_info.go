/* Copyright 2025. McKinsey & Company */

// Package v1prealpha1 contains API Schema definitions for the ark v1prealpha1 API group.
// +kubebuilder:object:generate=true
// +groupName=ark.mckinsey.com
package v1prealpha1

import (
	"k8s.io/apimachinery/pkg/runtime/schema"
	"sigs.k8s.io/controller-runtime/pkg/scheme"
)

var (
	GroupVersion  = schema.GroupVersion{Group: "ark.mckinsey.com", Version: "v1prealpha1"}
	SchemeBuilder = &scheme.Builder{GroupVersion: GroupVersion}
	AddToScheme   = SchemeBuilder.AddToScheme
)
