# VaultRelay

> Zero-trust middleware for natural-language querying of legacy SQL databases.

## Architecture

- **Guardian** — Cloud gateway (Python/FastAPI)
- **Sentry** — Local agent (Go)

## Repository Structure

vaultrelay/ ├── guardian/ # FastAPI cloud gateway ├── sentry/ # Go local agent ├── docs/ # PRD and architecture docs ├── scripts/ # Dev and deployment scripts └── .github/ # CI/CD workflows


## Development

See `docs/VaultRelay-PRD-1.md` for full product requirements.

## Phases

Phase 1 — Foundation (Weeks 1–6)
The skeleton. Everything talks to everything.

Monorepo scaffold, CI/CD setup
Guardian skeleton — FastAPI, tenant registry, API key auth
Sentry skeleton — Go binary, startup self-check, DB connection pool
WebSocket tunnel — outbound from Sentry to Guardian, HMAC signing, TLS
SQL validation — SELECT only, reject everything else
Read-only credential enforcement
Integration test harness — round trip from Guardian to Sentry and back

Exit criteria: Encrypted round-trip from NL input to SQL result confirmed.

Phase 2 — Intelligence (Weeks 7–12)
The brain. Natural language actually works.

Claude Sonnet API integrated for NL-to-SQL
Schema metadata registry — what tables/columns the LLM can see
PII redaction engine — emails, phones, SSNs, credit cards
Rate limiting — per user and per tenant, Redis backed
Audit logging — every query logged with request ID, user, timestamp
Multi-turn conversation context — 10 turn memory
MySQL and SQL Server support added to Sentry

Exit criteria: Two pilot tenants running real queries. Zero data leakage.

Phase 3 — Hardening (Weeks 13–18)
Security and compliance. No shortcuts.

External penetration test — all Critical and High findings fixed
RBAC — Viewer, Analyst, Admin roles fully implemented
OAuth 2.0 + PKCE — proper auth flow, MFA for Admin
Secret rotation — zero downtime key rotation for Sentry
Multi-region Guardian deployment — EU, US, APAC
Query confidence scoring — low confidence = clarification prompt, not execution
Operator dashboard — Sentry health, tunnel status, query volume, errors
GDPR + HIPAA self assessment complete
Load testing at 2× peak load

Exit criteria: Pen test sign-off. Compliance assessment done. Load test passing.

Phase 4 — Stabilisation (Weeks 19–26)
Production ready. Operators can self-serve.

Self-service onboarding — account creation, Sentry download, config wizard
Public REST API docs + OpenAPI spec
Python and Node.js SDKs
Webhook support — post-query callbacks
Multi-database routing per tenant
Audit log export — CSV and JSON
SLA monitoring — PagerDuty, status page
