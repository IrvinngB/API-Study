from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from database import get_supabase_anon, get_user_supabase
import jwt
from typing import Dict, Any

security = HTTPBearer()

async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
    """Verify JWT token and return user info"""
    try:
        token = credentials.credentials
        print(f"🔑 Received token: {token[:20]}...")
        
        # Create a Supabase client with anon key
        supabase = get_supabase_anon()
        
        # Try to get user with the provided JWT token
        try:
            # This should work with a valid JWT token
            user_response = supabase.auth.get_user(token)
            print(f"📋 Supabase response: {user_response}")
            
            if not user_response.user:
                print("❌ No user found in token response")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid authentication token"
                )
            
            print(f"✅ User authenticated: {user_response.user.email}")
            return {
                "user_id": user_response.user.id,
                "email": user_response.user.email,
                "token": token
            }
            
        except Exception as auth_error:
            print(f"❌ Supabase auth error: {auth_error}")
            print(f"❌ Error type: {type(auth_error)}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not authenticated"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ General authentication error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )

async def get_current_user(auth_data: Dict[str, Any] = Depends(verify_token)) -> Dict[str, Any]:
    """Get current authenticated user"""
    return auth_data
