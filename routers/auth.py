from fastapi import APIRouter, HTTPException, status, Depends
from database import get_supabase_anon, get_user_supabase, get_supabase_service
from models import UserProfile, UserProfileCreate, UserProfileUpdate
from auth_middleware import get_current_user
from typing import Dict, Any, Optional
from pydantic import BaseModel, EmailStr
import requests
import os
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

# Configuración de Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL", "https://llnmvrxgiykxeiinycbt.supabase.co")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imxsbm12cnhnaXlreGVpaW55Y2J0Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTAzMDA0NjIsImV4cCI6MjA2NTg3NjQ2Mn0.TCuyoJagBgoOhVnsCQabuXmeFy1o0QeEMR6e1gL40MI")

class SignUpRequest(BaseModel):
    email: EmailStr
    password: str
    name: Optional[str] = None

class SignInRequest(BaseModel):
    email: EmailStr
    password: str

class ResetPasswordRequest(BaseModel):
    email: EmailStr

class UpdatePasswordRequest(BaseModel):
    password: str

class AuthResponse(BaseModel):
    message: str
    user: Optional[Dict[str, Any]] = None
    session: Optional[Dict[str, Any]] = None
    email_confirmation_required: Optional[bool] = None

def validate_password(password: str) -> bool:
    """Validate password strength"""
    if len(password) < 8:
        return False
    
    has_upper = any(c.isupper() for c in password)
    has_lower = any(c.islower() for c in password)
    has_digit = any(c.isdigit() for c in password)
    
    return has_upper and has_lower and has_digit

@router.post("/signup", response_model=AuthResponse)
async def signup(request: SignUpRequest):
    """
    Registrar nuevo usuario con confirmación de email
    El usuario recibirá un email con enlace de confirmación
    """
    try:
        # Validar fortaleza de contraseña
        if not validate_password(request.password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La contraseña debe tener al menos 8 caracteres, incluir mayúsculas, minúsculas y números"
            )

        supabase = get_supabase_anon()
        
        # Configurar metadata del usuario
        user_metadata = {}
        if request.name:
            user_metadata["full_name"] = request.name

        response = supabase.auth.sign_up({
            "email": request.email,
            "password": request.password,
            "options": {
                "emailRedirectTo": "studyvault://confirm-email",
                "data": user_metadata
            }
        })
        
        if response.user:
            logger.info(f"✅ User signed up: {response.user.id} - {request.email}")
            
            # Crear perfil de usuario usando service client
            try:
                service_supabase = get_supabase_service()
                
                profile_data = {
                    "id": response.user.id,
                    "email": request.email,
                    "full_name": request.name or "",
                    "timezone": "America/Panama",
                    "avatar_url": None,
                    "bio": None,
                    "preferences": {},
                    "created_at": "now()",
                    "updated_at": "now()"
                }
                
                profile_response = service_supabase.table("user_profiles").insert(profile_data).execute()
                logger.info(f"✅ Profile created: {profile_response.data}")
                
            except Exception as profile_error:
                logger.error(f"❌ Failed to create profile: {profile_error}")
                # No fallar el registro si la creación del perfil falla
            
            return AuthResponse(
                message="Usuario registrado exitosamente. Revisa tu email para confirmar tu cuenta antes de poder iniciar sesión.",
                user=response.user.model_dump() if hasattr(response.user, 'model_dump') else dict(response.user),
                session=response.session.model_dump() if response.session and hasattr(response.session, 'model_dump') else dict(response.session) if response.session else None,
                email_confirmation_required=True
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No se pudo crear el usuario. Verifica que el email no esté ya registrado."
            )
            
    except Exception as e:
        logger.error(f"❌ Signup error: {e}")
        error_message = str(e)
        
        # Personalizar mensajes de error comunes
        if "already_registered" in error_message.lower() or "already exists" in error_message.lower():
            error_message = "Este email ya está registrado. Usa otro email o inicia sesión."
        elif "invalid_email" in error_message.lower():
            error_message = "El formato del email no es válido."
        elif "weak_password" in error_message.lower():
            error_message = "La contraseña es muy débil. Debe tener al menos 8 caracteres."
            
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_message
        )

