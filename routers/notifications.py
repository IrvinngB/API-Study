from fastapi import APIRouter, HTTPException, status, Depends, Query
from database import get_user_supabase
from models import Notification, NotificationCreate, NotificationUpdate
from auth_middleware import get_current_user
from typing import List, Dict, Any, Optional
from uuid import UUID
from datetime import datetime

router = APIRouter()

@router.get("/", response_model=List[Notification])
async def get_notifications(
    current_user: Dict[str, Any] = Depends(get_current_user),
    is_read: Optional[bool] = Query(None),
    limit: int = Query(50, le=100)
):
    """Get notifications for the current user with optional filters"""
    try:
        supabase = get_user_supabase(current_user["token"])
        query = supabase.table("notifications").select("*").eq("user_id", current_user["user_id"])
        
        if is_read is not None:
            query = query.eq("is_read", is_read)
            
        query = query.limit(limit).order("created_at", desc=True)
        response = query.execute()
        
        return response.data
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/", response_model=Notification)
async def create_notification(
    notification_data: NotificationCreate,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Create a new notification"""
    try:
        supabase = get_user_supabase(current_user["token"])
        
        # Serialize datetime fields properly
        insert_data = notification_data.model_dump(mode='json')
        insert_data["user_id"] = current_user["user_id"]
        
        response = supabase.table("notifications").insert(insert_data).execute()
        
        if response.data:
            return response.data[0]
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to create notification"
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/{notification_id}", response_model=Notification)
async def get_notification(
    notification_id: UUID,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get a specific notification"""
    try:
        supabase = get_user_supabase(current_user["token"])
        response = supabase.table("notifications").select("*").eq("id", str(notification_id)).eq("user_id", current_user["user_id"]).execute()
        
        if response.data:
            return response.data[0]
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Notification not found"
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.put("/{notification_id}", response_model=Notification)
async def update_notification(
    notification_id: UUID,
    notification_update: NotificationUpdate,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Update a notification"""
    try:
        supabase = get_user_supabase(current_user["token"])
        
        # Serialize datetime fields properly
        update_data = notification_update.model_dump(exclude_unset=True, mode='json')
        
        response = supabase.table("notifications").update(update_data).eq("id", str(notification_id)).eq("user_id", current_user["user_id"]).execute()
        
        if response.data:
            return response.data[0]
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Notification not found"
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.patch("/{notification_id}", response_model=Notification)
async def patch_notification(
    notification_id: UUID,
    notification_update: NotificationUpdate,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Partially update a notification (PATCH method)"""
    try:
        supabase = get_user_supabase(current_user["token"])
        
        # Only include non-None values in the update, serialize datetime properly
        update_data = notification_update.model_dump(exclude_unset=True, exclude_none=True, mode='json')
        if not update_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No fields provided for update"
            )
        
        response = supabase.table("notifications").update(update_data).eq("id", str(notification_id)).eq("user_id", current_user["user_id"]).execute()
        
        if response.data:
            return response.data[0]
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Notification not found"
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/{notification_id}/mark-read")
async def mark_notification_read(
    notification_id: UUID,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Mark a notification as read"""
    try:
        supabase = get_user_supabase(current_user["token"])
        
        update_data = {
            "is_read": True
        }
        
        response = supabase.table("notifications").update(update_data).eq("id", str(notification_id)).eq("user_id", current_user["user_id"]).execute()
        
        if response.data:
            return {"message": "Notification marked as read"}
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Notification not found"
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.delete("/{notification_id}")
async def delete_notification(
    notification_id: UUID,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Delete a notification"""
    try:
        supabase = get_user_supabase(current_user["token"])
        response = supabase.table("notifications").delete().eq("id", str(notification_id)).eq("user_id", current_user["user_id"]).execute()
        
        if response.data:
            return {"message": "Notification deleted successfully"}
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Notification not found"
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
