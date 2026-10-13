"""Regressions for audit chain authenticity and public API validation."""
import pytest
from agents.base import AuditTrail
from agents.models import SystemTaskPayload

def test_audit_chain_detects_metadata_and_signature_tampering():
    audit = AuditTrail(secret_key="fixture-key-not-a-production-secret")
    first = audit.log("operator", "supervisor", "AUDIT", {"device": "D1"})
    audit.log("operator", "supervisor", "AUDIT", {"device": "D2"})
    assert audit.verify_integrity()
    audit.logs[0]["actor"] = "forged"
    assert not audit.verify_integrity()
    audit.logs[0]["actor"] = "operator"
    assert audit.verify_integrity()
    audit.logs[1]["current_hash"] = "0" * 64
    assert not audit.verify_integrity()

def test_public_audit_trail_is_a_copy():
    audit = AuditTrail(secret_key="fixture-key-not-a-production-secret")
    audit.log("operator", "supervisor", "AUDIT", {"device": "D1"})
    exported = audit.get_trail()
    exported[0]["actor"] = "forged"
    assert audit.verify_integrity()

def test_api_rejects_blocked_identifiers_without_server_error():
    from fastapi.testclient import TestClient
    from agents.api import app
    client = TestClient(app)
    payload = SystemTaskPayload(
        task_id="T1", target_identifier="DEVICE-1", primary_metric=10
    ).model_dump()
    payload["target_identifier"] = "Patient MRN-994827"
    response = client.post("/api/audit", json=payload)
    assert response.status_code == 422

def test_api_health_and_audit():
    from fastapi.testclient import TestClient
    from agents.api import app
    client = TestClient(app)
    assert client.get("/health").status_code == 200
    result = client.post("/api/audit", json={
        "task_id": "T2", "target_identifier": "DEVICE-2",
        "primary_metric": 26, "secondary_metric": 0,
        "status_descriptor": "NOMINAL"
    })
    assert result.status_code == 200
    assert result.json()["total_alerts"] >= 1
