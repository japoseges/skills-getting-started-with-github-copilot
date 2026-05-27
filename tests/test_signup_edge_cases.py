import pytest


class TestBusinessLogic:
    """Tests for business logic and edge cases"""
    
    def test_capacity_limits_respected(self, client):
        """Test that participant count respects capacity limits"""
        # Arrange: Get activities
        response = client.get("/activities")
        data = response.json()
        
        # Act & Assert
        for activity_name, activity_data in data.items():
            participants_count = len(activity_data["participants"])
            max_participants = activity_data["max_participants"]
            
            # Assert
            assert participants_count <= max_participants, \
                f"{activity_name} has {participants_count} participants but max is {max_participants}"


class TestMultipleSignups:
    """Tests for multiple signup scenarios"""
    
    def test_student_can_signup_for_multiple_activities(self, client):
        """Test that one student can signup for multiple activities"""
        # Arrange
        student_email = "multistudent@mergington.edu"
        activities_to_join = ["Chess Club", "Programming Class"]
        
        # Act
        for activity in activities_to_join:
            response = client.post(
                f"/activities/{activity}/signup?email={student_email}"
            )
            assert response.status_code == 200
        
        # Assert
        verify_response = client.get("/activities")
        verify_data = verify_response.json()
        for activity in activities_to_join:
            assert student_email in verify_data[activity]["participants"]

    def test_multiple_students_can_signup_for_same_activity(self, client):
        """Test that multiple students can signup for the same activity"""
        # Arrange
        activity_name = "Gym Class"
        new_students = ["student1@test.edu", "student2@test.edu", "student3@test.edu"]
        
        # Act
        for email in new_students:
            response = client.post(
                f"/activities/{activity_name}/signup?email={email}"
            )
            assert response.status_code == 200
        
        # Assert
        verify_response = client.get("/activities")
        verify_data = verify_response.json()
        for email in new_students:
            assert email in verify_data[activity_name]["participants"]


class TestSignupAndDeleteSequences:
    """Tests for complex signup and delete sequences"""
    
    def test_signup_delete_and_resign(self, client):
        """Test signup, delete, then re-signup sequence"""
        # Arrange
        student_email = "resignstudent@mergington.edu"
        activity_name = "Chess Club"
        
        # Act: Initial signup
        response1 = client.post(
            f"/activities/{activity_name}/signup?email={student_email}"
        )
        assert response1.status_code == 200
        
        # Assert: Verify added
        verify1 = client.get("/activities").json()
        assert student_email in verify1[activity_name]["participants"]
        
        # Act: Delete
        response2 = client.delete(
            f"/activities/{activity_name}/signup?email={student_email}"
        )
        assert response2.status_code == 200
        
        # Assert: Verify removed
        verify2 = client.get("/activities").json()
        assert student_email not in verify2[activity_name]["participants"]
        
        # Act: Re-signup
        response3 = client.post(
            f"/activities/{activity_name}/signup?email={student_email}"
        )
        
        # Assert: Verify re-registered
        assert response3.status_code == 200
        verify3 = client.get("/activities").json()
        assert student_email in verify3[activity_name]["participants"]

    def test_delete_and_verify_count_decreases(self, client):
        """Test that participant count decreases after deletion"""
        # Arrange
        activity_name = "Programming Class"
        email = "newuser@test.edu"
        
        # Arrange: Get initial count
        initial_response = client.get("/activities")
        initial_count = len(initial_response.json()[activity_name]["participants"])
        
        # Act: Add participant
        client.post(f"/activities/{activity_name}/signup?email={email}")
        
        # Assert: Count increased
        after_signup = client.get("/activities")
        count_after_signup = len(after_signup.json()[activity_name]["participants"])
        assert count_after_signup == initial_count + 1
        
        # Act: Delete participant
        client.delete(f"/activities/{activity_name}/signup?email={email}")
        
        # Assert: Count back to initial
        after_delete = client.get("/activities")
        count_after_delete = len(after_delete.json()[activity_name]["participants"])
        assert count_after_delete == initial_count
