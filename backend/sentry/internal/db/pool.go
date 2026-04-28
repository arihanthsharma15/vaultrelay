package db

import (
	"context"
	"database/sql"
	"fmt"
	"time"

	_ "github.com/lib/pq"
)

const (
	MinConnections  = 2
	MaxConnections  = 20
	ConnMaxLifetime = 30 * time.Minute
	ConnMaxIdleTime = 5 * time.Minute
	PingTimeout     = 5 * time.Second
)

type Pool struct {
	db *sql.DB
}

func NewPool(dsn string) (*Pool, error) {
	db, err := sql.Open("postgres", dsn)
	if err != nil {
		return nil, fmt.Errorf("failed to open DB: %w", err)
	}

	// Configure pool
	db.SetMaxOpenConns(MaxConnections)
	db.SetMaxIdleConns(MinConnections)
	db.SetConnMaxLifetime(ConnMaxLifetime)
	db.SetConnMaxIdleTime(ConnMaxIdleTime)

	// Verify connection
	ctx, cancel := context.WithTimeout(context.Background(), PingTimeout)
	defer cancel()

	if err := db.PingContext(ctx); err != nil {
		return nil, fmt.Errorf("failed to ping DB: %w", err)
	}

	return &Pool{db: db}, nil
}

func (p *Pool) DB() *sql.DB {
	return p.db
}

func (p *Pool) Ping(ctx context.Context) error {
	return p.db.PingContext(ctx)
}

func (p *Pool) Close() error {
	return p.db.Close()
}

func (p *Pool) Stats() sql.DBStats {
	return p.db.Stats()
}
