# VaultRelay

> Zero-trust middleware for natural-language querying of legacy SQL databases.

VaultRelay lets users ask questions in plain English while keeping customer
databases private. Guardian generates and validates SQL in the cloud; Sentry
runs inside the customer network, validates the query again, and executes it
with bounded access.

## Architecture

- **Guardian** (`backend/guardian`) - FastAPI gateway for authentication,
  Groq-powered NL-to-SQL, schema context, rate limiting, PII redaction, audit
  logging, and WebSocket tunnel management.
- **Sentry** (`backend/sentry`) - Go agent for startup checks, outbound tunnel
  connectivity, SQL validation, PostgreSQL execution, and resource limits.
- **PostgreSQL** - Tenant metadata, audit data, and the development query
  target.
- **Redis** - Sliding-window request rate limiting.

```text
User -> Guardian -> validated SQL -> outbound WebSocket tunnel -> Sentry
User <- Guardian <- redacted result <- query execution <- PostgreSQL
```

## Current Status

Phase 2 is in progress. The following Guardian capabilities are implemented:

- Groq NL-to-SQL generation and SELECT-only validation
- Schema metadata context and PII marking
- Pattern-based and column-based PII redaction
- Redis sliding-window rate limiting
- Database-backed audit logging

Sentry includes PostgreSQL pooling, query limits, SQL validation, tunnel
reconnection, heartbeat handling, startup self-checks, and graceful shutdown.

See [docs/PROGRESS.md](docs/PROGRESS.md) for the detailed roadmap.

### Prototype Limitations

- The NL-to-SQL endpoint currently returns validated SQL; dispatching it to a
  connected Sentry and awaiting the result is not wired yet.
- Guardian verifies HMAC-signed tunnel messages, but Sentry-side message
  signing still needs to be implemented.
- The development tunnel uses `ws://`; production deployment requires TLS with
  `wss://`.

## Test The Project

Install the Guardian dependencies in `backend/guardian/venv`, then run:

```bash
./scripts/test-all.sh
```

The command runs:

- Ruff over Guardian application and test code
- All Guardian unit and HTTP endpoint tests
- `gofmt` verification for Sentry
- `go vet ./...`
- All Sentry tests

Current verified result:

```text
Guardian: 55 passed
Sentry:   22 passed
```

## Run Locally

Set a Groq API key and start the development stack:

```bash
export GROQ_API_KEY="your-key"
docker-compose up --build
```

Guardian is exposed at `http://localhost:8000`, with health status at
`http://localhost:8000/health`.

## Repository Structure

```text
vaultrelay/
├── backend/
│   ├── guardian/       # Python/FastAPI gateway
│   └── sentry/         # Go local agent
├── docs/               # PRD and progress documentation
├── scripts/            # Development and validation scripts
├── .github/workflows/  # Guardian and Sentry CI
└── docker-compose.yml  # Local development stack
```

## Product Requirements

See [docs/VaultRelay-PRD-1.md](docs/VaultRelay-PRD-1.md) for the full product
requirements and security model.
