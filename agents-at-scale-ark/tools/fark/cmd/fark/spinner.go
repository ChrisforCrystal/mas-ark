package main

import (
	"fmt"
	"os"
	"time"
)

// Spinner represents a simple command-line spinner.
type Spinner struct {
	stopChan chan struct{}
	doneChan chan struct{}
	frames   []string
	interval time.Duration
	active   bool
}

var defaultSpinnerFrames = []string{"—", "\\", "|", "/"}

// NewSpinner creates a new Spinner with default frames and interval.
func NewSpinner() *Spinner {
	return &Spinner{
		stopChan: make(chan struct{}),
		doneChan: make(chan struct{}),
		frames:   defaultSpinnerFrames,
		interval: 100 * time.Millisecond,
		active:   false,
	}
}

// Start begins the spinner animation.
func (s *Spinner) Start() {
	if s.active {
		return
	}

	s.active = true
	go func() {
		defer close(s.doneChan)
		for i := 0; ; i++ {
			select {
			case <-s.stopChan:
				fmt.Fprint(os.Stderr, "\r ") // Clear the spinner
				return
			case <-time.After(s.interval):
				fmt.Fprintf(os.Stderr, "\r%s", s.frames[i%len(s.frames)])
			}
		}
	}()
}

// Stop halts the spinner animation.
func (s *Spinner) Stop() {
	if !s.active {
		return
	}

	close(s.stopChan)
	<-s.doneChan // Wait for the spinner goroutine to finish
	s.active = false
	s.stopChan = make(chan struct{}) // Reset for next start
	s.doneChan = make(chan struct{}) // Reset for next start
}
