from fastapi import APIRouter, Depends, HTTPException, status
from app.core.auth import get_current_user, CurrentUser
from app.schemas.activity import ActivityCreate, ActivityUpdate, ActivityResponse
from app.services import (
    get_trip,
    get_itinerary,
    create_activity,
    update_activity,
    delete_activity,
    get_activities
)

router = APIRouter(prefix="/api/v1/trips/{trip_id}/activities", tags=["Activities"])

@router.post("", response_model=ActivityResponse, status_code=status.HTTP_201_CREATED)
async def add_activity(
    trip_id: str,
    activity_in: ActivityCreate,
    current_user: CurrentUser = Depends(get_current_user)
):
    trip = get_trip(trip_id, current_user.id)
    if not trip:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Trip not found.")

    itinerary = get_itinerary(trip_id, current_user.id)
    if not itinerary:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Itinerary does not exist for this trip.")

    act_dict = activity_in.model_dump()
    act_dict["is_custom"] = True
    created = create_activity(itinerary["id"], trip_id, current_user.id, act_dict)
    return ActivityResponse(**created)

@router.put("/{activity_id}", response_model=ActivityResponse)
async def modify_activity(
    trip_id: str,
    activity_id: str,
    activity_in: ActivityUpdate,
    current_user: CurrentUser = Depends(get_current_user)
):
    trip = get_trip(trip_id, current_user.id)
    if not trip:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Trip not found.")

    updated = update_activity(activity_id, current_user.id, activity_in.model_dump(exclude_unset=True))
    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Activity not found.")

    return ActivityResponse(**updated)

@router.delete("/{activity_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_activity(
    trip_id: str,
    activity_id: str,
    current_user: CurrentUser = Depends(get_current_user)
):
    trip = get_trip(trip_id, current_user.id)
    if not trip:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Trip not found.")

    deleted_trip_id = delete_activity(activity_id, current_user.id)
    if not deleted_trip_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Activity not found.")

    return None
