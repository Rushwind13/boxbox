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

2. **Python Virtual Environment**
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    pip3 install --upgrade pip
    pip3 install -r requirements.txt

## Run API Server
    ```bash
    uvicorn src.main:app --reload

## Run tests
    ```bash
    pytest

## Deployment
See deployment/notes.md for AWS strategy options and cost/performance notes.

## Acceptance Criteria & Tasks
Maintained in ACCEPTANCE_CRITERIA.md
