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
    # Initial schema requires 'input_data'
    payload = {"input_data": "hello"}
    response = client.post("/process", json=payload)
    assert response.status_code == 200
    result = response.json()
    assert "result" in result
    assert result["result"] == "Echo: hello"
