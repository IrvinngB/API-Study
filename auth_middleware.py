from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from database import get_supabase_anon
import jwt
from typing import Dict, Any

security = HTTPBearer()

async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
    """Verify JWT token and return user info"""
    try:
        token = credentials.credentials
        
        # Verify token with Supabase
        supabase = get_supabase_anon()
        response = supabase.auth.get_user(token)
        
        if not response.user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token"
            )
        
        return {
            "user_id": response.user.id,
            "email": response.user.email,
            "token": token
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )

async def get_current_user(auth_data: Dict[str, Any] = Depends(verify_token)) -> Dict[str, Any]:
    """Get current authenticated user"""
    return auth_data
