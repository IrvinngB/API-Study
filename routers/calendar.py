from fastapi import APIRouter, HTTPException, status, Depends, Query
from database import get_user_supabase
from models import CalendarEvent, CalendarEventCreate, CalendarEventUpdate
from auth_middleware import get_current_user
from typing import List, Dict, Any, Optional
from uuid import UUID
from datetime import datetime, date

router = APIRouter()

@router.get("/", response_model=List[CalendarEvent])
async def get_events(
    current_user: Dict[str, Any] = Depends(get_current_user),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    class_id: Optional[UUID] = Query(None),
    event_type: Optional[str] = Query(None)
):
    """Get calendar events for the current user"""
    try:
        supabase = get_user_supabase(current_user["token"])
        query = supabase.table("calendar_events").select("*").eq("user_id", current_user["user_id"])
        
        if start_date:
            query = query.gte("start_datetime", start_date.isoformat())
        if end_date:
            query = query.lte("end_datetime", end_date.isoformat())
        if class_id:
            query = query.eq("class_id", str(class_id))
        if event_type:
            query = query.eq("event_type", event_type)
            
        query = query.order("start_datetime", desc=False)
        response = query.execute()
        
        return response.data
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/", response_model=CalendarEvent)
async def create_event(
    event_data: CalendarEventCreate,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Create a new calendar event"""
    try:
        supabase = get_user_supabase(current_user["token"])
        
        insert_data = event_data.dict()
        insert_data["user_id"] = current_user["user_id"]
        
        response = supabase.table("calendar_events").insert(insert_data).execute()
        
        if response.data:
            return response.data[0]
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to create event"
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/{event_id}", response_model=CalendarEvent)
async def get_event(
    event_id: UUID,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get a specific calendar event"""
    try:
        supabase = get_user_supabase(current_user["token"])
        response = supabase.table("calendar_events").select("*").eq("id", str(event_id)).eq("user_id", current_user["user_id"]).execute()
        
        if response.data:
            return response.data[0]
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Event not found"
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.put("/{event_id}", response_model=CalendarEvent)
async def update_event(
    event_id: UUID,
    event_update: CalendarEventUpdate,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Update a calendar event"""
    try:
        supabase = get_user_supabase(current_user["token"])
        
        update_data = event_update.dict(exclude_unset=True)
        update_data["updated_at"] = "now()"
        
        response = supabase.table("calendar_events").update(update_data).eq("id", str(event_id)).eq("user_id", current_user["user_id"]).execute()
        
        if response.data:
            return response.data[0]
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Event not found"
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.delete("/{event_id}")
async def delete_event(
    event_id: UUID,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Delete a calendar event"""
    try:
        supabase = get_user_supabase(current_user["token"])
        response = supabase.table("calendar_events").delete().eq("id", str(event_id)).eq("user_id", current_user["user_id"]).execute()
        
        if response.data:
            return {"message": "Event deleted successfully"}
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Event not found"
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
