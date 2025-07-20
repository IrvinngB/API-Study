from fastapi import APIRouter, HTTPException, status, Depends, Query
from database import get_user_supabase
from models import Task, TaskCreate, TaskUpdate
from auth_middleware import get_current_user
from typing import List, Dict, Any, Optional
from uuid import UUID
from datetime import datetime

router = APIRouter()

@router.get("/", response_model=List[Task])
async def get_tasks(
    current_user: Dict[str, Any] = Depends(get_current_user),
    class_id: Optional[UUID] = Query(None),
    status: Optional[str] = Query(None),
    priority: Optional[int] = Query(None),
    limit: int = Query(100, le=1000)
):
    """Get tasks for the current user with optional filters"""
    try:
        supabase = get_user_supabase(current_user["token"])
        query = supabase.table("tasks").select("*").eq("user_id", current_user["user_id"])
        
        if class_id:
            query = query.eq("class_id", str(class_id))
        if status:
            query = query.eq("status", status)
        if priority:
            query = query.eq("priority", priority)
            
        query = query.limit(limit).order("created_at", desc=True)
        response = query.execute()
        
        return response.data
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/", response_model=Task)
async def create_task(
    task_data: TaskCreate,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Create a new task"""
    try:
        supabase = get_user_supabase(current_user["token"])
        
        # Serialize datetime fields properly
        insert_data = task_data.model_dump(mode='json')
        insert_data["user_id"] = current_user["user_id"]
        
        response = supabase.table("tasks").insert(insert_data).execute()
        
        if response.data:
            return response.data[0]
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to create task"
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/{task_id}", response_model=Task)
async def get_task(
    task_id: UUID,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get a specific task"""
    try:
        supabase = get_user_supabase(current_user["token"])
        response = supabase.table("tasks").select("*").eq("id", str(task_id)).eq("user_id", current_user["user_id"]).execute()
        
        if response.data:
            return response.data[0]
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.put("/{task_id}", response_model=Task)
async def update_task(
    task_id: UUID,
    task_update: TaskUpdate,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Update a task"""
    try:
        supabase = get_user_supabase(current_user["token"])
        
        # Serialize datetime fields properly
        update_data = task_update.model_dump(exclude_unset=True, mode='json')
        update_data["updated_at"] = "now()"
        
        # If marking as completed, set completed_at
        if update_data.get("status") == "completed" and not update_data.get("completed_at"):
            update_data["completed_at"] = datetime.utcnow().isoformat()
        
        response = supabase.table("tasks").update(update_data).eq("id", str(task_id)).eq("user_id", current_user["user_id"]).execute()
        
        if response.data:
            return response.data[0]
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.patch("/{task_id}", response_model=Task)
async def patch_task(
    task_id: UUID,
    task_update: TaskUpdate,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Partially update a task (PATCH method)"""
    try:
        supabase = get_user_supabase(current_user["token"])
        
        # Only include non-None values in the update, serialize datetime properly
        update_data = task_update.model_dump(exclude_unset=True, exclude_none=True, mode='json')
        if not update_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No fields provided for update"
            )
            
        update_data["updated_at"] = "now()"
        
        # If marking as completed, set completed_at
        if update_data.get("status") == "completed" and not update_data.get("completed_at"):
            update_data["completed_at"] = datetime.utcnow().isoformat()
        
        response = supabase.table("tasks").update(update_data).eq("id", str(task_id)).eq("user_id", current_user["user_id"]).execute()
        
        if response.data:
            return response.data[0]
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.delete("/{task_id}")
async def delete_task(
    task_id: UUID,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Delete a task"""
    try:
        supabase = get_user_supabase(current_user["token"])
        response = supabase.table("tasks").delete().eq("id", str(task_id)).eq("user_id", current_user["user_id"]).execute()
        
        if response.data:
            return {"message": "Task deleted successfully"}
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/{task_id}/complete")
async def complete_task(
    task_id: UUID,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Mark a task as completed"""
    try:
        supabase = get_user_supabase(current_user["token"])
        
        update_data = {
            "status": "completed",
            "completion_percentage": 100,
            "completed_at": datetime.utcnow().isoformat(),
            "updated_at": "now()"
        }
        
        response = supabase.table("tasks").update(update_data).eq("id", str(task_id)).eq("user_id", current_user["user_id"]).execute()
        
        if response.data:
            return response.data[0]
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
