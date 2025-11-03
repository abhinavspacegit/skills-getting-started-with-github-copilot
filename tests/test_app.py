from fastapi.testclient import TestClient
import pytest
from src.app import app

client = TestClient(app)

def test_read_activities():
    """Test getting all activities"""
    response = client.get("/activities")
    assert response.status_code == 200
    activities = response.json()
    assert isinstance(activities, dict)
    assert "Chess Club" in activities
    assert "Programming Class" in activities

def test_signup_for_activity():
    """Test signing up for an activity"""
    email = "test@mergington.edu"
    activity_name = "Chess Club"
    
    response = client.post(f"/activities/{activity_name}/signup?email={email}")
    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {email} for {activity_name}"

    # Verify the participant was added
    activities = client.get("/activities").json()
    assert email in activities[activity_name]["participants"]

def test_signup_for_nonexistent_activity():
    """Test signing up for an activity that doesn't exist"""
    email = "test@mergington.edu"
    activity_name = "Nonexistent Club"
    
    response = client.post(f"/activities/{activity_name}/signup?email={email}")
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"

def test_duplicate_signup():
    """Test signing up for an activity when already registered"""
    email = "test@mergington.edu"
    activity_name = "Programming Class"
    
    # First signup
    response = client.post(f"/activities/{activity_name}/signup?email={email}")
    assert response.status_code == 200
    
    # Try to signup again
    response = client.post(f"/activities/{activity_name}/signup?email={email}")
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"

def test_unregister_from_activity():
    """Test unregistering from an activity"""
    email = "test@mergington.edu"
    activity_name = "Chess Club"
    
    # First sign up for the activity
    client.post(f"/activities/{activity_name}/signup?email={email}")
    
    # Then unregister
    response = client.post(f"/activities/{activity_name}/unregister?email={email}")
    assert response.status_code == 200
    assert response.json()["message"] == f"Unregistered {email} from {activity_name}"
    
    # Verify the participant was removed
    activities = client.get("/activities").json()
    assert email not in activities[activity_name]["participants"]

def test_unregister_from_nonexistent_activity():
    """Test unregistering from an activity that doesn't exist"""
    email = "test@mergington.edu"
    activity_name = "Nonexistent Club"
    
    response = client.post(f"/activities/{activity_name}/unregister?email={email}")
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"

def test_unregister_when_not_registered():
    """Test unregistering when not registered for the activity"""
    email = "notregistered@mergington.edu"
    activity_name = "Chess Club"
    
    response = client.post(f"/activities/{activity_name}/unregister?email={email}")
    assert response.status_code == 400
    assert response.json()["detail"] == "Student is not registered for this activity"

def test_max_participants():
    """Test signing up when activity is full"""
    activity_name = "Chess Club"
    activities = client.get("/activities").json()
    max_participants = activities[activity_name]["max_participants"]
    current_participants = len(activities[activity_name]["participants"])
    spots_remaining = max_participants - current_participants
    
    # Fill up the remaining spots
    for i in range(spots_remaining + 1):
        email = f"newstudent{i}@mergington.edu"
        response = client.post(f"/activities/{activity_name}/signup?email={email}")
        
        if i < spots_remaining:
            assert response.status_code == 200, f"Failed to add student when {spots_remaining - i} spots remained"
        else:
            # This should fail as we've reached max participants
            assert response.status_code == 400, "Should not allow signup when activity is full"
            assert "Activity is full" in response.json()["detail"]