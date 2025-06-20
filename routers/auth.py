from fastapi import APIRouter, HTTPException, status, Depends
from database import get_supabase_anon, get_user_supabase
from models import UserProfile, UserProfileCreate, UserProfileUpdate
from auth_middleware import get_current_user
from typing import Dict, Any

router = APIRouter()

@router.post("/signup")
async def signup(email: str, password: str):
    """Sign up a new user"""
    try:
        supabase = get_supabase_anon()
        response = supabase.auth.sign_up({
            "email": email,
            "password": password
        })
        
        if response.user:
            # Create user profile
            profile_data = {
                "id": response.user.id,
                "email": email,
                "full_name": None,
                "timezone": "America/Panama"
            }
            
            supabase.table("user_profiles").insert(profile_data).execute()
            
            return {
                "message": "User created successfully",
                "user": response.user,
                "session": response.session
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
async def signin(email: str, password: str):
    """Sign in user"""
    try:
        supabase = get_supabase_anon()
        response = supabase.auth.sign_in_with_password({
            "email": email,
            "password": password
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

@router.get("/profile", response_model=UserProfile)
async def get_profile(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Get user profile"""
    try:
        supabase = get_user_supabase(current_user["token"])
        response = supabase.table("user_profiles").select("*").eq("id", current_user["user_id"]).execute()
        
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

@router.put("/profile", response_model=UserProfile)
async def update_profile(
    profile_update: UserProfileUpdate,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Update user profile"""
    try:
        supabase = get_user_supabase(current_user["token"])
        
        update_data = profile_update.dict(exclude_unset=True)
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
