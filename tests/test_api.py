import copy
import pytest
from fastapi.testclient import TestClient
from src import app as app_module

client = TestClient(app_module.app)

# Keep a deep copy of initial activities to restore between tests
_INITIAL_ACTIVITIES = copy.deepcopy(app_module.activities)

@pytest.fixture(autouse=True)
def reset_activities():
    # Restore the in-memory activities before each test
    app_module.activities = copy.deepcopy(_INITIAL_ACTIVITIES)
    yield


def test_get_activities_structure():
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data
    assert "participants" in data["Chess Club"]


def test_signup_adds_participant():
    email = "unittest1@example.com"
    resp = client.post(f"/activities/Chess%20Club/signup?email={email}")
    assert resp.status_code == 200
    assert "Signed up" in resp.json().get("message", "")

    # Verify participant added
    participants = client.get("/activities").json()["Chess Club"]["participants"]
    assert email in participants


def test_signup_duplicate_returns_400():
    # Use existing participant from initial data
    existing = _INITIAL_ACTIVITIES["Chess Club"]["participants"][0]
    resp = client.post(f"/activities/Chess%20Club/signup?email={existing}")
    assert resp.status_code == 400


def test_unregister_removes_participant():
    email = "temp_remove@example.com"
    # First sign up
    s = client.post(f"/activities/Chess%20Club/signup?email={email}")
    assert s.status_code == 200

    # Now unregister
    d = client.delete(f"/activities/Chess%20Club/unregister?email={email}")
    assert d.status_code == 200
    assert "Unregistered" in d.json().get("message", "")

    participants = client.get("/activities").json()["Chess Club"]["participants"]
    assert email not in participants


def test_unregister_not_registered_returns_400():
    email = "i-dont-exist@example.com"
    resp = client.delete(f"/activities/Chess%20Club/unregister?email={email}")
    assert resp.status_code == 400


def test_activity_not_found_errors():
    resp = client.post("/activities/DoesNotExist/signup?email=x@example.com")
    assert resp.status_code == 404

    resp = client.delete("/activities/DoesNotExist/unregister?email=x@example.com")
    assert resp.status_code == 404
