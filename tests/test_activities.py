"""
Test cases for activities data structure and business logic

Tests cover:
- Initial activities data structure
- Data validation and integrity
- State management across operations
- Edge cases in activity and participant management
"""

import pytest
from src.app import activities


class TestActivitiesDataStructure:
    """Tests for the initial activities data structure"""

    def test_activities_is_dictionary(self):
        """Test that activities is a dictionary"""
        assert isinstance(activities, dict)

    def test_activities_has_nine_activities(self):
        """Test that there are exactly 9 activities defined"""
        assert len(activities) == 9

    def test_all_expected_activities_exist(self):
        """Test that all expected activities are present"""
        expected_activities = [
            "Chess Club",
            "Programming Class",
            "Gym Class",
            "Soccer Team",
            "Basketball Club",
            "Art Studio",
            "Drama Society",
            "Debate Club",
            "Math Olympiad"
        ]
        
        for expected in expected_activities:
            assert expected in activities, f"{expected} not found in activities"

    def test_each_activity_has_required_fields(self):
        """Test that each activity has all required fields"""
        required_fields = ["description", "schedule", "max_participants", "participants"]
        
        for activity_name, activity_data in activities.items():
            for field in required_fields:
                assert field in activity_data, f"{activity_name} missing {field}"

    def test_activity_descriptions_are_strings(self):
        """Test that all activity descriptions are non-empty strings"""
        for activity_name, activity_data in activities.items():
            assert isinstance(activity_data["description"], str)
            assert len(activity_data["description"]) > 0

    def test_activity_schedules_are_strings(self):
        """Test that all activity schedules are non-empty strings"""
        for activity_name, activity_data in activities.items():
            assert isinstance(activity_data["schedule"], str)
            assert len(activity_data["schedule"]) > 0

    def test_max_participants_are_positive_integers(self):
        """Test that all max_participants values are positive integers"""
        for activity_name, activity_data in activities.items():
            assert isinstance(activity_data["max_participants"], int)
            assert activity_data["max_participants"] > 0

    def test_participants_are_lists(self):
        """Test that all participants fields are lists"""
        for activity_name, activity_data in activities.items():
            assert isinstance(activity_data["participants"], list)


class TestInitialParticipants:
    """Tests for the initial state of participants"""

    def test_chess_club_initial_participants(self):
        """Test Chess Club has correct initial participants"""
        expected_participants = ["michael@mergington.edu", "daniel@mergington.edu"]
        assert activities["Chess Club"]["participants"] == expected_participants

    def test_programming_class_initial_participants(self):
        """Test Programming Class has correct initial participants"""
        expected_participants = ["emma@mergington.edu", "sophia@mergington.edu"]
        assert activities["Programming Class"]["participants"] == expected_participants

    def test_all_activities_have_initial_participants(self):
        """Test that all activities start with at least some participants"""
        for activity_name, activity_data in activities.items():
            # Each activity should have exactly 2 initial participants based on the data
            assert len(activity_data["participants"]) == 2, \
                f"{activity_name} should have 2 initial participants"

    def test_initial_participants_are_valid_emails(self):
        """Test that all initial participants have email-like format"""
        for activity_name, activity_data in activities.items():
            for participant in activity_data["participants"]:
                assert isinstance(participant, str)
                assert "@" in participant
                assert "." in participant


class TestActivityCapacityLimits:
    """Tests for activity capacity and participant limits"""

    def test_max_participants_varies_by_activity(self):
        """Test that different activities have different maximum capacities"""
        max_values = [activity["max_participants"] for activity in activities.values()]
        # Should have at least a few different values
        assert len(set(max_values)) > 1

    def test_specific_activity_capacities(self):
        """Test specific known activity capacities"""
        assert activities["Chess Club"]["max_participants"] == 12
        assert activities["Programming Class"]["max_participants"] == 20
        assert activities["Gym Class"]["max_participants"] == 30
        assert activities["Soccer Team"]["max_participants"] == 22

    def test_initial_participants_below_max(self):
        """Test that initial participant counts are below maximum capacity"""
        for activity_name, activity_data in activities.items():
            current_count = len(activity_data["participants"])
            max_count = activity_data["max_participants"]
            assert current_count < max_count, \
                f"{activity_name} has {current_count} participants but max is {max_count}"


