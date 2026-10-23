from typing import Optional
from datetime import date, datetime
from pydantic import BaseModel, Field, ConfigDict

class ActivityBase(BaseModel):
    day_number: int = Field(..., ge=1, description="Day sequence number (1, 2, 3...)")
    date: Optional[date] = None
    title: str = Field(..., min_length=1, description="Name of activity or venue")
    description: Optional[str] = None
    time_slot: str = Field("Morning", description="Morning, Afternoon, Evening, or Night")
    start_time: Optional[str] = Field("09:00", description="Suggested start time")
    end_time: Optional[str] = Field("11:00", description="Suggested end time")
    location: Optional[str] = None
    duration_minutes: int = Field(90, ge=10, le=720, description="Estimated duration in minutes")
    estimated_cost: float = Field(0.0, ge=0.0, description="Estimated cost in currency")
    currency: str = Field("USD", min_length=3, max_length=10)
    transportation_suggestion: Optional[str] = None
    practical_tips: Optional[str] = None
    is_custom: bool = False
    order_index: int = 0

class ActivityCreate(ActivityBase):
    pass

class ActivityUpdate(BaseModel):
    day_number: Optional[int] = Field(None, ge=1)
    date: Optional[date] = None
    title: Optional[str] = None
    description: Optional[str] = None
    time_slot: Optional[str] = None
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    location: Optional[str] = None
    duration_minutes: Optional[int] = Field(None, ge=10, le=720)
    estimated_cost: Optional[float] = Field(None, ge=0.0)
    currency: Optional[str] = None
    transportation_suggestion: Optional[str] = None
    practical_tips: Optional[str] = None
    is_custom: Optional[bool] = None
    order_index: Optional[int] = None

class ActivityResponse(ActivityBase):
    id: str
    itinerary_id: str
    trip_id: str
    user_id: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
