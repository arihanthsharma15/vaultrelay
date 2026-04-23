package unit

import (
	"testing"

	"github.com/arihanthsharma15/vaultrelay/sentry/internal/db"
)

func TestNewPool_InvalidDSN(t *testing.T) {
	_, err := db.NewPool("invalid-dsn")
	if err == nil {
		t.Error("expected error for invalid DSN")
	}
}

func TestPoolConstants(t *testing.T) {
	if db.MinConnections <= 0 {
		t.Error("MinConnections must be positive")
	}
	if db.MaxConnections < db.MinConnections {
		t.Error("MaxConnections must be >= MinConnections")
	}
	if db.DefaultRowLimit <= 0 {
		t.Error("DefaultRowLimit must be positive")
	}
}

func TestQueryResult_Structure(t *testing.T) {
	result := db.QueryResult{
		Columns:  []string{"id", "name"},
		Rows:     [][]interface{}{{1, "test"}},
		RowCount: 1,
	}
	if result.RowCount != len(result.Rows) {
		t.Error("RowCount must match len(Rows)")
	}
}
