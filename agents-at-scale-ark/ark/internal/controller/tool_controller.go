/* Copyright 2025. McKinsey & Company */

package controller

import (
	"context"
	"fmt"

	"k8s.io/apimachinery/pkg/runtime"
	ctrl "sigs.k8s.io/controller-runtime"
	"sigs.k8s.io/controller-runtime/pkg/client"

	arkv1alpha1 "mckinsey.com/ark/api/v1alpha1"
)

type ToolReconciler struct {
	client.Client
	Scheme *runtime.Scheme
}

// +kubebuilder:rbac:groups=ark.mckinsey.com,resources=tools,verbs=get;list;watch;create;update;patch;delete
// +kubebuilder:rbac:groups=ark.mckinsey.com,resources=tools/status,verbs=get;update;patch
// +kubebuilder:rbac:groups=ark.mckinsey.com,resources=tools/finalizers,verbs=update

func (r *ToolReconciler) Reconcile(ctx context.Context, req ctrl.Request) (ctrl.Result, error) {
	tool := &arkv1alpha1.Tool{}
	if err := r.Get(ctx, req.NamespacedName, tool); err != nil {
		return ctrl.Result{}, client.IgnoreNotFound(err)
	}

	if tool.Status.State == arkv1alpha1.ToolStateReady {
		return ctrl.Result{}, nil
	}

	return r.updateToolStatus(ctx, tool, arkv1alpha1.ToolStateReady, "Tool configuration is valid")
}

func (r *ToolReconciler) updateToolStatus(ctx context.Context, tool *arkv1alpha1.Tool, state, message string) (ctrl.Result, error) {
	tool.Status.State = state
	tool.Status.Message = message

	if err := r.Status().Update(ctx, tool); err != nil {
		return ctrl.Result{}, fmt.Errorf("failed to update tool status: %v", err)
	}

	return ctrl.Result{}, nil
}

func (r *ToolReconciler) SetupWithManager(mgr ctrl.Manager) error {
	return ctrl.NewControllerManagedBy(mgr).For(&arkv1alpha1.Tool{}).Named("tool").Complete(r)
}
