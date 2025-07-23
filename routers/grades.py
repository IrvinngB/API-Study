# routers/grades.py

from typing import List, Dict, Any, Optional
from uuid import UUID

from fastapi import APIRouter, HTTPException, status, Depends, Query

from database import get_user_supabase
from auth_middleware import get_current_user
from models import (
    Grade       as GradeModel,
    GradeCreate as GradeCreateModel,
    GradeUpdate as GradeUpdateModel,
)

router = APIRouter(tags=["Grades"])


@router.get("/", response_model=List[GradeModel])
async def list_grades(
    current_user: Dict[str, Any] = Depends(get_current_user),
    class_id: Optional[UUID] = Query(
        None,
        title="Filter by class UUID",
        description="UUID de la clase para filtrar calificaciones"
    ),
):
    """
    List all grades for the authenticated user, optionally filtered by class.
    """
    try:
        supabase = get_user_supabase(current_user["token"])
        query = (
            supabase
            .table("grades")
            .select("*")
            .eq("user_id", current_user["user_id"])
            .order("graded_at", desc=True)
        )
        if class_id is not None:
            query = query.eq("class_id", str(class_id))

        result = query.execute()
        return result.data or []
    except Exception as exc:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=f"Error listing grades: {exc}")


@router.post("/", response_model=GradeModel, status_code=status.HTTP_201_CREATED)
async def create_grade(
    payload: GradeCreateModel,
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """
    Create a new grade record for the user.
    """
    try:
        supabase = get_user_supabase(current_user["token"])
        data = payload.model_dump(mode="json", exclude_none=True)
        data["user_id"] = current_user["user_id"]

        result = supabase.table("grades").insert(data).execute()
        if result.data:
            return result.data[0]
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="Failed to create grade")
    except Exception as exc:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=f"Error creating grade: {exc}")


@router.get("/{grade_id}", response_model=GradeModel)
async def get_grade(
    grade_id: UUID,
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """
    Retrieve a single grade by its UUID.
    """
    try:
        supabase = get_user_supabase(current_user["token"])
        result = (
            supabase
            .table("grades")
            .select("*")
            .eq("id", str(grade_id))
            .eq("user_id", current_user["user_id"])
            .execute()
        )
        if not result.data:
            raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Grade not found")
        return result.data[0]
    except Exception as exc:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=f"Error retrieving grade: {exc}")


@router.put("/{grade_id}", response_model=GradeModel)
async def update_grade(
    grade_id: UUID,
    payload: GradeUpdateModel,
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """
    Replace an existing grade's fields completely.
    """
    try:
        supabase = get_user_supabase(current_user["token"])
        update_data = payload.model_dump(exclude_unset=True, mode="json")

        result = (
            supabase
            .table("grades")
            .update(update_data)
            .eq("id", str(grade_id))
            .eq("user_id", current_user["user_id"])
            .execute()
        )
        if not result.data:
            raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Grade not found")
        return result.data[0]
    except Exception as exc:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=f"Error updating grade: {exc}")


@router.patch("/{grade_id}", response_model=GradeModel)
async def patch_grade(
    grade_id: UUID,
    payload: GradeUpdateModel,
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """
    Partially update only provided fields of a grade.
    """
    try:
        supabase = get_user_supabase(current_user["token"])
        update_data = payload.model_dump(
            exclude_unset=True, exclude_none=True, mode="json"
        )
        if not update_data:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="No fields provided")

        result = (
            supabase
            .table("grades")
            .update(update_data)
            .eq("id", str(grade_id))
            .eq("user_id", current_user["user_id"])
            .execute()
        )
        if not result.data:
            raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Grade not found")
        return result.data[0]
    except Exception as exc:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=f"Error patching grade: {exc}")


@router.delete("/{grade_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_grade(
    grade_id: UUID,
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """
    Delete a grade by its UUID.
    """
    try:
        supabase = get_user_supabase(current_user["token"])
        result = (
            supabase
            .table("grades")
            .delete()
            .eq("id", str(grade_id))
            .eq("user_id", current_user["user_id"])
            .execute()
        )
        if not result.data:
            raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Grade not found")
    except Exception as exc:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=f"Error deleting grade: {exc}")
