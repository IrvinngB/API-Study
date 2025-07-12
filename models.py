from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from uuid import UUID

# User Models
class UserProfile(BaseModel):
    id: UUID
    email: str
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None
    timezone: str = "America/Panama"
    subscription_tier: str = "free"
    preferences: Dict[str, Any] = {}
    created_at: datetime
    updated_at: datetime

class UserProfileCreate(BaseModel):
    email: str
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None
    timezone: str = "America/Panama"
    preferences: Dict[str, Any] = {}

class UserProfileUpdate(BaseModel):
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None
    timezone: Optional[str] = None
    preferences: Optional[Dict[str, Any]] = None

# Class Models
class ClassBase(BaseModel):
    name: str
    code: Optional[str] = None
    instructor: Optional[str] = None
    color: str = "#3B82F6"
    credits: Optional[int] = None
    semester: Optional[str] = None
    description: Optional[str] = None
    syllabus_url: Optional[str] = None
    is_active: bool = True

class ClassCreate(ClassBase):
    pass

class ClassUpdate(BaseModel):
    name: Optional[str] = None
    code: Optional[str] = None
    instructor: Optional[str] = None
    color: Optional[str] = None
    credits: Optional[int] = None
    semester: Optional[str] = None
    description: Optional[str] = None
    syllabus_url: Optional[str] = None
    is_active: Optional[bool] = None

class Class(ClassBase):
    id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: datetime

# Task Models
class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    due_date: Optional[datetime] = None
    priority: int = Field(default=2, ge=1, le=3)
    status: str = "pending"
    estimated_duration: Optional[int] = None
    completion_percentage: int = Field(default=0, ge=0, le=100)
    tags: List[str] = []

class TaskCreate(TaskBase):
    class_id: Optional[UUID] = None
    device_created: Optional[str] = None

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    due_date: Optional[datetime] = None
    priority: Optional[int] = Field(None, ge=1, le=3)
    status: Optional[str] = None
    estimated_duration: Optional[int] = None
    completion_percentage: Optional[int] = Field(None, ge=0, le=100)
    tags: Optional[List[str]] = None
    completed_at: Optional[datetime] = None

class Task(TaskBase):
    id: UUID
    user_id: UUID
    class_id: Optional[UUID] = None
    device_created: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None

# Calendar Event Models
class CalendarEventBase(BaseModel):
    title: str
    description: Optional[str] = None
    start_datetime: datetime
    end_datetime: datetime
    event_type: str = "class"
    is_recurring: bool = False
    recurrence_pattern: Dict[str, Any] = {}
    location: Optional[str] = None
    reminder_minutes: int = 15

class CalendarEventCreate(CalendarEventBase):
    class_id: Optional[UUID] = None

class CalendarEventUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    start_datetime: Optional[datetime] = None
    end_datetime: Optional[datetime] = None
    event_type: Optional[str] = None
    is_recurring: Optional[bool] = None
    recurrence_pattern: Optional[Dict[str, Any]] = None
    location: Optional[str] = None
    reminder_minutes: Optional[int] = None

class CalendarEvent(CalendarEventBase):
    id: UUID
    user_id: UUID
    class_id: Optional[UUID] = None
    google_calendar_id: Optional[str] = None
    external_calendar_sync: Dict[str, Any] = {}
    created_at: datetime
    updated_at: datetime

# Note Models
class NoteBase(BaseModel):
    title: str
    content: str
    ai_summary: Optional[str] = None
    lesson_date: Optional[date] = None
    tags: List[str] = []
    local_files_path: str = "StudyFiles"
    attachments: List[Dict[str, Any]] = []
    is_favorite: bool = False

class NoteCreate(NoteBase):
    class_id: UUID

class NoteUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    ai_summary: Optional[str] = None
    lesson_date: Optional[date] = None
    tags: Optional[List[str]] = None
    local_files_path: Optional[str] = None
    attachments: Optional[List[Dict[str, Any]]] = None
    is_favorite: Optional[bool] = None

class Note(NoteBase):
    id: UUID
    user_id: UUID
    class_id: UUID
    last_edited: datetime
    created_at: datetime
    updated_at: datetime

class NoteVersionBase(BaseModel):
    content: str
    ai_summary: Optional[str] = None
    change_description: Optional[str] = None
    device_created: Optional[str] = None

class NoteVersionCreate(NoteVersionBase):
    pass

class NoteVersion(NoteVersionBase):
    id: UUID
    user_id: UUID
    note_id: UUID
    version_number: int
    created_at: datetime

# Sync Models
class SyncRequest(BaseModel):
    device_id: str
    last_sync: Optional[datetime] = None
    tables: List[str] = []

class SyncResponse(BaseModel):
    success: bool
    last_sync: datetime
    data: Dict[str, List[Dict[str, Any]]]
    conflicts: List[Dict[str, Any]] = []

# Analytics Models
class ProductivityMetrics(BaseModel):
    metric_date: date
    total_study_minutes: int = 0
    tasks_completed: int = 0
    tasks_created: int = 0
    classes_attended: int = 0
    productivity_score: Optional[float] = None

class StudySession(BaseModel):
    id: UUID
    user_id: UUID
    class_id: Optional[UUID] = None
    task_id: Optional[UUID] = None
    session_date: date
    total_duration_minutes: int
    session_count: int = 1
    average_productivity: Optional[float] = None
    session_type: str = "study"
    device_id: Optional[str] = None
    created_at: datetime


# --------- Grade Type Models ---------

class GradeTypeBase(BaseModel):
    name: str
    description: Optional[str] = None

class GradeTypeCreate(GradeTypeBase):
    pass

class GradeTypeUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None

class GradeType(GradeTypeBase):
    id: UUID
    user_id: UUID
    created_at: datetime

# --------- Grade Models ---------

class GradeBase(BaseModel):
    class_id: UUID
    grade_type_id: UUID
    title: Optional[str] = None
    score: float = Field(..., ge=0)
    max_score: float = Field(default=100, ge=0)
    weight: Optional[float] = Field(None, ge=0, le=100)
    graded_at: Optional[datetime] = None
    notes: Optional[str] = None

class GradeCreate(GradeBase):
    pass

class GradeUpdate(BaseModel):
    class_id: Optional[UUID] = None
    grade_type_id: Optional[UUID] = None
    title: Optional[str] = None
    score: Optional[float] = Field(None, ge=0)
    max_score: Optional[float] = Field(None, ge=0)
    weight: Optional[float] = Field(None, ge=0, le=100)
    graded_at: Optional[datetime] = None
    notes: Optional[str] = None

class Grade(GradeBase):
    id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: datetime