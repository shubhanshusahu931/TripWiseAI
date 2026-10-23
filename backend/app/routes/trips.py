from datetime import datetime, date
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from app.core.auth import get_current_user, CurrentUser
from app.schemas.trip import TripCreate, TripUpdate, TripResponse
from app.schemas.itinerary import (
    TripDetailResponse,
    ItineraryResponse,
    DayPlan,
    CostBreakdown,
    GenerateTripRequest,
    RegenerateDayRequest
)
from app.schemas.activity import ActivityResponse
from app.services import (
    create_trip,
    get_trip,
    list_trips,
    update_trip,
    delete_trip,
    duplicate_trip,
    get_itinerary,
    save_itinerary,
    get_activities,
    create_activity,
    replace_day_activities,
    calculate_budget,
    generate_itinerary_with_llm,
    regenerate_single_day
)

router = APIRouter(prefix="/api/v1/trips", tags=["Trips"])

def _build_itinerary_response(trip: dict, itinerary: dict) -> ItineraryResponse:
    activities_raw = get_activities(itinerary["id"])
    activities_by_day = {}
    for act in activities_raw:
        d = act["day_number"]
        if d not in activities_by_day:
            activities_by_day[d] = []
        activities_by_day[d].append(ActivityResponse(**act))

    # Calculate days count
    try:
        d1 = datetime.strptime(str(trip["start_date"]), "%Y-%m-%d").date()
        d2 = datetime.strptime(str(trip["end_date"]), "%Y-%m-%d").date()
        num_days = max(1, (d2 - d1).days + 1)
    except Exception:
        num_days = max(activities_by_day.keys()) if activities_by_day else 1

    days_list = []
    for day_num in range(1, num_days + 1):
        days_list.append(DayPlan(
            day_number=day_num,
            theme=f"Day {day_num} in {trip['destination']}",
            activities=activities_by_day.get(day_num, [])
        ))

    # Recalculate dynamic budget
    budget_stats = calculate_budget(
        activities=activities_raw,
        num_travelers=trip.get("num_travelers", 1),
        total_budget=float(trip.get("total_budget", 0.0)),
        num_days=num_days,
        travel_style=trip.get("travel_style", "standard")
    )

    cost_breakdown = CostBreakdown(**budget_stats["cost_breakdown"])

    return ItineraryResponse(
        id=itinerary["id"],
        trip_id=trip["id"],
        user_id=trip["user_id"],
        summary=itinerary.get("summary") or f"Your personalized {num_days}-day itinerary for {trip['destination']}.",
        estimated_total_cost=budget_stats["estimated_total_cost"],
        cost_per_person=budget_stats["cost_per_person"],
        remaining_budget=budget_stats["remaining_budget"],
        cost_breakdown=cost_breakdown,
        days=days_list,
        is_sample_data=bool(itinerary.get("is_sample_data", False)),
        created_at=datetime.fromisoformat(itinerary["created_at"]) if isinstance(itinerary["created_at"], str) else itinerary["created_at"],
        updated_at=datetime.fromisoformat(itinerary["updated_at"]) if isinstance(itinerary["updated_at"], str) else itinerary["updated_at"]
    )

@router.get("", response_model=List[TripResponse])
async def get_all_trips(
    search: Optional[str] = Query(None, description="Search by title or destination"),
    status_filter: Optional[str] = Query(None, alias="status", description="Filter by status"),
    sort_by: Optional[str] = Query(None, description="Sort order: newest, budget_high, budget_low, date_soonest"),
    current_user: CurrentUser = Depends(get_current_user)
):
    trips = list_trips(current_user.id, search=search, status=status_filter, sort_by=sort_by)
    return [TripResponse(**t) for t in trips]