@router.post("/signin", response_model=AuthResponse)
async def signin(request: SignInRequest):
    """Iniciar sesión"""
    try:
        supabase = get_supabase_anon()
        response = supabase.auth.sign_in_with_password({
            "email": request.email,
            "password": request.password
        })
        
        if response.user and response.session:
            # Verificar si el email está confirmado
            if not response.user.email_confirmed_at:
                return AuthResponse(
                    message="Debes confirmar tu email antes de poder iniciar sesión. Revisa tu bandeja de entrada.",
                    user=None,
                    session=None,
                    email_confirmation_required=True
                )
            
            logger.info(f"✅ User signed in: {response.user.id} - {request.email}")
            
            return AuthResponse(
                message="Sesión iniciada exitosamente",
                user=response.user.model_dump() if hasattr(response.user, 'model_dump') else dict(response.user),
                session=response.session.model_dump() if hasattr(response.session, 'model_dump') else dict(response.session)
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credenciales inválidas"
            )
            
    except Exception as e:
        logger.error(f"❌ Signin error: {e}")
        error_message = str(e)
        
        # Personalizar mensajes de error
        if "invalid_credentials" in error_message.lower() or "invalid login" in error_message.lower():
            error_message = "Email o contraseña incorrectos"
        elif "email_not_confirmed" in error_message.lower():
            error_message = "Debes confirmar tu email antes de poder iniciar sesión"
        
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=error_message
        )

@router.post("/signout")
async def signout(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Cerrar sesión"""
    try:
        supabase = get_user_supabase(current_user["token"])
        supabase.auth.sign_out()
        
        logger.info(f"✅ User signed out: {current_user['user_id']}")
        return {"message": "Sesión cerrada exitosamente"}
        
    except Exception as e:
        logger.error(f"❌ Signout error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error al cerrar sesión"
        )

@router.post("/reset-password")
async def reset_password(request: ResetPasswordRequest):
    """
    Enviar email de restablecimiento de contraseña
    Siempre retorna éxito por seguridad (no revelar si email existe)
    """
    try:
        logger.info(f"🔑 Password reset requested for: {request.email}")
        
        # Método 1: Usar Supabase client (recomendado)
        try:
            supabase = get_supabase_anon()
            response = supabase.auth.reset_password_email(
                request.email,
                options={
                    "redirectTo": "studyvault://reset-password"
                }
            )
            logger.info(f"✅ Password reset email sent via client")
            
        except Exception as client_error:
            logger.warning(f"⚠️ Client method failed, trying REST API: {client_error}")
            
            # Método 2: Fallback usando REST API directa
            url = f"{SUPABASE_URL}/auth/v1/recover"
            headers = {
                "apikey": SUPABASE_ANON_KEY,
                "Authorization": f"Bearer {SUPABASE_ANON_KEY}",
                "Content-Type": "application/json",
            }
            
            payload = {
                "email": request.email,
                "options": {
                    "redirectTo": "studyvault://reset-password"
                }
            }
            
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            
            if response.status_code in [200, 201]:
                logger.info(f"✅ Password reset email sent via REST API")
            else:
                logger.error(f"❌ REST API error: {response.status_code} - {response.text}")
        
        # Siempre retornar éxito por seguridad
        return {
            "message": "Si el email está registrado en nuestro sistema, recibirás un enlace para restablecer tu contraseña en los próximos minutos.",
            "success": True
        }
        
    except Exception as e:
        logger.error(f"❌ Reset password error: {e}")
        # Por seguridad, no revelar detalles del error
        return {
            "message": "Si el email está registrado en nuestro sistema, recibirás un enlace para restablecer tu contraseña en los próximos minutos.",
            "success": True
        }

@router.post("/update-password")
async def update_password(
    request: UpdatePasswordRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Actualizar contraseña del usuario
    Requiere que el usuario esté autenticado (tiene token válido de reset)
    """
    try:
        # Validar fortaleza de contraseña
        if not validate_password(request.password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La contraseña debe tener al menos 8 caracteres, incluir mayúsculas, minúsculas y números"
            )

        supabase = get_user_supabase(current_user["token"])
        response = supabase.auth.update_user({
            "password": request.password
        })
        
        if response.user:
            logger.info(f"✅ Password updated for user: {response.user.id}")
            return {
                "message": "Contraseña actualizada exitosamente",
                "success": True
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No se pudo actualizar la contraseña"
            )
            
    except Exception as e:
        logger.error(f"❌ Update password error: {e}")
        error_message = str(e)
        
        if "weak_password" in error_message.lower():
            error_message = "La contraseña es muy débil"
        elif "same_password" in error_message.lower():
            error_message = "La nueva contraseña debe ser diferente a la actual"
        elif "session_not_found" in error_message.lower():
            error_message = "Sesión expirada. Solicita un nuevo enlace de restablecimiento"
            
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_message
        )

