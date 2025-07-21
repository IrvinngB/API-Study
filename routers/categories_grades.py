# routers/categories_grades.py

from fastapi import APIRouter, HTTPException, status, Depends, Query
from typing import List, Optional, Dict, Any
from uuid import UUID

from database import get_user_supabase
from auth_middleware import get_current_user
from models import (
    CategoryGrade    as Category,
    CategoryGradeCreate as CategoryCreate,
    CategoryGradeUpdate as CategoryUpdate,
)

router = APIRouter(tags=["categories"])


@router.get("/", response_model=List[Category])
async def list_categories(
    current_user: Dict[str, Any] = Depends(get_current_user),
    class_id: Optional[UUID] = Query(None, description="Filter by class UUID"),
):
    """
    List all categories, optionally filtering by `class_id`.
    """
    try:
        supabase = get_user_supabase(current_user["token"])
        query = supabase.table("categories_grades").select("*")

        if class_id:
            query = query.eq("class_id", str(class_id))

        result = query.order("created_at", desc=False).execute()
        return result.data or []
    except Exception as exc:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=str(exc))


@router.post(
    "/",
    response_model=Category,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new category",
)
async def create_category(
    payload: CategoryCreate,
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """
    Insert a new category for a given class.
    """
    try:
        supabase = get_user_supabase(current_user["token"])
        insert_data = payload.model_dump(mode="json")
        result = supabase.table("categories_grades").insert(insert_data).execute()
        if result.data:
            return result.data[0]

        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            detail="Failed to create category",
        )
    except Exception as exc:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=str(exc))


@router.get(
    "/{category_id}",
    response_model=Category,
    summary="Get a category by ID",
)
async def get_category(
    category_id: UUID,
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """
    Retrieve a single category by its UUID.
    """
    try:
        supabase = get_user_supabase(current_user["token"])
        result = (
            supabase.table("categories_grades")
            .select("*")
            .eq("id", str(category_id))
            .execute()
        )
        data = result.data or []
        if data:
            return data[0]

        raise HTTPException(
            status.HTTP_404_NOT_FOUND, detail="Category not found"
        )
    except Exception as exc:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=str(exc))


@router.put(
    "/{category_id}",
    response_model=Category,
    summary="Update a category",
)
async def update_category(
    category_id: UUID,
    payload: CategoryUpdate,
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """
    Replace `name` and/or `percentage` fields of an existing category.
    """
    try:
        supabase = get_user_supabase(current_user["token"])
        update_data = payload.model_dump(exclude_unset=True, mode="json")
        result = (
            supabase.table("categories_grades")
            .update(update_data)
            .eq("id", str(category_id))
            .execute()
        )
        data = result.data or []
        if data:
            return data[0]

        raise HTTPException(
            status.HTTP_404_NOT_FOUND, detail="Category not found"
        )
    except Exception as exc:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=str(exc))


@router.delete(
    "/{category_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a category",
)
async def delete_category(
    category_id: UUID,
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """
    Remove a category by its UUID.
    """
    try:
        supabase = get_user_supabase(current_user["token"])
        result = (
            supabase.table("categories_grades")
            .delete()
            .eq("id", str(category_id))
            .execute()
        )
        if not result.data:
            raise HTTPException(
                status.HTTP_404_NOT_FOUND, detail="Category not found"
            )
    except Exception as exc:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=str(exc))
