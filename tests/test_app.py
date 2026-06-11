"""
Pytest tests for src.app using AAA pattern (Arrange, Act, Assert)
Tests the FastAPI endpoints with TestClient and fixtures for activity reset
"""

import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Ensure src is importable
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from app import app, activities


@pytest.fixture
def client():
    """Provide a TestClient for the FastAPI app"""
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    """Fixture to reset activities to a known state before and after each test"""
    original_activities = {
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
        },
        "Gym Class": {
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 30,
            "participants": ["john@mergington.edu", "olivia@mergington.edu"]
        },
        "Volleyball Team": {
            "description": "Competitive team practices and match play",
            "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:30 PM",
            "max_participants": 18,
            "participants": ["mason@mergington.edu", "ava@mergington.edu"]
        },
        "Swimming Team": {
            "description": "Swim training and swim meets for all levels",
            "schedule": "Mondays, Wednesdays, Fridays, 4:00 PM - 5:30 PM",
            "max_participants": 20,
            "participants": ["liam@mergington.edu", "mia@mergington.edu"]
        },
        "Art Club": {
            "description": "Explore drawing, painting, and creative projects",
            "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
            "max_participants": 15,
            "participants": ["sophia@mergington.edu", "nora@mergington.edu"]
        },
        "Drama Club": {
            "description": "Acting, stagecraft, and theater production",
            "schedule": "Tuesdays and Thursdays, 4:00 PM - 6:00 PM",
            "max_participants": 20,
            "participants": ["oliver@mergington.edu", "mia@mergington.edu"]
        },
        "Math Olympiad": {
            "description": "Advanced math problem solving and competition preparation",
            "schedule": "Mondays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["ethan@mergington.edu", "ava@mergington.edu"]
        },
        "Debate Team": {
            "description": "Prepare for debate tournaments and practice public speaking",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 16,
            "participants": ["isabella@mergington.edu", "noah@mergington.edu"]
        }
    }

    yield

    # Reset activities after test
    activities.clear()
    activities.update(original_activities)


class TestRootEndpoint:
    def test_root_redirect(self, client):
        # Arrange
        # Act
        response = client.get("/", follow_redirects=False)
        # Assert
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"


class TestActivitiesEndpoint:
    def test_get_all_activities(self, client, reset_activities):
        # Arrange
        expected_activity_count = 9
        # Act
        response = client.get("/activities")
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert len(data) == expected_activity_count
        assert "Chess Club" in data
        assert "Programming Class" in data

    def test_activity_has_required_fields(self, client, reset_activities):
        # Arrange
        required_fields = ["description", "schedule", "max_participants", "participants"]
        # Act
        response = client.get("/activities")
        data = response.json()
        chess_club = data["Chess Club"]
        # Assert
        for field in required_fields:
            assert field in chess_club

    def test_activity_participants_is_list(self, client, reset_activities):
        # Arrange / Act
        response = client.get("/activities")
        data = response.json()
        # Assert
        assert isinstance(data["Chess Club"]["participants"], list)
        assert len(data["Chess Club"]["participants"]) > 0


class TestSignupEndpoint:
    def test_signup_successful(self, client, reset_activities):
        # Arrange
        activity_name = "Chess Club"
        new_email = "newstudent@mergington.edu"
        # Act
        response = client.post(f"/activities/{activity_name}/signup", params={"email": new_email})
        # Assert
        assert response.status_code == 200
        assert "Signed up" in response.json()["message"]

    def test_signup_adds_participant(self, client, reset_activities):
        # Arrange
        activity_name = "Programming Class"
        new_email = "newstudent@mergington.edu"
        # Act
        client.post(f"/activities/{activity_name}/signup", params={"email": new_email})
        response = client.get("/activities")
        # Assert
        data = response.json()
        assert new_email in data[activity_name]["participants"]

    def test_signup_duplicate_email_fails(self, client, reset_activities):
        # Arrange
        activity_name = "Chess Club"
        existing_email = "michael@mergington.edu"
        # Act
        response = client.post(f"/activities/{activity_name}/signup", params={"email": existing_email})
        # Assert
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"]

    def test_signup_nonexistent_activity_fails(self, client, reset_activities):
        # Arrange
        activity_name = "Nonexistent Activity"
        email = "student@mergington.edu"
        # Act
        response = client.post(f"/activities/{activity_name}/signup", params={"email": email})
        # Assert
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]


class TestRemoveParticipantEndpoint:
    def test_remove_participant_successful(self, client, reset_activities):
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"
        # Act
        response = client.delete(f"/activities/{activity_name}/participants", params={"email": email})
        # Assert
        assert response.status_code == 200
        assert "Removed" in response.json()["message"]

    def test_remove_participant_actually_removes(self, client, reset_activities):
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"
        # Act
        client.delete(f"/activities/{activity_name}/participants", params={"email": email})
        response = client.get("/activities")
        # Assert
        data = response.json()
        assert email not in data[activity_name]["participants"]

    def test_remove_nonexistent_participant_fails(self, client, reset_activities):
        # Arrange
        activity_name = "Chess Club"
        email = "nonexistent@mergington.edu"
        # Act
        response = client.delete(f"/activities/{activity_name}/participants", params={"email": email})
        # Assert
        assert response.status_code == 404
        assert "not registered" in response.json()["detail"]

    def test_remove_from_nonexistent_activity_fails(self, client, reset_activities):
        # Arrange
        activity_name = "Nonexistent Activity"
        email = "student@mergington.edu"
        # Act
        response = client.delete(f"/activities/{activity_name}/participants", params={"email": email})
        # Assert
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]


class TestIntegrationScenarios:
    def test_full_signup_and_removal_flow(self, client, reset_activities):
        # Arrange
        activity_name = "Gym Class"
        new_email = "integrationtest@mergington.edu"
        initial_participants = client.get("/activities").json()[activity_name]["participants"]
        initial_count = len(initial_participants)

        # Act
        signup_response = client.post(f"/activities/{activity_name}/signup", params={"email": new_email})
        # Assert
        assert signup_response.status_code == 200
        after_signup = client.get("/activities").json()[activity_name]["participants"]
        assert len(after_signup) == initial_count + 1

        # Act
        remove_response = client.delete(f"/activities/{activity_name}/participants", params={"email": new_email})
        # Assert
        assert remove_response.status_code == 200
        after_removal = client.get("/activities").json()[activity_name]["participants"]
        assert len(after_removal) == initial_count

    def test_multiple_signups_same_activity(self, client, reset_activities):
        # Arrange
        activity_name = "Art Club"
        new_emails = [
            "student1@mergington.edu",
            "student2@mergington.edu",
            "student3@mergington.edu"
        ]
        # Act
        for email in new_emails:
            response = client.post(f"/activities/{activity_name}/signup", params={"email": email})
            # Assert: each signup succeeds
            assert response.status_code == 200

        # Assert: all students are registered
        final_response = client.get("/activities")
        participants = final_response.json()[activity_name]["participants"]
        for email in new_emails:
            assert email in participants
