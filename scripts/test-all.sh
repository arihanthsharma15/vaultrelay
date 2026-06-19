#!/usr/bin/env bash

set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
guardian_dir="$repo_root/backend/guardian"
sentry_dir="$repo_root/backend/sentry"

if [[ -x "$guardian_dir/venv/bin/python" ]]; then
  guardian_python="$guardian_dir/venv/bin/python"
else
  guardian_python="${PYTHON:-python3}"
fi

echo "==> Guardian lint"
(
  cd "$guardian_dir"
  "$guardian_python" -m ruff check app tests
)

echo "==> Guardian tests"
(
  cd "$guardian_dir"
  "$guardian_python" -m pytest -q
)

echo "==> Sentry formatting"
unformatted="$(
  cd "$sentry_dir"
  gofmt -l .
)"
if [[ -n "$unformatted" ]]; then
  echo "The following Go files need gofmt:"
  echo "$unformatted"
  exit 1
fi

echo "==> Sentry vet"
(
  cd "$sentry_dir"
  go vet ./...
)

echo "==> Sentry tests"
(
  cd "$sentry_dir"
  go test ./...
)

echo "==> All checks passed"
