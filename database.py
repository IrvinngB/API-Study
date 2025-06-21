import os
from supabase import create_client, Client
from fastapi import HTTPException
from typing import Optional
from dotenv import load_dotenv
# Cargar variables de entorno al inicio del módulo
load_dotenv()

# Supabase configuration
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")

# Global Supabase clients
supabase_service: Optional[Client] = None
supabase_anon: Optional[Client] = None

async def init_db():
    """Initialize Supabase clients"""
    global supabase_service, supabase_anon
    
    if not SUPABASE_URL or not SUPABASE_SERVICE_KEY:
        raise ValueError("Missing Supabase configuration")
    
    # Service role client for admin operations
    supabase_service = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)
    
    # Anonymous client for user operations
    supabase_anon = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)

def get_supabase_service() -> Client:
    """Get Supabase service role client"""
    if not supabase_service:
        raise HTTPException(status_code=500, detail="Database not initialized")
    return supabase_service

def get_supabase_anon() -> Client:
    """Get Supabase anonymous client"""
    if not supabase_anon:
        raise HTTPException(status_code=500, detail="Database not initialized")
    return supabase_anon

def get_user_supabase(access_token: str) -> Client:
    """Get Supabase client with user token"""
    if not SUPABASE_URL or not SUPABASE_ANON_KEY:
        raise HTTPException(status_code=500, detail="Database not configured")
    
    client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
    # Set the access token directly in the client
    client.auth._session = type('Session', (), {
        'access_token': access_token,
        'refresh_token': None,
        'expires_at': None,
        'user': None
    })()
    return client
