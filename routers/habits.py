from fastapi import APIRouter, HTTPException, status, Depends, Query
from database import get_user_supabase
from models import Habit, HabitCreate, HabitUpdate, HabitLog, HabitLogCreate
from auth_middleware import get_current_user
from typing import List, Dict, Any, Optional
from uuid import UUID
from datetime import date

router = APIRouter()

@router.get("/", response_model=List[Habit])
async def get_habits(
    current_user: Dict[str, Any] = Depends(get_current_user),
    is_active: Optional[bool] = Query(None)
):
    """Get habits for the current user"""
    try:
        supabase = get_user_supabase(current_user["token"])
        query = supabase.table("habits").select("*").eq("user_id", current_user["user_id"])
        
        if is_active is not None:
            query = query.eq("is_active", is_active)
            
        query = query.order("created_at", desc=True)
        response = query.execute()
        
        return response.data
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/", response_model=Habit)
async def create_habit(
    habit_data: HabitCreate,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Create a new habit"""
    try:
        supabase = get_user_supabase(current_user["token"])
        
        insert_data = habit_data.dict()
        insert_data["user_id"] = current_user["user_id"]
        
        response = supabase.table("habits").insert(insert_data).execute()
        
        if response.data:
            return response.data[0]
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to create habit"
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/{habit_id}", response_model=Habit)
async def get_habit(
    habit_id: UUID,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get a specific habit"""
    try:
        supabase = get_user_supabase(current_user["token"])
        response = supabase.table("habits").select("*").eq("id", str(habit_id)).eq("user_id", current_user["user_id"]).execute()
        
        if response.data:
            return response.data[0]
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Habit not found"
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.put("/{habit_id}", response_model=Habit)
async def update_habit(
    habit_id: UUID,
    habit_update: HabitUpdate,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Update a habit"""
    try:
        supabase = get_user_supabase(current_user["token"])
        
        update_data = habit_update.dict(exclude_unset=True)
        update_data["updated_at"] = "now()"
        
        response = supabase.table("habits").update(update_data).eq("id", str(habit_id)).eq("user_id", current_user["user_id"]).execute()
        
        if response.data:
            return response.data[0]
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Habit not found"
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.delete("/{habit_id}")
async def delete_habit(
    habit_id: UUID,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Delete a habit"""
    try:
        supabase = get_user_supabase(current_user["token"])
        response = supabase.table("habits").delete().eq("id", str(habit_id)).eq("user_id", current_user["user_id"]).execute()
        
        if response.data:
            return {"message": "Habit deleted successfully"}
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Habit not found"
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

# Habit Logs
@router.get("/{habit_id}/logs", response_model=List[HabitLog])
async def get_habit_logs(
    habit_id: UUID,
    current_user: Dict[str, Any] = Depends(get_current_user),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None)
):
    """Get logs for a specific habit"""
    try:
        supabase = get_user_supabase(current_user["token"])
        query = supabase.table("habit_logs").select("*").eq("habit_id", str(habit_id)).eq("user_id", current_user["user_id"])
        
        if start_date:
            query = query.gte("completed_date", start_date.isoformat())
        if end_date:
            query = query.lte("completed_date", end_date.isoformat())
            
        query = query.order("completed_date", desc=True)
        response = query.execute()
        
        return response.data
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/{habit_id}/logs", response_model=HabitLog)
async def create_habit_log(
    habit_id: UUID,
    log_data: HabitLogCreate,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Create a new habit log"""
    try:
        supabase = get_user_supabase(current_user["token"])
        
        insert_data = log_data.dict()
        insert_data["user_id"] = current_user["user_id"]
        insert_data["habit_id"] = str(habit_id)
        
        response = supabase.table("habit_logs").insert(insert_data).execute()
        
        if response.data:
            return response.data[0]
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to create habit log"
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
