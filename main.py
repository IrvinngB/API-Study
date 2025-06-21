from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import os
from dotenv import load_dotenv

from routers import auth, classes, tasks, calendar, habits, sync, analytics
from database import init_db
from auth_middleware import verify_token

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
    await init_db()

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
app.include_router(habits.router, prefix="/habits", tags=["Habits"])
app.include_router(sync.router, prefix="/sync", tags=["Synchronization"])
app.include_router(analytics.router, prefix="/analytics", tags=["Analytics"])

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
