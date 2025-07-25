from fastapi import APIRouter, HTTPException, status, Depends
from database import get_supabase_anon, get_user_supabase
from models import UserProfile, UserProfileCreate, UserProfileUpdate
from auth_middleware import get_current_user
from typing import Dict, Any
from pydantic import BaseModel
import requests
import os

router = APIRouter()

# Configuración de Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL", "https://llnmvrxgiykxeiinycbt.supabase.co")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "tu_service_role_key_aqui")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imxsbm12cnhnaXlreGVpaW55Y2J0Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTAzMDA0NjIsImV4cCI6MjA2NTg3NjQ2Mn0.TCuyoJagBgoOhVnsCQabuXmeFy1o0QeEMR6e1gL40MI")

class SignUpRequest(BaseModel):
    email: str
    password: str
    name: str = None

class SignInRequest(BaseModel):
    email: str
    password: str

class ResetPasswordRequest(BaseModel):
    email: str

class UpdatePasswordRequest(BaseModel):
    password: str

@router.post("/signup")
async def signup(request: SignUpRequest):
    """Sign up a new user with email confirmation redirect"""
    try:
        supabase = get_supabase_anon()
        response = supabase.auth.sign_up({
            "email": request.email,
            "password": request.password,
            "options": {
                "emailRedirectTo": "studyvault://confirm-email"
            }
        })
        
        if response.user:
            # Create user profile using service client
            from database import get_supabase_service
            service_supabase = get_supabase_service()
            
            profile_data = {
                "id": response.user.id,
                "email": request.email,
                "full_name": request.name,
                "timezone": "America/Panama"
            }
            
            try:
                profile_response = service_supabase.table("user_profiles").insert(profile_data).execute()
                print(f"✅ Profile created: {profile_response.data}")
            except Exception as profile_error:
                print(f"❌ Failed to create profile: {profile_error}")
                # Don't fail the signup if profile creation fails, but log it
            
            return {
                "message": "Usuario creado exitosamente. Revisa tu email para confirmar tu cuenta.",
                "user": response.user,
                "session": response.session,
                "email_confirmation_required": True
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to create user"
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/signin")
async def signin(request: SignInRequest):
    """Sign in user"""
    try:
        supabase = get_supabase_anon()
        response = supabase.auth.sign_in_with_password({
            "email": request.email,
            "password": request.password
        })
        
        if response.user and response.session:
            return {
                "message": "Signed in successfully",
                "user": response.user,
                "session": response.session
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )

@router.post("/signout")
async def signout(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Sign out user"""
    try:
        supabase = get_user_supabase(current_user["token"])
        supabase.auth.sign_out()
        return {"message": "Signed out successfully"}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/reset-password")
async def reset_password(request: ResetPasswordRequest):
    """Send password reset email using Supabase REST API"""
    try:
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
        
        # Usar requests para hacer la llamada directa a Supabase
        try:
            import requests
            response = requests.post(url, json=payload, headers=headers)
            
            if response.status_code == 200:
                return {
                    "message": "Si el email existe en nuestro sistema, recibirás un enlace para restablecer tu contraseña."
                }
            else:
                # Log del error para debugging
                print(f"Supabase error: {response.status_code} - {response.text}")
                
        except ImportError:
            # Fallback usando supabase client si requests no está disponible
            supabase = get_supabase_anon()
            response = supabase.auth.reset_password_email(request.email, {
                "redirectTo": "studyvault://reset-password"
            })
        
        return {
            "message": "Si el email existe en nuestro sistema, recibirás un enlace para restablecer tu contraseña."
        }
        
    except Exception as e:
        # Por seguridad, no revelamos si el email existe o no
        print(f"Reset password error: {e}")
        return {
            "message": "Si el email existe en nuestro sistema, recibirás un enlace para restablecer tu contraseña."
        }

@router.post("/update-password")
async def update_password(
    request: UpdatePasswordRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Update user password (used after reset)"""
    try:
        supabase = get_user_supabase(current_user["token"])
        response = supabase.auth.update_user({
            "password": request.password
        })
        
        if response.user:
            return {"message": "Contraseña actualizada exitosamente"}
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No se pudo actualizar la contraseña"
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/resend-confirmation")
async def resend_confirmation_email(request: ResetPasswordRequest):
    """Resend email confirmation with proper redirect"""
    try:
        supabase = get_supabase_anon()
        response = supabase.auth.resend(request.email, type='signup', options={
            "emailRedirectTo": "studyvault://confirm-email"
        })
        
        return {
            "message": "Si el email existe y no está confirmado, recibirás un nuevo enlace de confirmación."
        }
        
    except Exception as e:
        # Por seguridad, no revelamos si el email existe o no
        print(f"Resend confirmation error: {e}")
        return {
            "message": "Si el email existe y no está confirmado, recibirás un nuevo enlace de confirmación."
        }

@router.get("/profile", response_model=UserProfile)
async def get_profile(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Get user profile"""
    try:
        supabase = get_user_supabase(current_user["token"])
        response = supabase.table("user_profiles").select("*").eq("id", current_user["user_id"]).execute()
        
        if response.data:
            return response.data[0]
        else:
            # Profile doesn't exist, create it
            print(f"📝 Creating missing profile for user: {current_user['user_id']}")
            profile_data = {
                "id": current_user["user_id"],
                "email": current_user["email"],
                "full_name": None,
                "timezone": "America/Panama"
            }
            
            create_response = supabase.table("user_profiles").insert(profile_data).execute()
            if create_response.data:
                return create_response.data[0]
            else:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to create user profile"
                )
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.put("/profile", response_model=UserProfile)
async def update_profile(
    profile_update: UserProfileUpdate,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Update user profile"""
    try:
        supabase = get_user_supabase(current_user["token"])
        
        # Serialize fields properly
        update_data = profile_update.model_dump(exclude_unset=True, mode='json')
        update_data["updated_at"] = "now()"
        
        response = supabase.table("user_profiles").update(update_data).eq("id", current_user["user_id"]).execute()
        
        if response.data:
            return response.data[0]
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Profile not found"
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
