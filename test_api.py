from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_analyze_returns_structured_scores():
    response = client.post("/v1/analyze", json={
        "transcript": "This experiment explains why plants grow toward light. Research provides evidence for this process.",
        "user_interests": ["science", "biology"],
        "user_goal": "learn science"
    })
    assert response.status_code == 200
    body = response.json()
    assert 0 <= body["scores"]["relevance"] <= 1
    assert "limitations" in body
    assert body["model_mode"] == "rules_baseline"

def test_short_transcript_rejected():
    response = client.post("/v1/analyze", json={"transcript": "tiny"})
    assert response.status_code == 422
