import os

os.environ["DATABASE_URL"] = "sqlite:///./test.db"

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_generate_and_save_flow() -> None:
    persona = client.post(
        "/api/personas",
        json={"account_id": "a1", "name": "기본", "tone": "담백", "description": "desc"},
    ).json()

    diary = client.post("/api/diaries", json={"account_id": "a1", "title": "d1"}).json()

    link_resp = client.post(f"/api/diaries/{diary['id']}/personas/{persona['id']}")
    assert link_resp.status_code == 200

    gen_resp = client.post(
        "/api/entries/generate",
        json={"diary_id": diary["id"], "persona_id": persona["id"], "input_text": "오늘 산책했다"},
    )
    assert gen_resp.status_code == 200
    body = gen_resp.json()
    assert body["status"] == "draft"

    save_resp = client.post(f"/api/entries/{body['id']}/save", json={"draft": "수정된 문장"})
    assert save_resp.status_code == 200
    assert save_resp.json()["status"] == "saved"
