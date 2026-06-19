# VaultRelay

> Zero-trust middleware for secure natural-language querying of private SQL databases.

VaultRelay enables users to query databases using plain English without exposing those databases to the public internet. The platform converts natural language into validated SQL, executes queries through a secure outbound-only tunnel, and returns redacted results to the user.

## Architecture

### Guardian (`backend/guardian`)

Cloud-hosted FastAPI gateway responsible for:

* API authentication
* Groq-powered NL-to-SQL generation
* Schema-aware prompt construction
* SQL validation and safety checks
* Redis-backed rate limiting
* PII redaction
* Audit logging
* WebSocket tunnel management

### Sentry (`backend/sentry`)

Customer-hosted Go agent responsible for:

* Startup self-checks
* Outbound-only WebSocket tunnel
* Secondary SQL validation
* PostgreSQL query execution
* Query timeout enforcement
* Result-size and row-count limits
* Automatic reconnection and heartbeat handling

### Infrastructure

* PostgreSQL — tenant metadata, audit data, and development datasets
* Redis — sliding-window rate limiting
* Docker Compose — local development environment

```text
User
 ↓
Guardian (FastAPI)
 ↓
Groq NL→SQL
 ↓
SQL Validation
 ↓
HMAC-Signed WebSocket Tunnel
 ↓
Sentry (Go)
 ↓
PostgreSQL
 ↓
Query Result
 ↓
PII Redaction
 ↓
User
```

## Current Status

### Phase 2 — Intelligence

✅ Complete

Implemented capabilities:

* End-to-end NL-to-SQL query execution
* Groq-powered SQL generation
* Schema-aware context injection
* SELECT-only SQL enforcement
* Guardian-side SQL validation
* Sentry-side SQL validation
* HMAC-signed tunnel messaging
* Request/response correlation across tunnel
* Pattern-based PII redaction
* Column-level PII suppression
* Redis sliding-window rate limiting
* Audit logging
* WebSocket heartbeat monitoring
* Automatic tunnel reconnection
* PostgreSQL query execution with bounded limits

### Verified End-to-End Flow

```text
Question
 ↓
Groq
 ↓
Guardian Validation
 ↓
WebSocket Tunnel
 ↓
Sentry Validation
 ↓
PostgreSQL
 ↓
PII Redaction
 ↓
Response
```

## Quality Gates

Run the complete validation suite:

```bash
./scripts/test-all.sh
```

The script executes:

* Ruff linting
* Guardian unit tests
* Guardian integration tests
* gofmt verification
* go vet
* Sentry unit tests

Current verified result:

```text
Guardian: 55 tests passing
Sentry:   22 tests passing
```

## Run Locally

```bash
export GROQ_API_KEY="your-key"

docker compose up --build
```

Services:

```text
Guardian  -> http://localhost:8000
Postgres  -> localhost:5432
Redis     -> localhost:6379
```

Health endpoint:

```text
http://localhost:8000/health
```

## Repository Structure

```text
vaultrelay/
├── backend/
│   ├── guardian/
│   └── sentry/
├── docs/
├── scripts/
├── .github/workflows/
└── docker-compose.yml
```

## Current Limitations

* Development environment uses static schema metadata instead of tenant-managed schema discovery.
* Conversation memory for multi-turn database interactions is not yet implemented.
* Production deployment still requires TLS (`wss://`) and secret management hardening.
* MySQL and SQL Server support are planned for Phase 3.

## Documentation

* `docs/PROGRESS.md` — roadmap and implementation status
* `docs/VaultRelay-PRD-1.md` — product requirements document

## Tech Stack

### Guardian

* Python 3.12
* FastAPI
* SQLAlchemy
* PostgreSQL
* Redis
* Groq API

### Sentry

* Go 1.22
* gorilla/websocket
* database/sql
* lib/pq

### Infrastructure

* Docker
* Docker Compose
* GitHub Actions
