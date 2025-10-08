from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid

class Message(BaseModel):
    """Single message in a conversation"""
    role: str  # 'user' or 'assistant'
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    model_used: Optional[str] = None

class Conversation(BaseModel):
    """Conversation document"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str = "default_user"  # For future multi-user support
    messages: List[Message] = []
    personality: str = "superintendent"  # 'tharos' or 'superintendent'
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class Memory(BaseModel):
    """Memory/context storage"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str = "default_user"
    key: str  # Memory key (e.g., 'user_name', 'preferences')
    value: Any  # Memory value
    context: Optional[str] = None  # Additional context
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class PersonalitySettings(BaseModel):
    """User personality preferences"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str = "default_user"
    current_personality: str = "superintendent"  # 'tharos' or 'superintendent'
    tharos_customization: Optional[Dict[str, Any]] = None
    superintendent_customization: Optional[Dict[str, Any]] = None
    updated_at: datetime = Field(default_factory=datetime.utcnow)

# Request/Response Models
class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None
    personality: Optional[str] = "superintendent"

class ChatResponse(BaseModel):
    success: bool
    response: Optional[str] = None
    conversation_id: str
    model_used: Optional[str] = None
    personality: str
    error: Optional[str] = None

class PersonalityToggleRequest(BaseModel):
    personality: str  # 'tharos' or 'superintendent'

class MemoryCreateRequest(BaseModel):
    key: str
    value: Any
    context: Optional[str] = None