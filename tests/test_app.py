import os
from uuid import uuid4

os.environ["DATABASE_URL"] = "sqlite:///./test.db"
os.environ["ECHODIARY_DISABLE_LLM"] = "true"

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def login(username: str, password: str) -> dict[str, str]:
    response = client.post("/api/auth/login", json={"username": username, "password": password})
    assert response.status_code == 200
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def signup(username: str, password: str) -> None:
    response = client.post("/api/auth/signup", json={"username": username, "password": password})
    assert response.status_code in (200, 409)


def test_health() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_auth_required_for_protected_api() -> None:
    response = client.post(
        "/api/personas",
        json={"account_id": "a1", "name": "기본", "tone": "담백", "description": "desc"},
    )
    assert response.status_code == 401


def test_admin_page_authorization() -> None:
    signup("user-1", "pw-1")
    user_headers = login("user-1", "pw-1")
    user_response = client.get("/api/admin/page", headers=user_headers)
    assert user_response.status_code == 403

    admin_headers = login("admin", "admin")
    admin_response = client.get("/api/admin/page", headers=admin_headers)
    assert admin_response.status_code == 200
    assert admin_response.json()["title"] == "관리자 페이지"


def test_signup_and_login_flow() -> None:
    username = f"new-user-{uuid4()}"
    signup_response = client.post("/api/auth/signup", json={"username": username, "password": "new-pass"})
    assert signup_response.status_code == 200
    assert signup_response.json()["role"] == "user"

    duplicate_response = client.post("/api/auth/signup", json={"username": username, "password": "new-pass"})
    assert duplicate_response.status_code == 409

    login_response = client.post("/api/auth/login", json={"username": username, "password": "new-pass"})
    assert login_response.status_code == 200
    assert login_response.json()["token_type"] == "bearer"


def test_generate_and_save_flow() -> None:
    signup("a1-user", "pw")
    headers = login("a1-user", "pw")
    persona = client.post(
        "/api/personas",
        json={"account_id": "a1", "name": "기본", "tone": "담백", "description": "desc"},
        headers=headers,
    ).json()

    diary = client.post("/api/diaries", json={"account_id": "a1", "title": "d1"}, headers=headers).json()

    link_resp = client.post(f"/api/diaries/{diary['id']}/personas/{persona['id']}", headers=headers)
    assert link_resp.status_code == 200

    gen_resp = client.post(
        "/api/entries/generate",
        json={"diary_id": diary["id"], "persona_id": persona["id"], "input_text": "오늘 산책했다"},
        headers=headers,
    )
    assert gen_resp.status_code == 200
    body = gen_resp.json()
    assert body["status"] == "draft"

    save_resp = client.post(f"/api/entries/{body['id']}/save", json={"draft": "수정된 문장"}, headers=headers)
    assert save_resp.status_code == 200
    assert save_resp.json()["status"] == "saved"
