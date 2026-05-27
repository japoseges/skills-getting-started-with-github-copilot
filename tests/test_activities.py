import pytest


class TestGetActivities:
    """Tests for GET /activities endpoint"""
    
    def test_get_activities_returns_all_activities(self, client):
        """Test retrieving all activities"""
        # Arrange: Client is ready from fixture
        
        # Act
        response = client.get("/activities")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert "Chess Club" in data
        assert "Programming Class" in data
        assert "Gym Class" in data

    def test_get_activities_returns_correct_structure(self, client):
        """Test that activities have correct structure"""
        # Arrange: Client is ready from fixture
        
        # Act
        response = client.get("/activities")
        data = response.json()
        
        # Assert
        for activity_name, activity_data in data.items():
            assert isinstance(activity_name, str)
            assert isinstance(activity_data.get("description"), str)
            assert isinstance(activity_data.get("schedule"), str)
            assert isinstance(activity_data.get("max_participants"), int)
            assert isinstance(activity_data.get("participants"), list)

    def test_get_activities_contains_participants(self, client):
        """Test that activities contain expected participants"""
        # Arrange: Client is ready from fixture
        
        # Act
        response = client.get("/activities")
        data = response.json()
        
        # Assert
        assert "michael@mergington.edu" in data["Chess Club"]["participants"]
        assert "emma@mergington.edu" in data["Programming Class"]["participants"]


class TestSignupForActivity:
    """Tests for POST /activities/{activity_name}/signup endpoint"""
    
    def test_signup_new_student_successfully(self, client):
        """Test successful signup for a new student"""
        # Arrange
        activity_name = "Chess Club"
        new_email = "newstudent@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup?email={new_email}"
        )
        
        # Assert
        assert response.status_code == 200
        assert new_email in response.json()["message"]
        
        # Assert: Verify participant was added
        verify_response = client.get("/activities")
        verify_data = verify_response.json()
        assert new_email in verify_data[activity_name]["participants"]

    def test_signup_duplicate_student_fails(self, client):
        """Test that duplicate signup is rejected"""
        # Arrange
        activity_name = "Chess Club"
        new_email = "duplicate@mergington.edu"
        
        # Act: First signup
        response1 = client.post(
            f"/activities/{activity_name}/signup?email={new_email}"
        )
        assert response1.status_code == 200
        
        # Act: Duplicate signup
        response2 = client.post(
            f"/activities/{activity_name}/signup?email={new_email}"
        )
        
        # Assert
        assert response2.status_code == 400
        error_detail = response2.json()["detail"].lower()
        assert "already" in error_detail and ("signed up" in error_detail or "registered" in error_detail)

    def test_signup_nonexistent_activity_fails(self, client):
        """Test signup for activity that doesn't exist"""
        # Arrange
        activity_name = "Nonexistent Club"
        email = "student@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup?email={email}"
        )
        
        # Assert
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_signup_response_format(self, client):
        """Test that signup response has correct format"""
        # Arrange
        email = "formatcheck@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/Chess%20Club/signup?email={email}"
        )
        data = response.json()
        
        # Assert
        assert "message" in data
        assert isinstance(data["message"], str)
        assert email in data["message"]
        assert "Chess Club" in data["message"]


class TestDeleteParticipant:
    """Tests for DELETE /activities/{activity_name}/signup endpoint"""
    
    def test_delete_participant_successfully(self, client):
        """Test successful removal of a participant"""
        # Arrange
        activity_name = "Chess Club"
        new_email = "todelete@mergington.edu"
        
        # Arrange: Add participant first
        client.post(f"/activities/{activity_name}/signup?email={new_email}")
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/signup?email={new_email}"
        )
        
        # Assert
        assert response.status_code == 200
        assert new_email in response.json()["message"]
        
        # Assert: Verify participant was removed
        verify_response = client.get("/activities")
        verify_data = verify_response.json()
        assert new_email not in verify_data[activity_name]["participants"]

    def test_delete_existing_participant_from_initial_state(self, client):
        """Test removing a participant who was pre-registered"""
        # Arrange
        activity_name = "Chess Club"
        existing_email = "michael@mergington.edu"
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/signup?email={existing_email}"
        )
        
        # Assert
        assert response.status_code == 200
        
        # Assert: Verify participant was removed
        verify_response = client.get("/activities")
        verify_data = verify_response.json()
        assert existing_email not in verify_data[activity_name]["participants"]

    def test_delete_nonexistent_participant_fails(self, client):
        """Test removal of participant who isn't signed up"""
        # Arrange
        activity_name = "Chess Club"
        nonexistent_email = "notregistered@mergington.edu"
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/signup?email={nonexistent_email}"
        )
        
        # Assert
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_delete_from_nonexistent_activity_fails(self, client):
        """Test removal from activity that doesn't exist"""
        # Arrange
        activity_name = "Nonexistent Club"
        email = "student@mergington.edu"
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/signup?email={email}"
        )
        
        # Assert
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_delete_response_format(self, client):
        """Test that delete response has correct format"""
        # Arrange
        email = "michael@mergington.edu"
        
        # Act
        response = client.delete(
            f"/activities/Chess%20Club/signup?email={email}"
        )
        data = response.json()
        
        # Assert
        assert "message" in data
        assert isinstance(data["message"], str)
        assert email in data["message"]


class TestRootEndpoint:
    """Tests for root endpoint"""
    
    def test_root_redirects_to_static_index(self, client):
        """Test that root path redirects to static/index.html"""
        # Arrange: Client is ready
        
        # Act
        response = client.get("/", follow_redirects=False)
        
        # Assert
        assert response.status_code == 307
        assert "/static/index.html" in response.headers["location"]
