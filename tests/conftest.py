"""
Pytest configuration and fixtures for Mergington High School API tests
"""

import pytest
from fastapi.testclient import TestClient
from copy import deepcopy
from src.app import app, activities


# Store the initial state of activities
INITIAL_ACTIVITIES = {
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
    "Soccer Team": {
        "description": "Team-based soccer training and competitive matches",
        "schedule": "Mondays and Wednesdays, 4:00 PM - 5:30 PM",
        "max_participants": 22,
        "participants": ["liam@mergington.edu", "noah@mergington.edu"]
    },
    "Basketball Club": {
        "description": "Practice basketball fundamentals and play weekly scrimmages",
        "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:30 PM",
        "max_participants": 18,
        "participants": ["ava@mergington.edu", "mia@mergington.edu"]
    },
    "Art Studio": {
        "description": "Explore painting, sketching, and mixed media art",
        "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
        "max_participants": 15,
        "participants": ["isabella@mergington.edu", "charlotte@mergington.edu"]
    },
    "Drama Society": {
        "description": "Acting workshops and school theater productions",
        "schedule": "Fridays, 4:00 PM - 6:00 PM",
        "max_participants": 25,
        "participants": ["amelia@mergington.edu", "harper@mergington.edu"]
    },
    "Debate Club": {
        "description": "Develop public speaking and argumentation skills through debates",
        "schedule": "Thursdays, 3:30 PM - 5:00 PM",
        "max_participants": 16,
        "participants": ["ethan@mergington.edu", "james@mergington.edu"]
    },
    "Math Olympiad": {
        "description": "Solve advanced math problems and prepare for competitions",
        "schedule": "Mondays, 3:30 PM - 5:00 PM",
        "max_participants": 14,
        "participants": ["lucas@mergington.edu", "benjamin@mergington.edu"]
    }
}


@pytest.fixture
def client():
    """
    Provides a FastAPI TestClient instance for making HTTP requests to the API.
    
    This fixture creates a test client that can be used to make requests to the
    application without running a server.
    """
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    """
    Resets the activities dictionary to its initial state before each test.
    
    This fixture runs automatically before each test (autouse=True) to ensure
    test isolation by preventing tests from affecting each other through shared state.
    Uses deepcopy to ensure complete independence of the data structure.
    """
    activities.clear()
    activities.update(deepcopy(INITIAL_ACTIVITIES))
    yield
    # Teardown: reset again after the test
    activities.clear()
    activities.update(deepcopy(INITIAL_ACTIVITIES))


@pytest.fixture
def sample_emails():
    """
    Provides a list of sample email addresses for testing.
    
    Returns:
        dict: A dictionary with labeled test email addresses
    """
    return {
        "new_student": "newstudent@mergington.edu",
        "another_student": "anotherstudent@mergington.edu",
        "test_user": "testuser@example.com",
        "existing_chess": "michael@mergington.edu",  # Already in Chess Club
        "existing_programming": "emma@mergington.edu"  # Already in Programming Class
    }
