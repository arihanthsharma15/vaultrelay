## VaultRelay — Build Progress

> **Current Phase:** Phase 3 — Hardening
> **Last Updated:** June 19, 2026
> **Stack:** Guardian (Python/FastAPI) + Sentry (Go)

---

# What is VaultRelay?

VaultRelay is a zero-trust middleware platform that enables secure natural-language querying of SQL databases without exposing those databases to the public internet.

The platform consists of two components:

### Guardian

Cloud-hosted FastAPI service responsible for:

* Authentication
* NL-to-SQL generation
* Schema-aware prompting
* Query validation
* PII redaction
* Audit logging
* Request routing

### Sentry

Customer-hosted Go agent responsible for:

* Secure outbound tunnel creation
* Query validation
* Database execution
* Result delivery

No inbound firewall rules are required on customer infrastructure.

---

# Current Status

## Guardian (FastAPI)

| Feature                         | Status    |
| ------------------------------- | --------- |
| FastAPI application             | ✅ Done    |
| Health endpoint                 | ✅ Done    |
| Environment validation          | ✅ Done    |
| SQLAlchemy integration          | ✅ Done    |
| Tenant models and migrations    | ✅ Done    |
| API key authentication          | ✅ Done    |
| WebSocket tunnel server         | ✅ Done    |
| HMAC message signing            | ✅ Done    |
| Heartbeat handling              | ✅ Done    |
| Groq-powered NL-to-SQL          | ✅ Done    |
| Schema registry                 | ✅ Done    |
| PII redaction engine            | ✅ Done    |
| Redis rate limiting             | ✅ Done    |
| Audit logging                   | ✅ Done    |
| Request correlation             | ✅ Done    |
| Multi-turn conversation context | ⬜ Planned |

---

## Sentry (Go)

| Feature                            | Status    |
| ---------------------------------- | --------- |
| Go service                         | ✅ Done    |
| Health endpoint                    | ✅ Done    |
| Configuration loader               | ✅ Done    |
| Startup self-checks                | ✅ Done    |
| PostgreSQL connection pool         | ✅ Done    |
| Query execution                    | ✅ Done    |
| Row limits                         | ✅ Done    |
| Query timeout                      | ✅ Done    |
| Result size limits                 | ✅ Done    |
| SQL validation                     | ✅ Done    |
| WebSocket tunnel client            | ✅ Done    |
| Heartbeat system                   | ✅ Done    |
| Auto reconnect                     | ✅ Done    |
| Graceful shutdown                  | ✅ Done    |
| Guardian ↔ Sentry query round-trip | ✅ Done    |
| MySQL support                      | ⬜ Planned |
| SQL Server support                 | ⬜ Planned |

---

# End-to-End Validation

Validated against a seeded development database containing customer and order records.

Successfully tested:

* Customer retrieval queries
* Filtered customer queries
* Aggregation queries
* GROUP BY queries
* JOIN queries
* Guardian ↔ Sentry communication
* HMAC-signed tunnel communication
* PII redaction workflow
* Full NL → SQL → Database → Response pipeline

Example execution flow:

User Question
↓
Guardian (NL → SQL)
↓
SQL Validation
↓
HMAC-Signed WebSocket Tunnel
↓
Sentry
↓
PostgreSQL Execution
↓
JSON Result Set
↓
PII Redaction
↓
Safe Response Returned

---

# Test Coverage

| Service  | Tests | Status    |
| -------- | ----- | --------- |
| Guardian | 55    | ✅ Passing |
| Sentry   | 22    | ✅ Passing |

Local quality gate:

```bash
./scripts/test-all.sh
```

Latest Result:

✅ Guardian lint passing

✅ Guardian tests passing

✅ Sentry formatting passing

✅ Sentry vet passing

✅ Sentry tests passing

✅ All checks passing

---

# Tech Stack

| Component  | Technology           |
| ---------- | -------------------- |
| Guardian   | Python 3.12, FastAPI |
| Sentry     | Go 1.22              |
| Database   | PostgreSQL 16        |
| Cache      | Redis 7              |
| LLM        | Groq                 |
| ORM        | SQLAlchemy           |
| Migrations | Alembic              |
| Containers | Docker               |
| CI/CD      | GitHub Actions       |

---

# Architecture

User

↓ REST API

Guardian (FastAPI)

↓ NL-to-SQL (Groq)

↓ SQL Validation

↓ HMAC-Signed WebSocket Tunnel

Sentry (Go)

↓ SQL Validation

↓ PostgreSQL Execution

↑ JSON Results

Guardian

↓ PII Redaction

↓ Audit Logging

User

---

# Roadmap

## Phase 1 — Foundation

✅ Complete

* Guardian service
* Sentry agent
* PostgreSQL integration
* Docker deployment
* API authentication
* WebSocket tunnel
* SQL validation
* Query execution pipeline

---

## Phase 2 — Intelligence

✅ Complete

* Groq-powered NL-to-SQL
* Schema registry
* Schema-aware prompting
* PII redaction
* Redis rate limiting
* Audit logging
* Request correlation
* Guardian ↔ Sentry end-to-end query execution
* Validation against seeded development datasets

---

## Phase 3 — Hardening

🔄 Planned

### Intelligence

* Multi-turn conversation context
* Query confidence scoring
* Query history

### Database Support

* MySQL support
* SQL Server support

### Security & Platform

* RBAC
* OAuth 2.0 + PKCE
* MFA
* Secret rotation
* Multi-region deployment
* Security assessment
* Load testing
* Operator dashboard

---

## Phase 4 — Stabilisation

📋 Planned

* Self-service onboarding
* Public API documentation
* SDKs
* Webhooks
* Multi-database routing
* Audit log exports
* SLA monitoring
* Status page

---

# Next Milestone

Deploy VaultRelay on AWS using separate Guardian and Sentry instances and publish a complete end-to-end deployment walkthrough till phase 2. 

---

*VaultRelay · June 2026*



## Branch Strategy

| Branch | Purpose |
|---|---|
| `main` | Production ready. Phase complete code only. |
| `develop` | Integration branch. All features merge here. |
| `feature/*` | Individual feature work. PRs into develop. |
| `chore/*` | Setup, config, tooling. PRs into develop. |
| `docs/*` | Documentation only. PRs into main. |