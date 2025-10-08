from fastapi import FastAPI, APIRouter, HTTPException
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from datetime import datetime
from typing import List

from models import (
    ChatRequest, ChatResponse, Conversation, Message,
    PersonalitySettings, PersonalityToggleRequest,
    Memory, MemoryCreateRequest
)
from llm_router import llm_router

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI(title="SuperIntendent API")

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ============================================
# Chat Endpoints
# ============================================

@api_router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Main chat endpoint - routes to appropriate LLM based on intent
    """
    try:
        logger.info(f"Received chat request: {request.message[:50]}...")
        
        # Get or create conversation
        if request.conversation_id:
            conv_doc = await db.conversations.find_one({"id": request.conversation_id})
            if conv_doc:
                conversation = Conversation(**conv_doc)
            else:
                conversation = Conversation(personality=request.personality or "superintendent")
        else:
            conversation = Conversation(personality=request.personality or "superintendent")
        
        # Build context from conversation history
        context = [
            {"role": msg.role, "content": msg.content}
            for msg in conversation.messages[-5:]  # Last 5 messages
        ]
        
        # Route message to appropriate LLM
        result = await llm_router.route_message(
            message=request.message,
            personality=conversation.personality,
            context=context
        )
        
        if not result['success']:
            raise HTTPException(status_code=500, detail=result.get('error', 'Unknown error'))
        
        # Add user message and assistant response to conversation
        user_message = Message(role="user", content=request.message)
        assistant_message = Message(
            role="assistant",
            content=result['response'],
            model_used=result['model_used']
        )
        
        conversation.messages.append(user_message)
        conversation.messages.append(assistant_message)
        conversation.updated_at = datetime.utcnow()
        
        # Save conversation to database
        await db.conversations.update_one(
            {"id": conversation.id},
            {"$set": conversation.dict()},
            upsert=True
        )
        
        return ChatResponse(
            success=True,
            response=result['response'],
            conversation_id=conversation.id,
            model_used=result['model_used'],
            personality=conversation.personality
        )
        
    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/conversations/{conversation_id}")
async def get_conversation(conversation_id: str):
    """
    Get conversation history
    """
    try:
        conv_doc = await db.conversations.find_one({"id": conversation_id})
        if not conv_doc:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        return Conversation(**conv_doc)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting conversation: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/conversations")
async def list_conversations():
    """
    List all conversations
    """
    try:
        conversations = await db.conversations.find().sort("updated_at", -1).to_list(50)
        return [Conversation(**conv) for conv in conversations]
    except Exception as e:
        logger.error(f"Error listing conversations: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================
# Personality Endpoints
# ============================================

@api_router.post("/personality/toggle")
async def toggle_personality(request: PersonalityToggleRequest):
    """
    Toggle personality mode (Tharos <-> SuperIntendent)
    """
    try:
        if request.personality not in ['tharos', 'superintendent']:
            raise HTTPException(status_code=400, detail="Invalid personality. Must be 'tharos' or 'superintendent'")
        
        # Get or create personality settings
        settings_doc = await db.personality_settings.find_one({"user_id": "default_user"})
        
        if settings_doc:
            settings = PersonalitySettings(**settings_doc)
        else:
            settings = PersonalitySettings()
        
        settings.current_personality = request.personality
        settings.updated_at = datetime.utcnow()
        
        await db.personality_settings.update_one(
            {"user_id": "default_user"},
            {"$set": settings.dict()},
            upsert=True
        )
        
        return {
            "success": True,
            "personality": settings.current_personality,
            "message": f"Switched to {settings.current_personality.title()} mode"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error toggling personality: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/personality")
async def get_personality():
    """
    Get current personality settings
    """
    try:
        settings_doc = await db.personality_settings.find_one({"user_id": "default_user"})
        
        if settings_doc:
            return PersonalitySettings(**settings_doc)
        else:
            # Return default
            default_settings = PersonalitySettings()
            await db.personality_settings.insert_one(default_settings.dict())
            return default_settings
            
    except Exception as e:
        logger.error(f"Error getting personality: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================
# Memory Endpoints
# ============================================

@api_router.post("/memory")
async def create_memory(request: MemoryCreateRequest):
    """
    Store a memory/context item
    """
    try:
        memory = Memory(
            key=request.key,
            value=request.value,
            context=request.context
        )
        
        await db.memories.update_one(
            {"user_id": "default_user", "key": request.key},
            {"$set": memory.dict()},
            upsert=True
        )
        
        return {"success": True, "memory": memory}
        
    except Exception as e:
        logger.error(f"Error creating memory: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/memory/{key}")
async def get_memory(key: str):
    """
    Retrieve a specific memory
    """
    try:
        memory_doc = await db.memories.find_one({"user_id": "default_user", "key": key})
        
        if not memory_doc:
            raise HTTPException(status_code=404, detail="Memory not found")
        
        return Memory(**memory_doc)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting memory: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/memories")
async def list_memories():
    """
    List all memories
    """
    try:
        memories = await db.memories.find({"user_id": "default_user"}).to_list(100)
        return [Memory(**mem) for mem in memories]
    except Exception as e:
        logger.error(f"Error listing memories: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================
# Health Check
# ============================================

@api_router.get("/")
async def root():
    return {
        "message": "SuperIntendent API",
        "version": "1.0.0",
        "status": "operational"
    }

@api_router.get("/health")
async def health_check():
    """
    Health check endpoint
    """
    try:
        # Test database connection
        await db.command('ping')
        
        return {
            "status": "healthy",
            "database": "connected",
            "llm_providers": {
                "openai": bool(os.environ.get('OPENAI_API_KEY')),
                "gemini": bool(os.environ.get('GEMINI_API_KEY')),
                "deepseek": bool(os.environ.get('DEEPSEEK_API_KEY'))
            }
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()