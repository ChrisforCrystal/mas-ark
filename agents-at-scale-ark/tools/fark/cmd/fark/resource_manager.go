package main

import (
	"context"
	"fmt"

	metav1 "k8s.io/apimachinery/pkg/apis/meta/v1"
	"k8s.io/apimachinery/pkg/runtime"
	"k8s.io/apimachinery/pkg/runtime/schema"
)

type ResourceManager struct {
	config *Config
}

func NewResourceManager(config *Config) *ResourceManager {
	return &ResourceManager{config: config}
}

func (rm *ResourceManager) ListResources(resourceType ResourceType, namespace string) ([]map[string]any, error) {
	gvr := GetGVR(resourceType)
	return rm.listResourcesByGVR(gvr, namespace)
}

func (rm *ResourceManager) listResourcesByGVR(gvr schema.GroupVersionResource, namespace string) ([]map[string]any, error) {
	ctx := context.Background()
	unstructuredList, err := rm.config.DynamicClient.Resource(gvr).Namespace(namespace).List(ctx, metav1.ListOptions{})
	if err != nil {
		return nil, fmt.Errorf("failed to list resources: %v", err)
	}

	var resources []map[string]any
	for _, item := range unstructuredList.Items {
		resourceMap := make(map[string]any)
		if err := runtime.DefaultUnstructuredConverter.FromUnstructured(item.Object, &resourceMap); err != nil {
			continue
		}
		resources = append(resources, resourceMap)
	}

	return resources, nil
}

func (rm *ResourceManager) GetResourceNames(resourceType ResourceType, namespace string) ([]string, error) {
	gvr := GetGVR(resourceType)
	resources, err := rm.config.DynamicClient.Resource(gvr).Namespace(namespace).List(
		context.TODO(),
		metav1.ListOptions{},
	)
	if err != nil {
		return nil, err
	}

	var names []string
	for _, item := range resources.Items {
		if name := item.GetName(); name != "" {
			names = append(names, name)
		}
	}
	return names, nil
}