class TestActivityStateManagement:
    """Tests for managing activity state across operations"""

    def test_participant_list_is_mutable(self, client, sample_emails):
        """Test that participant lists can be modified"""
        initial_count = len(activities["Chess Club"]["participants"])
        
        # Add a participant via API
        client.post(f"/activities/Chess Club/signup?email={sample_emails['new_student']}")
        
        # Verify count increased
        assert len(activities["Chess Club"]["participants"]) == initial_count + 1

    def test_removing_participant_decreases_count(self, client, sample_emails):
        """Test that removing a participant decreases the count"""
        initial_count = len(activities["Programming Class"]["participants"])
        
        # Remove a participant
        client.delete(f"/activities/Programming Class/participants/{sample_emails['existing_programming']}")
        
        # Verify count decreased
        assert len(activities["Programming Class"]["participants"]) == initial_count - 1

    def test_multiple_operations_maintain_correct_state(self, client, sample_emails):
        """Test that multiple operations maintain correct state"""
        activity_name = "Basketball Club"
        initial_participants = activities[activity_name]["participants"].copy()
        
        # Add a new student
        new_email = sample_emails["new_student"]
        client.post(f"/activities/{activity_name}/signup?email={new_email}")
        
        # Remove an existing student
        existing_email = activities[activity_name]["participants"][0]
        client.delete(f"/activities/{activity_name}/participants/{existing_email}")
        
        # Verify final state
        final_participants = activities[activity_name]["participants"]
        assert new_email in final_participants
        assert existing_email not in final_participants
        assert len(final_participants) == len(initial_participants)  # Added 1, removed 1

    def test_operations_on_one_activity_dont_affect_others(self, client, sample_emails):
        """Test that operations on one activity don't affect other activities"""
        # Store initial state of all activities
        initial_states = {
            name: data["participants"].copy()
            for name, data in activities.items()
        }
        
        # Modify Chess Club
        client.post(f"/activities/Chess Club/signup?email={sample_emails['new_student']}")
        
        # Verify other activities unchanged
        for activity_name, initial_participants in initial_states.items():
            if activity_name != "Chess Club":
                assert activities[activity_name]["participants"] == initial_participants


class TestActivityNaming:
    """Tests for activity naming and lookup"""

    def test_activity_names_contain_spaces(self):
        """Test that some activity names contain spaces"""
        names_with_spaces = [name for name in activities.keys() if " " in name]
        assert len(names_with_spaces) > 0

    def test_activity_lookup_exact_match_required(self, client):
        """Test that activity lookup requires exact name match"""
        # This is implicitly tested by trying to access with wrong case
        response = client.get("/activities")
        assert "Chess Club" in response.json()
        assert "chess club" not in response.json()

    def test_all_activity_names_are_unique(self):
        """Test that all activity names are unique (no duplicates)"""
        activity_names = list(activities.keys())
        assert len(activity_names) == len(set(activity_names))


class TestFixtureIsolation:
    """Tests to verify that the reset_activities fixture provides proper test isolation"""

    def test_modifications_dont_persist_between_tests_first(self, client, sample_emails):
        """First test that modifies data"""
        # Add a participant to Chess Club
        client.post(f"/activities/Chess Club/signup?email={sample_emails['test_user']}")
        assert sample_emails['test_user'] in activities["Chess Club"]["participants"]

    def test_modifications_dont_persist_between_tests_second(self, sample_emails):
        """Second test that should see fresh data"""
        # The test_user should NOT be in Chess Club because the fixture reset the data
        assert sample_emails['test_user'] not in activities["Chess Club"]["participants"]

    def test_fixture_resets_to_initial_state(self):
        """Test that fixture properly resets activities to initial state"""
        # After any test, we should have exactly 9 activities
        assert len(activities) == 9
        
        # And Chess Club should have its initial 2 participants
        assert len(activities["Chess Club"]["participants"]) == 2
        assert "michael@mergington.edu" in activities["Chess Club"]["participants"]
        assert "daniel@mergington.edu" in activities["Chess Club"]["participants"]
