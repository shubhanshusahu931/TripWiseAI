import os
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from app.core.config import settings
from app.routes import trips_router, activities_router, profile_router

app = FastAPI(
    title="TripWise AI Backend API",
    description="Personalized Travel Itinerary Planner powered by AI, Supabase, and FastAPI",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows browser frontend on any local port (3000, 5500, 8000, 8080)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Exception handlers
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={
            "error": "InternalServerError",
            "message": str(exc),
            "path": request.url.path
        }
    )

# Health Check
@app.get("/health", tags=["Health"])
async def health_check():
    return {
        "status": "healthy",
        "service": "TripWise AI Backend",
        "version": "1.0.0",
        "ai_provider": settings.AI_PROVIDER,
        "environment": settings.ENVIRONMENT
    }

# Include REST Routers
app.include_router(trips_router)
app.include_router(activities_router)
app.include_router(profile_router)

# Mount frontend directory for easy all-in-one local serving if present
frontend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "frontend"))
if os.path.exists(frontend_dir):
    app.mount("/app", StaticFiles(directory=frontend_dir, html=True), name="frontend")
