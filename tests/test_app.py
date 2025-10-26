import copy
import pytest
from fastapi.testclient import TestClient

from src import app as app_module

client = TestClient(app_module.app)


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset the in-memory activities dict before/after each test to avoid side effects."""
    orig = copy.deepcopy(app_module.activities)
    try:
        yield
    finally:
        app_module.activities.clear()
        app_module.activities.update(orig)


def test_get_activities():
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    assert "Chess Club" in data
    assert isinstance(data["Chess Club"]["participants"], list)


def test_signup_and_duplicate_rejected():
    email = "test_student@mergington.edu"
    activity = "Chess Club"

    # Ensure clean start
    if email in app_module.activities[activity]["participants"]:
        app_module.activities[activity]["participants"].remove(email)

    resp = client.post(f"/activities/{activity}/signup?email={email}")
    assert resp.status_code == 200
    assert email in app_module.activities[activity]["participants"]

    # Duplicate signup should return 400
    resp2 = client.post(f"/activities/{activity}/signup?email={email}")
    assert resp2.status_code == 400


def test_remove_participant():
    email = "to_remove@mergington.edu"
    activity = "Programming Class"

    # Ensure participant exists
    if email not in app_module.activities[activity]["participants"]:
        app_module.activities[activity]["participants"].append(email)

    resp = client.delete(f"/activities/{activity}/participants?email={email}")
    assert resp.status_code == 200
    assert email not in app_module.activities[activity]["participants"]

    # Removing again should return 404
    resp2 = client.delete(f"/activities/{activity}/participants?email={email}")
    assert resp2.status_code == 404


def test_signup_unknown_activity():
    resp = client.post("/activities/NoSuchActivity/signup?email=a@b.c")
    assert resp.status_code == 404
