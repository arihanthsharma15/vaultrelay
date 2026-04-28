package selfcheck

import (
	"context"
	"database/sql"
	"fmt"
	"net/http"
	"strings"
	"time"

	_ "github.com/lib/pq"
)

type Result struct {
	Name    string
	Passed  bool
	Message string
}

func CheckSecretNonEmpty(secret string) Result {
	if secret == "" {
		return Result{
			Name:    "secret_non_empty",
			Passed:  false,
			Message: "VAULTRELAY_SECRET is empty",
		}
	}
	return Result{
		Name:    "secret_non_empty",
		Passed:  true,
		Message: "secret key is set",
	}
}

func CheckGuardianReachable(url string) Result {
	httpURL := strings.Replace(url, "ws://", "http://", 1)
	httpURL = strings.Replace(httpURL, "wss://", "https://", 1)
	httpURL = strings.TrimSuffix(httpURL, "/ws") + "/health"

	client := &http.Client{Timeout: 5 * time.Second}
	resp, err := client.Get(httpURL)
	if err != nil {
		return Result{
			Name:    "guardian_reachable",
			Passed:  false,
			Message: fmt.Sprintf("Guardian unreachable: %v", err),
		}
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		return Result{
			Name:    "guardian_reachable",
			Passed:  false,
			Message: fmt.Sprintf("Guardian returned %d", resp.StatusCode),
		}
	}

	return Result{
		Name:    "guardian_reachable",
		Passed:  true,
		Message: "Guardian is reachable",
	}
}

func CheckDBConnection(dsn string) Result {
	db, err := sql.Open("postgres", dsn)
	if err != nil {
		return Result{
			Name:    "db_connection",
			Passed:  false,
			Message: fmt.Sprintf("Failed to open DB: %v", err),
		}
	}
	defer db.Close()

	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()

	if err := db.PingContext(ctx); err != nil {
		return Result{
			Name:    "db_connection",
			Passed:  false,
			Message: fmt.Sprintf("DB ping failed: %v", err),
		}
	}

	return Result{
		Name:    "db_connection",
		Passed:  true,
		Message: "DB connection successful",
	}
}

func CheckDBReadOnly(dsn string) Result {
	db, err := sql.Open("postgres", dsn)
	if err != nil {
		return Result{
			Name:    "db_readonly",
			Passed:  false,
			Message: fmt.Sprintf("Failed to open DB: %v", err),
		}
	}
	defer db.Close()

	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()

	_, err = db.ExecContext(ctx,
		"CREATE TABLE IF NOT EXISTS _vaultrelay_writecheck (id INT)",
	)
	if err != nil {
		return Result{
			Name:    "db_readonly",
			Passed:  true,
			Message: "DB user is read-only",
		}
	}

	// If we got here write succeeded — not read only
	_, _ = db.ExecContext(ctx, "DROP TABLE IF EXISTS _vaultrelay_writecheck")
	return Result{
		Name:    "db_readonly",
		Passed:  false,
		Message: "DB user has write permissions — use a read-only user",
	}
}

func RunAll(secret, guardianURL, dsn string) []Result {
	return []Result{
		CheckSecretNonEmpty(secret),
		CheckGuardianReachable(guardianURL),
		CheckDBConnection(dsn),
		CheckDBReadOnly(dsn),
	}
}
