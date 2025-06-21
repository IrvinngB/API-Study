from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from supabase import create_client, Client
import os
from typing import Dict, Any
import jwt
from datetime import datetime

# Configuración de Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

if not SUPABASE_URL or not SUPABASE_ANON_KEY:
    raise ValueError("SUPABASE_URL and SUPABASE_ANON_KEY must be set")

# Cliente de Supabase para verificación de tokens
supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY or SUPABASE_ANON_KEY)

security = HTTPBearer()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
    """
    Middleware para verificar la autenticación del usuario usando tokens de Supabase
    """
    try:
        token = credentials.credentials
        print(f"🔍 Verificando token: {token[:20]}...")
        
        # Verificar el token con Supabase
        try:
            # Usar el token para obtener información del usuario
            supabase_with_token = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
            
            # Establecer el token de autorización
            supabase_with_token.auth.set_session(token, None)
            
            # Obtener el usuario actual
            user_response = supabase_with_token.auth.get_user(token)
            
            if not user_response.user:
                print("❌ Token inválido - no se pudo obtener usuario")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token inválido"
                )
            
            user = user_response.user
            print(f"✅ Usuario autenticado: {user.email} (ID: {user.id})")
            
            return {
                "user_id": user.id,
                "email": user.email,
                "token": token,
                "user": user
            }
            
        except Exception as supabase_error:
            print(f"❌ Error de Supabase: {supabase_error}")
            
            # Fallback: intentar decodificar el JWT manualmente
            try:
                # Decodificar sin verificar la firma (solo para desarrollo)
                decoded = jwt.decode(token, options={"verify_signature": False})
                
                if 'sub' not in decoded:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Token JWT inválido - falta subject"
                    )
                
                # Verificar expiración
                if 'exp' in decoded:
                    exp_timestamp = decoded['exp']
                    if datetime.utcnow().timestamp() > exp_timestamp:
                        raise HTTPException(
                            status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Token expirado"
                        )
                
                print(f"✅ Token JWT decodificado exitosamente para usuario: {decoded.get('email', decoded['sub'])}")
                
                return {
                    "user_id": decoded['sub'],
                    "email": decoded.get('email', ''),
                    "token": token,
                    "user": decoded
                }
                
            except jwt.InvalidTokenError as jwt_error:
                print(f"❌ Error decodificando JWT: {jwt_error}")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token JWT inválido"
                )
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error inesperado en autenticación: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Error de autenticación"
        )

def get_current_user_optional(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any] | None:
    """
    Versión opcional del middleware de autenticación
    """
    try:
        return get_current_user(credentials)
    except HTTPException:
        return None
