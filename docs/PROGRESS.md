# VaultRelay — Build Progress

> **Current Phase:** Phase 2 — Intelligence
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
| #13 | `feature/sentry-sql-validator` | SELECT only enforcement, injection prevention, 9 tests | ✅ Merged |
| #14 | `feature/sentry-tunnel-client` | WebSocket client, heartbeat, auto reconnect, query handler | ✅ Merged |
| #15 | `feature/sentry-query-execution` | Wire everything, graceful shutdown, full query flow | ✅ Merged |

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
| NL-to-SQL (Claude Sonnet) | ⬜ Phase 2 — PR #18 |
| Schema metadata registry | ⬜ Phase 2 — PR #19 |
| PII redaction engine | ⬜ Phase 2 — PR #20 |
| Rate limiting (Redis) | ⬜ Phase 2 — PR #21 |
| Audit logging | ⬜ Phase 2 — PR #22 |
| Multi-turn conversation context | ⬜ Phase 2 — PR #23 |
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
| SQL validator (SELECT only) | ✅ Done |
| WebSocket tunnel client | ✅ Done |
| Heartbeat every 30s | ✅ Done |
| Auto reconnect with backoff | ✅ Done |
| Query execution end to end | ✅ Done |
| Graceful shutdown (SIGTERM) | ✅ Done |
| MySQL + SQL Server support | ⬜ Phase 2 |

---

## Test Coverage

| Service | Test Type | Count | Status |
|---|---|---|---|
| Guardian | Unit tests | 21 | ✅ Passing |
| Sentry | Unit tests | 15 | ✅ Passing |

---

## Phase Roadmap

### Phase 1 — Foundation
Weeks 1-6 · ✅ COMPLETE
_Last Phase 1 PR:_ **#17**
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
✅ SQL validator (Sentry)
✅ WebSocket tunnel client (Sentry)
✅ Query execution end to end
✅ Graceful shutdown

---

### Phase 2 — Intelligence
Weeks 7-12 · 🔄 In Progress
⬜ PR #18 — Claude Sonnet NL-to-SQL integration
⬜ PR #19 — Schema metadata registry
⬜ PR #20 — PII redaction engine
⬜ PR #21 — Rate limiting — Redis backed
⬜ PR #22 — Audit logging
⬜ PR #23 — Multi-turn conversation context
⬜ PR #24 — MySQL + SQL Server support in Sentry

---

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

---

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
| Sentry | Go 1.22 | stdlib | net/http, database/sql, lib/pq, gorilla/websocket |
| Database | PostgreSQL 16 | — | — |
| Cache | Redis 7 | — | — |
| CI/CD | — | GitHub Actions | ruff, pytest, go vet, go test |

---

## Architecture
User
↓ REST API (X-API-Key auth)
Guardian (FastAPI — Cloud)
↓ NL-to-SQL (Claude Sonnet)
↓ SQL validation (SELECT only)
↓ WebSocket tunnel (HMAC signed)
Sentry (Go — Customer infrastructure)
↓ SQL validation (last line of defence)
↓ PostgreSQL connection pool
↓ Query execution (30s timeout, 1000 row limit)
↑ JSON result set
Guardian
↓ PII redaction
↓ Audit logging
User ← safe result

---

## Next Up — Phase 2 Start

**PR #18 — `feature/guardian-nl-to-sql`**
Integrate Claude Sonnet API. Accept natural language query. Generate SQL. Return to user.

All Phase 2 feature PRs merge into `develop`.

---

*VaultRelay · Build Progress · April 2026*
