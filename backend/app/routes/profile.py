from fastapi import APIRouter, Depends, HTTPException, status
from app.core.auth import get_current_user, CurrentUser
from app.schemas.profile import ProfileUpdate, ProfileResponse
from app.services import get_profile, update_profile

router = APIRouter(prefix="/api/v1/profile", tags=["Profile"])

@router.get("", response_model=ProfileResponse)
async def fetch_profile(current_user: CurrentUser = Depends(get_current_user)):
    profile_data = get_profile(current_user.id, current_user.email)
    return ProfileResponse(**profile_data)

@router.put("", response_model=ProfileResponse)
async def save_profile(
    profile_in: ProfileUpdate,
    current_user: CurrentUser = Depends(get_current_user)
):
    updated = update_profile(current_user.id, profile_in.model_dump(exclude_unset=True))
    updated["email"] = current_user.email
    return ProfileResponse(**updated)
