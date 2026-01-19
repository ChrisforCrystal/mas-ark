package main

import (
	"context"
	"fmt"
	"os"
	"os/signal"
	"syscall"
	"time"

	"go.uber.org/zap"
	"slices"
)

func setupQueryContext(timeout time.Duration, logger *zap.Logger) context.Context {
	ctx, cancel := context.WithTimeout(context.Background(), timeout)

	sigChan := make(chan os.Signal, 1)
	signal.Notify(sigChan, syscall.SIGINT, syscall.SIGTERM)

	ctx, signalCancel := context.WithCancel(ctx)

	go func() {
		defer cancel()
		defer signalCancel()
		select {
		case <-sigChan:
			logger.Info("Received interrupt signal, cancelling query...")
			signalCancel()
		case <-ctx.Done():
		}
	}()

	return ctx
}

func validateTargetType(targetType string) error {
	validTypes := []string{"agent", "team", "model", "tool"}
	if slices.Contains(validTypes, targetType) {
		return nil
	}
	return fmt.Errorf("invalid target type '%s'. Valid types: %v", targetType, validTypes)
}
