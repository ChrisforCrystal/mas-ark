/* Copyright 2025. McKinsey & Company */

package common

import (
	"context"
	"strings"
	"testing"

	corev1 "k8s.io/api/core/v1"
	metav1 "k8s.io/apimachinery/pkg/apis/meta/v1"
	"k8s.io/apimachinery/pkg/runtime"
	"k8s.io/apimachinery/pkg/util/intstr"
	arkv1alpha1 "mckinsey.com/ark/api/v1alpha1"
	"sigs.k8s.io/controller-runtime/pkg/client"
	"sigs.k8s.io/controller-runtime/pkg/client/fake"
)

func createTestServices() []*corev1.Service {
	return []*corev1.Service{
		{
			ObjectMeta: metav1.ObjectMeta{
				Name:      "test-service",
				Namespace: "test-namespace",
			},
			Spec: corev1.ServiceSpec{
				Ports: []corev1.ServicePort{
					{
						Name:       "http",
						Port:       80,
						TargetPort: intstr.FromInt(8080),
						Protocol:   corev1.ProtocolTCP,
					},
					{
						Name:       "https",
						Port:       443,
						TargetPort: intstr.FromInt(8443),
						Protocol:   corev1.ProtocolTCP,
					},
				},
			},
		},
		{
			ObjectMeta: metav1.ObjectMeta{
				Name:      "single-port-service",
				Namespace: "test-namespace",
			},
			Spec: corev1.ServiceSpec{
				Ports: []corev1.ServicePort{
					{
						Port:       9000,
						TargetPort: intstr.FromInt(9000),
						Protocol:   corev1.ProtocolTCP,
					},
				},
			},
		},
		{
			ObjectMeta: metav1.ObjectMeta{
				Name:      "no-port-service",
				Namespace: "test-namespace",
			},
			Spec: corev1.ServiceSpec{
				Ports: []corev1.ServicePort{},
			},
		},
	}
}

type testCase struct {
	name             string
	serviceRef       *arkv1alpha1.ServiceReference
	defaultNamespace string
	expected         string
	expectError      bool
	errorContains    string
}

func getTestCases() []testCase {
	return []testCase{
		{
			name: "basic service reference with named port",
			serviceRef: &arkv1alpha1.ServiceReference{
				Name: "test-service",
				Port: "http",
			},
			defaultNamespace: "test-namespace",
			expected:         "http://test-service.test-namespace.svc.cluster.local:80",
		},
		{
			name: "service reference with explicit namespace",
			serviceRef: &arkv1alpha1.ServiceReference{
				Name:      "test-service",
				Namespace: "test-namespace",
				Port:      "https",
			},
			defaultNamespace: "other-namespace",
			expected:         "http://test-service.test-namespace.svc.cluster.local:443",
		},
		{
			name: "service reference with path",
			serviceRef: &arkv1alpha1.ServiceReference{
				Name: "test-service",
				Port: "http",
				Path: "api/v1",
			},
			defaultNamespace: "test-namespace",
			expected:         "http://test-service.test-namespace.svc.cluster.local:80/api/v1",
		},
		{
			name: "service reference with path starting with slash",
			serviceRef: &arkv1alpha1.ServiceReference{
				Name: "test-service",
				Port: "http",
				Path: "/api/v1",
			},
			defaultNamespace: "test-namespace",
			expected:         "http://test-service.test-namespace.svc.cluster.local:80/api/v1",
		},
		{
			name: "service reference without port uses first port",
			serviceRef: &arkv1alpha1.ServiceReference{
				Name: "test-service",
			},
			defaultNamespace: "test-namespace",
			expected:         "http://test-service.test-namespace.svc.cluster.local:80",
		},
		{
			name: "single port service without port specification",
			serviceRef: &arkv1alpha1.ServiceReference{
				Name: "single-port-service",
			},
			defaultNamespace: "test-namespace",
			expected:         "http://single-port-service.test-namespace.svc.cluster.local:9000",
		},
		{
			name: "non-existent service",
			serviceRef: &arkv1alpha1.ServiceReference{
				Name: "non-existent-service",
			},
			defaultNamespace: "test-namespace",
			expectError:      true,
			errorContains:    "failed to get service",
		},
		{
			name: "non-existent port",
			serviceRef: &arkv1alpha1.ServiceReference{
				Name: "test-service",
				Port: "non-existent-port",
			},
			defaultNamespace: "test-namespace",
			expectError:      true,
			errorContains:    "port non-existent-port not found",
		},
		{
			name: "service with no ports",
			serviceRef: &arkv1alpha1.ServiceReference{
				Name: "no-port-service",
			},
			defaultNamespace: "test-namespace",
			expectError:      true,
			errorContains:    "has no ports",
		},
	}
}

func validateTestResult(t *testing.T, tt testCase, result string, err error) {
	if tt.expectError {
		validateError(t, tt, err)
	} else {
		validateSuccess(t, tt, result, err)
	}
}

func validateError(t *testing.T, tt testCase, err error) {
	if err == nil {
		t.Errorf("expected error but got none")
		return
	}
	if tt.errorContains == "" {
		return
	}
	if !strings.Contains(err.Error(), tt.errorContains) {
		t.Errorf("expected error containing %q, got %q", tt.errorContains, err.Error())
	}
}

func validateSuccess(t *testing.T, tt testCase, result string, err error) {
	if err != nil {
		t.Errorf("unexpected error: %v", err)
		return
	}
	if result != tt.expected {
		t.Errorf("expected %q, got %q", tt.expected, result)
	}
}

func TestResolveServiceReference(t *testing.T) {
	scheme := runtime.NewScheme()
	_ = corev1.AddToScheme(scheme)

	services := createTestServices()
	serviceObjects := make([]client.Object, len(services))
	for i, service := range services {
		serviceObjects[i] = service
	}

	testClient := fake.NewClientBuilder().
		WithScheme(scheme).
		WithObjects(serviceObjects...).
		Build()

	tests := getTestCases()

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			result, err := ResolveServiceReference(context.Background(), testClient, tt.serviceRef, tt.defaultNamespace)
			validateTestResult(t, tt, result, err)
		})
	}
}
