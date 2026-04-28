package validator

import (
	"fmt"
	"strings"
	"unicode"
)

var blockedKeywords = []string{
	"INSERT", "UPDATE", "DELETE", "DROP", "CREATE",
	"ALTER", "TRUNCATE", "REPLACE", "MERGE", "EXEC",
	"EXECUTE", "CALL", "GRANT", "REVOKE", "COMMIT",
	"ROLLBACK", "SAVEPOINT", "LOCK", "UNLOCK",
}

var blockedPatterns = []string{
	"--",
	"/*",
	"XP_",
	"SP_",
}

type ValidationResult struct {
	Valid   bool
	Message string
}

func ValidateSQL(query string) ValidationResult {
	if query == "" {
		return ValidationResult{
			Valid:   false,
			Message: "query is empty",
		}
	}

	trimmed := strings.TrimSpace(query)
	upper := strings.ToUpper(trimmed)

	// Must start with SELECT
	if !strings.HasPrefix(upper, "SELECT") {
		return ValidationResult{
			Valid:   false,
			Message: fmt.Sprintf("only SELECT statements allowed, got: %s", firstWord(upper)),
		}
	}

	// Check for blocked keywords
	words := tokenize(upper)
	for _, word := range words {
		for _, blocked := range blockedKeywords {
			if word == blocked {
				return ValidationResult{
					Valid:   false,
					Message: fmt.Sprintf("blocked keyword detected: %s", word),
				}
			}
		}
	}

	// Check for blocked patterns against uppercased query
	for _, pattern := range blockedPatterns {
		if strings.Contains(upper, pattern) {
			return ValidationResult{
				Valid:   false,
				Message: fmt.Sprintf("blocked pattern detected: %s", pattern),
			}
		}
	}

	// Check for multiple statements
	if containsMultipleStatements(trimmed) {
		return ValidationResult{
			Valid:   false,
			Message: "multiple statements not allowed",
		}
	}

	return ValidationResult{
		Valid:   true,
		Message: "query is valid",
	}
}

func firstWord(s string) string {
	fields := strings.Fields(s)
	if len(fields) == 0 {
		return ""
	}
	return fields[0]
}

func tokenize(s string) []string {
	return strings.FieldsFunc(s, func(r rune) bool {
		return !unicode.IsLetter(r) && !unicode.IsDigit(r) && r != '_'
	})
}

func containsMultipleStatements(query string) bool {
	inString := false
	quoteChar := rune(0)

	for _, ch := range query {
		if inString {
			if ch == quoteChar {
				inString = false
			}
			continue
		}
		if ch == '\'' || ch == '"' {
			inString = true
			quoteChar = ch
			continue
		}
		if ch == ';' {
			return true
		}
	}
	return false
}
