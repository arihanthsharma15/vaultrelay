package unit

import (
	"testing"

	"github.com/arihanthsharma15/vaultrelay/sentry/internal/tunnel"
)

func TestNewClient(t *testing.T) {
	handler := func(query string, requestID string) (string, error) {
		return "{}", nil
	}

	client := tunnel.NewClient(
		"tenant-123",
		"secret",
		"ws://localhost:8000/ws",
		handler,
	)

	if client == nil {
		t.Error("expected client to be created")
	}
}

func TestMessageTypes(t *testing.T) {
	if tunnel.TypeHeartbeat != "heartbeat" {
		t.Error("wrong heartbeat type")
	}
	if tunnel.TypeQuery != "query" {
		t.Error("wrong query type")
	}
	if tunnel.TypeResult != "result" {
		t.Error("wrong result type")
	}
	if tunnel.TypeError != "error" {
		t.Error("wrong error type")
	}
}

func TestReconnectConstants(t *testing.T) {
	if tunnel.ReconnectDelay <= 0 {
		t.Error("ReconnectDelay must be positive")
	}
	if tunnel.HeartbeatInterval <= 0 {
		t.Error("HeartbeatInterval must be positive")
	}
	if tunnel.MaxReconnectDelay < tunnel.ReconnectDelay {
		t.Error("MaxReconnectDelay must be >= ReconnectDelay")
	}
}
