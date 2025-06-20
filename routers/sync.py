from fastapi import APIRouter, HTTPException, status, Depends
from database import get_user_supabase
from models import SyncRequest, SyncResponse
from auth_middleware import get_current_user
from typing import Dict, Any, List
from datetime import datetime

router = APIRouter()

@router.post("/pull", response_model=SyncResponse)
async def pull_data(
    sync_request: SyncRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Pull data from server for synchronization"""
    try:
        supabase = get_user_supabase(current_user["token"])
        
        # Register or update device
        device_data = {
            "user_id": current_user["user_id"],
            "device_id": sync_request.device_id,
            "last_sync": datetime.utcnow().isoformat(),
            "is_active": True
        }
        
        supabase.table("user_devices").upsert(device_data, on_conflict="user_id,device_id").execute()
        
        sync_data = {}
        tables_to_sync = sync_request.tables or ["classes", "tasks", "calendar_events", "habits", "habit_logs"]
        
        for table in tables_to_sync:
            query = supabase.table(table).select("*").eq("user_id", current_user["user_id"])
            
            if sync_request.last_sync:
                query = query.gte("updated_at", sync_request.last_sync.isoformat())
                
            response = query.execute()
            sync_data[table] = response.data
        
        # Log sync operation
        log_data = {
            "user_id": current_user["user_id"],
            "device_id": sync_request.device_id,
            "table_name": "multiple",
            "operation": "pull",
            "records_count": sum(len(data) for data in sync_data.values()),
            "success": True
        }
        supabase.table("sync_logs").insert(log_data).execute()
        
        return SyncResponse(
            success=True,
            last_sync=datetime.utcnow(),
            data=sync_data
        )
        
    except Exception as e:
        # Log failed sync
        try:
            log_data = {
                "user_id": current_user["user_id"],
                "device_id": sync_request.device_id,
                "table_name": "multiple",
                "operation": "pull",
                "records_count": 0,
                "success": False,
                "error_message": str(e)
            }
            supabase.table("sync_logs").insert(log_data).execute()
        except:
            pass
            
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/push")
async def push_data(
    table_name: str,
    records: List[Dict[str, Any]],
    device_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Push data to server for synchronization"""
    try:
        supabase = get_user_supabase(current_user["token"])
        
        # Validate table name
        allowed_tables = ["classes", "tasks", "calendar_events", "habits", "habit_logs"]
        if table_name not in allowed_tables:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Table {table_name} not allowed for sync"
            )
        
        # Add user_id to all records
        for record in records:
            record["user_id"] = current_user["user_id"]
            record["updated_at"] = datetime.utcnow().isoformat()
        
        # Upsert records
        response = supabase.table(table_name).upsert(records).execute()
        
        # Log sync operation
        log_data = {
            "user_id": current_user["user_id"],
            "device_id": device_id,
            "table_name": table_name,
            "operation": "push",
            "records_count": len(records),
            "success": True
        }
        supabase.table("sync_logs").insert(log_data).execute()
        
        return {
            "success": True,
            "message": f"Successfully synced {len(records)} records to {table_name}",
            "synced_records": len(response.data) if response.data else 0
        }
        
    except Exception as e:
        # Log failed sync
        try:
            log_data = {
                "user_id": current_user["user_id"],
                "device_id": device_id,
                "table_name": table_name,
                "operation": "push",
                "records_count": len(records),
                "success": False,
                "error_message": str(e)
            }
            supabase.table("sync_logs").insert(log_data).execute()
        except:
            pass
            
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/status")
async def get_sync_status(
    device_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get synchronization status for a device"""
    try:
        supabase = get_user_supabase(current_user["token"])
        
        # Get device info
        device_response = supabase.table("user_devices").select("*").eq("user_id", current_user["user_id"]).eq("device_id", device_id).execute()
        
        # Get recent sync logs
        logs_response = supabase.table("sync_logs").select("*").eq("user_id", current_user["user_id"]).eq("device_id", device_id).order("created_at", desc=True).limit(10).execute()
        
        return {
            "device": device_response.data[0] if device_response.data else None,
            "recent_syncs": logs_response.data,
            "last_sync": device_response.data[0]["last_sync"] if device_response.data else None
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