@router.post("", response_model=TripDetailResponse, status_code=status.HTTP_201_CREATED)
async def create_new_trip(
    trip_in: TripCreate,
    current_user: CurrentUser = Depends(get_current_user)
):
    if trip_in.end_date < trip_in.start_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="End date cannot be earlier than start date."
        )

    trip_dict = trip_in.model_dump()
    created_trip = create_trip(current_user.id, trip_dict)

    # Immediately generate initial itinerary
    ai_result = await generate_itinerary_with_llm(created_trip)
    
    # Save Itinerary
    itinerary = save_itinerary(
        trip_id=created_trip["id"],
        user_id=current_user.id,
        summary=ai_result.get("summary", ""),
        raw_ai_response=ai_result,
        cost_breakdown={},
        is_sample_data=ai_result.get("is_sample_data", True)
    )

    # Save generated activities
    for day in ai_result.get("days", []):
        day_num = day.get("day_number", 1)
        for act in day.get("activities", []):
            act["day_number"] = day_num
            create_activity(itinerary["id"], created_trip["id"], current_user.id, act)

    itin_resp = _build_itinerary_response(created_trip, itinerary)
    return TripDetailResponse(**created_trip, itinerary=itin_resp)

@router.get("/{trip_id}", response_model=TripDetailResponse)
async def get_trip_details(
    trip_id: str,
    current_user: CurrentUser = Depends(get_current_user)
):
    trip = get_trip(trip_id, current_user.id)
    if not trip:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Trip not found.")

    itinerary = get_itinerary(trip_id, current_user.id)
    itin_resp = _build_itinerary_response(trip, itinerary) if itinerary else None
    return TripDetailResponse(**trip, itinerary=itin_resp)

@router.put("/{trip_id}", response_model=TripResponse)
async def update_trip_details(
    trip_id: str,
    trip_in: TripUpdate,
    current_user: CurrentUser = Depends(get_current_user)
):
    existing = get_trip(trip_id, current_user.id)
    if not existing:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Trip not found.")

    updated = update_trip(trip_id, current_user.id, trip_in.model_dump(exclude_unset=True))
    return TripResponse(**updated)

@router.delete("/{trip_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_trip(
    trip_id: str,
    current_user: CurrentUser = Depends(get_current_user)
):
    success = delete_trip(trip_id, current_user.id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Trip not found.")
    return None

@router.post("/{trip_id}/duplicate", response_model=TripResponse, status_code=status.HTTP_201_CREATED)
async def duplicate_existing_trip(
    trip_id: str,
    current_user: CurrentUser = Depends(get_current_user)
):
    new_trip = duplicate_trip(trip_id, current_user.id)
    if not new_trip:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Trip not found.")
    return TripResponse(**new_trip)

@router.post("/{trip_id}/generate", response_model=ItineraryResponse)
async def generate_trip_itinerary(
    trip_id: str,
    gen_req: Optional[GenerateTripRequest] = None,
    current_user: CurrentUser = Depends(get_current_user)
):
    trip = get_trip(trip_id, current_user.id)
    if not trip:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Trip not found.")

    prompt_notes = gen_req.prompt_notes if gen_req else None
    ai_result = await generate_itinerary_with_llm(trip, prompt_notes=prompt_notes)

    # Save Itinerary
    itinerary = save_itinerary(
        trip_id=trip["id"],
        user_id=current_user.id,
        summary=ai_result.get("summary", ""),
        raw_ai_response=ai_result,
        cost_breakdown={},
        is_sample_data=ai_result.get("is_sample_data", False)
    )

    # Replace activities
    # Clean previous activities for this trip
    existing_activities = get_activities(itinerary["id"])
    for act in existing_activities:
        from app.services import delete_activity
        delete_activity(act["id"], current_user.id)

    # Insert new activities
    for day in ai_result.get("days", []):
        day_num = day.get("day_number", 1)
        for act in day.get("activities", []):
            act["day_number"] = day_num
            create_activity(itinerary["id"], trip["id"], current_user.id, act)

    return _build_itinerary_response(trip, itinerary)

@router.post("/{trip_id}/regenerate-day", response_model=ItineraryResponse)
async def regenerate_trip_day(
    trip_id: str,
    regen_req: RegenerateDayRequest,
    current_user: CurrentUser = Depends(get_current_user)
):
    trip = get_trip(trip_id, current_user.id)
    if not trip:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Trip not found.")

    itinerary = get_itinerary(trip_id, current_user.id)
    if not itinerary:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Itinerary has not been generated yet.")

    new_acts = await regenerate_single_day(trip, regen_req.day_number, regen_req.prompt_notes)
    replace_day_activities(itinerary["id"], trip["id"], current_user.id, regen_req.day_number, new_acts)

    return _build_itinerary_response(trip, itinerary)
