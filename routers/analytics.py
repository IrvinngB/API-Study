from fastapi import APIRouter, HTTPException, status, Depends, Query
from database import get_user_supabase
from models import ProductivityMetrics, StudySession
from auth_middleware import get_current_user
from typing import Dict, Any, List, Optional
from datetime import date, datetime, timedelta

router = APIRouter()

@router.get("/productivity", response_model=List[ProductivityMetrics])
async def get_productivity_metrics(
    current_user: Dict[str, Any] = Depends(get_current_user),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    days: int = Query(30, le=365)
):
    """Get productivity metrics for the current user"""
    try:
        supabase = get_user_supabase(current_user["token"])
        
        if not start_date:
            start_date = date.today() - timedelta(days=days)
        if not end_date:
            end_date = date.today()
        
        response = supabase.table("productivity_metrics").select("*").eq("user_id", current_user["user_id"]).gte("metric_date", start_date.isoformat()).lte("metric_date", end_date.isoformat()).order("metric_date", desc=True).execute()
        
        return response.data
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/study-sessions", response_model=List[StudySession])
async def get_study_sessions(
    current_user: Dict[str, Any] = Depends(get_current_user),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    days: int = Query(30, le=365)
):
    """Get study sessions for the current user"""
    try:
        supabase = get_user_supabase(current_user["token"])
        
        if not start_date:
            start_date = date.today() - timedelta(days=days)
        if not end_date:
            end_date = date.today()
        
        response = supabase.table("study_sessions").select("*").eq("user_id", current_user["user_id"]).gte("session_date", start_date.isoformat()).lte("session_date", end_date.isoformat()).order("session_date", desc=True).execute()
        
        return response.data
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/dashboard")
async def get_dashboard_data(
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get dashboard analytics data"""
    try:
        supabase = get_user_supabase(current_user["token"])
        
        today = date.today()
        week_ago = today - timedelta(days=7)
        month_ago = today - timedelta(days=30)
        
        # Get tasks statistics
        tasks_response = supabase.table("tasks").select("status, created_at, completed_at").eq("user_id", current_user["user_id"]).execute()
        
        tasks_data = tasks_response.data
        total_tasks = len(tasks_data)
        completed_tasks = len([t for t in tasks_data if t["status"] == "completed"])
        pending_tasks = len([t for t in tasks_data if t["status"] == "pending"])
        
        # Tasks created this week
        tasks_this_week = len([
            t for t in tasks_data 
            if datetime.fromisoformat(t["created_at"].replace('Z', '+00:00')).date() >= week_ago
        ])
        
        # Tasks completed this week
        completed_this_week = len([
            t for t in tasks_data 
            if t["completed_at"] and datetime.fromisoformat(t["completed_at"].replace('Z', '+00:00')).date() >= week_ago
        ])
        
        # Get habits statistics
        habits_response = supabase.table("habits").select("id, name").eq("user_id", current_user["user_id"]).eq("is_active", True).execute()
        
        active_habits = len(habits_response.data)
        
        # Get habit logs for this week
        habit_logs_response = supabase.table("habit_logs").select("habit_id, completed_date").eq("user_id", current_user["user_id"]).gte("completed_date", week_ago.isoformat()).execute()
        
        habit_completions_this_week = len(habit_logs_response.data)
        
        # Get study sessions for this month
        study_sessions_response = supabase.table("study_sessions").select("total_duration_minutes, session_date").eq("user_id", current_user["user_id"]).gte("session_date", month_ago.isoformat()).execute()
        
        total_study_time = sum(session["total_duration_minutes"] for session in study_sessions_response.data)
        
        # Get upcoming events (next 7 days)
        upcoming_events_response = supabase.table("calendar_events").select("title, start_datetime, event_type").eq("user_id", current_user["user_id"]).gte("start_datetime", today.isoformat()).lte("start_datetime", (today + timedelta(days=7)).isoformat()).order("start_datetime").limit(5).execute()
        
        return {
            "tasks": {
                "total": total_tasks,
                "completed": completed_tasks,
                "pending": pending_tasks,
                "created_this_week": tasks_this_week,
                "completed_this_week": completed_this_week,
                "completion_rate": round((completed_tasks / total_tasks * 100) if total_tasks > 0 else 0, 1)
            },
            "habits": {
                "active_habits": active_habits,
                "completions_this_week": habit_completions_this_week,
                "average_per_day": round(habit_completions_this_week / 7, 1)
            },
            "study_time": {
                "total_minutes_this_month": total_study_time,
                "total_hours_this_month": round(total_study_time / 60, 1),
                "average_per_day": round(total_study_time / 30, 1)
            },
            "upcoming_events": upcoming_events_response.data
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/study-session")
async def create_study_session(
    class_id: Optional[str] = None,
    task_id: Optional[str] = None,
    duration_minutes: int = 0,
    session_type: str = "study",
    productivity_rating: Optional[float] = None,
    device_id: Optional[str] = None,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Create a new study session record"""
    try:
        supabase = get_user_supabase(current_user["token"])
        
        session_data = {
            "user_id": current_user["user_id"],
            "class_id": class_id,
            "task_id": task_id,
            "session_date": date.today().isoformat(),
            "total_duration_minutes": duration_minutes,
            "session_count": 1,
            "average_productivity": productivity_rating,
            "session_type": session_type,
            "device_id": device_id
        }
        
        response = supabase.table("study_sessions").insert(session_data).execute()
        
        if response.data:
            return {"message": "Study session recorded successfully", "session": response.data[0]}
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to create study session"
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
