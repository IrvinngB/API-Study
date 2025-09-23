# database.py
import os
from supabase import create_client, Client
from fastapi import HTTPException
from typing import Optional
from dotenv import load_dotenv
# Cargar variables de entorno al inicio del módulo
load_dotenv()

# Supabase configuration
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")

# S3 Storage credentials for Supabase Storage
SUPABASE_STORAGE_ACCESS_KEY = os.getenv("SUPABASE_STORAGE_ACCESS_KEY", "d5e36f4426e5bf65f74ebea2544d9cbc")
SUPABASE_STORAGE_SECRET_KEY = os.getenv("SUPABASE_STORAGE_SECRET_KEY", "c0288b41cc802cc4326517e7a336c78d30a286bf8a9dd77c6dfa5cdae1b4bbae")
SUPABASE_STORAGE_REGION = os.getenv("SUPABASE_STORAGE_REGION", "us-east-2")

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
    
    # Set the session properly with access and refresh tokens
    try:
        # Create a mock session object
        session_data = {
            "access_token": access_token,
            "refresh_token": "",  # Empty but required
            "expires_in": 3600,
            "token_type": "bearer"
        }
        client.auth._session = type('Session', (), session_data)()
        
        # Set the access token directly in the client headers
        client.options.headers.update({
            "Authorization": f"Bearer {access_token}"
        })
        
    except Exception as e:
        print(f"❌ Error setting session: {e}")
        
    return client

def get_supabase_with_s3_credentials() -> Client:
    """Get Supabase client configured with S3 credentials for storage operations"""
    if not SUPABASE_URL:
        raise HTTPException(status_code=500, detail="Database not configured")
    
    # Create client with service role key for storage operations
    client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)
    
    # Configure S3 credentials for storage operations
    try:
        # Set S3 credentials in the client options
        client.options.headers.update({
            "X-Access-Key": SUPABASE_STORAGE_ACCESS_KEY,
            "X-Secret-Key": SUPABASE_STORAGE_SECRET_KEY,
            "X-Region": SUPABASE_STORAGE_REGION
        })
        
        print(f"🔑 S3 Credentials configured - Access Key: {SUPABASE_STORAGE_ACCESS_KEY[:8]}...")
        
    except Exception as e:
        print(f"❌ Error setting S3 credentials: {e}")
        
    return client
