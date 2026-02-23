"""
Tests for the GET /activities endpoint.

This module tests retrieval of all available extracurricular activities.
Uses the AAA (Arrange-Act-Assert) pattern for test structure.
"""

import pytest


class TestGetActivities:
    """Test cases for GET /activities endpoint"""

    def test_get_all_activities_success(self, client):
        """
        Test happy path: successfully retrieve all activities.
        
        AAA Pattern:
        - Arrange: Client is ready (fixture)
        - Act: GET /activities
        - Assert: Status is 200 and returns all 9 activities with correct structure
        """
        # Arrange
        client = client
        
        # Act
        response = client.get("/activities")
        
        # Assert
        assert response.status_code == 200
        activities = response.json()
        
        # Verify we get all 9 activities
        assert len(activities) == 9
        assert "Chess Club" in activities
        assert "Programming Class" in activities
        assert "Gym Class" in activities
        assert "Basketball Team" in activities
        assert "Tennis Club" in activities
        assert "Debate Club" in activities
        assert "Robotics Club" in activities
        assert "Art Studio" in activities
        assert "Jazz Band" in activities

    def test_activity_structure_has_required_fields(self, client):
        """
        Test that each activity has the required fields.
        
        AAA Pattern:
        - Arrange: Client is ready (fixture)
        - Act: GET /activities
        - Assert: Each activity has description, schedule, max_participants, participants
        """
        # Arrange
        client = client
        required_fields = {"description", "schedule", "max_participants", "participants"}
        
        # Act
        response = client.get("/activities")
        activities = response.json()
        
        # Assert
        for activity_name, activity_data in activities.items():
            assert isinstance(activity_data, dict), f"{activity_name} should be a dictionary"
            assert required_fields.issubset(set(activity_data.keys())), \
                f"{activity_name} missing required fields: {required_fields - set(activity_data.keys())}"
            
            # Verify field types
            assert isinstance(activity_data["description"], str), \
                f"{activity_name} description should be a string"
            assert isinstance(activity_data["schedule"], str), \
                f"{activity_name} schedule should be a string"
            assert isinstance(activity_data["max_participants"], int), \
                f"{activity_name} max_participants should be an integer"
            assert isinstance(activity_data["participants"], list), \
                f"{activity_name} participants should be a list"

    def test_participants_are_email_strings(self, client):
        """
        Test that all participants in activities are stored as email strings.
        
        AAA Pattern:
        - Arrange: Client is ready (fixture)
        - Act: GET /activities
        - Assert: All participants are strings (emails)
        """
        # Arrange
        client = client
        
        # Act
        response = client.get("/activities")
        activities = response.json()
        
        # Assert
        for activity_name, activity_data in activities.items():
            for participant in activity_data["participants"]:
                assert isinstance(participant, str), \
                    f"{activity_name} contains non-string participant: {participant}"
                assert "@" in participant, \
                    f"{activity_name} contains invalid email format: {participant}"

    def test_initial_participants_count(self, client, sample_activities):
        """
        Test that initial participant counts match expected values.
        
        AAA Pattern:
        - Arrange: sample_activities fixture provides initial state
        - Act: GET /activities
        - Assert: Participant counts match initial state
        """
        # Arrange
        client = client
        
        # Act
        response = client.get("/activities")
        activities = response.json()
        
        # Assert
        for activity_name, expected_data in sample_activities.items():
            actual_count = len(activities[activity_name]["participants"])
            expected_count = len(expected_data["participants"])
            assert actual_count == expected_count, \
                f"{activity_name} participant count mismatch: " \
                f"expected {expected_count}, got {actual_count}"
