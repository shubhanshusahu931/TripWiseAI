import pytest

def test_health_check(client):
    res = client.get("/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "healthy"

def test_unauthorized_access(client):
    res = client.get("/api/v1/trips")
    assert res.status_code == 401

def test_create_and_get_trip(client, auth_headers):
    payload = {
        "destination": "Tokyo",
        "origin": "San Francisco",
        "start_date": "2026-09-10",
        "end_date": "2026-09-13",
        "num_travelers": 2,
        "total_budget": 3500.0,
        "currency": "USD",
        "travel_style": "standard",
        "travel_pace": "balanced",
        "interests": ["sightseeing", "food", "culture"],
        "accommodation_preference": "hotel",
        "dietary_restrictions": ["none"]
    }
    # Create trip
    res = client.post("/api/v1/trips", json=payload, headers=auth_headers)
    assert res.status_code == 201
    data = res.json()
    trip_id = data["id"]
    assert data["destination"] == "Tokyo"
    assert "itinerary" in data
    assert data["itinerary"] is not None
    assert len(data["itinerary"]["days"]) >= 1

    # Get trips list
    res_list = client.get("/api/v1/trips", headers=auth_headers)
    assert res_list.status_code == 200
    trips = res_list.json()
    assert any(t["id"] == trip_id for t in trips)

    # Get single trip details
    res_detail = client.get(f"/api/v1/trips/{trip_id}", headers=auth_headers)
    assert res_detail.status_code == 200
    assert res_detail.json()["id"] == trip_id

    # Update trip
    res_up = client.put(f"/api/v1/trips/{trip_id}", json={"title": "Updated Tokyo Tour"}, headers=auth_headers)
    assert res_up.status_code == 200
    assert res_up.json()["title"] == "Updated Tokyo Tour"

    # Duplicate trip
    res_dup = client.post(f"/api/v1/trips/{trip_id}/duplicate", headers=auth_headers)
    assert res_dup.status_code == 201
    dup_data = res_dup.json()
    assert "Copy of" in dup_data["title"]

    # Delete trip
    res_del = client.delete(f"/api/v1/trips/{trip_id}", headers=auth_headers)
    assert res_del.status_code == 204
