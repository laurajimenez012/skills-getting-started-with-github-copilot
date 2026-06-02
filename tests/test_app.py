import copy
from urllib.parse import quote

import pytest
from fastapi.testclient import TestClient

from src.app import activities, app

client = TestClient(app)
initial_activities = copy.deepcopy(activities)


@pytest.fixture(autouse=True)
def reset_activities():
    activities.clear()
    activities.update(copy.deepcopy(initial_activities))


def encode_activity_name(name: str) -> str:
    return quote(name, safe="")


def test_get_activities_returns_activities():
    # Arrange

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert "Chess Club" in data
    assert isinstance(data["Chess Club"]["participants"], list)
    assert "michael@mergington.edu" in data["Chess Club"]["participants"]


def test_signup_adds_participant():
    # Arrange
    activity_name = "Chess Club"
    email = "newstudent@mergington.edu"
    url = f"/activities/{encode_activity_name(activity_name)}/signup"

    # Act
    response = client.post(url, params={"email": email})

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {email} for {activity_name}"

    activities_response = client.get("/activities").json()
    assert email in activities_response[activity_name]["participants"]


def test_signup_duplicate_returns_400():
    # Arrange
    activity_name = "Chess Club"
    email = "michael@mergington.edu"
    url = f"/activities/{encode_activity_name(activity_name)}/signup"

    # Act
    response = client.post(url, params={"email": email})

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"


def test_remove_participant_success():
    # Arrange
    activity_name = "Chess Club"
    email = "michael@mergington.edu"
    url = f"/activities/{encode_activity_name(activity_name)}/participants"

    # Act
    response = client.delete(url, params={"email": email})

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Removed {email} from {activity_name}"

    activities_response = client.get("/activities").json()
    assert email not in activities_response[activity_name]["participants"]


def test_remove_missing_participant_returns_404():
    # Arrange
    activity_name = "Chess Club"
    email = "not_registered@mergington.edu"
    url = f"/activities/{encode_activity_name(activity_name)}/participants"

    # Act
    response = client.delete(url, params={"email": email})

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found"


def test_signup_activity_not_found_returns_404():
    # Arrange
    activity_name = "Nonexistent Club"
    email = "test@mergington.edu"
    url = f"/activities/{encode_activity_name(activity_name)}/signup"

    # Act
    response = client.post(url, params={"email": email})

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_remove_participant_activity_not_found_returns_404():
    # Arrange
    activity_name = "Nonexistent Club"
    email = "test@mergington.edu"
    url = f"/activities/{encode_activity_name(activity_name)}/participants"

    # Act
    response = client.delete(url, params={"email": email})

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"
