from fastapi import APIRouter, HTTPException, status, Depends, Query
from database import get_user_supabase
from auth_middleware import get_current_user
from typing import List, Dict, Any, Optional
from uuid import UUID

router = APIRouter()

# --------- GRADE TYPES ---------

@router.get("/types", response_model=List[Dict[str, Any]])
async def get_grade_types(
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """List grade types for the current user"""
    try:
        supabase = get_user_supabase(current_user["token"])
        response = supabase.table("grade_types").select("*").eq("user_id", current_user["user_id"]).order("created_at", desc=False).execute()
        return response.data
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/types", response_model=Dict[str, Any])
async def create_grade_type(
    data: Dict[str, Any],
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Create a new grade type"""
    try:
        supabase = get_user_supabase(current_user["token"])
        insert_data = data.copy()
        insert_data["user_id"] = current_user["user_id"]
        response = supabase.table("grade_types").insert(insert_data).execute()
        if response.data:
            return response.data[0]
        raise HTTPException(status_code=400, detail="Failed to create grade type")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/types/{type_id}", response_model=Dict[str, Any])
async def update_grade_type(
    type_id: UUID,
    data: Dict[str, Any],
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Update a grade type"""
    try:
        supabase = get_user_supabase(current_user["token"])
        response = supabase.table("grade_types").update(data).eq("id", str(type_id)).eq("user_id", current_user["user_id"]).execute()
        if response.data:
            return response.data[0]
        raise HTTPException(status_code=404, detail="Grade type not found")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/types/{type_id}")
async def delete_grade_type(
    type_id: UUID,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Delete a grade type"""
    try:
        supabase = get_user_supabase(current_user["token"])
        response = supabase.table("grade_types").delete().eq("id", str(type_id)).eq("user_id", current_user["user_id"]).execute()
        if response.data:
            return {"message": "Grade type deleted"}
        raise HTTPException(status_code=404, detail="Grade type not found")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# --------- GRADES ---------

@router.get("/", response_model=List[Dict[str, Any]])
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

@router.post("/", response_model=Dict[str, Any])
async def create_grade(
    data: Dict[str, Any],
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Create a new grade"""
    try:
        supabase = get_user_supabase(current_user["token"])
        insert_data = data.copy()
        insert_data["user_id"] = current_user["user_id"]
        response = supabase.table("grades").insert(insert_data).execute()
        if response.data:
            return response.data[0]
        raise HTTPException(status_code=400, detail="Failed to create grade")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{grade_id}", response_model=Dict[str, Any])
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

@router.put("/{grade_id}", response_model=Dict[str, Any])
async def update_grade(
    grade_id: UUID,
    data: Dict[str, Any],
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Update a grade"""
    try:
        supabase = get_user_supabase(current_user["token"])
        response = supabase.table("grades").update(data).eq("id", str(grade_id)).eq("user_id", current_user["user_id"]).execute()
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