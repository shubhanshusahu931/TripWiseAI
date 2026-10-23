import math
from typing import List, Dict, Any
from app.schemas.itinerary import CostBreakdown

DAILY_RATES = {
    "budget": {
        "accommodation": 45.0,  # per room (up to 2 people)
        "food": 25.0,           # per person/day
        "transport": 10.0,       # per person/day
    },
    "standard": {
        "accommodation": 120.0, # per room (up to 2 people)
        "food": 65.0,           # per person/day
        "transport": 25.0,       # per person/day
    },
    "luxury": {
        "accommodation": 320.0, # per room (up to 2 people)
        "food": 160.0,          # per person/day
        "transport": 70.0,       # per person/day
    }
}

def calculate_budget(
    activities: List[Dict[str, Any]],
    num_travelers: int,
    total_budget: float,
    num_days: int,
    travel_style: str = "standard"
) -> Dict[str, Any]:
    travel_style = travel_style.lower() if travel_style else "standard"
    if travel_style not in DAILY_RATES:
        travel_style = "standard"

    rates = DAILY_RATES[travel_style]
    travelers = max(1, num_travelers)
    days = max(1, num_days)

    # 1. Activities cost sum
    activities_cost = sum(float(act.get("estimated_cost", 0.0) or 0.0) for act in activities)

    # 2. Accommodation: rooms needed = ceil(travelers / 2)
    rooms_needed = math.ceil(travelers / 2.0)
    # Nights = max(1, days - 1)
    nights = max(1, days - 1)
    accommodation_cost = rates["accommodation"] * rooms_needed * nights

    # 3. Food cost: per person per day
    food_cost = rates["food"] * travelers * days

    # 4. Local Transportation: per person per day
    transportation_cost = rates["transport"] * travelers * days

    # 5. Miscellaneous: 5% of subtotal
    subtotal = activities_cost + accommodation_cost + food_cost + transportation_cost
    miscellaneous_cost = round(subtotal * 0.05, 2)

    total_estimated = round(activities_cost + accommodation_cost + food_cost + transportation_cost + miscellaneous_cost, 2)
    cost_per_person = round(total_estimated / travelers, 2)
    remaining_budget = round(total_budget - total_estimated, 2)

    return {
        "estimated_total_cost": total_estimated,
        "cost_per_person": cost_per_person,
        "remaining_budget": remaining_budget,
        "cost_breakdown": {
            "activities": round(activities_cost, 2),
            "accommodation": round(accommodation_cost, 2),
            "food": round(food_cost, 2),
            "transportation": round(transportation_cost, 2),
            "miscellaneous": miscellaneous_cost
        }
    }
