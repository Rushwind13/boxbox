# Acceptance Criteria & Worklist

This document tracks all current and upcoming requirements for the FastAPI RESTful API project.

## Initial Acceptance Criteria
- [x] FastAPI app with `/process`, `/health`, `/version` endpoints
- [x] Logging is cloud-ready and configurable
- [x] Unit tests for all endpoints
- [x] OpenAPI/Swagger auto-docs enabled
- [x] All Python dev in isolated virtualenv
- [x] Project uses modern `src/` layout
- [x] Request/response schemas clearly defined (TBD as project evolves)
- [ ] Schema validation, error handling best practice
- [ ] README, setup, and deployment docs are complete and clear
- [ ] AWS deployment strategies discussed in `deployment/notes.md`
- [ ] Worklist/prioritization section always up to date

## Worklist / TODO
- [ ] Add CI/CD workflow (GitHub Actions, etc)
- [ ] Monitor and log API performance
- [ ] Add runtime liveness and readiness probes for cloud deployment
- [ ] Document version management and upgrade strategy
- [ ] Evolve schemas and endpoint logic as requirements develop
- [ ] Respond to research/acceptance criteria updates as they arise

---

## 📋 Current & Completed Work

### ✅ **Completed**
- FastAPI app with OpenAPI (Swagger) documentation (hidden in production)
- Hardened `/process` endpoint (JWT-protected), `/health`, `/version`, `/token` (demo)
- Multi-stage, non-root, production-ready Dockerfile
- Uvicorn server, JSON structured logging
- Global error handling with consistent JSON error schema
- CORS lockdown (env-configurable, secure by default)
- Security headers on all responses
- JWT authentication (env-configurable secret, per-request auth)
- Rate limiting (SlowAPI): per-IP for `/process` and `/health`
- Full pytest suite (with JWT-injecting test client)
- CI/CD (GitHub Actions): lint, typecheck, coverage, Docker build
- requirements.txt covers FastAPI, PyJWT, SlowAPI, Flake8, Mypy, Pytest, Pytest-cov, Uvicorn, httpx
- Deployment docs (README.md, deployment/notes.md) and setup instructions

---

## 🟡 Upcoming / Next Priorities

- [ ] **Deployment Automation:** AWS Lambda, ECS, EKS, or EC2. Add sample IaC (Terraform, CloudFormation)
- [ ] **Production Auth:** Replace `/token` with real login (username/password), user DB, or SSO/OAuth2
- [ ] **Claims-Based or User-Based Rate Limiting:** Optionally limit by JWT claims (user) not just IP
- [ ] **Monitoring & Metrics:** `/metrics` endpoint (Prometheus), centralized logging, alerting
- [ ] **API Versioning:** Via URL or header for future-safe upgrades
- [ ] **Audit Logging:** Who/when/what for every action, redact sensitive data
- [ ] **Protect `/token`:** Basic auth, or remove/replace for prod
- [ ] **API Key Support (optional):** For clients that can't use JWT
- [ ] **Enhanced Tests:** Edge cases for rate limit, auth failures, error propagation, integration/property-based tests
- [ ] **Documentation:** Hardened operator/usage docs, security review, architecture diagrams

---

*Update this file as new requirements are discovered or priorities shift.*
