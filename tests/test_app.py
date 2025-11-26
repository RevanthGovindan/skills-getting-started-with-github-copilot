"""Tests for the Mergington High School Activities API."""
import pytest
from fastapi import HTTPException


class TestGetActivities:
    """Tests for the GET /activities endpoint."""

    def test_get_activities_returns_200(self, client):
        """Test that GET /activities returns a 200 status code."""
        response = client.get("/activities")
        assert response.status_code == 200

    def test_get_activities_returns_dict(self, client):
        """Test that GET /activities returns a dictionary."""
        response = client.get("/activities")
        data = response.json()
        assert isinstance(data, dict)

    def test_get_activities_contains_expected_activities(self, client):
        """Test that activities response contains expected activity names."""
        response = client.get("/activities")
        data = response.json()
        expected_activities = [
            "Chess Club",
            "Programming Class",
            "Gym Class",
            "Basketball Team",
            "Tennis Club",
            "Art Studio",
            "Drama Club",
            "Debate Team",
            "Robotics Club",
        ]
        for activity in expected_activities:
            assert activity in data

    def test_activity_has_required_fields(self, client):
        """Test that each activity has required fields."""
        response = client.get("/activities")
        data = response.json()
        required_fields = [
            "description",
            "schedule",
            "max_participants",
            "participants",
        ]
        for activity_name, activity_data in data.items():
            for field in required_fields:
                assert field in activity_data, f"Activity {activity_name} missing {field}"

    def test_participants_is_list(self, client):
        """Test that participants field is a list."""
        response = client.get("/activities")
        data = response.json()
        for activity_name, activity_data in data.items():
            assert isinstance(
                activity_data["participants"], list
            ), f"Participants for {activity_name} should be a list"

    def test_max_participants_is_positive_integer(self, client):
        """Test that max_participants is a positive integer."""
        response = client.get("/activities")
        data = response.json()
        for activity_name, activity_data in data.items():
            assert isinstance(
                activity_data["max_participants"], int
            ), f"max_participants for {activity_name} should be an integer"
            assert (
                activity_data["max_participants"] > 0
            ), f"max_participants for {activity_name} should be positive"


class TestSignupForActivity:
    """Tests for the POST /activities/{activity_name}/signup endpoint."""

    def test_signup_with_valid_activity_and_email(self, client):
        """Test signing up for an activity with valid inputs."""
        response = client.post(
            "/activities/Chess%20Club/signup?email=newstudent@mergington.edu"
        )
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "newstudent@mergington.edu" in data["message"]

    def test_signup_adds_participant_to_activity(self, client):
        """Test that signup actually adds the participant."""
        email = "test.participant@mergington.edu"
        activity = "Chess Club"
        
        # Get current participants
        response = client.get("/activities")
        initial_participants = response.json()[activity]["participants"].copy()
        
        # Sign up
        client.post(
            f"/activities/{activity}/signup?email={email}"
        )
        
        # Check that participant was added
        response = client.get("/activities")
        new_participants = response.json()[activity]["participants"]
        assert email in new_participants
        assert len(new_participants) == len(initial_participants) + 1

    def test_signup_with_duplicate_email_returns_400(self, client):
        """Test that signing up with an already registered email returns 400."""
        activity = "Chess Club"
        email = "michael@mergington.edu"  # Already registered
        
        response = client.post(
            f"/activities/{activity}/signup?email={email}"
        )
        assert response.status_code == 400
        data = response.json()
        assert "already signed up" in data["detail"]

    def test_signup_with_invalid_activity_returns_404(self, client):
        """Test that signing up for a non-existent activity returns 404."""
        response = client.post(
            "/activities/Invalid%20Activity/signup?email=test@mergington.edu"
        )
        assert response.status_code == 404
        data = response.json()
        assert "Activity not found" in data["detail"]

    def test_signup_response_format(self, client):
        """Test that signup response has correct format."""
        response = client.post(
            "/activities/Art%20Studio/signup?email=artist@mergington.edu"
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert "message" in data
        assert isinstance(data["message"], str)


class TestUnregisterFromActivity:
    """Tests for the POST /activities/{activity_name}/unregister endpoint."""

    def test_unregister_removes_participant(self, client):
        """Test that unregister removes the participant from an activity."""
        activity = "Chess Club"
        email = "michael@mergington.edu"  # Already registered
        
        # Verify participant is registered
        response = client.get("/activities")
        assert email in response.json()[activity]["participants"]
        
        # Unregister
        response = client.post(
            f"/activities/{activity}/unregister?email={email}"
        )
        assert response.status_code == 200
        
        # Verify participant was removed
        response = client.get("/activities")
        assert email not in response.json()[activity]["participants"]

    def test_unregister_with_invalid_activity_returns_404(self, client):
        """Test that unregistering from non-existent activity returns 404."""
        response = client.post(
            "/activities/Invalid%20Activity/unregister?email=test@mergington.edu"
        )
        assert response.status_code == 404
        data = response.json()
        assert "Activity not found" in data["detail"]

    def test_unregister_not_registered_participant_returns_400(self, client):
        """Test that unregistering a non-registered participant returns 400."""
        response = client.post(
            "/activities/Chess%20Club/unregister?email=notregistered@mergington.edu"
        )
        assert response.status_code == 400
        data = response.json()
        assert "not registered" in data["detail"]

    def test_unregister_response_format(self, client):
        """Test that unregister response has correct format."""
        activity = "Programming Class"
        email = "emma@mergington.edu"  # Already registered
        
        response = client.post(
            f"/activities/{activity}/unregister?email={email}"
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert "message" in data
        assert isinstance(data["message"], str)


class TestRootEndpoint:
    """Tests for the root endpoint."""

    def test_root_redirect_to_static(self, client):
        """Test that root endpoint redirects to static content."""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert "/static/index.html" in response.headers["location"]


class TestIntegration:
    """Integration tests for multiple operations."""

    def test_signup_and_unregister_workflow(self, client):
        """Test the complete signup and unregister workflow."""
        activity = "Tennis Club"
        email = "integration.test@mergington.edu"
        
        # Get initial count
        response = client.get("/activities")
        initial_count = len(response.json()[activity]["participants"])
        
        # Sign up
        response = client.post(
            f"/activities/{activity}/signup?email={email}"
        )
        assert response.status_code == 200
        
        # Verify signup worked
        response = client.get("/activities")
        assert len(response.json()[activity]["participants"]) == initial_count + 1
        assert email in response.json()[activity]["participants"]
        
        # Unregister
        response = client.post(
            f"/activities/{activity}/unregister?email={email}"
        )
        assert response.status_code == 200
        
        # Verify back to initial state
        response = client.get("/activities")
        assert len(response.json()[activity]["participants"]) == initial_count
        assert email not in response.json()[activity]["participants"]

    def test_multiple_signups_increase_participant_count(self, client):
        """Test that multiple signups increase participant count."""
        activity = "Debate Team"
        
        response = client.get("/activities")
        initial_count = len(response.json()[activity]["participants"])
        
        # Sign up multiple participants
        for i in range(3):
            email = f"debate.student{i}@mergington.edu"
            response = client.post(
                f"/activities/{activity}/signup?email={email}"
            )
            assert response.status_code == 200
        
        # Verify all were added
        response = client.get("/activities")
        final_count = len(response.json()[activity]["participants"])
        assert final_count == initial_count + 3
