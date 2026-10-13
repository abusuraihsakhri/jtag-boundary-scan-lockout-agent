"""Regressions for audit chain authenticity and public API validation."""
from agents.base import AuditTrail
from agents.models import SystemTaskPayload

def test_audit_chain_detects_metadata_and_signature_tampering():
    audit = AuditTrail(secret_key="fixture-key-not-a-production-secret")
    returned = audit.log("operator", "supervisor", "AUDIT", {"device": "D1"})
    returned["actor"] = "changed-outside"
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

def test_batch_rejects_same_input_and_output(tmp_path, monkeypatch):
    from cli import main as enterprise_main
    from jtag_lockout.cli import main as legacy_main
    monkeypatch.chdir(tmp_path)
    source = tmp_path / "cases.csv"
    original = "task_id,target_identifier,primary_metric,secondary_metric,status_descriptor\nT1,DEVICE-1,1,1,NOMINAL\n"
    source.write_text(original, encoding="utf-8")
    for main in (enterprise_main, legacy_main):
        assert main(["batch", "-i", "cases.csv", "-o", "cases.csv"]) == 1
        assert source.read_text(encoding="utf-8") == original
