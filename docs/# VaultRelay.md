# VaultRelay
### Product Requirements Document — v1.0 | April 2026 

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Problem Statement](#2-problem-statement)
3. [Product Vision & Goals](#3-product-vision--goals)
4. [Architecture Overview](#4-architecture-overview)
5. [Functional Requirements](#5-functional-requirements)
6. [Non-Functional Requirements](#6-non-functional-requirements)
7. [Implementation Phases](#7-implementation-phases)
8. [Edge Cases & Known Failure Modes](#8-edge-cases--known-failure-modes)
9. [Risk Register](#9-risk-register)
10. [Success Metrics](#10-success-metrics)
11. [Open Questions](#11-open-questions--decisions-required)
12. [Glossary](#12-glossary)

---

## 1. Executive Summary

VaultRelay is a zero-trust middleware platform that enables secure, natural-language querying of legacy SQL databases (PostgreSQL, MySQL, SQL Server) without ever exposing those databases to the public internet.

The system addresses a critical gap for small and medium enterprises (SMEs) that hold significant operational data in aging on-premise infrastructure yet lack the engineering resources to build secure AI integrations themselves. By combining a lightweight local agent (**Sentry**) with a cloud-hosted AI gateway (**Guardian**), VaultRelay delivers AI-powered analytics with enterprise-grade security controls.

This document defines the product vision, functional and non-functional requirements, phased delivery roadmap, and an honest assessment of edge cases and failure modes that must be mitigated before the system can be considered production-ready.

---

## 2. Problem Statement

### 2.1 Context

The majority of SMEs in sectors such as healthcare, legal, manufacturing, and retail operate mission-critical databases that were deployed well before the era of AI-driven analytics. These systems hold years of transactional, operational, and customer data but remain effectively inaccessible to modern tooling.

### 2.2 Core Pain Points

#### 🔵 Data Accessibility Gap
- No natural-language interface exists for ad-hoc querying of legacy databases.
- Business users must rely on developers or BI tools to extract insights, with turnaround ranging from hours to days.
- Structured data remains siloed even when adjacent AI tooling is adopted elsewhere in the organisation.

#### 🔴 Security Risks
- Exposing databases directly to the internet invites SQL injection, credential stuffing, and data exfiltration.
- PII and regulated data (PHI, financial records) are at high risk under naive integrations.
- Most LLM-to-database connectors in the market lack fine-grained access controls.
- Third-party AI services should never receive raw database credentials or full schema dumps.

#### 🟡 Integration Complexity
- Building secure database-to-AI pipelines requires expertise in tunnelling, authentication, and LLM prompt engineering simultaneously.
- SMEs rarely have in-house security or DevOps talent to build and maintain such connectors.
- Commercial solutions often impose cloud-residency requirements that violate data-sovereignty obligations.

### 2.3 Target Users

| User Segment | Primary Need |
|---|---|
| SME Business Analyst | Self-service natural-language queries without SQL knowledge |
| IT / Database Admin | Maintain security and control while enabling AI access |
| SaaS Platform Builder | Offer "Chat with Your Data" as an embedded product feature |
| Compliance Officer | Audit logs, PII redaction, and data-residency guarantees |
| Medical / Legal Practice | Query case/patient data with strict access controls; no cloud storage of raw records |

---

## 3. Product Vision & Goals

### 3.1 Vision Statement

> *To become the most trusted bridge between legacy data infrastructure and modern AI — enabling any organisation to unlock the intelligence within their existing databases without trading security for accessibility.*

### 3.2 Strategic Goals

- Security parity with zero-trust networking standards (NIST SP 800-207).
- Sub-3-second query round-trip latency at the 95th percentile.
- No raw database credentials or schema details transmitted to or stored in the cloud.
- Support PostgreSQL, MySQL, and SQL Server at v1.0; extensible to Oracle, SQLite, and MongoDB.
- Operators can deploy Sentry in under 30 minutes using a single Docker command.
- GDPR and HIPAA compliant by design, with configurable PII redaction.

### 3.3 Non-Goals (v1.0)

- No real-time streaming or CDC (change data capture) — batch query model only.
- No write operations to the database via natural language — read-only scope.
- No multi-tenant Sentry agent — one agent per database cluster.
- No self-hosted Guardian deployment option.
- No support for NoSQL or graph databases.

---

## 4. Architecture Overview

### 4.1 Two-Tier Design

VaultRelay is composed of two independently deployable components, architecturally isolated to enforce separation of concerns and minimise the attack surface.

| Component | Role & Responsibilities |
|---|---|
| **Sentry** (Local Agent) | Runs on customer-controlled infrastructure. Initiates outbound-only encrypted connection to Guardian. Receives validated SQL queries. Executes them against the local database. Returns result sets only — never schema or credentials. |
| **Guardian** (Cloud Gateway) | Multi-tenant cloud service. Authenticates users via OAuth 2.0 / API key. Validates and rate-limits incoming queries. Calls LLM for NL-to-SQL translation. Routes generated SQL to the correct Sentry instance via the persistent tunnel. Applies PII redaction before returning results. |

### 4.2 Communication Channel

- All Sentry-to-Guardian communication occurs over a persistent, authenticated WebSocket connection established **outbound from Sentry**.
- Encrypted in transit using TLS 1.3 minimum.
- Guardian **never** initiates inbound connections to Sentry — no inbound firewall rule is required on the client side.
- Channel heartbeats every 30 seconds with automatic reconnect logic on the Sentry side.
- Each message is signed with an HMAC derived from a per-tenant shared secret.

### 4.3 Query Lifecycle

| Step | Component | Action |
|---|---|---|
| 1 | Client | User submits natural-language query via API or web UI |
| 2 | Guardian | Authentication token validated; rate-limit counter checked |
| 3 | Guardian | Input sanitised; PII patterns detected and flagged |
| 4 | Guardian (LLM) | Query + schema context sent to Claude Sonnet; SQL generated |
| 5 | Guardian | Generated SQL reviewed against allowlist of safe operations (SELECT only) |
| 6 | Guardian → Sentry | Validated SQL dispatched over encrypted WebSocket tunnel with unique request ID |
| 7 | Sentry | SQL executed against local database with read-only credentials |
| 8 | Sentry → Guardian | Result set (JSON) returned over tunnel, referenced by request ID |
| 9 | Guardian | PII redaction applied to result set per tenant policy |
| 10 | Client | Formatted, safe response returned to requesting user |

---

## 5. Functional Requirements

### 5.1 Authentication & Identity

- **FR-AUTH-01** — Guardian must support OAuth 2.0 (Authorization Code + PKCE) and API key authentication.
- **FR-AUTH-02** — Each Sentry instance must be uniquely identified by a tenant ID and a rotatable secret key.
- **FR-AUTH-03** — Sentry must re-authenticate on reconnection; stale tokens must be rejected.
- **FR-AUTH-04** — Role-Based Access Control (RBAC) with at minimum three roles: Viewer, Analyst, Admin.
- **FR-AUTH-05** — Admin role required to register a new Sentry agent or modify schema metadata.

### 5.2 Natural Language Query Processing

- **FR-NL-01** — Guardian must accept a plain-text query string of up to 2,000 characters.
- **FR-NL-02** — Schema context (table names, column names, types — never sample data) must be provided to the LLM at query time.
- **FR-NL-03** — LLM-generated SQL must be validated syntactically before dispatch.
- **FR-NL-04** — Only SELECT statements may be generated; any DDL, DML, or DCL must be rejected.
- **FR-NL-05** — If SQL generation confidence is low, Guardian must return a clarification prompt rather than a potentially incorrect query.
- **FR-NL-06** — Guardian must support multi-turn conversation context (up to 10 prior turns) to handle follow-up queries.

### 5.3 Security Controls

- **FR-SEC-01** — PII redaction engine must detect and redact names, emails, phone numbers, NI/SSN patterns, credit card numbers, and IP addresses by default.
- **FR-SEC-02** — Tenant admins must be able to define custom redaction patterns via regex.
- **FR-SEC-03** — All queries and results must be logged with a request ID, timestamp, user ID, and redaction action taken.
- **FR-SEC-04** — Rate limiting: 60 queries per minute per user, 500 per hour per tenant (configurable).
- **FR-SEC-05** — Sentry must only accept connections from Guardian's registered IP range.
- **FR-SEC-06** — All audit logs must be immutable and signed.

### 5.4 Sentry Agent

Sentry supports two deployment modes. Operators choose based on their infrastructure. Both modes are first-class — neither is a fallback.

#### 5.4.1 Deployment Mode A — Docker Container

- **FR-SENTRY-01a** — Deployable as a Docker container with single environment-variable configuration (`VAULTRELAY_TENANT_ID`, `VAULTRELAY_SECRET`, `DB_DSN`, `GUARDIAN_URL`).
- **FR-SENTRY-01b** — Official image published to Docker Hub (`vaultrelay/sentry:latest`); pinned version tags required for production.
- **FR-SENTRY-01c** — Must support `docker-compose` single-file setup for operators running multiple services.
- **FR-SENTRY-01d** — Container must run as a non-root user (`uid 1001`) by default; root execution must be explicitly opted into and documented as insecure.
- **FR-SENTRY-01e** — Container image must pass Trivy vulnerability scan with zero Critical CVEs before any release.

**Example `docker-compose.yml` (reference):**
```yaml
services:
  sentry:
    image: vaultrelay/sentry:1.0.0
    restart: always
    user: "1001:1001"
    environment:
      VAULTRELAY_TENANT_ID: ${TENANT_ID}
      VAULTRELAY_SECRET: ${SECRET}
      DB_DSN: postgres://readonly_user:pass@localhost:5432/mydb
      GUARDIAN_URL: wss://gateway.vaultrelay.io
    network_mode: host
```

#### 5.4.2 Deployment Mode B — Linux Daemon (systemd)

For environments where Docker is unavailable or prohibited (bare-metal servers, hardened Linux installations, air-gapped systems), Sentry must be distributable as a standalone binary that integrates with `systemd`.

- **FR-SENTRY-02a** — Sentry must be compilable to a single static binary (Go or Rust target) with no runtime dependencies beyond libc.
- **FR-SENTRY-02b** — An official `sentry.service` unit file must be provided and installable via a one-line install script.
- **FR-SENTRY-02c** — The systemd service must run under a dedicated low-privilege system user (`vaultrelay-sentry`, no login shell, no home directory).
- **FR-SENTRY-02d** — The unit file must set `Restart=on-failure`, `RestartSec=5s`, and `StartLimitIntervalSec=60s` to ensure automatic recovery.
- **FR-SENTRY-02e** — The unit file must use `CapabilityBoundingSet=` and `NoNewPrivileges=true` to prevent privilege escalation.
- **FR-SENTRY-02f** — Configuration must be read from `/etc/vaultrelay/sentry.conf` (INI format) with file permissions `640` owned by `root:vaultrelay-sentry`.
- **FR-SENTRY-02g** — Logs must be emitted to `stdout` in structured JSON format, captured by `journald`. Operators can forward via `journalctl` or any log shipper.

**Reference `sentry.service` unit file:**
```ini
[Unit]
Description=VaultRelay Sentry Agent
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=vaultrelay-sentry
Group=vaultrelay-sentry
ExecStart=/usr/local/bin/vaultrelay-sentry --config /etc/vaultrelay/sentry.conf
Restart=on-failure
RestartSec=5s
StartLimitIntervalSec=60s
NoNewPrivileges=true
CapabilityBoundingSet=
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=/var/log/vaultrelay

[Install]
WantedBy=multi-user.target
```

**One-line install (Debian/Ubuntu/RHEL):**
```bash
curl -fsSL https://install.vaultrelay.io/sentry | sudo bash
```
This script: downloads the binary, creates the system user, installs the unit file, prompts for config values, and runs `systemctl enable --now vaultrelay-sentry`.

#### 5.4.3 Shared Requirements (Both Modes)

- **FR-SENTRY-03** — Must support connection pooling (min 2, max 20 connections) to the local database.
- **FR-SENTRY-04** — Must enforce a per-query row limit (default 1,000 rows; configurable up to 50,000).
- **FR-SENTRY-05** — Must enforce a query execution timeout (default 30 seconds; configurable).
- **FR-SENTRY-06** — Must expose a local health-check endpoint on `127.0.0.1:9101/health` only — never on a public interface.
- **FR-SENTRY-07** — Must emit structured JSON logs to stdout for operator consumption.
- **FR-SENTRY-08** — On startup, must validate: DB connection succeeds, DB user is read-only, Guardian URL is reachable, secret key is non-empty. Must refuse to start and exit with a descriptive error if any check fails.
- **FR-SENTRY-09** — Must support graceful shutdown: on `SIGTERM`, drain in-flight queries (up to 10 seconds), close DB connections cleanly, then exit.

### 5.5 Guardian Cloud Gateway

- **FR-GUARD-01** — Must handle at least 100 concurrent user sessions per tenant at launch.
- **FR-GUARD-02** — Must support multiple registered Sentry instances per tenant (multi-database routing).
- **FR-GUARD-03** — Must provide a REST API and a WebSocket API for client integration.
- **FR-GUARD-04** — Must expose usage analytics: query volume, latency distribution, error rates per user.
- **FR-GUARD-05** — Must support configurable data-residency settings (EU, US, APAC) for LLM API calls.

---

## 6. Non-Functional Requirements

| Requirement | Target |
|---|---|
| Query Round-Trip (P50) | < 1.5 seconds (excluding LLM inference) |
| Query Round-Trip (P95) | < 3.0 seconds |
| Guardian Uptime SLA | 99.9% monthly (< 44 min downtime/month) |
| Sentry Reconnect Time | < 5 seconds after network interruption |
| PII Redaction Latency | < 50ms overhead on result sets up to 10,000 rows |
| Concurrent Users (v1.0) | 100 per tenant, 2,000 globally |
| Data at Rest | AES-256 for all stored schema metadata and audit logs |
| Data in Transit | TLS 1.3 minimum on all channels |
| Sentry Container Size | < 150MB compressed Docker image |
| Sentry Binary Size (Daemon) | < 20MB static binary, no runtime dependencies |
| Sentry Memory Footprint | < 256MB resident under normal operation |
| Audit Log Retention | 90 days default; configurable to 7 years |
| Deployment Time — Docker | < 15 minutes from `docker pull` to first query |
| Deployment Time — Daemon | < 30 minutes via one-line install script |
| Sentry Startup Self-Check | Must complete in < 10 seconds on boot |
| Graceful Shutdown Drain | Up to 10 seconds to drain in-flight queries on SIGTERM |

---

## 7. Implementation Phases

> No phase begins without the security review from the preceding phase being signed off.

---

### Phase 1 — Foundation: Core Infrastructure
**Duration: Weeks 1–6**

**Objective:** Establish a working, encrypted tunnel with basic SQL pass-through. Internal demo only.

- Define and document the wire protocol between Sentry and Guardian (message schema, versioning, error codes).
- Implement WebSocket tunnel: outbound-only connection, HMAC message signing, TLS 1.3 enforcement.
- Build Sentry agent core: dual deployment targets — Docker container (environment-variable config) and standalone static binary for systemd daemon mode.
- Implement `sentry.service` systemd unit file with hardening flags (`NoNewPrivileges`, `ProtectSystem`, `CapabilityBoundingSet`).
- Implement startup self-check: validate DB connectivity, read-only user enforcement, Guardian reachability before accepting any queries.
- Implement graceful shutdown on SIGTERM: drain in-flight queries, close DB pool cleanly.
- Build connection pooling to PostgreSQL (shared across both deployment modes).
- Build Guardian skeleton: tenant registry, API key auth, request routing by tenant ID.
- Implement read-only SQL enforcement layer in Sentry (parse and reject non-SELECT statements).
- Write integration test harness for Sentry-to-Guardian message round-trips.
- Set up CI/CD pipeline with security linting (Semgrep, Bandit) and dependency scanning.

**Exit Criteria:** Encrypted round-trip from NL input to SQL result confirmed. Security linting passing in CI.

---

### Phase 2 — Intelligence: NL-to-SQL & Security Controls
**Duration: Weeks 7–12**

**Objective:** End-to-end NL query with PII redaction. Closed beta with two pilot customers.

- Integrate Claude Sonnet API into Guardian for NL-to-SQL translation.
- Build schema metadata registry: admin UI to define table/column allowlist sent to LLM (no sample data).
- Implement SQL validation layer: syntax check, SELECT-only enforcement, injection pattern detection.
- Build PII redaction engine: default patterns (email, phone, SSN, credit card, IP); regex extension interface.
- Implement rate limiting middleware with per-user and per-tenant counters (Redis-backed).
- Add structured audit logging: request ID, timestamp, user, query hash, redaction actions, latency.
- Implement multi-turn conversation context management (session window, 10-turn memory).
- Expand Sentry to support MySQL and SQL Server.

**Exit Criteria:** Two pilot tenants running queries in a closed environment. Zero data leakage incidents.

---

### Phase 3 — Hardening: Security, Compliance & Reliability
**Duration: Weeks 13–18**

**Objective:** Compliance-ready build. Security sign-off required to proceed to Phase 4.

- Commission external penetration test; address all Critical and High findings before phase completion.
- RBAC implementation: Viewer, Analyst, Admin roles with permission matrices.
- OAuth 2.0 + PKCE integration; MFA enforcement for Admin role.
- Sentry secret rotation workflow: zero-downtime key rotation procedure.
- Implement Guardian multi-region deployment with configurable data-residency routing.
- Build query confidence scoring: low-confidence queries return a clarification prompt instead of executing.
- Operator dashboard: Sentry health, tunnel status, query volume, error rates, latency histograms.
- Conduct GDPR/HIPAA self-assessment and produce compliance documentation.
- Load testing at 2× projected v1.0 peak load; tune connection pools and rate-limit thresholds.

**Exit Criteria:** Pen test sign-off. GDPR/HIPAA assessment complete. Load test passing at 2× peak.

---

### Phase 4 — Stabilisation: Self-Service Onboarding & Extensibility
**Duration: Weeks 19–26**

**Objective:** Feature-complete, documented, and operator-ready build.

- Self-service onboarding flow: account creation, Sentry download, configuration wizard, first-query tutorial.
- Public REST API documentation and OpenAPI spec publication.
- SDK packages for Python and Node.js with worked examples.
- Webhook support: post-query callbacks for downstream automation.
- Multi-database routing per tenant: users can target different registered Sentry instances.
- Public audit log export: CSV and JSON download for compliance teams.
- SLA monitoring and alerting: PagerDuty integration, status page.

**Exit Criteria:** Sentry deployment success rate ≥ 90% without engineering support. All documentation reviewed and published.

---

## 8. Edge Cases & Known Failure Modes

> This section is written with deliberate candor. VaultRelay sits at the intersection of natural language ambiguity, database query complexity, network reliability, and security enforcement. The following failure modes are real, not hypothetical.

---

### 8.1 NL-to-SQL Translation Failures

#### Ambiguous Natural Language

**🔴 Case:** User asks *"Show me the best customers."* — "best" is undefined. The LLM may silently assume a metric (e.g., revenue) that does not match business intent, returning a confidently wrong result with no error signal.

**Mitigation:** Guardian must detect low-confidence or undefined-metric queries and return a clarifying prompt rather than executing. Confidence scoring on generated SQL is mandatory, not optional.

**🔴 Case:** Temporal references like *"last quarter"* or *"recently"* are ambiguous without a timezone and fiscal calendar context. The LLM may generate date ranges that are off by weeks.

**Mitigation:** Tenant configuration must include timezone and fiscal year definition. These must be injected into every LLM prompt as hard context, not left to inference.

---

#### Schema Complexity Overload

**🟡 Case:** Schemas with 50+ tables and hundreds of columns will exceed LLM context windows if sent in full. Truncation will cause the model to generate SQL referencing tables it has no metadata for, silently hallucinating column names.

**Mitigation:** Schema must be chunked. Only tables relevant to the query should be selected via embedding similarity search. Irrelevant tables must never appear in the LLM prompt.

**🟡 Case:** Columns with non-descriptive names (e.g., `col_a`, `tbl_003`) provide no semantic signal to the LLM, producing incorrect column references with high confidence.

**Mitigation:** Admins must provide human-readable aliases for tables and columns in the metadata registry. Queries against unaliased schema must surface a warning to the operator.

---

#### SQL Injection via Natural Language

**🔴 Case:** A malicious user embeds SQL fragments in the natural-language query: *"Show me users; DROP TABLE users;"*. If the LLM echoes this into the generated SQL, catastrophic data loss is possible.

**Mitigation:** The SQL validation layer in Sentry must be the last line of defence — it must syntactically parse and reject **any** statement that is not a pure SELECT. The LLM is not trusted as a security control. Ever.

**🔴 Case:** Prompt injection via column values: if column data contains adversarial text designed to manipulate LLM behaviour, a future "explain this result" feature could be exploited to exfiltrate data or alter system behaviour.

**Mitigation:** Result data must never be sent back to the LLM. Explanation features must operate only on SQL and schema metadata — never on raw query results.

---

### 8.2 Network & Connectivity Failures

#### Tunnel Interruption & Message Loss

**🟡 Case:** The WebSocket tunnel drops mid-query. Guardian has dispatched SQL to Sentry; Sentry has started executing. When the tunnel reconnects, the query may execute twice, or the result may be lost entirely.

**Mitigation:** Every query must carry a globally unique idempotency key. Sentry must deduplicate and cache results for in-flight request IDs for 60 seconds after execution.

**🟡 Case:** A network partition lasts longer than Sentry's reconnect window. Queries queue up on Guardian's side. On reconnect, a burst of queued queries hits Sentry simultaneously, causing database connection pool exhaustion.

**Mitigation:** Guardian must implement a per-tenant in-flight query limit (default: 5). Queued queries must expire after 30 seconds with an appropriate error returned to the user.

---

#### Sentry Behind Strict Firewalls or Proxies

**🟡 Case:** Corporate firewalls with deep packet inspection may detect and terminate long-lived WebSocket connections. Sentry will appear connected but messages will be silently dropped — the worst failure mode, as it appears healthy.

**Mitigation:** Sentry must implement application-layer heartbeats every 15 seconds and treat missed heartbeat acknowledgements as a connection failure, triggering reconnect.

**🟡 Case:** Outbound proxies requiring NTLM or Kerberos authentication are not supported by most WebSocket libraries out of the box. Deployment will silently fail with no useful error message.

**Mitigation:** Proxy configuration (`HTTP_PROXY`, `HTTPS_PROXY`) must be explicitly supported via Sentry environment variables. NTLM proxy support must be scoped for a future release and documented as a known limitation at launch.

---

### 8.3 Database-Side Failures

#### Long-Running Query Abuse

**🔴 Case:** A user crafts a natural-language query that translates to a full-table scan with multiple JOINs on a multi-million-row database. The query consumes 100% of database CPU for minutes, blocking all other operations.

**Mitigation:** Sentry must enforce a hard query execution timeout (30 seconds default). For PostgreSQL/MySQL, statement-level timeouts must be set on the connection **before** execution — not via application-level timers, which can be bypassed.

**🟡 Case:** Row-count-based limits are not sufficient. A query returning 100 rows of 10MB BLOB columns will exceed memory limits and may crash the Sentry process.

**Mitigation:** Sentry must enforce a result set byte-size limit (default: 10MB) in addition to row limits. Large BLOB/TEXT columns must be truncated with a clear indicator in the response.

---

#### Read-Only Credential Enforcement

**🔴 Case:** Sentry is configured with database credentials that have write permissions. A SQL validation bug or LLM hallucination slips a non-SELECT statement through. Data is modified or deleted.

**Mitigation:** Sentry must connect using a dedicated read-only database user. This is a **deployment requirement, not a preference**. Sentry must validate on startup that its database user cannot execute INSERT, UPDATE, DELETE, or DDL, and **refuse to start** if it can.

**🔴 Case:** Read-only restrictions on the application user do not prevent SELECT queries that invoke stored procedures with side effects (e.g., `EXEC sp_something` in SQL Server).

**Mitigation:** Stored procedure invocations must be explicitly blocked at the SQL validation layer. The allowlist is SELECT only — not "SELECT and EXEC".

---

### 8.4 PII & Compliance Failures

#### PII Redaction Gaps

**🟡 Case:** PII redaction relies on pattern matching. Novel PII formats (non-US tax IDs, custom employee codes, proprietary identifiers) will pass through unredacted.

**Mitigation:** Default redaction must be conservative and tenant-configurable. Compliance-sensitive tenants (healthcare, legal) must complete a schema annotation step that flags PII columns explicitly, enabling column-level suppression in addition to pattern matching.

**🟡 Case:** Redaction operates on the result set returned from Sentry. But the natural-language query itself may reference PII: *"Show me all orders for john.doe@company.com."* This email is logged in the audit trail in plaintext.

**Mitigation:** Input sanitisation must apply PII detection to the incoming query string and redact it in the audit log before storage. The raw query string must never be stored in plaintext.

---

### 8.5 LLM Availability & Cost

#### Third-Party LLM Dependency

**🟡 Case:** An Anthropic API outage means no NL-to-SQL generation is possible. The entire product becomes unavailable even if Sentry and the database are fully healthy.

**Mitigation:** Guardian must implement a graceful degradation mode: if LLM inference fails, users with Analyst or Admin roles may submit raw SQL directly through the validated pass-through channel. This must be opt-in per tenant.

**🟡 Case:** LLM inference costs are variable and unbounded. A tenant running thousands of complex queries per day may generate unexpected API costs that are not surfaced until the billing cycle.

**Mitigation:** Query token budgets must be enforced. Schema context sent to the LLM must be bounded. Usage dashboards must expose per-tenant LLM token consumption in real time.

**🟡 Case:** LLM model updates by Anthropic may change SQL generation behaviour, silently breaking query accuracy for existing tenants without any deployment action taken.

**Mitigation:** Pin to a specific model version in production. Model version changes must pass a regression test suite of known queries before deployment.

---

## 9. Risk Register

| Risk | Likelihood | Impact | Owner | Mitigation |
|---|---|---|---|---|
| LLM generates incorrect SQL silently | High | High | Engineering | Confidence scoring; clarification prompts; user feedback loop |
| SQL injection via NL input | Medium | Critical | Security | Server-side SQL parser as final guard; LLM never trusted as a security control |
| Tunnel message loss during reconnect | Medium | High | Engineering | Idempotency keys; result caching; duplicate detection |
| PII leaks through redaction gaps | Medium | Critical | Security + Compliance | Column-level suppression; mandatory PII annotation for regulated tenants |
| Database overloaded by runaway queries | Medium | High | Engineering | Hard DB-level timeouts; concurrent query limits; circuit breakers |
| Anthropic API outage | Low | High | Product | Graceful degradation to raw SQL mode for power users |
| Sentry deployed with write credentials | Low | Critical | Operations | Startup self-check; deployment checklist; documentation |
| Corporate proxy blocks WebSocket | High | Medium | Engineering | App-layer heartbeats; proxy env var support; documented workarounds |
| LLM model update breaks SQL generation | Low | Medium | Engineering | Pin model version; regression test suite; canary deployments |
| Tenant schema contains PII column names | Medium | Medium | Compliance | Schema metadata never returned to users; LLM context scoped to column names only |

---

## 10. Success Metrics

### Month 1 (Launch)
- 25 active tenants with at least one Sentry agent registered and at least 10 queries executed.
- Zero Critical security incidents.
- P95 query round-trip under 3.0 seconds across all tenants.
- Sentry deployment success rate above 90% without engineering support.

### Month 6
- 200 active tenants.
- Query accuracy rate above 85% (measured by user thumbs-up/thumbs-down signal).
- NPS above 40 among Analyst and Business Analyst user segments.
- Zero regulatory compliance incidents.

### Ongoing Health
- Guardian uptime: 99.9% monthly.
- Sentry reconnect events per tenant: fewer than 5 per day on average.
- PII redaction miss rate: below 0.1% on a benchmark test corpus (measured quarterly).
- LLM token cost per query: below $0.005 average.

---

## 11. Open Questions & Decisions Required

| Question | Decision Required By |
|---|---|
| Should VaultRelay offer a self-hosted Guardian option for air-gapped environments? | Phase 2 planning (Week 6) |
| What is the data retention policy for query audit logs? Varies by region and customer type. | Legal review before Phase 3 |
| Should write operations (INSERT/UPDATE) be scoped for a future version, or excluded permanently? | Product strategy review (Week 4) |
| How should schema metadata (table/column names) be classified — is it sensitive data under GDPR? | Legal + DPO review before Phase 2 |
| Should the LLM system prompt and query templates be customer-configurable (advanced tier)? | Product strategy review (Week 8) |

---

## 12. Glossary

| Term | Definition |
|---|---|
| **Zero-Trust Architecture** | A security model that assumes no implicit trust, requiring every request to be authenticated and authorised regardless of network location. |
| **Sentry** | The local agent component of VaultRelay deployed within the customer's infrastructure. |
| **Guardian** | The cloud-hosted gateway component that handles the user-facing API, LLM integration, and query routing. |
| **NL-to-SQL** | Natural language to SQL: converting a plain-text user query into a valid SQL statement using an LLM. |
| **PII Redaction** | Automatic detection and removal or masking of Personally Identifiable Information from query results. |
| **Idempotency Key** | A unique identifier attached to each query request that allows duplicate requests to be safely detected and deduplicated. |
| **Connection Pool** | A cache of database connections maintained by Sentry to avoid the latency of establishing a new connection per query. |
| **RBAC** | Role-Based Access Control: restricting access based on the roles assigned to individual users. |
| **TLS 1.3** | Transport Layer Security version 1.3: the current standard protocol for encrypting data in transit. |
| **HMAC** | Hash-based Message Authentication Code: a mechanism for verifying both the integrity and authenticity of a message. |

---

*VaultRelay PRD · Version 1.0 · April 2026 ·