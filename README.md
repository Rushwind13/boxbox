# boxbox
All burger and no bun

# FastAPI RESTful API Template

A Python 3 FastAPI REST API with full test coverage, logging, OpenAPI docs, and AWS-oriented deployment strategy.  
Endpoints: `/process` (POST), `/health`, `/version`.  

## Features
- JSON request/response via `/process`
- Health and version endpoints
- Logging (cloud-ready)
- Automatic OpenAPI docs (`/docs`)
- Unit tests (pytest)
- Deployment notes for AWS targets (Lambda, EKS, EC2)
- Dynamic acceptance criteria/worklist

## API Docs
Visit: http://localhost:8000/docs

## Installation & Setup

See `requirements.txt` for dependencies.

1. **Clone the repository**
    ```bash
    git clone git@github.com:Rushwind13/boxbox.git
    cd boxbox
    ```

2. **Python Virtual Environment**
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    pip3 install --upgrade pip
    pip3 install -r requirements.txt
    ```

## Linting & Pre-Commit Hook
We use [pre-commit](https://pre-commit.com/) to enforce linting before every commit.
- Setup: `pip install pre-commit && pre-commit install`
- Now all `git commit`s will run `flake8` and block if not clean.

## How to Use:
Set environment variables for ENV (dev or prod), ALLOWED_ORIGINS, and JWT_SECRET.

In production, /docs, /openapi.json will be hidden, CORS will allow only listed origins, and JWT will be required for /process.

Obtain a JWT with a POST to /token, then use it as a Bearer token in Authorization header for /process.

## Run API Server
```bash
    uvicorn src.main:app --reload
 ```

## Run tests
 ```bash
    pytest
```

## Docker
```bash
    docker build -t processor .
    docker run -p 8000:8000 processor
```



## Deployment
See deployment/notes.md for AWS strategy options and cost/performance notes.

## Acceptance Criteria & Tasks
Maintained in ACCEPTANCE_CRITERIA.md

## System Architecture

```mermaid
flowchart TD
    User([User or Client App])
    LB[ALB / API Gateway]
    API[FastAPI App]
    RL(Rate Limiting: SlowAPI)
    JWT(JWT Auth: PyJWT, Bearer)
    CORS(CORS & Security Headers)
    Log(Structured Logging)
    SSM(Secrets Manager / SSM)
    CloudWatch(CloudWatch / ELK)
    ECR([ECR Docker Images])

    subgraph "API Endpoints"
        V1_Process[[/v1/process]]
        V1_Health[[/v1/health]]
        V1_Token[[/v1/token]]
    end

    User -->|HTTPS/API Request - Bearer Token| LB
    LB -->|Route to Container/Lambda| API

    API --> V1_Process
    API --> V1_Health
    API --> V1_Token

    API -- Middleware/Dependencies --> RL
    API -- Middleware/Dependencies --> JWT
    API -- Middleware/Dependencies --> CORS

    API -- Logs --> Log
    Log --> CloudWatch

    API -- Configuration/Secrets --> SSM

    API -->|Response| User
```
