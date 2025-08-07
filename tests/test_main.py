from fastapi.testclient import TestClient

from src.main import app

client = TestClient(app)


def get_jwt_token():
    response = client.post("/v1/token")
    assert response.status_code == 200
    return response.json()["access_token"]


def test_health():
    response = client.get("/v1/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_version():
    response = client.get("/v1/version")
    assert response.status_code == 200
    assert "version" in response.json()


def test_process_echo():
    token = get_jwt_token()
    payload = {"input_data": "hello"}
    headers = {"Authorization": f"Bearer {token}"}
    response = client.post("/v1/process", json=payload, headers=headers)
    assert response.status_code == 200
    result = response.json()
    assert "result" in result
    assert result["result"] == "Echo: hello"


def test_process_validation_error():
    token = get_jwt_token()
    payload = {}
    headers = {"Authorization": f"Bearer {token}"}
    response = client.post("/v1/process", json=payload, headers=headers)
    assert response.status_code == 422
    body = response.json()
    assert "error" in body
    assert "Validation failed" in body["error"]
    assert body["code"] == 422
    assert "request_id" in body


def test_process_malformed_json():
    token = get_jwt_token()
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    response = client.post("/v1/process", data="not a json", headers=headers)
    assert response.status_code in (400, 422, 500)
    body = response.json()
    assert "error" in body
    assert body["code"] in (400, 422, 500)
    assert "request_id" in body


def test_security_headers():
    token = get_jwt_token()
    payload = {"input_data": "check security"}
    headers = {"Authorization": f"Bearer {token}"}
    response = client.post("/v1/process", json=payload, headers=headers)
    assert response.headers.get("X-Content-Type-Options") == "nosniff"
    assert response.headers.get("X-Frame-Options") == "DENY"
    assert response.headers.get("X-XSS-Protection") == "1; mode=block"
