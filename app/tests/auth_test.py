# app/tests/auth_test.py
import sys
import os

# Add the app directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from fastapi.testclient import TestClient
from main import app
import base64

client = TestClient(app)

def test_login_success():
    valid_credentials = base64.b64encode(b"stu01:stu01").decode("utf-8")
    response = client.post(
        "/login",
        headers={"Authorization": f"Basic {valid_credentials}"}
    )
    assert response.status_code == 200
    assert "Login successful" in response.json()["message"]

def test_login_failure():
    invalid_credentials = base64.b64encode(b"wronguser:wrongpassword").decode("utf-8")
    response = client.post(
        "/login",
        headers={"Authorization": f"Basic {invalid_credentials}"}
    )
    assert response.status_code == 400
    assert response.json() == {"detail": "Incorrect username or password"}
