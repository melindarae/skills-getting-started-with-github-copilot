"""
Test cases for all API endpoints in the Mergington High School API

Tests cover:
- Root endpoint redirection
- List activities endpoint
- Signup endpoint (happy paths and error cases)
- Remove participant endpoint (happy paths and error cases)
- Edge cases including URL encoding
"""

import pytest
from urllib.parse import quote


class TestRootEndpoint:
    """Tests for the root endpoint (/)"""

    def test_root_redirects_to_static_index(self, client):
        """Test that GET / redirects to the static index.html page"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"


class TestGetActivities:
    """Tests for the GET /activities endpoint"""

    def test_get_activities_success(self, client):
        """Test that GET /activities returns all activities with correct structure"""
        response = client.get("/activities")
        assert response.status_code == 200
        
        activities = response.json()
        assert isinstance(activities, dict)
        assert len(activities) == 9

    def test_get_activities_has_required_fields(self, client):
        """Test that each activity has required fields"""
        response = client.get("/activities")
        activities = response.json()
        
        for activity_name, activity_data in activities.items():
            assert "description" in activity_data
            assert "schedule" in activity_data
            assert "max_participants" in activity_data
            assert "participants" in activity_data
            assert isinstance(activity_data["participants"], list)

    def test_get_activities_includes_all_expected_activities(self, client):
        """Test that all expected activities are present"""
        response = client.get("/activities")
        activities = response.json()
        
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
            assert expected in activities


class TestSignupEndpoint:
    """Tests for the POST /activities/{activity_name}/signup endpoint"""

    def test_signup_success(self, client, sample_emails):
        """Test successful signup for an activity"""
        activity_name = "Chess Club"
        email = sample_emails["new_student"]
        
        response = client.post(f"/activities/{activity_name}/signup?email={email}")
        assert response.status_code == 200
        assert response.json() == {"message": f"Signed up {email} for {activity_name}"}

    def test_signup_adds_participant_to_activity(self, client, sample_emails):
        """Test that signup actually adds the participant to the activity"""
        activity_name = "Programming Class"
        email = sample_emails["new_student"]
        
        # Sign up
        client.post(f"/activities/{activity_name}/signup?email={email}")
        
        # Verify participant was added
        response = client.get("/activities")
        activities = response.json()
        assert email in activities[activity_name]["participants"]

    def test_signup_with_url_encoded_activity_name(self, client, sample_emails):
        """Test signup works with URL-encoded activity names (spaces)"""
        activity_name = "Chess Club"
        encoded_name = quote(activity_name)
        email = sample_emails["new_student"]
        
        response = client.post(f"/activities/{encoded_name}/signup?email={email}")
        assert response.status_code == 200

    def test_signup_activity_not_found(self, client, sample_emails):
        """Test 404 error when activity doesn't exist"""
        response = client.post(
            f"/activities/Nonexistent Activity/signup?email={sample_emails['new_student']}"
        )
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"

    def test_signup_student_already_signed_up(self, client, sample_emails):
        """Test 400 error when student is already signed up"""
        activity_name = "Chess Club"
        email = sample_emails["existing_chess"]  # michael@mergington.edu is already in Chess Club
        
        response = client.post(f"/activities/{activity_name}/signup?email={email}")
        assert response.status_code == 400
        assert response.json()["detail"] == "Student already signed up"

    def test_signup_multiple_students_same_activity(self, client, sample_emails):
        """Test multiple students can sign up for the same activity"""
        activity_name = "Math Olympiad"
        
        # Sign up first student
        response1 = client.post(
            f"/activities/{activity_name}/signup?email={sample_emails['new_student']}"
        )
        assert response1.status_code == 200
        
        # Sign up second student
        response2 = client.post(
            f"/activities/{activity_name}/signup?email={sample_emails['another_student']}"
        )
        assert response2.status_code == 200
        
        # Verify both are in the activity
        activities_response = client.get("/activities")
        activities = activities_response.json()
        assert sample_emails['new_student'] in activities[activity_name]["participants"]
        assert sample_emails['another_student'] in activities[activity_name]["participants"]

    def test_signup_student_for_multiple_activities(self, client, sample_emails):
        """Test a student can sign up for multiple activities"""
        email = sample_emails["new_student"]
        
        # Sign up for Chess Club
        response1 = client.post(f"/activities/Chess Club/signup?email={email}")
        assert response1.status_code == 200
        
        # Sign up for Programming Class
        response2 = client.post(f"/activities/Programming Class/signup?email={email}")
        assert response2.status_code == 200
        
        # Verify student is in both activities
        activities_response = client.get("/activities")
        activities = activities_response.json()
        assert email in activities["Chess Club"]["participants"]
        assert email in activities["Programming Class"]["participants"]


