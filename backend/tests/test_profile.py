import pytest

def test_profile_operations(client, auth_headers):
    # Fetch initial profile
    res = client.get("/api/v1/profile", headers=auth_headers)
    assert res.status_code == 200
    data = res.json()
    assert "email" in data
    assert data["preferred_currency"] in ("USD", "EUR", "GBP", "JPY")

    # Update profile
    up_res = client.put("/api/v1/profile", json={
        "display_name": "Globetrotter Alex",
        "preferred_currency": "EUR",
        "preferred_travel_style": "luxury",
        "home_city": "London"
    }, headers=auth_headers)
    assert up_res.status_code == 200
    up_data = up_res.json()
    assert up_data["display_name"] == "Globetrotter Alex"
    assert up_data["preferred_currency"] == "EUR"
    assert up_data["preferred_travel_style"] == "luxury"
    assert up_data["home_city"] == "London"
