/* Copyright 2025. McKinsey & Company */

package common

import (
	"context"
	"fmt"
	"path"

	corev1 "k8s.io/api/core/v1"
	"k8s.io/apimachinery/pkg/types"
	arkv1alpha1 "mckinsey.com/ark/api/v1alpha1"
	"sigs.k8s.io/controller-runtime/pkg/client"
)

// ResolveServiceReference builds the correct URL from service reference components,
func ResolveServiceReference(ctx context.Context, k8sClient client.Client, serviceRef *arkv1alpha1.ServiceReference, defaultNamespace string) (string, error) {
	namespace := serviceRef.Namespace
	if namespace == "" {
		namespace = defaultNamespace
	}

	var service corev1.Service
	key := types.NamespacedName{
		Name:      serviceRef.Name,
		Namespace: namespace,
	}

	if err := k8sClient.Get(ctx, key, &service); err != nil {
		return "", fmt.Errorf("failed to get service %s/%s: %w", namespace, serviceRef.Name, err)
	}

	// Find the port
	var port int32
	if serviceRef.Port != "" {
		// Find port by name
		found := false
		for _, p := range service.Spec.Ports {
			if p.Name == serviceRef.Port {
				port = p.Port
				found = true
				break
			}
		}
		if !found {
			return "", fmt.Errorf("port %s not found in service %s/%s", serviceRef.Port, namespace, serviceRef.Name)
		}
	} else {
		// Use first port if no port specified
		if len(service.Spec.Ports) == 0 {
			return "", fmt.Errorf("service %s/%s has no ports", namespace, serviceRef.Name)
		}
		port = service.Spec.Ports[0].Port
	}

	// Standard Kubernetes service DNS
	baseURL := fmt.Sprintf("http://%s.%s.svc.cluster.local:%d", serviceRef.Name, namespace, port)
	if serviceRef.Path != "" {
		return baseURL + path.Join("/", serviceRef.Path), nil
	}

	return baseURL, nil
}
