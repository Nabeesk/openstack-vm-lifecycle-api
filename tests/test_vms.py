from fastapi.testclient import TestClient

from app.main import app


def test_healthz() -> None:
    client = TestClient(app)
    resp = client.get("/healthz")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


def test_vm_lifecycle_happy_path() -> None:
    client = TestClient(app)

    # create
    resp = client.post(
        "/v1/vms",
        json={"name": "demo", "image": "ubuntu", "flavor": "m1.small", "network": "private"},
    )
    assert resp.status_code == 200
    vm = resp.json()
    vm_id = vm["id"]
    assert vm["status"] == "ACTIVE"

    # stop
    resp = client.post(f"/v1/vms/{vm_id}/stop")
    assert resp.status_code == 200
    assert resp.json()["status"] == "STOPPED"

    # resize (allowed only when STOPPED)
    resp = client.post(f"/v1/vms/{vm_id}/resize", json={"new_flavor": "m1.medium"})
    assert resp.status_code == 200
    assert resp.json()["flavor"] == "m1.medium"
    assert resp.json()["status"] == "STOPPED"

    # start
    resp = client.post(f"/v1/vms/{vm_id}/start")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ACTIVE"

    # reboot
    resp = client.post(f"/v1/vms/{vm_id}/reboot", json={"type": "soft"})
    assert resp.status_code == 200
    assert resp.json()["status"] == "ACTIVE"

    # list
    resp = client.get("/v1/vms")
    assert resp.status_code == 200
    data = resp.json()
    assert "items" in data
    assert any(item["id"] == vm_id for item in data["items"])

    # delete
    resp = client.delete(f"/v1/vms/{vm_id}")
    assert resp.status_code == 200
    assert resp.json()["status"] == "DELETED"

    # get after delete -> 404
    resp = client.get(f"/v1/vms/{vm_id}")
    assert resp.status_code == 404


def test_invalid_transitions_return_409() -> None:
    client = TestClient(app)

    resp = client.post(
        "/v1/vms",
        json={"name": "demo2", "image": "ubuntu", "flavor": "m1.small", "network": "private"},
    )
    vm_id = resp.json()["id"]

    # cannot resize when ACTIVE
    resp = client.post(f"/v1/vms/{vm_id}/resize", json={"new_flavor": "m1.large"})
    assert resp.status_code == 409
    payload = resp.json()
    assert payload["error"] == "invalid_transition"

    # stop then stop again (idempotent)
    resp = client.post(f"/v1/vms/{vm_id}/stop")
    assert resp.status_code == 200
    resp = client.post(f"/v1/vms/{vm_id}/stop")
    assert resp.status_code == 200
    assert resp.json()["status"] == "STOPPED"

    # cannot reboot when STOPPED
    resp = client.post(f"/v1/vms/{vm_id}/reboot", json={"type": "hard"})
    assert resp.status_code == 409
    assert resp.json()["error"] == "invalid_transition"
