from fastapi import APIRouter, HTTPException, status, Depends, Query
from database import get_user_supabase
from models import Task, TaskCreate, TaskUpdate, CalendarWithGrades, GradeByCategory, GradeByCourse, CalendarGradesLinked
from auth_middleware import get_current_user
from typing import List, Dict, Any, Optional
from uuid import UUID
from datetime import datetime

router = APIRouter()

# --- ENDPOINTS PARA VISTAS SQL (usando Supabase) ---

@router.get("/vw/calendar-with-grades", response_model=List[CalendarWithGrades])
async def get_calendar_with_grades(
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get calendar with grades view for the authenticated user"""
    try:
        supabase = get_user_supabase(current_user["token"])
        result = (
            supabase
            .table("vw_calendar_with_grades")
            .select("*")
            .eq("user_id", current_user["user_id"])
            .execute()
        )
        return result.data or []
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail=f"Error fetching calendar with grades: {exc}"
        )

@router.get("/vw/grades-by-category", response_model=List[GradeByCategory])
async def get_grades_by_category(
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get grades by category view for the authenticated user"""
    try:
        supabase = get_user_supabase(current_user["token"])
        result = (
            supabase
            .table("vw_grades_by_category")
            .select("*")
            .eq("user_id", current_user["user_id"])
            .execute()
        )
        return result.data or []
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail=f"Error fetching grades by category: {exc}"
        )

@router.get("/vw/grades-by-course", response_model=List[GradeByCourse])
async def get_grades_by_course(
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get grades by course view for the authenticated user"""
    try:
        supabase = get_user_supabase(current_user["token"])
        result = (
            supabase
            .table("vw_grades_by_course")
            .select("*")
            .eq("user_id", current_user["user_id"])
            .execute()
        )
        return result.data or []
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail=f"Error fetching grades by course: {exc}"
        )

@router.get("/vw/calendar-grades-linked", response_model=List[CalendarGradesLinked])
async def get_calendar_grades_linked(
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get calendar grades linked view for the authenticated user"""
    try:
        supabase = get_user_supabase(current_user["token"])
        result = (
            supabase
            .table("vw_calendar_grades_linked")
            .select("*")
            .eq("user_id", current_user["user_id"])
            .execute()
        )
        return result.data or []
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail=f"Error fetching calendar grades linked: {exc}"
        )



# --- PATCH ÚNICO PARA ACTUALIZAR VALUE DE GRADES ---
@router.patch("/{grade_id}/complete", status_code=status.HTTP_200_OK)
async def complete_grade(
    grade_id: UUID,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Cambia el valor de grades.value de 1 a 0 para la calificación indicada.
    """
    try:
        supabase = get_user_supabase(current_user["token"])
        result = (
            supabase
            .table("grades")
            .update({"value": 0})
            .eq("id", str(grade_id))
            .eq("user_id", current_user["user_id"])
            .eq("value", 1)
            .execute()
        )
        if not result.data:
            return {"message": "Grade was already 0 or not found."}
        return {"message": "Grade value updated to 0."}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error updating grade value: {e}"
        )