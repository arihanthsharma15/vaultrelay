package unit

import (
	"testing"

	"github.com/arihanthsharma15/vaultrelay/sentry/internal/db"
	"github.com/arihanthsharma15/vaultrelay/sentry/internal/validator"
)

func TestQueryValidationBeforeExecution(t *testing.T) {
	result := validator.ValidateSQL("SELECT * FROM users LIMIT 10")
	if !result.Valid {
		t.Errorf("expected valid query, got: %s", result.Message)
	}
}

func TestQueryRejectedBeforeExecution(t *testing.T) {
	result := validator.ValidateSQL("DROP TABLE users")
	if result.Valid {
		t.Error("expected DROP to be rejected")
	}
}

func TestQueryResultStructure(t *testing.T) {
	result := db.QueryResult{
		Columns:  []string{"id", "name", "email"},
		Rows:     [][]interface{}{{1, "Arihanth", "test@test.com"}},
		RowCount: 1,
	}
	if len(result.Columns) != 3 {
		t.Errorf("expected 3 columns, got %d", len(result.Columns))
	}
	if result.RowCount != 1 {
		t.Errorf("expected 1 row, got %d", result.RowCount)
	}
}
