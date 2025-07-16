from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
import os
from dotenv import load_dotenv

from routers import auth, classes, tasks, calendar, notes, sync, grades, notifications, user_devices, user_profiles
from database import init_db

load_dotenv()

app = FastAPI(
    title="StudyVault API",
    description="API backend for StudyVault student productivity app",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Para desarrollo local
        "http://127.0.0.1:3000",
        "http://localhost:8081",  # Para Expo
        "http://127.0.0.1:8081",
        "*"  # Para Railway - en producción, especifica tu dominio exacto
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

@app.on_event("startup")
async def startup_event():
    """Initialize database connection on startup"""
    try:
        await init_db()
        print("✅ Database initialized successfully")
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        raise e

@app.get("/")
async def root():
    return {"message": "StudyVault API is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "StudyVault API"}

# Include routers
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(classes.router, prefix="/classes", tags=["Classes"])
app.include_router(tasks.router, prefix="/tasks", tags=["Tasks"])
app.include_router(calendar.router, prefix="/calendar", tags=["Calendar"])
app.include_router(notes.router, prefix="/notes", tags=["Notes"])
app.include_router(sync.router, prefix="/sync", tags=["Sync"])
app.include_router(grades.router, prefix="/grades", tags=["Grades"])
app.include_router(notifications.router, prefix="/notifications", tags=["Notifications"])
app.include_router(user_devices.router, prefix="/devices", tags=["User Devices"])
app.include_router(user_profiles.router, prefix="/profile", tags=["User Profile"])


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=False)
