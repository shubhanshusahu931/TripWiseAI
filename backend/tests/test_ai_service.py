import pytest
import asyncio
from app.services.ai_service import generate_itinerary_with_llm, regenerate_single_day

@pytest.mark.asyncio
async def test_ai_fallback_generation():
    trip = {
        "destination": "Rome",
        "start_date": "2026-08-10",
        "end_date": "2026-08-12",
        "num_travelers": 2,
        "total_budget": 2000.0,
        "currency": "EUR",
        "travel_style": "standard",
        "travel_pace": "balanced",
        "interests": ["history", "food"]
    }
    result = await generate_itinerary_with_llm(trip)
    assert "days" in result
    assert len(result["days"]) == 3
    for day in result["days"]:
        assert "day_number" in day
        assert "activities" in day
        assert len(day["activities"]) >= 2
        for act in day["activities"]:
            assert "title" in act
            assert "time_slot" in act
            assert "estimated_cost" in act

@pytest.mark.asyncio
async def test_ai_regenerate_single_day():
    trip = {
        "destination": "Bali",
        "travel_style": "luxury",
        "currency": "USD"
    }
    acts = await regenerate_single_day(trip, day_number=2, prompt_notes="More beach and water sports")
    assert len(acts) == 3
    for act in acts:
        assert act["day_number"] == 2
        assert "estimated_cost" in act
