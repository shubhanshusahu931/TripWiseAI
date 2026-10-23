import pytest

def test_activity_lifecycle_and_budget(client, auth_headers):
    # 1. Create a trip
    trip_res = client.post("/api/v1/trips", json={
        "destination": "Paris",
        "start_date": "2026-07-01",
        "end_date": "2026-07-03",
        "num_travelers": 1,
        "total_budget": 1500.0,
        "currency": "EUR",
        "travel_style": "standard"
    }, headers=auth_headers)
    assert trip_res.status_code == 201
    trip_data = trip_res.json()
    trip_id = trip_data["id"]
    initial_total = trip_data["itinerary"]["estimated_total_cost"]

    # 2. Add custom activity
    new_act = {
        "day_number": 1,
        "title": "Private Seine Dinner Cruise",
        "time_slot": "Evening",
        "start_time": "19:30",
        "end_time": "22:00",
        "location": "Pont Alexandre III",
        "duration_minutes": 150,
        "estimated_cost": 120.0,
        "currency": "EUR",
        "transportation_suggestion": "Taxi from hotel",
        "practical_tips": "Smart casual dress code required"
    }
    act_res = client.post(f"/api/v1/trips/{trip_id}/activities", json=new_act, headers=auth_headers)
    assert act_res.status_code == 201
    act_data = act_res.json()
    act_id = act_data["id"]
    assert act_data["title"] == "Private Seine Dinner Cruise"
    assert act_data["is_custom"] is True

    # 3. Check updated trip itinerary and budget
    detail_res = client.get(f"/api/v1/trips/{trip_id}", headers=auth_headers)
    updated_total = detail_res.json()["itinerary"]["estimated_total_cost"]
    # Total should have increased by cost + 5% misc
    assert updated_total > initial_total

    # 4. Modify activity cost
    client.put(
        f"/api/v1/trips/{trip_id}/activities/{act_id}",
        json={"estimated_cost": 150.0, "title": "VIP Seine Dinner Cruise"},
        headers=auth_headers
    )
    detail_res2 = client.get(f"/api/v1/trips/{trip_id}", headers=auth_headers)
    assert detail_res2.json()["itinerary"]["estimated_total_cost"] > updated_total

    # 5. Delete activity
    del_res = client.delete(f"/api/v1/trips/{trip_id}/activities/{act_id}", headers=auth_headers)
    assert del_res.status_code == 204

    # 6. Verify budget returned back
    detail_res3 = client.get(f"/api/v1/trips/{trip_id}", headers=auth_headers)
    assert round(detail_res3.json()["itinerary"]["estimated_total_cost"], 1) == round(initial_total, 1)
