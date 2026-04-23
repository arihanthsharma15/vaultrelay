package db

import (
	"context"
	"database/sql"
	"fmt"
	"time"
)

const (
	DefaultRowLimit    = 1000
	DefaultTimeout     = 30 * time.Second
	MaxResultSizeBytes = 10 * 1024 * 1024 // 10MB
)

type QueryResult struct {
	Columns []string        `json:"columns"`
	Rows    [][]interface{} `json:"rows"`
	RowCount int            `json:"row_count"`
}

func (p *Pool) ExecuteQuery(
	ctx context.Context,
	query string,
	rowLimit int,
) (*QueryResult, error) {
	if rowLimit <= 0 || rowLimit > 50000 {
		rowLimit = DefaultRowLimit
	}

	// Enforce timeout
	ctx, cancel := context.WithTimeout(ctx, DefaultTimeout)
	defer cancel()

	rows, err := p.db.QueryContext(ctx, query)
	if err != nil {
		return nil, fmt.Errorf("query failed: %w", err)
	}
	defer rows.Close()

	// Get column names
	columns, err := rows.Columns()
	if err != nil {
		return nil, fmt.Errorf("failed to get columns: %w", err)
	}

	var resultRows [][]interface{}
	totalSize := 0

	for rows.Next() {
		if len(resultRows) >= rowLimit {
			break
		}

		// Scan row
		values := make([]interface{}, len(columns))
		valuePtrs := make([]interface{}, len(columns))
		for i := range values {
			valuePtrs[i] = &values[i]
		}

		if err := rows.Scan(valuePtrs...); err != nil {
			return nil, fmt.Errorf("failed to scan row: %w", err)
		}

		// Convert to safe types
		row := make([]interface{}, len(columns))
		for i, v := range values {
			row[i] = convertValue(v)
			totalSize += estimateSize(row[i])
		}

		// Check result size limit
		if totalSize > MaxResultSizeBytes {
			return nil, fmt.Errorf(
				"result set exceeds 10MB limit",
			)
		}

		resultRows = append(resultRows, row)
	}

	if err := rows.Err(); err != nil {
		return nil, fmt.Errorf("row iteration error: %w", err)
	}

	return &QueryResult{
		Columns:  columns,
		Rows:     resultRows,
		RowCount: len(resultRows),
	}, nil
}

func convertValue(v interface{}) interface{} {
	switch val := v.(type) {
	case []byte:
		return string(val)
	case time.Time:
		return val.Format(time.RFC3339)
	case *sql.NullString:
		if val.Valid {
			return val.String
		}
		return nil
	default:
		return val
	}
}

func estimateSize(v interface{}) int {
	switch val := v.(type) {
	case string:
		return len(val)
	case []byte:
		return len(val)
	default:
		return 8
	}
}
