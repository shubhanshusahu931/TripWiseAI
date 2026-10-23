from app.routes.trips import router as trips_router
from app.routes.activities import router as activities_router
from app.routes.profile import router as profile_router

__all__ = ["trips_router", "activities_router", "profile_router"]
