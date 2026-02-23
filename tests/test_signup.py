"""
Tests for the POST /activities/{activity_name}/signup endpoint.

This module tests student signup functionality for extracurricular activities.
Uses the AAA (Arrange-Act-Assert) pattern for test structure.
"""

import pytest


class TestSignupForActivity:
    """Test cases for POST /activities/{activity_name}/signup endpoint"""

    def test_successful_signup(self, client):
        """
        Test happy path: student successfully signs up for an activity.
        
        AAA Pattern:
        - Arrange: Set up test data (activity name, email)
        - Act: POST signup request
        - Assert: Status 200, success message returned
        """
        # Arrange
        activity_name = "Chess Club"
        email = "newstudent@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert email in data["message"]
        assert activity_name in data["message"]

    def test_signup_adds_participant_to_list(self, client):
        """
        Test that signup actually adds the student to the activity's participant list.
        
        AAA Pattern:
        - Arrange: Set up test data and get initial participant list
        - Act: POST signup request and verify participant was added
        - Assert: Participant list now contains the new email
        """
        # Arrange
        activity_name = "Programming Class"
        email = "newprogrammer@mergington.edu"
        
        # Get initial state
        initial_response = client.get("/activities")
        initial_participants = initial_response.json()[activity_name]["participants"].copy()
        
        # Act
        signup_response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert - verify signup succeeded
        assert signup_response.status_code == 200
        
        # Verify participant was actually added
        updated_response = client.get("/activities")
        updated_participants = updated_response.json()[activity_name]["participants"]
        
        assert email in updated_participants
        assert len(updated_participants) == len(initial_participants) + 1

    def test_signup_nonexistent_activity_returns_404(self, client):
        """
        Test error case: signup for activity that doesn't exist returns 404.
        
        AAA Pattern:
        - Arrange: Set up test data with fake activity name
        - Act: POST signup request for nonexistent activity
        - Assert: Status 404 and error detail returned
        """
        # Arrange
        activity_name = "Nonexistent Activity"
        email = "student@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "not found" in data["detail"].lower()

    def test_signup_duplicate_email_returns_400(self, client):
        """
        Test error case: student cannot sign up twice for same activity.
        
        AAA Pattern:
        - Arrange: Use an email already signed up for the activity
        - Act: POST signup request with duplicate email
        - Assert: Status 400 and error detail about already being signed up
        """
        # Arrange
        activity_name = "Chess Club"
        # michael@mergington.edu is already in Chess Club participants
        duplicate_email = "michael@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": duplicate_email}
        )
        
        # Assert
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        assert "already" in data["detail"].lower()

    def test_signup_different_activities_allowed(self, client):
        """
        Test that same student can sign up for multiple different activities.
        
        AAA Pattern:
        - Arrange: Set up email and two different activities
        - Act: POST signup for first activity, then second activity
        - Assert: Both signups succeed with status 200
        """
        # Arrange
        email = "multitasker@mergington.edu"
        activity1 = "Chess Club"
        activity2 = "Robotics Club"
        
        # Act
        response1 = client.post(
            f"/activities/{activity1}/signup",
            params={"email": email}
        )
        response2 = client.post(
            f"/activities/{activity2}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response1.status_code == 200
        assert response2.status_code == 200
        
        # Verify student is in both activities
        activities = client.get("/activities").json()
        assert email in activities[activity1]["participants"]
        assert email in activities[activity2]["participants"]

    def test_signup_case_sensitive_activity_name(self, client):
        """
        Test that activity names are case-sensitive.
        
        AAA Pattern:
        - Arrange: Use wrong case for activity name
        - Act: POST signup with wrong case
        - Assert: Status 404 (not found)
        """
        # Arrange
        activity_name = "chess club"  # lowercase instead of "Chess Club"
        email = "casesensitive@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 404

    def test_signup_empty_email_string(self, client):
        """
        Test handling of empty email string.
        
        AAA Pattern:
        - Arrange: Set up empty email parameter
        - Act: POST signup with empty email
        - Assert: Request processes (endpoint accepts it, but may add empty string)
        """
        # Arrange
        activity_name = "Basketball Team"
        email = ""
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert - endpoint will accept it since it doesn't validate email format
        assert response.status_code == 200
        
        # Empty string was added to participants
        activities = client.get("/activities").json()
        assert "" in activities[activity_name]["participants"]
