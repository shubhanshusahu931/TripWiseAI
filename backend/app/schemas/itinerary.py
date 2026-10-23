from typing import List, Optional, Dict, Any
from datetime import date, datetime
from pydantic import BaseModel, Field, ConfigDict
from app.schemas.trip import TripResponse
from app.schemas.activity import ActivityResponse

class CostBreakdown(BaseModel):
    activities: float = 0.0
    accommodation: float = 0.0
    food: float = 0.0
    transportation: float = 0.0
    miscellaneous: float = 0.0

class DayPlan(BaseModel):
    day_number: int
    date: Optional[date] = None
    theme: Optional[str] = None
    activities: List[ActivityResponse] = Field(default_factory=list)

class ItineraryResponse(BaseModel):
    id: str
    trip_id: str
    user_id: str
    summary: Optional[str] = None
    estimated_total_cost: float = 0.0
    cost_per_person: float = 0.0
    remaining_budget: float = 0.0
    cost_breakdown: CostBreakdown = Field(default_factory=CostBreakdown)
    days: List[DayPlan] = Field(default_factory=list)
    is_sample_data: bool = False
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class TripDetailResponse(TripResponse):
    itinerary: Optional[ItineraryResponse] = None

class RegenerateDayRequest(BaseModel):
    day_number: int = Field(..., ge=1)
    prompt_notes: Optional[str] = Field(None, description="Custom prompt notes for day regeneration")

class GenerateTripRequest(BaseModel):
    prompt_notes: Optional[str] = Field(None, description="Custom refinement notes for AI generator")
