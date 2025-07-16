from fastapi import APIRouter, HTTPException, status, Depends
from database import get_user_supabase
from models import UserProfile, UserProfileCreate, UserProfileUpdate
from auth_middleware import get_current_user
from typing import Dict, Any
from uuid import UUID

router = APIRouter()

@router.get("/me", response_model=UserProfile)
async def get_current_user_profile(
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get the current user's profile"""
    try:
        supabase = get_user_supabase(current_user["token"])
        response = supabase.table("user_profiles").select("*").eq("id", current_user["user_id"]).execute()
        
        if response.data:
            return response.data[0]
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User profile not found"
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/", response_model=UserProfile)
async def create_user_profile(
    profile_data: UserProfileCreate,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Create a user profile"""
    try:
        supabase = get_user_supabase(current_user["token"])
        
        insert_data = profile_data.dict()
        insert_data["id"] = current_user["user_id"]
        
        response = supabase.table("user_profiles").insert(insert_data).execute()
        
        if response.data:
            return response.data[0]
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to create user profile"
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.put("/me", response_model=UserProfile)
async def update_user_profile(
    profile_update: UserProfileUpdate,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Update the current user's profile"""
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
                detail="User profile not found"
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.patch("/me", response_model=UserProfile)
async def patch_user_profile(
    profile_update: UserProfileUpdate,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Partially update the current user's profile (PATCH method)"""
    try:
        supabase = get_user_supabase(current_user["token"])
        
        # Only include non-None values in the update
        update_data = profile_update.dict(exclude_unset=True, exclude_none=True)
        if not update_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No fields provided for update"
            )
            
        update_data["updated_at"] = "now()"
        
        response = supabase.table("user_profiles").update(update_data).eq("id", current_user["user_id"]).execute()
        
        if response.data:
            return response.data[0]
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User profile not found"
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.delete("/me")
async def delete_user_profile(
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Delete the current user's profile"""
    try:
        supabase = get_user_supabase(current_user["token"])
        response = supabase.table("user_profiles").delete().eq("id", current_user["user_id"]).execute()
        
        if response.data:
            return {"message": "User profile deleted successfully"}
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User profile not found"
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
