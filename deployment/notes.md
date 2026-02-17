# AWS Deployment Strategy — FastAPI RESTful API

## Deployment Targets Considered

### AWS Lambda (Serverless)
- **Pros:** 
  - Pay-per-use, scales to zero, no server management
  - Easy API Gateway integration
- **Cons:** 
  - Cold start latency, constrained execution time
  - Packaging Python dependencies for Lambda (with FastAPI, may require extra tooling)
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

- Pin all dependencies; use Docker for reproducibility (see example Dockerfile in future update)
- Use AWS Secrets Manager or SSM for config/keys
- Monitor API Gateway/CloudWatch logs and error rates
- Add CloudFormation or Terraform templates for full infra-as-code

---

*Expand this document with actual deployment scripts, IAM policies, and detailed CI/CD guidance as your deployment plans solidify.*

