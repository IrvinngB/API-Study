#auth_middleware.py
from fastapi import HTTPException, status, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from database import get_supabase_service
from typing import Dict, Any, Optional
import os

security = HTTPBearer()

async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
    """Verify JWT token and return user info"""
    try:
        token = credentials.credentials
        print(f"🔑 Received token: {token[:50]}...")
        
        # Use service role client to verify user tokens
        supabase = get_supabase_service()
        
        try:
            # Verificar el token con Supabase usando service role
            user_response = supabase.auth.get_user(token)
            print(f"📋 Supabase user response: {user_response}")
            
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
                "token": token,
                "user": user_response.user
            }
            
        except Exception as auth_error:
            print(f"❌ Supabase auth error: {auth_error}")
            print(f"❌ Error type: {type(auth_error)}")
            
            # Si Supabase falla, intenta verificar el JWT manualmente
            try:
                from jwt import decode, ExpiredSignatureError, InvalidTokenError
                
                # Usar el JWT secret de Supabase
                jwt_secret = os.getenv("SUPABASE_JWT_SECRET")
                if not jwt_secret:
                    print("❌ SUPABASE_JWT_SECRET not found in environment")
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail="Server configuration error"
                    )
                
                # Verificar y decodificar el token
                decoded = decode(
                    token, 
                    jwt_secret, 
                    algorithms=["HS256"],
                    audience="authenticated"
                )
                
                print(f"🔍 Token decoded successfully: {decoded.get('email')}")
                
                return {
                    "user_id": decoded['sub'],
                    "email": decoded['email'],
                    "token": token,
                    "decoded_token": decoded
                }
                
            except ExpiredSignatureError:
                print("❌ Token has expired")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token has expired"
                )
            except InvalidTokenError as jwt_error:
                print(f"❌ Invalid token: {jwt_error}")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token"
                )
            except Exception as jwt_error:
                print(f"❌ JWT decode error: {jwt_error}")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Could not validate token"
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

async def get_optional_current_user(request: Request) -> Optional[Dict[str, Any]]:
    """Get current authenticated user if Authorization header is provided, otherwise return None"""
    auth_header = request.headers.get("Authorization")
    
    if not auth_header or not auth_header.startswith("Bearer "):
        return None
    
    try:
        token = auth_header.split(" ")[1]
        print(f"🔑 Optional auth - Received token: {token[:50]}...")
        
        # Use service role client to verify user tokens
        supabase = get_supabase_service()
        
        try:
            # Verificar el token con Supabase usando service role
            user_response = supabase.auth.get_user(token)
            print(f"📋 Optional auth - Supabase user response: {user_response}")
            
            if not user_response.user:
                print("❌ Optional auth - No user found in token response")
                return None
            
            print(f"✅ Optional auth - User authenticated: {user_response.user.email}")
            return {
                "user_id": user_response.user.id,
                "email": user_response.user.email,
                "token": token,
                "user": user_response.user
            }
            
        except Exception as auth_error:
            print(f"❌ Optional auth - Supabase auth error: {auth_error}")
            return None
        
    except Exception as e:
        print(f"❌ Optional auth - General error: {e}")
        return None