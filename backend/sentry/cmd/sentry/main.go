package main

import (
	"context"
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"os"
	"os/signal"
	"syscall"

	"github.com/arihanthsharma15/vaultrelay/sentry/internal/config"
	"github.com/arihanthsharma15/vaultrelay/sentry/internal/db"
	"github.com/arihanthsharma15/vaultrelay/sentry/internal/health"
	"github.com/arihanthsharma15/vaultrelay/sentry/internal/selfcheck"
	"github.com/arihanthsharma15/vaultrelay/sentry/internal/tunnel"
	"github.com/arihanthsharma15/vaultrelay/sentry/internal/validator"
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

	// Initialize DB pool
	pool, err := db.NewPool(cfg.DBDSN)
	if err != nil {
		log.Fatalf("Failed to create DB pool: %v", err)
	}
	defer pool.Close()
	log.Println("Database pool initialized")

	// Context for graceful shutdown
	ctx, cancel := context.WithCancel(context.Background())
	defer cancel()

	// Handle SIGTERM and SIGINT
	sigCh := make(chan os.Signal, 1)
	signal.Notify(sigCh, syscall.SIGTERM, syscall.SIGINT)
	go func() {
		sig := <-sigCh
		log.Printf("Received signal %v. Shutting down...", sig)
		cancel()
	}()

	// Query handler — validates and executes SQL
	queryHandler := func(query string, requestID string) (string, error) {
		result := validator.ValidateSQL(query)
		if !result.Valid {
			return "", fmt.Errorf("invalid SQL: %s", result.Message)
		}

		qResult, err := pool.ExecuteQuery(ctx, query, cfg.RowLimit)
		if err != nil {
			return "", fmt.Errorf("execution failed: %w", err)
		}

		data, err := json.Marshal(qResult)
		if err != nil {
			return "", fmt.Errorf("serialization failed: %w", err)
		}

		log.Printf(
			"Query executed: request_id=%s rows=%d",
			requestID,
			qResult.RowCount,
		)
		return string(data), nil
	}

	// Start tunnel client
	client := tunnel.NewClient(
		cfg.TenantID,
		cfg.Secret,
		cfg.GuardianURL,
		queryHandler,
	)
	go client.Start(ctx)
	log.Printf("Tunnel client started: guardian=%s", cfg.GuardianURL)

	// Start health check server
	mux := http.NewServeMux()
	mux.HandleFunc("/health", health.Handler)

	server := &http.Server{
		Addr:    "127.0.0.1:9101",
		Handler: mux,
	}

	go func() {
		<-ctx.Done()
		log.Println("Shutting down health server...")
		server.Shutdown(context.Background())
	}()

	log.Println("Health check listening on 127.0.0.1:9101")
	if err := server.ListenAndServe(); err != http.ErrServerClosed {
		log.Fatalf("Health server error: %v", err)
	}

	log.Println("Sentry shutdown complete.")
}
