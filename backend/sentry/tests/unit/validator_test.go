package unit

import (
	"testing"

	"github.com/arihanthsharma15/vaultrelay/sentry/internal/validator"
)

func TestValidSQL(t *testing.T) {
	result := validator.ValidateSQL("SELECT * FROM users LIMIT 10")
	if !result.Valid {
		t.Errorf("expected valid, got: %s", result.Message)
	}
}

func TestEmptyQuery(t *testing.T) {
	result := validator.ValidateSQL("")
	if result.Valid {
		t.Error("expected invalid for empty query")
	}
}

func TestNonSelectRejected(t *testing.T) {
	queries := []string{
		"INSERT INTO users VALUES (1, 'test')",
		"UPDATE users SET name = 'x'",
		"DELETE FROM users",
		"DROP TABLE users",
		"CREATE TABLE test (id INT)",
		"ALTER TABLE users ADD COLUMN x INT",
		"TRUNCATE TABLE users",
	}
	for _, q := range queries {
		result := validator.ValidateSQL(q)
		if result.Valid {
			t.Errorf("expected invalid for: %s", q)
		}
	}
}

func TestBlockedKeywordInSelect(t *testing.T) {
	// SELECT with embedded DROP
	result := validator.ValidateSQL(
		"SELECT * FROM users; DROP TABLE users",
	)
	if result.Valid {
		t.Error("expected invalid for multi-statement query")
	}
}

func TestCommentInjectionRejected(t *testing.T) {
	result := validator.ValidateSQL("SELECT * FROM users -- comment")
	if result.Valid {
		t.Error("expected invalid for comment injection")
	}
}

func TestMultipleStatementsRejected(t *testing.T) {
	result := validator.ValidateSQL(
		"SELECT 1; SELECT 2",
	)
	if result.Valid {
		t.Error("expected invalid for multiple statements")
	}
}

func TestSelectWithJoin(t *testing.T) {
	result := validator.ValidateSQL(
		"SELECT u.name, o.total FROM users u JOIN orders o ON u.id = o.user_id",
	)
	if !result.Valid {
		t.Errorf("expected valid JOIN query, got: %s", result.Message)
	}
}

func TestSelectWithSubquery(t *testing.T) {
	result := validator.ValidateSQL(
		"SELECT * FROM users WHERE id IN (SELECT user_id FROM orders)",
	)
	if !result.Valid {
		t.Errorf("expected valid subquery, got: %s", result.Message)
	}
}

func TestStoredProcedureRejected(t *testing.T) {
	result := validator.ValidateSQL("SELECT xp_cmdshell('dir')")
	if result.Valid {
		t.Error("expected invalid for stored procedure pattern")
	}
}
