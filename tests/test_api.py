from fastapi.testclient import TestClient

from claim_trellis.api import create_app
from claim_trellis.config import Settings


def test_end_to_end_without_provider_routes_to_human_review(tmp_path) -> None:
    app = create_app(Settings(data_dir=tmp_path, jev_api_key=None))
    with TestClient(app) as client:
        parsed = client.post(
            "/api/v1/documents/parse",
            files={
                "document": (
                    "source.txt",
                    b"The intervention reduced risk compared with placebo.",
                    "text/plain",
                )
            },
        )
        assert parsed.status_code == 200
        audit = client.post(
            "/api/v1/audits",
            json={
                "claim": "The intervention reduced risk compared with placebo.",
                "source_text": parsed.json()["text"],
                "source": {"access_tier": "full_text"},
                "use_judgment_provider": False,
            },
        )
        assert audit.status_code == 201
        body = audit.json()
        assert body["proposal"]["status"] == "review_required"
        reviewed = client.post(
            f"/api/v1/audits/{body['audit_id']}/reviews",
            json={"decision": "accept", "notes": "Read in context.", "reviewer": "reviewer-1"},
        )
        assert reviewed.status_code == 200
        assert reviewed.json()["human_review"]["decision"] == "accept"


def test_health_never_returns_api_key(tmp_path) -> None:
    app = create_app(Settings(data_dir=tmp_path, jev_api_key="super-secret"))
    with TestClient(app) as client:
        body = client.get("/healthz").json()
    assert body["provider_configured"] is True
    assert "super-secret" not in str(body)
