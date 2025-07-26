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
            print(f"📋 Retrieved profile data: {response.data[0]}")
            return response.data[0]
        else:
            # Check if a profile with the same email already exists
            email_check_response = supabase.table("user_profiles").select("*").eq("email", current_user["email"]).execute()

            if email_check_response.data:
                print(f"⚠️ Profile with email already exists: {email_check_response.data[0]}")
                return email_check_response.data[0]

            # Create a default profile if none exists
            default_profile = {
                "id": current_user["user_id"],
                "email": current_user["email"],
                "full_name": current_user.get("user_metadata", {}).get("full_name", ""),
                "timezone": "UTC",  # Default timezone
                "created_at": "now()",
                "updated_at": "now()"
            }

            create_response = supabase.table("user_profiles").insert(default_profile).execute()

            if create_response.data:
                print(f"✅ Default profile created: {create_response.data[0]}")
                return create_response.data[0]
            else:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to create default profile"
                )

    except Exception as e:
        print(f"❌ Error retrieving or creating profile: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        ) from e

@router.post("/", response_model=UserProfile)
async def create_user_profile(
    profile_data: UserProfileCreate,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Create a user profile"""
    try:
        supabase = get_user_supabase(current_user["token"])

        # Check if a profile with the same email already exists
        existing_profile = supabase.table("user_profiles").select("*").eq("email", profile_data.email).execute()
        if existing_profile.data:
            print(f"⚠️ Profile with email already exists: {existing_profile.data[0]}")
            return existing_profile.data[0]

        # Serialize fields properly
        insert_data = profile_data.model_dump(mode='json')
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
        ) from e

@router.put("/me", response_model=UserProfile)
async def update_user_profile(
    profile_update: UserProfileUpdate,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Update the current user's profile"""
    try:
        supabase = get_user_supabase(current_user["token"])
        
        print(f"🔍 Checking user profile for ID: {current_user['user_id']}")
        print(f"📥 Received profile update data: {profile_update}")
        
        # Serialize fields properly
        update_data = profile_update.model_dump(exclude_unset=True, mode='json')
        update_data["updated_at"] = "now()"
        
        # Primero, verificar si el perfil existe
        check_response = supabase.table("user_profiles").select("*").eq("id", current_user["user_id"]).execute()
        print(f"🔍 Profile check results: {check_response.data}")
        
        if not check_response.data:
            # Si el perfil no existe, intentar obtenerlo a través de email
            print(f"⚠️ Profile not found in direct check, trying email search for: {current_user['email']}")
            
            # Intentar con una búsqueda por email
            email_response = supabase.table("user_profiles").select("*").eq("email", current_user["email"]).execute()
            print(f"📧 Email search results: {email_response.data}")
            
            if email_response.data:
                # Si encontramos el perfil por email, actualizar usando ese ID
                print(f"✉️ Found profile by email: {email_response.data[0]}")
                profile_id = email_response.data[0].get("id")
                response = supabase.table("user_profiles").update(update_data).eq("id", profile_id).execute()
                
                if response.data:
                    print(f"✅ Profile updated successfully: {response.data[0]}")
                    return response.data[0]
                else:
                    print("❌ Failed to update profile found by email")
            
            # Si todavía no encontramos el perfil, crearlo
            print(f"🆕 Creating new profile for user: {current_user['user_id']}")
            default_profile = {
                "id": current_user["user_id"],
                "email": current_user["email"],
                "full_name": profile_update.full_name or current_user.get("user_metadata", {}).get("full_name", ""),
                "timezone": profile_update.timezone or "UTC",
                "created_at": "now()",
                "updated_at": "now()"
            }
            
            # Agregar campos opcionales si están presentes
            if profile_update.avatar_url:
                default_profile["avatar_url"] = profile_update.avatar_url
            if profile_update.subscription_tier:
                default_profile["subscription_tier"] = profile_update.subscription_tier
            if profile_update.preferences:
                default_profile["preferences"] = profile_update.preferences
            
            print(f"📝 Creating profile with data: {default_profile}")
            create_response = supabase.table("user_profiles").insert(default_profile).execute()
            print(f"📎 Create response: {create_response}")
            
            if create_response.data:
                print(f"✅ Profile created successfully: {create_response.data[0]}")
                return create_response.data[0]
            else:
                error_message = getattr(create_response, "error", "Unknown error")
                print(f"❌ Failed to create profile: {error_message}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Failed to create profile: {error_message}"
                )
        
        # Si el perfil existe, actualizarlo
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
        ) from e

@router.patch("/me", response_model=UserProfile)
async def patch_user_profile(
    profile_update: UserProfileUpdate,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Partially update the current user's profile (PATCH method)"""
    try:
        supabase = get_user_supabase(current_user["token"])
        
        print(f"🔍 Checking user profile for ID: {current_user['user_id']}")
        print(f"📥 Received profile update data: {profile_update}")
        
        # Only include non-None values in the update, serialize fields properly
        update_data = profile_update.model_dump(exclude_unset=True, exclude_none=True, mode='json')
        if not update_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No fields provided for update"
            )
            
        update_data["updated_at"] = "now()"
        
        # Primero, verificar si el perfil existe
        check_response = supabase.table("user_profiles").select("*").eq("id", current_user["user_id"]).execute()
        print(f"🔍 Profile check results: {check_response.data}")
        
        if not check_response.data:
            # Si el perfil no existe, intentar obtenerlo a través de email
            print(f"⚠️ Profile not found in direct check, trying email search for: {current_user['email']}")
            
            # Intentar con una búsqueda por email
            email_response = supabase.table("user_profiles").select("*").eq("email", current_user["email"]).execute()
            print(f"📧 Email search results: {email_response.data}")
            
            if email_response.data:
                # Si encontramos el perfil por email, actualizar usando ese ID
                print(f"✉️ Found profile by email: {email_response.data[0]}")
                profile_id = email_response.data[0].get("id")
                response = supabase.table("user_profiles").update(update_data).eq("id", profile_id).execute()
                
                if response.data:
                    print(f"✅ Profile updated successfully: {response.data[0]}")
                    return response.data[0]
                else:
                    print("❌ Failed to update profile found by email")
            
            # Si todavía no encontramos el perfil, crearlo
            print(f"🆕 Creating new profile for user: {current_user['user_id']}")
            default_profile = {
                "id": current_user["user_id"],
                "email": current_user["email"],
                "full_name": profile_update.full_name or current_user.get("user_metadata", {}).get("full_name", ""),
                "timezone": profile_update.timezone or "UTC",
                "created_at": "now()",
                "updated_at": "now()"
            }
            
            # Agregar campos opcionales si están presentes
            if profile_update.avatar_url:
                default_profile["avatar_url"] = profile_update.avatar_url
            if profile_update.subscription_tier:
                default_profile["subscription_tier"] = profile_update.subscription_tier
            if profile_update.preferences:
                default_profile["preferences"] = profile_update.preferences
            
            print(f"📝 Creating profile with data: {default_profile}")
            create_response = supabase.table("user_profiles").insert(default_profile).execute()
            print(f"📎 Create response: {create_response}")
            
            if create_response.data:
                print(f"✅ Profile created successfully: {create_response.data[0]}")
                return create_response.data[0]
            else:
                error_message = getattr(create_response, "error", "Unknown error")
                print(f"❌ Failed to create profile: {error_message}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Failed to create profile: {error_message}"
                )
        
        # Si el perfil existe, actualizarlo
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
        ) from e

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
        ) from e