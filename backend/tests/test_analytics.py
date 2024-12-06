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
def sample_data(client, auth_headers):
    # Create some leads
    for i in range(3):
        client.post("/leads/", 
            headers=auth_headers,
            json={
                "first_name": f"User{i}",
                "last_name": "Test",
                "email": f"user{i}@example.com",
                "source": "website"
            }
        )
    
    # Create some transactions
    closing_date = (datetime.utcnow() + timedelta(days=30)).isoformat()
    for i in range(2):
        client.post("/transactions/",
            headers=auth_headers,
            json={
                "lead_id": f"user{i}",
                "property_address": f"{i} Main St",
                "price": str(500000 + i*50000),
                "closing_date": closing_date
            }
        )

def test_generate_report(client, auth_headers, sample_data):
    response = client.post("/analytics/report",
        headers=auth_headers,
        json={
            "date_range": 30,
            "send_email": False
        }
    )
    assert response.status_code == 200
    data = response.json()
    
    # Check report structure
    assert "report" in data
    assert "visualizations" in data
    assert "analysis" in data
    
    # Check report content
    report = data["report"]
    assert "lead_metrics" in report
    assert "transaction_metrics" in report
    assert report["lead_metrics"]["total_leads"] == 3
    assert report["transaction_metrics"]["total_transactions"] == 2

def test_create_visualization(client, auth_headers, sample_data):
    # First get report data
    report_response = client.post("/analytics/report",
        headers=auth_headers,
        json={
            "date_range": 30,
            "send_email": False
        }
    )
    report_data = report_response.json()["report"]
    
    # Test creating different visualizations
    viz_types = ["leads_over_time", "transactions_by_status"]
    for viz_type in viz_types:
        response = client.post(f"/analytics/visualizations/{viz_type}",
            headers=auth_headers,
            json={
                "data": report_data
            }
        )
        assert response.status_code == 200
        viz_data = response.json()
        assert "data" in viz_data

def test_get_metrics(client, auth_headers, sample_data):
    response = client.get("/analytics/metrics",
        headers=auth_headers,
        params={
            "metric_type": "leads",
            "date_range": 30
        }
    )
    assert response.status_code == 200
    data = response.json()
    
    # Check metrics content
    assert "total_leads" in data
    assert data["total_leads"] == 3
    assert "leads_by_source" in data
    assert data["leads_by_source"]["website"] == 3
