from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict

class ProfileBase(BaseModel):
    display_name: Optional[str] = Field("Travel Explorer", description="User's public display name")
    preferred_currency: str = Field("USD", min_length=3, max_length=10)
    preferred_travel_style: str = Field("standard", description="budget, standard, or luxury")
    home_city: Optional[str] = Field(None, description="Departure home base")
    avatar_url: Optional[str] = None

class ProfileUpdate(BaseModel):
    display_name: Optional[str] = None
    preferred_currency: Optional[str] = None
    preferred_travel_style: Optional[str] = None
    home_city: Optional[str] = None
    avatar_url: Optional[str] = None

class ProfileResponse(ProfileBase):
    id: str
    email: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
