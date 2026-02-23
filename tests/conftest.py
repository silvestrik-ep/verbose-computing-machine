"""
Shared test fixtures for FastAPI tests.

This module provides reusable fixtures following the pytest convention.
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture
def client():
    """
    Provide a TestClient for the FastAPI application.
    
    Returns:
        TestClient: Test client for making requests to the app
    """
    return TestClient(app)


@pytest.fixture
def sample_activities():
    """
    Provide a snapshot of the initial activities state.
    
    This fixture captures the initial state of activities before any test modifications.
    Note: The activities dictionary is mutable and shared across requests during tests,
    so tests should be aware that they may affect each other's state.
    
    Returns:
        dict: Copy of the activities dictionary with initial state
    """
    return {
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
        "Basketball Team": {
            "description": "Competitive basketball training and games",
            "schedule": "Mondays and Thursdays, 4:00 PM - 5:30 PM",
            "max_participants": 15,
            "participants": ["alex@mergington.edu"]
        },
        "Tennis Club": {
            "description": "Tennis coaching and match play",
            "schedule": "Wednesdays and Saturdays, 3:00 PM - 4:30 PM",
            "max_participants": 10,
            "participants": ["sarah@mergington.edu", "james@mergington.edu"]
        },
        "Debate Club": {
            "description": "Develop critical thinking and public speaking skills",
            "schedule": "Tuesdays, 3:30 PM - 4:45 PM",
            "max_participants": 18,
            "participants": ["rachel@mergington.edu", "mark@mergington.edu"]
        },
        "Robotics Club": {
            "description": "Design, build, and program competitive robots",
            "schedule": "Wednesdays and Fridays, 4:00 PM - 5:30 PM",
            "max_participants": 16,
            "participants": ["david@mergington.edu"]
        },
        "Art Studio": {
            "description": "Painting, drawing, and sculpture techniques",
            "schedule": "Mondays and Wednesdays, 3:30 PM - 4:45 PM",
            "max_participants": 14,
            "participants": ["grace@mergington.edu", "lucas@mergington.edu"]
        },
        "Jazz Band": {
            "description": "Learn and perform jazz music",
            "schedule": "Thursdays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["noah@mergington.edu"]
        }
    }


@pytest.fixture(autouse=True)
def reset_activities(sample_activities):
    """
    Reset activities to initial state before each test.
    
    This fixture automatically runs before each test to ensure a clean state.
    It restores the activities dictionary to match the sample_activities fixture.
    """
    yield
    # After test completes, reset the activities to initial state
    activities.clear()
    for name, activity_data in sample_activities.items():
        activities[name] = {
            "description": activity_data["description"],
            "schedule": activity_data["schedule"],
            "max_participants": activity_data["max_participants"],
            "participants": activity_data["participants"].copy()
        }
