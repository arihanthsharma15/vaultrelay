package unit

import (
	"testing"

	"github.com/arihanthsharma15/vaultrelay/sentry/internal/selfcheck"
)

func TestCheckSecretNonEmpty_Pass(t *testing.T) {
	result := selfcheck.CheckSecretNonEmpty("my-secret")
	if !result.Passed {
		t.Errorf("expected pass, got fail: %s", result.Message)
	}
}

func TestCheckSecretNonEmpty_Fail(t *testing.T) {
	result := selfcheck.CheckSecretNonEmpty("")
	if result.Passed {
		t.Errorf("expected fail for empty secret")
	}
}

func TestCheckGuardianReachable_Fail(t *testing.T) {
	result := selfcheck.CheckGuardianReachable("ws://localhost:19999")
	if result.Passed {
		t.Errorf("expected fail for unreachable Guardian")
	}
}
