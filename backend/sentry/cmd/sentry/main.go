package main

import (
	"log"
	"net/http"

	"github.com/arihanthsharma15/vaultrelay/sentry/internal/health"
)

func main() {
	mux := http.NewServeMux()
	mux.HandleFunc("/health", health.Handler)

	addr := "127.0.0.1:9101"
	log.Printf("Sentry health check listening on %s", addr)

	if err := http.ListenAndServe(addr, mux); err != nil {
		log.Fatalf("Failed to start health server: %v", err)
	}
}
