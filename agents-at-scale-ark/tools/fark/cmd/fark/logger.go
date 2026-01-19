package main

import (
	"go.uber.org/zap"
	"go.uber.org/zap/zapcore"
)

func initLogger() *zap.Logger {
	return initLoggerWithVerbose(false)
}

func initLoggerWithVerbose(verbose bool) *zap.Logger {
	if !verbose {
		return zap.NewNop()
	}

	return buildLogger()
}

func buildLogger() *zap.Logger {
	config := zap.NewProductionConfig()

	// Set default log level to info
	config.Level = zap.NewAtomicLevelAt(zap.InfoLevel)

	// Configure to output to stderr
	config.OutputPaths = []string{"stderr"}
	config.ErrorOutputPaths = []string{"stderr"}

	// Use console encoding for better readability
	config.Encoding = "console"
	config.EncoderConfig = zap.NewDevelopmentEncoderConfig()
	config.EncoderConfig.TimeKey = "time"
	config.EncoderConfig.EncodeTime = zapcore.TimeEncoderOfLayout("15:04:05")
	config.EncoderConfig.LevelKey = ""      // Hide log level
	config.EncoderConfig.EncodeCaller = nil // Disable caller info
	config.EncoderConfig.StacktraceKey = "" // Disable stacktrace

	logger, err := config.Build()
	if err != nil {
		panic(err)
	}

	return logger

}

func getLogger(config *Config, verbose, silent, jsonOutput bool) *zap.Logger {
	if silent {
		return zap.NewNop()
	}
	if !verbose {
		return zap.NewNop()
	}
	return initLoggerWithVerbose(true)
}