@router.post("/resend-confirmation")
async def resend_confirmation_email(request: ResetPasswordRequest):
    """
    Reenviar email de confirmación
    Para usuarios que no han confirmado su email
    """
    try:
        logger.info(f"📧 Resend confirmation requested for: {request.email}")
        
        supabase = get_supabase_anon()
        response = supabase.auth.resend(
            request.email,
            type='signup',
            options={
                "emailRedirectTo": "studyvault://confirm-email"
            }
        )
        
        logger.info(f"✅ Confirmation email resent")
        
        return {
            "message": "Si tu email está registrado y pendiente de confirmación, recibirás un nuevo enlace de confirmación.",
            "success": True
        }
        
    except Exception as e:
        logger.error(f"❌ Resend confirmation error: {e}")
        # Por seguridad, no revelar si el email existe
        return {
            "message": "Si tu email está registrado y pendiente de confirmación, recibirás un nuevo enlace de confirmación.",
            "success": True
        }

@router.post("/confirm-email")
async def confirm_email():
    """
    Endpoint para manejar confirmación de email
    En realidad, Supabase maneja esto automáticamente con el deep link
    Este endpoint es principalmente informativo
    """
    return {
        "message": "Email confirmado exitosamente. Ya puedes iniciar sesión.",
        "success": True
    }

@router.get("/profile", response_model=UserProfile)
async def get_profile(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Obtener perfil del usuario"""
    try:
        supabase = get_user_supabase(current_user["token"])
        response = supabase.table("user_profiles").select("*").eq("id", current_user["user_id"]).execute()

        if response.data:
            logger.info(f"📋 Retrieved profile for user: {current_user['user_id']}")
            return response.data[0]
        else:
            # Verificar si existe perfil con el mismo email
            email_check_response = supabase.table("user_profiles").select("*").eq("email", current_user["email"]).execute()

            if email_check_response.data:
                logger.info(f"⚠️ Found profile by email: {current_user['email']}")
                return email_check_response.data[0]

            # Crear perfil por defecto si no existe
            default_profile = {
                "id": current_user["user_id"],
                "email": current_user["email"],
                "full_name": current_user.get("user_metadata", {}).get("full_name", ""),
                "timezone": "America/Panama",
                "avatar_url": None,
                "bio": None,
                "preferences": {},
                "created_at": "now()",
                "updated_at": "now()"
            }

            create_response = supabase.table("user_profiles").insert(default_profile).execute()

            if create_response.data:
                logger.info(f"✅ Default profile created for: {current_user['user_id']}")
                return create_response.data[0]
            else:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="No se pudo crear el perfil de usuario"
                )

    except Exception as e:
        logger.error(f"❌ Error with profile: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.put("/profile", response_model=UserProfile)
async def update_profile(
    profile_update: UserProfileUpdate,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Actualizar perfil del usuario"""
    try:
        supabase = get_user_supabase(current_user["token"])
        
        # Serializar campos correctamente
        update_data = profile_update.model_dump(exclude_unset=True, mode='json')
        update_data["updated_at"] = "now()"
        
        response = supabase.table("user_profiles").update(update_data).eq("id", current_user["user_id"]).execute()
        
        if response.data:
            logger.info(f"✅ Profile updated for: {current_user['user_id']}")
            return response.data[0]
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Perfil no encontrado"
            )
            
    except Exception as e:
        logger.error(f"❌ Error updating profile: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )