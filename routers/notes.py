
from fastapi import APIRouter, HTTPException, status, Depends, Query, UploadFile, File, Form
from fastapi.responses import FileResponse
from database import get_user_supabase
from models import Note, NoteCreate, NoteUpdate
from auth_middleware import get_current_user
from typing import List, Dict, Any, Optional
from uuid import UUID
from datetime import date, datetime
import os
import httpx
import shutil
import uuid
from pathlib import Path

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

# File management endpoints
@router.post("/{note_id}/upload-file")
async def upload_file_to_note(
    note_id: UUID,
    file: UploadFile = File(...),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Upload a file attachment to a note"""
    try:
        # Verify note exists and belongs to user
        supabase = get_user_supabase(current_user["token"])
        note_response = supabase.table("notes").select("*").eq("id", str(note_id)).eq("user_id", current_user["user_id"]).execute()
        
        if not note_response.data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found")
        
        note = note_response.data[0]
        
        # Create uploads directory if it doesn't exist
        uploads_dir = Path("uploads") / "notes" / str(note_id)
        uploads_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate unique filename
        file_extension = Path(file.filename).suffix if file.filename else ""
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        file_path = uploads_dir / unique_filename
        
        # Save file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Get file info
        file_size = file_path.stat().st_size
        
        # Update note attachments
        current_attachments = note.get("attachments", [])
        new_attachment = {
            "filename": file.filename,
            "type": "document" if file_extension in ['.pdf', '.doc', '.docx', '.txt'] else "other",
            "size": file_size,
            "local_path": str(file_path),
            "mime_type": file.content_type,
            "uploaded_at": datetime.now().isoformat()
        }
        
        current_attachments.append(new_attachment)
        
        # Update note in database
        update_response = supabase.table("notes").update({
            "attachments": current_attachments,
            "updated_at": "now()"
        }).eq("id", str(note_id)).eq("user_id", current_user["user_id"]).execute()
        
        if update_response.data:
            return {
                "message": "File uploaded successfully",
                "attachment": new_attachment,
                "file_path": str(file_path)
            }
        else:
            # Clean up file if database update fails
            file_path.unlink()
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to update note with file attachment")
            
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.get("/{note_id}/download/{file_id}")
async def download_file_from_note(
    note_id: UUID,
    file_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Download a file attachment from a note"""
    try:
        # Verify note exists and belongs to user
        supabase = get_user_supabase(current_user["token"])
        note_response = supabase.table("notes").select("*").eq("id", str(note_id)).eq("user_id", current_user["user_id"]).execute()
        
        if not note_response.data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found")
        
        note = note_response.data[0]
        attachments = note.get("attachments", [])
        
        # Find the file by filename or index
        try:
            file_index = int(file_id)
            if file_index >= len(attachments):
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found")
            attachment = attachments[file_index]
        except ValueError:
            # Search by filename
            attachment = next((att for att in attachments if att.get("filename") == file_id), None)
            if not attachment:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found")
        
        file_path = Path(attachment["local_path"])
        
        if not file_path.exists():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found on server")
        
        return FileResponse(
            path=str(file_path),
            filename=attachment["filename"],
            media_type=attachment.get("mime_type", "application/octet-stream")
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.delete("/{note_id}/files/{file_id}")
async def delete_file_from_note(
    note_id: UUID,
    file_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Delete a file attachment from a note"""
    try:
        # Verify note exists and belongs to user
        supabase = get_user_supabase(current_user["token"])
        note_response = supabase.table("notes").select("*").eq("id", str(note_id)).eq("user_id", current_user["user_id"]).execute()
        
        if not note_response.data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found")
        
        note = note_response.data[0]
        attachments = note.get("attachments", [])
        
        # Find the file
        try:
            file_index = int(file_id)
            if file_index >= len(attachments):
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found")
            attachment = attachments[file_index]
        except ValueError:
            # Search by filename
            attachment = next((att for att in attachments if att.get("filename") == file_id), None)
            if not attachment:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found")
        
        # Remove file from filesystem
        file_path = Path(attachment["local_path"])
        if file_path.exists():
            file_path.unlink()
        
        # Remove from attachments list
        new_attachments = [att for att in attachments if att != attachment]
        
        # Update note in database
        update_response = supabase.table("notes").update({
            "attachments": new_attachments,
            "updated_at": "now()"
        }).eq("id", str(note_id)).eq("user_id", current_user["user_id"]).execute()
        
        if update_response.data:
            return {"message": "File deleted successfully"}
        else:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to update note")
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.get("/{note_id}/files")
async def list_note_files(
    note_id: UUID,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """List all file attachments for a note"""
    try:
        # Verify note exists and belongs to user
        supabase = get_user_supabase(current_user["token"])
        note_response = supabase.table("notes").select("*").eq("id", str(note_id)).eq("user_id", current_user["user_id"]).execute()
        
        if not note_response.data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found")
        
        note = note_response.data[0]
        attachments = note.get("attachments", [])
        
        # Return file info without local paths
        file_list = []
        for i, attachment in enumerate(attachments):
            file_info = {
                "id": i,
                "filename": attachment.get("filename"),
                "type": attachment.get("type"),
                "size": attachment.get("size"),
                "mime_type": attachment.get("mime_type"),
                "uploaded_at": attachment.get("uploaded_at")
            }
            file_list.append(file_info)
        
        return {"files": file_list}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
