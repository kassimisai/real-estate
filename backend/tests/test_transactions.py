import pytest
from datetime import datetime, timedelta
from fastapi.testclient import TestClient

@pytest.fixture
def auth_headers(client, test_user):
    response = client.post("/auth/token", data={
        "username": "test@example.com",
        "password": "testpassword123"
    })
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
def test_lead(client, auth_headers):
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
    return response.json()

def test_create_transaction(client, auth_headers, test_lead):
    closing_date = (datetime.utcnow() + timedelta(days=30)).isoformat()
    response = client.post("/transactions/",
        headers=auth_headers,
        json={
            "lead_id": test_lead["id"],
            "property_address": "123 Main St",
            "price": "500000",
            "closing_date": closing_date,
            "notes": "Test transaction"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["property_address"] == "123 Main St"
    assert "id" in data

def test_get_transactions(client, auth_headers, test_lead):
    # First create a transaction
    closing_date = (datetime.utcnow() + timedelta(days=30)).isoformat()
    client.post("/transactions/",
        headers=auth_headers,
        json={
            "lead_id": test_lead["id"],
            "property_address": "123 Main St",
            "price": "500000",
            "closing_date": closing_date,
            "notes": "Test transaction"
        }
    )
    
    # Then get all transactions
    response = client.get("/transactions/", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert data[0]["property_address"] == "123 Main St"

def test_update_transaction(client, auth_headers, test_lead):
    # First create a transaction
    closing_date = (datetime.utcnow() + timedelta(days=30)).isoformat()
    create_response = client.post("/transactions/",
        headers=auth_headers,
        json={
            "lead_id": test_lead["id"],
            "property_address": "123 Main St",
            "price": "500000",
            "closing_date": closing_date,
            "notes": "Test transaction"
        }
    )
    transaction_id = create_response.json()["id"]
    
    # Then update the transaction
    new_closing_date = (datetime.utcnow() + timedelta(days=45)).isoformat()
    response = client.put(f"/transactions/{transaction_id}",
        headers=auth_headers,
        json={
            "price": "550000",
            "closing_date": new_closing_date,
            "status": "under_contract"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["price"] == "550000"
    assert data["status"] == "under_contract"
