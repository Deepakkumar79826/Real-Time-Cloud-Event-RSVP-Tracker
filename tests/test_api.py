import os, tempfile
os.environ["DATABASE_URL"] = "sqlite:///./test_event_tracker.db"
os.environ["JWT_SECRET"] = "test-secret"

from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

def test_health():
    assert client.get("/api/health").status_code == 200

def test_register_and_login():
    email = "testuser@example.com"
    r = client.post("/api/register", json={"name":"Test User","email":email,"password":"Password123!","role":"ATTENDEE"})
    assert r.status_code in (200,409)
    r = client.post("/api/login", json={"email":email,"password":"Password123!"})
    assert r.status_code == 200
    assert "access_token" in r.json()

def test_invalid_login():
    r = client.post("/api/login", json={"email":"nobody@example.com","password":"wrongpass"})
    assert r.status_code == 401
