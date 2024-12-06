import pytest
from fastapi.testclient import TestClient

@pytest.fixture
def auth_headers(client, test_user):
    response = client.post("/auth/token", data={
        "username": "test@example.com",
        "password": "testpassword123"
    })
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

def test_create_lead(client, auth_headers):
    response = client.post("/leads/", 
        headers=auth_headers,
        json={
            "first_name": "John",
            "last_name": "Doe",
            "email": "john@example.com",
            "phone": "1234567890",
            "source": "website"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["first_name"] == "John"
    assert data["last_name"] == "Doe"
    assert "id" in data

def test_get_leads(client, auth_headers):
    # First create a lead
    client.post("/leads/", 
        headers=auth_headers,
        json={
            "first_name": "John",
            "last_name": "Doe",
            "email": "john@example.com",
            "phone": "1234567890",
            "source": "website"
        }
    )
    
    # Then get all leads
    response = client.get("/leads/", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert data[0]["first_name"] == "John"

def test_update_lead(client, auth_headers):
    # First create a lead
    create_response = client.post("/leads/", 
        headers=auth_headers,
        json={
            "first_name": "John",
            "last_name": "Doe",
            "email": "john@example.com",
            "phone": "1234567890",
            "source": "website"
        }
    )
    lead_id = create_response.json()["id"]
    
    # Then update the lead
    response = client.put(f"/leads/{lead_id}",
        headers=auth_headers,
        json={
            "first_name": "Jane",
            "last_name": "Doe",
            "status": "contacted"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["first_name"] == "Jane"
    assert data["status"] == "contacted"
