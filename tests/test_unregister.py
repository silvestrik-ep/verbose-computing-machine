"""
Tests for the DELETE /activities/{activity_name}/unregister endpoint.

This module tests student unregistration functionality from extracurricular activities.
Uses the AAA (Arrange-Act-Assert) pattern for test structure.
"""

import pytest


class TestUnregisterFromActivity:
    """Test cases for DELETE /activities/{activity_name}/unregister endpoint"""

    def test_successful_unregister(self, client):
        """
        Test happy path: student successfully unregisters from an activity.
        
        AAA Pattern:
        - Arrange: Set up test data (activity name, registered student email)
        - Act: DELETE unregister request
        - Assert: Status 200, success message returned
        """
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"  # Already registered
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert email in data["message"]
        assert activity_name in data["message"]

    def test_unregister_removes_participant_from_list(self, client):
        """
        Test that unregister actually removes the student from the activity's participant list.
        
        AAA Pattern:
        - Arrange: Set up test data and get initial participant list
        - Act: DELETE unregister request and verify participant was removed
        - Assert: Participant list no longer contains the email
        """
        # Arrange
        activity_name = "Debate Club"
        email = "rachel@mergington.edu"  # Already registered
        
        # Get initial state
        initial_response = client.get("/activities")
        initial_participants = initial_response.json()[activity_name]["participants"].copy()
        assert email in initial_participants
        
        # Act
        unregister_response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )
        
        # Assert - verify unregister succeeded
        assert unregister_response.status_code == 200
        
        # Verify participant was actually removed
        updated_response = client.get("/activities")
        updated_participants = updated_response.json()[activity_name]["participants"]
        
        assert email not in updated_participants
        assert len(updated_participants) == len(initial_participants) - 1

    def test_unregister_nonexistent_activity_returns_404(self, client):
        """
        Test error case: unregister from activity that doesn't exist returns 404.
        
        AAA Pattern:
        - Arrange: Set up test data with fake activity name
        - Act: DELETE unregister request for nonexistent activity
        - Assert: Status 404 and error detail returned
        """
        # Arrange
        activity_name = "Fake Activity"
        email = "student@mergington.edu"
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "not found" in data["detail"].lower()

    def test_unregister_not_registered_student_returns_400(self, client):
        """
        Test error case: cannot unregister if student is not signed up for activity.
        
        AAA Pattern:
        - Arrange: Use an email not registered for the activity
        - Act: DELETE unregister request for unregistered student
        - Assert: Status 400 and error detail about not being registered
        """
        # Arrange
        activity_name = "Tennis Club"
        # noone@mergington.edu is not in Tennis Club participants
        unregistered_email = "noone@mergington.edu"
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": unregistered_email}
        )
        
        # Assert
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        assert "not sign" in data["detail"].lower()

    def test_unregister_then_signup_again_succeeds(self, client):
        """
        Test that a student can unregister and then re-signup for the same activity.
        
        AAA Pattern:
        - Arrange: Get a registered student and the activity
        - Act: DELETE unregister, then POST signup again
        - Assert: Both operations succeed
        """
        # Arrange
        activity_name = "Gym Class"
        email = "john@mergington.edu"  # Already registered
        
        # Act - unregister
        unregister_response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )
        
        # Assert unregister succeeded
        assert unregister_response.status_code == 200
        
        # Verify removed
        activities = client.get("/activities").json()
        assert email not in activities[activity_name]["participants"]
        
        # Act - signup again
        signup_response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert signup succeeded
        assert signup_response.status_code == 200
        
        # Verify added back
        activities = client.get("/activities").json()
        assert email in activities[activity_name]["participants"]

    def test_unregister_case_sensitive_activity_name(self, client):
        """
        Test that activity names are case-sensitive for unregister.
        
        AAA Pattern:
        - Arrange: Use wrong case for activity name
        - Act: DELETE unregister with wrong case
        - Assert: Status 404 (not found)
        """
        # Arrange
        activity_name = "jazz band"  # lowercase instead of "Jazz Band"
        email = "noah@mergington.edu"
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 404

    def test_unregister_idempotent_double_unregister(self, client):
        """
        Test that unregistering twice returns error on second attempt (not idempotent).
        
        AAA Pattern:
        - Arrange: Get a registered student
        - Act: DELETE unregister first time, then DELETE unregister second time
        - Assert: First succeeds (200), second fails (400)
        """
        # Arrange
        activity_name = "Art Studio"
        email = "grace@mergington.edu"  # Already registered
        
        # Act - first unregister
        response1 = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )
        
        # Assert first unregister succeeded
        assert response1.status_code == 200
        
        # Act - try to unregister again
        response2 = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )
        
        # Assert second unregister fails
        assert response2.status_code == 400
        data = response2.json()
        assert "not sign" in data["detail"].lower()

    def test_unregister_different_students_independent(self, client):
        """
        Test that unregistering one student doesn't affect others in the activity.
        
        AAA Pattern:
        - Arrange: Get activity with multiple registered students
        - Act: DELETE unregister for one student
        - Assert: Other students remain registered
        """
        # Arrange
        activity_name = "Robotics Club"
        student_to_remove = "david@mergington.edu"
        
        # Get initial state
        initial = client.get("/activities").json()
        initial_participants = initial[activity_name]["participants"].copy()
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": student_to_remove}
        )
        
        # Assert
        assert response.status_code == 200
        
        # Verify correct student removed and others unchanged
        updated = client.get("/activities").json()
        updated_participants = updated[activity_name]["participants"]
        
        assert student_to_remove not in updated_participants
        # Verify other participants are still there
        for participant in initial_participants:
            if participant != student_to_remove:
                assert participant in updated_participants
