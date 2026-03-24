"""
Test suite for the FastAPI Extracurricular Activities Application.
Tests are written using the AAA (Arrange-Act-Assert) pattern for clarity and maintainability.
"""

import pytest
from fastapi.testclient import TestClient


class TestGetActivities:
    """Tests for GET /activities endpoint"""

    def test_get_activities_success(self, client: TestClient, reset_activities):
        """
        Test successful retrieval of all activities.
        
        Arrange: TestClient is ready
        Act: GET /activities
        Assert: Response status is 200 and contains all expected activities
        """
        # Arrange
        expected_activities = [
            "Chess Club", "Programming Class", "Gym Class", "Basketball",
            "Tennis Club", "Drama Club", "Art Studio", "Robotics Club", "Debate Team"
        ]
        
        # Act
        response = client.get("/activities")
        
        # Assert
        assert response.status_code == 200
        activities_response = response.json()
        assert isinstance(activities_response, dict)
        assert len(activities_response) == len(expected_activities)
        for activity_name in expected_activities:
            assert activity_name in activities_response

    def test_get_activities_response_structure(self, client: TestClient, reset_activities):
        """
        Test that each activity has the required fields.
        
        Arrange: TestClient is ready
        Act: GET /activities
        Assert: Each activity contains required fields (description, schedule, max_participants, participants)
        """
        # Arrange
        required_fields = {"description", "schedule", "max_participants", "participants"}
        
        # Act
        response = client.get("/activities")
        activities_response = response.json()
        
        # Assert
        for activity_name, activity_data in activities_response.items():
            assert isinstance(activity_data, dict), f"{activity_name} should be a dict"
            assert required_fields.issubset(activity_data.keys()), \
                f"{activity_name} missing required fields. Got: {activity_data.keys()}"
            assert isinstance(activity_data["description"], str)
            assert isinstance(activity_data["schedule"], str)
            assert isinstance(activity_data["max_participants"], int)
            assert isinstance(activity_data["participants"], list)


class TestSignupForActivity:
    """Tests for POST /activities/{activity_name}/signup endpoint"""

    def test_signup_success(self, client: TestClient, reset_activities):
        """
        Test successful signup for an activity.
        
        Arrange: TestClient ready with an activity and a new student email
        Act: POST /activities/{activity}/signup with new email
        Assert: Response status is 200 and student is added to participants
        """
        # Arrange
        activity_name = "Chess Club"
        new_email = "newstudent@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": new_email}
        )
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert new_email in data["message"]
        assert activity_name in data["message"]
        
        # Verify student was actually added
        activities_response = client.get("/activities").json()
        assert new_email in activities_response[activity_name]["participants"]

    def test_signup_activity_not_found(self, client: TestClient, reset_activities):
        """
        Test signup fails when activity does not exist.
        
        Arrange: TestClient with a fake activity name
        Act: POST /activities/FakeActivity/signup
        Assert: Response status is 404 with error detail
        """
        # Arrange
        fake_activity = "Nonexistent Activity"
        email = "student@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{fake_activity}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "Activity not found" in data["detail"]

    def test_signup_duplicate(self, client: TestClient, reset_activities):
        """
        Test signup fails when student is already signed up.
        
        Arrange: TestClient with an email already in an activity's participants
        Act: POST /activities/{activity}/signup with duplicate email
        Assert: Response status is 400 with error detail
        """
        # Arrange
        activity_name = "Chess Club"
        duplicate_email = "michael@mergington.edu"  # Already in Chess Club
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": duplicate_email}
        )
        
        # Assert
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        assert "already signed up" in data["detail"]


class TestUnregisterFromActivity:
    """Tests for POST /activities/{activity_name}/unregister endpoint"""

    def test_unregister_success(self, client: TestClient, reset_activities):
        """
        Test successful unregistration from an activity.
        
        Arrange: TestClient with a student in an activity
        Act: POST /activities/{activity}/unregister with student email
        Assert: Response status is 200 and student is removed from participants
        """
        # Arrange
        activity_name = "Chess Club"
        email_to_remove = "michael@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/unregister",
            params={"email": email_to_remove}
        )
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert email_to_remove in data["message"]
        assert activity_name in data["message"]
        
        # Verify student was actually removed
        activities_response = client.get("/activities").json()
        assert email_to_remove not in activities_response[activity_name]["participants"]

    def test_unregister_activity_not_found(self, client: TestClient, reset_activities):
        """
        Test unregister fails when activity does not exist.
        
        Arrange: TestClient with a fake activity name
        Act: POST /activities/FakeActivity/unregister
        Assert: Response status is 404 with error detail
        """
        # Arrange
        fake_activity = "Nonexistent Activity"
        email = "student@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{fake_activity}/unregister",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "Activity not found" in data["detail"]

    def test_unregister_not_registered(self, client: TestClient, reset_activities):
        """
        Test unregister fails when student is not signed up.
        
        Arrange: TestClient with an email not in an activity's participants
        Act: POST /activities/{activity}/unregister with unregistered email
        Assert: Response status is 400 with error detail
        """
        # Arrange
        activity_name = "Chess Club"
        unregistered_email = "notinlist@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/unregister",
            params={"email": unregistered_email}
        )
        
        # Assert
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        assert "not signed up" in data["detail"]


class TestRootRedirect:
    """Tests for GET / endpoint"""

    def test_root_redirect(self, client: TestClient, reset_activities):
        """
        Test that root path redirects to static index page.
        
        Arrange: TestClient is ready
        Act: GET / with follow_redirects=False
        Assert: Response is a redirect (307) with Location header pointing to /static/index.html
        """
        # Arrange
        # (TestClient is ready from fixture)
        
        # Act
        response = client.get("/", follow_redirects=False)
        
        # Assert
        assert response.status_code in [301, 302, 303, 307, 308]  # Various redirect codes
        assert "location" in response.headers or "Location" in response.headers
        location = response.headers.get("location") or response.headers.get("Location")
        assert location == "/static/index.html"
