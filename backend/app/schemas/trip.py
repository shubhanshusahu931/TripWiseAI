from typing import List, Optional
from datetime import date, datetime
from pydantic import BaseModel, Field, ConfigDict

class TripBase(BaseModel):
    destination: str = Field(..., min_length=1, description="Primary destination city or country")
    origin: Optional[str] = Field(None, description="Starting departure location")
    start_date: date = Field(..., description="Trip start date (YYYY-MM-DD)")
    end_date: date = Field(..., description="Trip end date (YYYY-MM-DD)")
    num_travelers: int = Field(1, ge=1, le=50, description="Total count of travelers")
    total_budget: float = Field(0.0, ge=0.0, description="Budget cap allocated for the trip")
    currency: str = Field("USD", min_length=3, max_length=10, description="3-letter currency code")
    travel_style: str = Field("standard", description="budget, standard, or luxury")
    interests: List[str] = Field(default_factory=list, description="List of user interests")
    travel_pace: str = Field("balanced", description="relaxed, balanced, or packed")
    accommodation_preference: Optional[str] = Field("hotel", description="hotel, hostel, resort, apartment, etc.")
    dietary_restrictions: List[str] = Field(default_factory=list, description="vegetarian, vegan, halal, etc.")
    transportation_preference: Optional[str] = Field("public_transit", description="public_transit, walking, rental_car, taxi")
    additional_notes: Optional[str] = Field(None, description="Special instructions or constraints")
    cover_image_url: Optional[str] = None

class TripCreate(TripBase):
    title: Optional[str] = Field(None, description="Custom title, or generated from destination")

class TripUpdate(BaseModel):
    title: Optional[str] = None
    destination: Optional[str] = None
    origin: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    num_travelers: Optional[int] = Field(None, ge=1, le=50)
    total_budget: Optional[float] = Field(None, ge=0.0)
    currency: Optional[str] = None
    travel_style: Optional[str] = None
    interests: Optional[List[str]] = None
    travel_pace: Optional[str] = None
    accommodation_preference: Optional[str] = None
    dietary_restrictions: Optional[List[str]] = None
    transportation_preference: Optional[str] = None
    additional_notes: Optional[str] = None
    status: Optional[str] = None
    cover_image_url: Optional[str] = None

class TripResponse(TripBase):
    id: str
    user_id: str
    title: str
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
