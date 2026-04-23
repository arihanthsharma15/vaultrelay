# VaultRelay — Build Progress

> **Current Phase:** Phase 1 — Foundation
> **Last Updated:** April 2026
> **Stack:** Guardian (Python/FastAPI) + Sentry (Go)

---

## What is VaultRelay?

A zero-trust middleware platform that enables secure natural-language querying of legacy SQL databases without ever exposing those databases to the public internet.

Two components:
- **Guardian** — Cloud gateway (FastAPI). Handles auth, NL-to-SQL, PII redaction, query routing.
- **Sentry** — Local agent (Go). Runs on customer infrastructure. Executes validated SQL against local database.

---

## Branch Strategy

| Branch | Purpose |
|---|---|
| `main` | Production ready. Phase complete code only. |
| `develop` | Integration branch. All features merge here. |
| `feature/*` | Individual feature work. PRs into develop. |
| `chore/*` | Setup, config, tooling. PRs into develop. |
| `docs/*` | Documentation only. PRs into main. |

---

## PR History

### Infrastructure
| PR | Branch | Description | Status |
|---|---|---|---|
| #1 | `chore/monorepo-scaffold` | Folder structure, .gitignore, README, docker-compose | ✅ Merged |
| #2 | `chore/ci-workflows` | Guardian CI + Sentry CI GitHub Actions pipelines | ✅ Merged |

### Guardian — FastAPI (Python)
| PR | Branch | Description | Status |
|---|---|---|---|
| #3 | `chore/guardian-scaffold` | FastAPI app, /health endpoint, Dockerfile, requirements | ✅ Merged |
| #5 | `feature/guardian-config` | Pydantic settings, env validation, .env setup | ✅ Merged |
| #6 | `feature/guardian-db-models` | SQLAlchemy async engine, Tenant model, Alembic migrations | ✅ Merged |
| #7 | `feature/api-key-auth` | API key generation, SHA-256 hashing, auth dependency | ✅ Merged |
| #9 | `feature/websocket-tunnel-server` | WS endpoint, HMAC signing, connection manager, heartbeat | ✅ Merged |

### Sentry — Go
| PR | Branch | Description | Status |
|---|---|---|---|
| #4 | `chore/sentry-scaffold` | Go module, config loader, /health handler, Dockerfile | ✅ Merged |
| #10 | `feature/sentry-startup-selfcheck` | 4 startup checks, refuses to start on failure | ✅ Merged |
| #11 | `feature/sentry-db-pool` | Connection pool, query executor, row/size/timeout limits | ✅ Merged |

---

## Current State

### Guardian (/backend/guardian)
| Feature | Status |
|---|---|
| FastAPI app boots | ✅ Done |
| /health endpoint | ✅ Done |
| Pydantic config management | ✅ Done |
| Environment variable validation | ✅ Done |
| SQLAlchemy async engine | ✅ Done |
| Tenant model + migrations | ✅ Done |
| APIKey model | ✅ Done |
| API key generation + hashing | ✅ Done |
| Auth middleware (X-API-Key) | ✅ Done |
| WebSocket tunnel server | ✅ Done |
| HMAC message signing | ✅ Done |
| Heartbeat handling | ✅ Done |
| Query routing by tenant | ⬜ Pending |
| NL-to-SQL (Claude Sonnet) | ⬜ Phase 2 |
| PII redaction engine | ⬜ Phase 2 |
| Rate limiting (Redis) | ⬜ Phase 2 |
| Audit logging | ⬜ Phase 2 |
| RBAC — Viewer, Analyst, Admin | ⬜ Phase 3 |

### Sentry (/backend/sentry)
| Feature | Status |
|---|---|
| Go binary boots | ✅ Done |
| /health endpoint (127.0.0.1:9101) | ✅ Done |
| Config loader (env variables) | ✅ Done |
| Startup self-check (4 checks) | ✅ Done |
| PostgreSQL connection pool | ✅ Done |
| Query executor + row limits | ✅ Done |
| Query timeout (30s default) | ✅ Done |
| Result size limit (10MB) | ✅ Done |
| SQL validator (SELECT only) | ⬜ Next — PR #12 |
| WebSocket tunnel client | ⬜ Next — PR #13 |
| Query execution end to end | ⬜ Next — PR #14 |
| Graceful shutdown (SIGTERM) | ⬜ Pending |

---

## Test Coverage

| Service | Test Type | Count | Status |
|---|---|---|---|
| Guardian | Unit tests | 21 | ✅ Passing |
| Sentry | Unit tests | 6 | ✅ Passing |

---

## Phase Roadmap

### Phase 1 — Foundation
Weeks 1-6 · In Progress
✅ Monorepo scaffold
✅ CI/CD pipelines
✅ Guardian skeleton
✅ Sentry skeleton
✅ Guardian config management
✅ Guardian DB models + Alembic
✅ API key auth
✅ WebSocket tunnel server (Guardian)
✅ Sentry startup self-check
✅ PostgreSQL connection pool (Sentry)
⬜ SQL validator (Sentry)           — PR #12
⬜ WebSocket tunnel client (Sentry) — PR #13
⬜ Query execution end to end       — PR #14
⬜ Integration tests                — PR #15

### Phase 2 — Intelligence
Weeks 7-12 · Not Started
⬜ Claude Sonnet NL-to-SQL integration
⬜ Schema metadata registry
⬜ SQL validation layer (Guardian)
⬜ PII redaction engine
⬜ Rate limiting — Redis backed
⬜ Audit logging
⬜ Multi-turn conversation context
⬜ MySQL + SQL Server support in Sentry

### Phase 3 — Hardening
Weeks 13-18 · Not Started
⬜ External penetration test
⬜ RBAC — Viewer, Analyst, Admin roles
⬜ OAuth 2.0 + PKCE
⬜ MFA for Admin role
⬜ Secret rotation — zero downtime
⬜ Multi-region Guardian deployment
⬜ Query confidence scoring
⬜ Operator dashboard
⬜ GDPR + HIPAA self assessment
⬜ Load testing at 2x peak

### Phase 4 — Stabilisation
Weeks 19-26 · Not Started
⬜ Self-service onboarding flow
⬜ Public REST API docs + OpenAPI spec
⬜ Python + Node.js SDKs
⬜ Webhook support
⬜ Multi-database routing per tenant
⬜ Audit log export — CSV + JSON
⬜ SLA monitoring + PagerDuty
⬜ Status page

---

## Tech Stack

| Component | Language | Framework | Key Libraries |
|---|---|---|---|
| Guardian | Python 3.12 | FastAPI 0.115 | SQLAlchemy 2.0, Pydantic 2.8, Alembic, asyncpg |
| Sentry | Go 1.22 | stdlib | net/http, database/sql, lib/pq |
| Database | PostgreSQL 16 | — | — |
| Cache | Redis 7 | — | — |
| CI/CD | — | GitHub Actions | ruff, pytest, go vet, go test |

---

## Next Up

**PR #12 — feature/sentry-sql-validator**
SELECT only enforcement. Any DDL, DML, or stored procedure call rejected before execution.

**PR #13 — feature/sentry-tunnel-client**
Sentry connects to Guardian via WebSocket. HMAC signed messages. Heartbeat every 30 seconds. Auto reconnect.

**PR #14 — feature/sentry-query-execution**
Full query flow. Guardian sends SQL to Sentry, Sentry executes, results back to Guardian.

**PR #15 — feature/integration-tests**
End to end round trip. Phase 1 complete.

---

*VaultRelay · Build Progress · April 2026*
