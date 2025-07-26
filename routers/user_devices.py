from fastapi import APIRouter, HTTPException, status, Depends
from database import get_user_supabase
from models import UserDevice, UserDeviceCreate, UserDeviceUpdate
from auth_middleware import get_current_user
from typing import List, Dict, Any
from datetime import datetime

router = APIRouter()

@router.get("/", response_model=List[UserDevice])
async def get_user_devices(
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get all devices for the current user"""
    try:
        supabase = get_user_supabase(current_user["token"])
        response = supabase.table("user_devices").select("*").eq("user_id", current_user["user_id"]).order("last_sync", desc=True).execute()
        
        return response.data
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/", response_model=UserDevice)
async def register_device(
    device_data: UserDeviceCreate,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Register a new device for the current user"""
    try:
        supabase = get_user_supabase(current_user["token"])

        # Check if device already exists
        existing_response = supabase.table("user_devices").select("*").eq("user_id", current_user["user_id"]).eq("device_id", device_data.device_id).execute()

        if existing_response.data:
            print(f"⚠️ Device already exists: {existing_response.data[0]}")
            # Update existing device, serialize fields properly
            update_data = device_data.model_dump(mode='json')
            update_data["last_sync"] = datetime.utcnow().isoformat()
            update_data["is_active"] = True

            response = supabase.table("user_devices").update(update_data).eq("user_id", current_user["user_id"]).eq("device_id", device_data.device_id).execute()
            return response.data[0]
        else:
            # Create new device, serialize fields properly
            insert_data = device_data.model_dump(mode='json')
            insert_data["user_id"] = current_user["user_id"]

            response = supabase.table("user_devices").insert(insert_data).execute()

            if response.data:
                return response.data[0]
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Failed to register device"
                )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        ) from e

@router.get("/{device_id}", response_model=UserDevice)
async def get_device(
    device_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get a specific device"""
    try:
        supabase = get_user_supabase(current_user["token"])
        response = supabase.table("user_devices").select("*").eq("user_id", current_user["user_id"]).eq("device_id", device_id).execute()
        
        if response.data:
            return response.data[0]
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Device not found"
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.put("/{device_id}", response_model=UserDevice)
async def update_device(
    device_id: str,
    device_update: UserDeviceUpdate,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Update a device"""
    try:
        supabase = get_user_supabase(current_user["token"])
        
        # Serialize fields properly
        update_data = device_update.model_dump(exclude_unset=True, mode='json')
        update_data["last_sync"] = datetime.utcnow().isoformat()
        
        response = supabase.table("user_devices").update(update_data).eq("user_id", current_user["user_id"]).eq("device_id", device_id).execute()
        
        if response.data:
            return response.data[0]
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Device not found"
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.patch("/{device_id}", response_model=UserDevice)
async def patch_device(
    device_id: str,
    device_update: UserDeviceUpdate,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Partially update a device (PATCH method)"""
    try:
        supabase = get_user_supabase(current_user["token"])
        
        # Only include non-None values in the update, serialize fields properly
        update_data = device_update.model_dump(exclude_unset=True, exclude_none=True, mode='json')
        if not update_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No fields provided for update"
            )
            
        update_data["last_sync"] = datetime.utcnow().isoformat()
        
        response = supabase.table("user_devices").update(update_data).eq("user_id", current_user["user_id"]).eq("device_id", device_id).execute()
        
        if response.data:
            return response.data[0]
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Device not found"
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/{device_id}/sync")
async def sync_device(
    device_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Update device sync timestamp"""
    try:
        supabase = get_user_supabase(current_user["token"])
        
        update_data = {
            "last_sync": datetime.utcnow().isoformat(),
            "is_active": True
        }
        
        response = supabase.table("user_devices").update(update_data).eq("user_id", current_user["user_id"]).eq("device_id", device_id).execute()
        
        if response.data:
            return {"message": "Device sync updated", "last_sync": update_data["last_sync"]}
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Device not found"
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.delete("/{device_id}")
async def deactivate_device(
    device_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Deactivate a device (mark as inactive instead of deleting)"""
    try:
        supabase = get_user_supabase(current_user["token"])
        
        update_data = {
            "is_active": False
        }
        
        response = supabase.table("user_devices").update(update_data).eq("user_id", current_user["user_id"]).eq("device_id", device_id).execute()
        
        if response.data:
            return {"message": "Device deactivated successfully"}
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Device not found"
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
