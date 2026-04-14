package unit

import (
	"net/http"
	"net/http/httptest"
	"testing"

	"github.com/arihanthsharma15/vaultrelay/sentry/internal/health"
)

func TestHealthHandler(t *testing.T) {
	req := httptest.NewRequest(http.MethodGet, "/health", nil)
	rec := httptest.NewRecorder()

	health.Handler(rec, req)

	if rec.Code != http.StatusOK {
		t.Errorf("expected 200 got %d", rec.Code)
	}
}
