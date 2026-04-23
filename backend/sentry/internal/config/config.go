package config

import (
	"fmt"
	"os"
)

type Config struct {
	TenantID    string
	Secret      string
	DBDSN       string
	GuardianURL string
	RowLimit    int
	QueryTimeout int
}

func Load() (*Config, error) {
	cfg := &Config{
		TenantID:     os.Getenv("VAULTRELAY_TENANT_ID"),
		Secret:       os.Getenv("VAULTRELAY_SECRET"),
		DBDSN:        os.Getenv("DB_DSN"),
		GuardianURL:  os.Getenv("GUARDIAN_URL"),
		RowLimit:     1000,
		QueryTimeout: 30,
	}

	if cfg.TenantID == "" {
		return nil, fmt.Errorf("VAULTRELAY_TENANT_ID is required")
	}
	if cfg.Secret == "" {
		return nil, fmt.Errorf("VAULTRELAY_SECRET is required")
	}
	if cfg.DBDSN == "" {
		return nil, fmt.Errorf("DB_DSN is required")
	}
	if cfg.GuardianURL == "" {
		return nil, fmt.Errorf("GUARDIAN_URL is required")
	}

	return cfg, nil
}
