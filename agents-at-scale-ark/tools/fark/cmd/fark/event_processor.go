package main

import (
	"context"
	"encoding/json"
	"fmt"
	"net/http"

	"k8s.io/apimachinery/pkg/apis/meta/v1/unstructured"

	arkv1alpha1 "mckinsey.com/ark/api/v1alpha1"
)

type EventProcessor struct {
	config *Config
}

func NewEventProcessor(config *Config) *EventProcessor {
	return &EventProcessor{config: config}
}

func (ep *EventProcessor) StreamQueryEvents(ctx context.Context, w http.ResponseWriter, flusher http.Flusher, queryName string) {
	watcher := NewQueryWatcher(ep.config, queryName, ep.config.Namespace, ep.config.Logger)
	resultChan, err := watcher.Watch(ctx)
	if err != nil {
		ep.writeStreamError(w, flusher, err)
		return
	}

	for result := range resultChan {
		if result.Error != nil {
			ep.writeStreamError(w, flusher, result.Error)
			return
		}

		if result.IsEvent {
			ep.writeKubernetesEvent(w, flusher, result.Event)
			continue
		}

		if result.Query != nil {
			ep.writeQueryEvent(w, flusher, result.Query, result.Phase)
			if result.Done {
				return
			}
		}
	}

	ep.writeStreamEvent(w, flusher, map[string]any{"type": "completed"})
}

func (ep *EventProcessor) writeQueryEvent(w http.ResponseWriter, flusher http.Flusher, query *arkv1alpha1.Query, phase string) {
	// Log token usage if available
	logTokenUsage(ep.config.Logger, query, phase)

	eventData := map[string]any{
		"type":  "query",
		"phase": phase,
		"query": query,
	}
	ep.writeStreamEvent(w, flusher, eventData)
}

func (ep *EventProcessor) writeKubernetesEvent(w http.ResponseWriter, flusher http.Flusher, eventObj *unstructured.Unstructured) {
	eventType, _, _ := unstructured.NestedString(eventObj.Object, "type")
	reason, _, _ := unstructured.NestedString(eventObj.Object, "reason")
	message, _, _ := unstructured.NestedString(eventObj.Object, "message")
	source, _, _ := unstructured.NestedString(eventObj.Object, "source", "component")

	eventData := map[string]any{
		"type":      "kubernetes_event",
		"eventType": eventType,
		"reason":    reason,
		"message":   message,
		"source":    source,
		"object":    eventObj.Object,
	}

	ep.writeStreamEvent(w, flusher, eventData)
}

func (ep *EventProcessor) writeStreamEvent(w http.ResponseWriter, flusher http.Flusher, data map[string]any) {
	if jsonData, err := json.Marshal(data); err == nil {
		fmt.Fprintf(w, "data: %s\n\n", jsonData)
		flusher.Flush()
	}
}

func (ep *EventProcessor) writeStreamError(w http.ResponseWriter, flusher http.Flusher, err error) {
	errorData := map[string]any{
		"type":    "error",
		"message": err.Error(),
	}
	ep.writeStreamEvent(w, flusher, errorData)
}
