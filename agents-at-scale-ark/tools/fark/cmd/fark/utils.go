package main

import (
	"fmt"
	"os"
	"strings"

	"github.com/spf13/cobra"
	"go.uber.org/zap"

	arkv1alpha1 "mckinsey.com/ark/api/v1alpha1"
)

func getNamespaceOrDefault(specified, defaultNs string) string {
	if specified != "" {
		return specified
	}
	return defaultNs
}

func readInputFile(filePath string) (string, error) {
	fileInfo, err := os.Stat(filePath)
	if err != nil {
		return "", fmt.Errorf("cannot access file: %v", err)
	}

	if fileInfo.Size() > 3*1024*1024 {
		return "", fmt.Errorf("file size (%d bytes) exceeds 3MB limit", fileInfo.Size())
	}

	content, err := os.ReadFile(filePath)
	if err != nil {
		return "", fmt.Errorf("cannot read file: %v", err)
	}
	return string(content), nil
}

func parseParameters(parameters []string) ([]arkv1alpha1.Parameter, error) {
	var result []arkv1alpha1.Parameter

	for _, param := range parameters {
		parts := strings.SplitN(param, "=", 2)
		if len(parts) != 2 {
			return nil, fmt.Errorf("parameter must be in key=value format, got: %s", param)
		}

		key := strings.TrimSpace(parts[0])
		value := strings.TrimSpace(parts[1])

		if key == "" {
			return nil, fmt.Errorf("parameter key cannot be empty in: %s", param)
		}

		result = append(result, arkv1alpha1.Parameter{
			Name:  key,
			Value: value,
		})
	}

	return result, nil
}

func getResourceCompletions(config *Config, resourceType, namespace string) []string {
	ns := getNamespaceOrDefault(namespace, config.Namespace)
	rm := NewResourceManager(config)

	rt := ResourceType(resourceType)
	names, err := rm.GetResourceNames(rt, ns)
	if err != nil {
		return nil
	}
	return names
}

func handleQueryError(cmd *cobra.Command, err error) error {
	if err != nil {
		cmd.SilenceUsage = true
		cmd.SilenceErrors = true
	}
	return err
}

func logTokenUsage(logger *zap.Logger, query *arkv1alpha1.Query, phase string) {
	if query.Status.TokenUsage.TotalTokens > 0 {
		actualPhase := phase
		if actualPhase == "" {
			actualPhase = query.Status.Phase
		}

		logger.Info("Query tokens",
			zap.String("query", query.Name),
			zap.String("namespace", query.Namespace),
			zap.String("phase", actualPhase),
			zap.Int64("prompt_tokens", query.Status.TokenUsage.PromptTokens),
			zap.Int64("completion_tokens", query.Status.TokenUsage.CompletionTokens),
			zap.Int64("total_tokens", query.Status.TokenUsage.TotalTokens),
		)
	}
}
