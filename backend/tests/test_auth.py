from fastapi.testclient import TestClient

def test_signup(client):
    response = client.post("/auth/signup", json={
        "email": "newuser@example.com",
        "password": "password123",
        "full_name": "New User"
    })
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert data["email"] == "newuser@example.com"

def test_login(client, test_user):
    response = client.post("/auth/token", data={
        "username": "test@example.com",
        "password": "testpassword123"
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_get_current_user(client, test_user):
    # First login to get token
    response = client.post("/auth/token", data={
        "username": "test@example.com",
        "password": "testpassword123"
    })
    token = response.json()["access_token"]
    
    # Then get current user with token
    response = client.get("/auth/me", headers={
        "Authorization": f"Bearer {token}"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test@example.com"
