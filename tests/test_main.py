# tests/test_main.py
import pytest
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_version():
    response = client.get("/version")
    assert response.status_code == 200
    assert "version" in response.json()

def test_process_echo():
    payload = {"input_data": "hello"}
    response = client.post("/process", json=payload)
    assert response.status_code == 200
    result = response.json()
    assert "result" in result
    assert result["result"] == "Echo: hello"

def test_process_validation_error():
    # Missing required field
    payload = {}  # input_data required
    response = client.post("/process", json=payload)
    assert response.status_code == 422
    body = response.json()
    assert "error" in body
    assert "Validation failed" in body["error"]
    assert body["code"] == 422
    assert "request_id" in body

def test_process_malformed_json():
    # Bad JSON body (not a dict)
    response = client.post("/process", data="not a json", headers={"Content-Type": "application/json"})
    # FastAPI may respond with 422 or 400, both are handled as error
    assert response.status_code in (400, 422, 500)
    body = response.json()
    assert "error" in body
    assert body["code"] in (400, 422, 500)
    assert "request_id" in body

def test_security_headers():
    payload = {"input_data": "check security"}
    response = client.post("/process", json=payload)
    # CORS is handled via preflight, security headers are always present
    assert response.headers.get("X-Content-Type-Options") == "nosniff"
    assert response.headers.get("X-Frame-Options") == "DENY"
    assert response.headers.get("X-XSS-Protection") == "1; mode=block"
