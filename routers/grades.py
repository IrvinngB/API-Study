from fastapi import APIRouter, HTTPException, status, Depends, Query
from database import get_user_supabase
from auth_middleware import get_current_user
from models import Grade, GradeCreate, GradeUpdate
from typing import List, Dict, Any, Optional
from uuid import UUID

router = APIRouter()

# --------- GRADES ---------

@router.get("/", response_model=List[Grade])
async def get_grades(
    current_user: Dict[str, Any] = Depends(get_current_user),
    class_id: Optional[UUID] = Query(None)
):
    """List grades for the current user (optionally filter by class)"""
    try:
        supabase = get_user_supabase(current_user["token"])
        query = supabase.table("grades").select("*").eq("user_id", current_user["user_id"])
        if class_id:
            query = query.eq("class_id", str(class_id))
        response = query.order("graded_at", desc=True).execute()
        return response.data
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/", response_model=Grade)
async def create_grade(
    data: GradeCreate,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Create a new grade"""
    try:
        supabase = get_user_supabase(current_user["token"])
        # Serialize datetime fields properly
        insert_data = data.model_dump(mode='json')
        insert_data["user_id"] = current_user["user_id"]
        response = supabase.table("grades").insert(insert_data).execute()
        if response.data:
            return response.data[0]
        raise HTTPException(status_code=400, detail="Failed to create grade")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{grade_id}", response_model=Grade)
async def get_grade(
    grade_id: UUID,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get a specific grade"""
    try:
        supabase = get_user_supabase(current_user["token"])
        response = supabase.table("grades").select("*").eq("id", str(grade_id)).eq("user_id", current_user["user_id"]).execute()
        if response.data:
            return response.data[0]
        raise HTTPException(status_code=404, detail="Grade not found")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/{grade_id}", response_model=Grade)
async def update_grade(
    grade_id: UUID,
    data: GradeUpdate,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Update a grade"""
    try:
        supabase = get_user_supabase(current_user["token"])
        # Serialize datetime fields properly
        update_data = data.model_dump(exclude_unset=True, mode='json')
        response = supabase.table("grades").update(update_data).eq("id", str(grade_id)).eq("user_id", current_user["user_id"]).execute()
        if response.data:
            return response.data[0]
        raise HTTPException(status_code=404, detail="Grade not found")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.patch("/{grade_id}", response_model=Grade)
async def patch_grade(
    grade_id: UUID,
    data: GradeUpdate,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Partially update a grade (PATCH method)"""
    try:
        supabase = get_user_supabase(current_user["token"])
        
        # Only include non-None values in the update, serialize datetime properly
        update_data = data.model_dump(exclude_unset=True, exclude_none=True, mode='json')
        if not update_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No fields provided for update"
            )
            
        update_data["updated_at"] = "now()"
        
        response = supabase.table("grades").update(update_data).eq("id", str(grade_id)).eq("user_id", current_user["user_id"]).execute()
        if response.data:
            return response.data[0]
        raise HTTPException(status_code=404, detail="Grade not found")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{grade_id}")
async def delete_grade(
    grade_id: UUID,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Delete a grade"""
    try:
        supabase = get_user_supabase(current_user["token"])
        response = supabase.table("grades").delete().eq("id", str(grade_id)).eq("user_id", current_user["user_id"]).execute()
        if response.data:
            return {"message": "Grade deleted"}
        raise HTTPException(status_code=404, detail="Grade not found")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
