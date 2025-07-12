from fastapi import APIRouter, HTTPException, status, Depends, Query
from database import get_user_supabase
from models import Note, NoteCreate, NoteUpdate, NoteVersion, NoteVersionCreate
from auth_middleware import get_current_user
from typing import List, Dict, Any, Optional
from uuid import UUID
from datetime import date, datetime

router = APIRouter()

@router.get("/", response_model=List[Note])
async def get_notes(
    current_user: Dict[str, Any] = Depends(get_current_user),
    class_id: Optional[UUID] = Query(None),
    lesson_date: Optional[date] = Query(None),
    is_favorite: Optional[bool] = Query(None),
    tags: Optional[List[str]] = Query(None)
):
    """Get notes for the current user"""
    try:
        supabase = get_user_supabase(current_user["token"])
        query = supabase.table("notes").select("*").eq("user_id", current_user["user_id"])
        
        if class_id:
            query = query.eq("class_id", str(class_id))
        if lesson_date:
            query = query.eq("lesson_date", lesson_date.isoformat())
        if is_favorite is not None:
            query = query.eq("is_favorite", is_favorite)
        if tags:
            for tag in tags:
                query = query.contains("tags", [tag])
            
        query = query.order("created_at", desc=True)
        response = query.execute()
        
        return response.data
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/", response_model=Note)
async def create_note(
    note_data: NoteCreate,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Create a new note"""
    try:
        supabase = get_user_supabase(current_user["token"])
        
        insert_data = note_data.dict()
        insert_data["user_id"] = current_user["user_id"]
        
        response = supabase.table("notes").insert(insert_data).execute()
        
        if response.data:
            # Create initial version
            note_id = response.data[0]["id"]
            version_data = {
                "user_id": current_user["user_id"],
                "note_id": note_id,
                "content": note_data.content,
                "ai_summary": note_data.ai_summary,
                "version_number": 1,
                "change_description": "Initial creation"
            }
            supabase.table("note_versions").insert(version_data).execute()
            
            return response.data[0]
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to create note"
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/{note_id}", response_model=Note)
async def get_note(
    note_id: UUID,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get a specific note"""
    try:
        supabase = get_user_supabase(current_user["token"])
        response = supabase.table("notes").select("*").eq("id", str(note_id)).eq("user_id", current_user["user_id"]).execute()
        
        if response.data:
            return response.data[0]
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Note not found"
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.put("/{note_id}", response_model=Note)
async def update_note(
    note_id: UUID,
    note_update: NoteUpdate,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Update a note"""
    try:
        supabase = get_user_supabase(current_user["token"])
        
        # Get current note to create version
        current_response = supabase.table("notes").select("*").eq("id", str(note_id)).eq("user_id", current_user["user_id"]).execute()
        if not current_response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Note not found"
            )
        
        current_note = current_response.data[0]
        
        # Get latest version number
        versions_response = supabase.table("note_versions").select("version_number").eq("note_id", str(note_id)).order("version_number", desc=True).limit(1).execute()
        latest_version = versions_response.data[0]["version_number"] if versions_response.data else 0
        
        update_data = note_update.dict(exclude_unset=True)
        update_data["updated_at"] = "now()"
        update_data["last_edited"] = "now()"
        
        response = supabase.table("notes").update(update_data).eq("id", str(note_id)).eq("user_id", current_user["user_id"]).execute()
        
        if response.data:
            # Create new version if content or ai_summary changed
            if "content" in update_data or "ai_summary" in update_data:
                version_data = {
                    "user_id": current_user["user_id"],
                    "note_id": str(note_id),
                    "content": update_data.get("content", current_note["content"]),
                    "ai_summary": update_data.get("ai_summary", current_note["ai_summary"]),
                    "version_number": latest_version + 1,
                    "change_description": "Content updated"
                }
                supabase.table("note_versions").insert(version_data).execute()
            
            return response.data[0]
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Note not found"
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.delete("/{note_id}")
async def delete_note(
    note_id: UUID,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Delete a note"""
    try:
        supabase = get_user_supabase(current_user["token"])
        response = supabase.table("notes").delete().eq("id", str(note_id)).eq("user_id", current_user["user_id"]).execute()
        
        if response.data:
            return {"message": "Note deleted successfully"}
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Note not found"
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

# Note Versions
@router.get("/{note_id}/versions", response_model=List[NoteVersion])
async def get_note_versions(
    note_id: UUID,
    current_user: Dict[str, Any] = Depends(get_current_user),
    limit: Optional[int] = Query(10, ge=1, le=50)
):
    """Get versions for a specific note"""
    try:
        supabase = get_user_supabase(current_user["token"])
        query = supabase.table("note_versions").select("*").eq("note_id", str(note_id)).eq("user_id", current_user["user_id"])
        query = query.order("version_number", desc=True).limit(limit)
        response = query.execute()
        
        return response.data
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/{note_id}/versions", response_model=NoteVersion)
async def create_note_version(
    note_id: UUID,
    version_data: NoteVersionCreate,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Create a new note version (manual backup)"""
    try:
        supabase = get_user_supabase(current_user["token"])
        
        # Get latest version number
        versions_response = supabase.table("note_versions").select("version_number").eq("note_id", str(note_id)).order("version_number", desc=True).limit(1).execute()
        latest_version = versions_response.data[0]["version_number"] if versions_response.data else 0
        
        insert_data = version_data.dict()
        insert_data["user_id"] = current_user["user_id"]
        insert_data["note_id"] = str(note_id)
        insert_data["version_number"] = latest_version + 1
        
        response = supabase.table("note_versions").insert(insert_data).execute()
        
        if response.data:
            return response.data[0]
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to create note version"
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

# Search and filter endpoints
@router.get("/search/by-class/{class_id}", response_model=List[Note])
async def get_notes_by_class(
    class_id: UUID,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get all notes for a specific class"""
    try:
        supabase = get_user_supabase(current_user["token"])
        response = supabase.table("notes").select("*").eq("class_id", str(class_id)).eq("user_id", current_user["user_id"]).order("lesson_date", desc=True).execute()
        
        return response.data
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/search/by-date-range", response_model=List[Note])
async def get_notes_by_date_range(
    start_date: date = Query(...),
    end_date: date = Query(...),
    current_user: Dict[str, Any] = Depends(get_current_user),
    class_id: Optional[UUID] = Query(None)
):
    """Get notes within a date range"""
    try:
        supabase = get_user_supabase(current_user["token"])
        query = supabase.table("notes").select("*").eq("user_id", current_user["user_id"])
        query = query.gte("lesson_date", start_date.isoformat()).lte("lesson_date", end_date.isoformat())
        
        if class_id:
            query = query.eq("class_id", str(class_id))
            
        query = query.order("lesson_date", desc=True)
        response = query.execute()
        
        return response.data
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/{note_id}/generate-summary")
async def generate_ai_summary(
    note_id: UUID,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Generate AI summary for a note"""
    try:
        supabase = get_user_supabase(current_user["token"])
        
        # Get the note
        response = supabase.table("notes").select("*").eq("id", str(note_id)).eq("user_id", current_user["user_id"]).execute()
        
        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Note not found"
            )
        
        note = response.data[0]
        
        # TODO: Integrate with AI service to generate summary
        # For now, return a placeholder
        ai_summary = f"AI Summary of: {note['title'][:50]}..."
        
        # Update the note with AI summary
        update_response = supabase.table("notes").update({
            "ai_summary": ai_summary,
            "updated_at": "now()"
        }).eq("id", str(note_id)).eq("user_id", current_user["user_id"]).execute()
        
        if update_response.data:
            return {"message": "AI summary generated successfully", "ai_summary": ai_summary}
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to update note with AI summary"
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
