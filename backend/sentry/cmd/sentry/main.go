package main

import (
	"log"
	"net/http"
	"os"

	"github.com/arihanthsharma15/vaultrelay/sentry/internal/config"
	"github.com/arihanthsharma15/vaultrelay/sentry/internal/health"
	"github.com/arihanthsharma15/vaultrelay/sentry/internal/selfcheck"
)

func main() {
	// Load config
	cfg, err := config.Load()
	if err != nil {
		log.Fatalf("Config error: %v", err)
	}

	// Run startup self-checks
	log.Println("Running startup self-checks...")
	results := selfcheck.RunAll(cfg.Secret, cfg.GuardianURL, cfg.DBDSN)

	allPassed := true
	for _, r := range results {
		if r.Passed {
			log.Printf("  ✓ %s: %s", r.Name, r.Message)
		} else {
			log.Printf("  ✗ %s: %s", r.Name, r.Message)
			allPassed = false
		}
	}

	if !allPassed {
		log.Fatal("Startup self-checks failed. Refusing to start.")
		os.Exit(1)
	}

	log.Println("All checks passed. Starting Sentry...")

	// Start health check server
	mux := http.NewServeMux()
	mux.HandleFunc("/health", health.Handler)

	addr := "127.0.0.1:9101"
	log.Printf("Health check listening on %s", addr)

	if err := http.ListenAndServe(addr, mux); err != nil {
		log.Fatalf("Failed to start health server: %v", err)
	}
}
