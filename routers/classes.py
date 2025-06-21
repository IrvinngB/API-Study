from fastapi import APIRouter, HTTPException, status, Depends
from database import get_user_supabase
from models import Class, ClassCreate, ClassUpdate
from auth_middleware import get_current_user
from typing import List, Dict, Any
from uuid import UUID

router = APIRouter()

@router.get("/", response_model=List[Class])
async def get_classes(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Get all classes for the current user"""
    try:
        supabase = get_user_supabase(current_user["token"])
        response = supabase.table("classes").select("*").eq("user_id", current_user["user_id"]).execute()
        
        return response.data
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/", response_model=Class)
async def create_class(
    class_data: ClassCreate,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Create a new class"""
    try:
        print(f"🎓 Creating class for user: {current_user['user_id']}")
        print(f"📋 Class data: {class_data.dict()}")
        
        # Use service client for database operations since user is already authenticated
        from database import get_supabase_service
        supabase = get_supabase_service()
        
        insert_data = class_data.dict()
        insert_data["user_id"] = current_user["user_id"]
        
        print(f"💾 Inserting data: {insert_data}")
        
        response = supabase.table("classes").insert(insert_data).execute()
        
        print(f"📊 Supabase response: {response}")
        
        if response.data:
            print(f"✅ Class created successfully: {response.data[0]}")
            return response.data[0]
        else:
            print("❌ No data returned from Supabase")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to create class"
            )
            
    except Exception as e:
        print(f"❌ Error creating class: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/{class_id}", response_model=Class)
async def get_class(
    class_id: UUID,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get a specific class"""
    try:
        supabase = get_user_supabase(current_user["token"])
        response = supabase.table("classes").select("*").eq("id", str(class_id)).eq("user_id", current_user["user_id"]).execute()
        
        if response.data:
            return response.data[0]
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Class not found"
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.put("/{class_id}", response_model=Class)
async def update_class(
    class_id: UUID,
    class_update: ClassUpdate,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Update a class"""
    try:
        supabase = get_user_supabase(current_user["token"])
        
        update_data = class_update.dict(exclude_unset=True)
        update_data["updated_at"] = "now()"
        
        response = supabase.table("classes").update(update_data).eq("id", str(class_id)).eq("user_id", current_user["user_id"]).execute()
        
        if response.data:
            return response.data[0]
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Class not found"
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.delete("/{class_id}")
async def delete_class(
    class_id: UUID,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Delete a class"""
    try:
        supabase = get_user_supabase(current_user["token"])
        response = supabase.table("classes").delete().eq("id", str(class_id)).eq("user_id", current_user["user_id"]).execute()
        
        if response.data:
            return {"message": "Class deleted successfully"}
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Class not found"
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
