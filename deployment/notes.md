# AWS Deployment Strategy — FastAPI RESTful API

## Deployment Targets Considered

### AWS Lambda (Serverless)
- **Pros:** 
  - Pay-per-use, scales to zero, no server management
  - Easy API Gateway integration
- **Cons:** 
  - Cold start latency, constrained execution time
  - Packaging Python dependencies for Lambda (with FastAPI, may require extra tooling, e.g., Lambda layers or container images)
- **Best for:** Low/variable throughput, event-driven APIs, cost-sensitive use cases

### AWS Elastic Kubernetes Service (EKS)
- **Pros:** 
  - Highly scalable and customizable
  - Supports rolling updates, blue/green deployments, advanced autoscaling
  - Suitable for high-throughput, enterprise-grade APIs
- **Cons:** 
  - More complex to set up/manage
  - Higher base cost, even when idle
- **Best for:** High-throughput, mission-critical workloads, microservices architectures

### AWS EC2 (Virtual Servers)
- **Pros:** 
  - Full control, no container/k8s overhead
  - Easy to get started, supports any Python runtime
- **Cons:** 
  - Manual scaling and management, higher maintenance burden
  - Potential under/over-provisioning
- **Best for:** Legacy workflows, lift-and-shift, predictable load

---

## Throughput and Cost Guidance

| **Target** | **Typical Startup** | **Max QPS (API Gateway default)** | **Scaling** | **Cost (Monthly min)** |
|------------|--------------------|--------------------|----------|---------------------|
| Lambda     | <1 min (cold start penalty) | 1,000+           | Auto     | $0 (scales to zero) |
| EKS        | 5–20 min (infra)   | 10,000+            | Auto     | $50+ (depends on node count) |
| EC2        | ~1 min             | 5,000+ (depends on instance) | Manual/auto | $10+ (small instance)  |

> *Tip: For most new REST APIs with uncertain load, start with Lambda for simplicity/cost, then graduate to EKS/EC2 as traffic grows.*

---

## Liveness and Readiness Probes

- **/health**: Used for AWS ALB/NLB, k8s, or Lambda health checks
- **/version**: For deployment/version tracking

---

## Deployment Recommendations

- **Containerization**: Use the provided Dockerfile for all environments (dev, CI/CD, prod).
  - Production image is non-root, multi-stage for small size and security.
- **Environment Variables**:  
  - `ENV` (`dev`/`prod`), `ALLOWED_ORIGINS` (CORS), and `JWT_SECRET` must be configured per environment.
  - All secrets (JWT, DB, etc.) should be managed via AWS Secrets Manager or SSM Parameter Store—**never in code or dockerfiles**.
- **CI/CD**: 
  - Use the provided GitHub Actions workflow for build, lint, typecheck, test, code coverage, and Docker image publishing.
  - Add a deploy step (to ECS/Lambda/ECR/EC2) as your infra matures.
- **Infrastructure as Code (IaC)**:
  - Strongly recommended: automate infrastructure with Terraform or CloudFormation (ALB/API Gateway, ECR, ECS, Lambda, IAM, VPC, etc.)
  - Example templates should be added as the next work item.
- **Monitoring & Logging**:
  - Centralize logs in CloudWatch, ELK, or similar.
  - Set up CloudWatch alarms for 4xx/5xx rates, latency, and rate-limiting events.
- **Security & Hardening**:
  - TLS/HTTPS enforced at ALB/API Gateway
  - Web Application Firewall (WAF) enabled for all public APIs
  - CORS restricted, security headers set, JWT and/or API Key required for all sensitive endpoints
  - /docs and /openapi.json **hidden in prod** for attack surface minimization
  - Rate limiting enabled via app and infra (API Gateway/WAF)
  - Use rolling deployments/zero downtime where possible

---

## 🟡 Upcoming Work & Next Steps

- [ ] Add production-grade authentication (replace `/token` with real user login, or SSO)
- [ ] IaC templates: Terraform/CloudFormation for all AWS resources
- [ ] Production deployment automation (CI/CD auto-deploy step)
- [ ] Centralized metrics and application monitoring (/metrics endpoint, Prometheus/Grafana, CloudWatch dashboards)
- [ ] Secrets management integration (AWS Secrets Manager/SSM)
- [ ] Protect `/token` endpoint or remove for production
- [ ] Add audit logging, enhanced error/alerting, and full production operations docs

---

## Example: Running Locally with Docker

```bash
docker build -t fastapi-app .
docker run -d -p 8000:8000 \
  -e ENV=prod \
  -e ALLOWED_ORIGINS="https://yourdomain.com" \
  -e JWT_SECRET="replace-this-secret" \
  fastapi-app