class TestRemoveParticipantEndpoint:
    """Tests for the DELETE /activities/{activity_name}/participants/{email} endpoint"""

    def test_remove_participant_success(self, client, sample_emails):
        """Test successful removal of a participant"""
        activity_name = "Chess Club"
        email = sample_emails["existing_chess"]  # michael@mergington.edu
        
        response = client.delete(f"/activities/{activity_name}/participants/{email}")
        assert response.status_code == 200
        assert response.json() == {"message": f"Removed {email} from {activity_name}"}

    def test_remove_participant_actually_removes(self, client, sample_emails):
        """Test that removal actually removes the participant from the activity"""
        activity_name = "Programming Class"
        email = sample_emails["existing_programming"]  # emma@mergington.edu
        
        # Remove participant
        client.delete(f"/activities/{activity_name}/participants/{email}")
        
        # Verify participant was removed
        response = client.get("/activities")
        activities = response.json()
        assert email not in activities[activity_name]["participants"]

    def test_remove_participant_with_url_encoded_activity_name(self, client, sample_emails):
        """Test removal works with URL-encoded activity names"""
        activity_name = "Chess Club"
        encoded_name = quote(activity_name)
        email = sample_emails["existing_chess"]
        
        response = client.delete(f"/activities/{encoded_name}/participants/{email}")
        assert response.status_code == 200

    def test_remove_participant_with_url_encoded_email(self, client):
        """Test removal works with URL-encoded email addresses"""
        activity_name = "Chess Club"
        email = "michael@mergington.edu"
        encoded_email = quote(email)
        
        response = client.delete(f"/activities/{activity_name}/participants/{encoded_email}")
        assert response.status_code == 200

    def test_remove_participant_activity_not_found(self, client, sample_emails):
        """Test 404 error when activity doesn't exist"""
        response = client.delete(
            f"/activities/Nonexistent Activity/participants/{sample_emails['new_student']}"
        )
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"

    def test_remove_participant_not_in_activity(self, client, sample_emails):
        """Test 404 error when student is not in the activity"""
        activity_name = "Chess Club"
        email = sample_emails["new_student"]  # This student is not in Chess Club
        
        response = client.delete(f"/activities/{activity_name}/participants/{email}")
        assert response.status_code == 404
        assert response.json()["detail"] == "Student not found in activity"

    def test_signup_then_remove_then_signup_again(self, client, sample_emails):
        """Test that a student can be removed and then sign up again"""
        activity_name = "Basketball Club"
        email = sample_emails["new_student"]
        
        # Sign up
        signup_response = client.post(f"/activities/{activity_name}/signup?email={email}")
        assert signup_response.status_code == 200
        
        # Remove
        remove_response = client.delete(f"/activities/{activity_name}/participants/{email}")
        assert remove_response.status_code == 200
        
        # Sign up again
        signup_again_response = client.post(f"/activities/{activity_name}/signup?email={email}")
        assert signup_again_response.status_code == 200
        
        # Verify student is in the activity
        activities_response = client.get("/activities")
        activities = activities_response.json()
        assert email in activities[activity_name]["participants"]


class TestEdgeCases:
    """Tests for edge cases and special scenarios"""

    def test_activity_name_case_sensitivity(self, client, sample_emails):
        """Test that activity names are case-sensitive"""
        # Try with wrong case
        response = client.post(
            f"/activities/chess club/signup?email={sample_emails['new_student']}"
        )
        assert response.status_code == 404

    def test_list_activities_after_modifications(self, client, sample_emails):
        """Test that GET /activities reflects all modifications"""
        # Add a participant to Chess Club
        client.post(f"/activities/Chess Club/signup?email={sample_emails['new_student']}")
        
        # Remove a participant from Programming Class
        client.delete(f"/activities/Programming Class/participants/{sample_emails['existing_programming']}")
        
        # Get activities and verify changes
        response = client.get("/activities")
        activities = response.json()
        
        assert sample_emails['new_student'] in activities["Chess Club"]["participants"]
        assert sample_emails['existing_programming'] not in activities["Programming Class"]["participants"]
