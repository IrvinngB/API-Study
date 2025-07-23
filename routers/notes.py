
from fastapi import APIRouter, HTTPException, status, Depends, Query
from database import get_user_supabase
from models import Note, NoteCreate, NoteUpdate
from auth_middleware import get_current_user
from typing import List, Dict, Any, Optional
from uuid import UUID
from datetime import date, datetime
import os
import httpx

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
        
        # Serialize datetime fields properly
        insert_data = note_data.model_dump(mode='json')
        insert_data["user_id"] = current_user["user_id"]
        
        response = supabase.table("notes").insert(insert_data).execute()
        
        if response.data:
            # Create initial version
            note_id = response.data[0]["id"]
            
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
        
        # Serialize datetime fields properly
        update_data = note_update.model_dump(exclude_unset=True, mode='json')
        update_data["updated_at"] = "now()"
        update_data["last_edited"] = "now()"
        
        response = supabase.table("notes").update(update_data).eq("id", str(note_id)).eq("user_id", current_user["user_id"]).execute()
        
        if response.data:
            # Update completed successfully
            
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

@router.patch("/{note_id}", response_model=Note)
async def patch_note(
    note_id: UUID,
    note_update: NoteUpdate,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Partially update a note (PATCH method)"""
    try:
        supabase = get_user_supabase(current_user["token"])
        
        # Only include non-None values in the update, serialize datetime properly
        update_data = note_update.model_dump(exclude_unset=True, exclude_none=True, mode='json')
        if not update_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No fields provided for update"
            )
        
        # Get current note to create version if content changes
        current_response = supabase.table("notes").select("*").eq("id", str(note_id)).eq("user_id", current_user["user_id"]).execute()
        if not current_response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Note not found"
            )
        
        current_note = current_response.data[0]
        
        update_data["updated_at"] = "now()"
        update_data["last_edited"] = "now()"
        
        response = supabase.table("notes").update(update_data).eq("id", str(note_id)).eq("user_id", current_user["user_id"]).execute()
        
        if response.data:
            # Update completed successfully
            
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
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found")
        note = response.data[0]

        # Obtener la URL de la IA desde variable de entorno
        ai_url = os.getenv("AI_SUMMARY_URL")
        if not ai_url:
            raise HTTPException(status_code=500, detail="AI_SUMMARY_URL not configured")

        # Preparar el contenido para la IA
        content_to_summarize = f"{note['title']}\n\n{note['content']}"

        # Llamar al servicio externo de IA
        async with httpx.AsyncClient(timeout=60) as client:
            ai_response = await client.post(
                ai_url,
                json={"notes": content_to_summarize},
                headers={"Content-Type": "application/json"}
            )
        if ai_response.status_code != 200:
            raise HTTPException(status_code=502, detail="Error al consultar el servicio de IA")
        ai_data = ai_response.json()
        if not ai_data.get("success") or not ai_data.get("summary"):
            raise HTTPException(status_code=502, detail="La IA no devolvió un resumen válido")

        # Formatear el resumen (puedes guardar el JSON o el texto formateado)
        ai_summary = ai_data["summary"] if isinstance(ai_data["summary"], str) else str(ai_data["summary"])

        # Actualizar la nota con el resumen generado
        update_response = supabase.table("notes").update({
            "ai_summary": ai_summary,
            "updated_at": "now()"
        }).eq("id", str(note_id)).eq("user_id", current_user["user_id"]).execute()

        if update_response.data:
            return {"message": "AI summary generated successfully", "ai_summary": ai_summary}
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Failed to update note with AI summary")

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
