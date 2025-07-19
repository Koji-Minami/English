from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from app.config.database import get_async_db
from app.services.database_service import DatabaseService
from app.models.schemas import (
    SessionCreate, SessionUpdate, SessionResponse, SessionListResponse,
    ConversationCreate, ConversationResponse, ConversationListResponse
)
from loguru import logger

router = APIRouter(prefix="/sessions", tags=["sessions"])


async def get_database_service(db: AsyncSession = Depends(get_async_db)) -> DatabaseService:
    return DatabaseService(db)


@router.post("/", response_model=SessionResponse)
async def create_session(
    session_data: SessionCreate,
    db_service: DatabaseService = Depends(get_database_service)
):
    """新しいセッションを作成"""
    try:
        session = await db_service.create_session(
            title=session_data.title,
            name=session_data.name,
            url=session_data.url
        )
        return SessionResponse.model_validate(session)
    except Exception as e:
        logger.error(f"Failed to create session: {e}")
        raise HTTPException(status_code=500, detail="Failed to create session")


@router.get("/", response_model=SessionListResponse)
async def get_sessions(
    name: Optional[str] = Query(None, description="ユーザー名でフィルタ"),
    db_service: DatabaseService = Depends(get_database_service)
):
    """セッション一覧を取得"""
    try:
        sessions = await db_service.get_all_sessions(name=name)
        return SessionListResponse(
            sessions=[SessionResponse.model_validate(session) for session in sessions],
            total=len(sessions)
        )
    except Exception as e:
        logger.error(f"Failed to get sessions: {e}")
        raise HTTPException(status_code=500, detail="Failed to get sessions")


@router.get("/{session_id}", response_model=SessionResponse)
async def get_session(
    session_id: str,
    db_service: DatabaseService = Depends(get_database_service)
):
    """特定のセッションを取得"""
    try:
        session = await db_service.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        return SessionResponse.model_validate(session)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get session: {e}")
        raise HTTPException(status_code=500, detail="Failed to get session")


@router.put("/{session_id}", response_model=SessionResponse)
async def update_session(
    session_id: str,
    session_data: SessionUpdate,
    db_service: DatabaseService = Depends(get_database_service)
):
    """セッションを更新"""
    try:
        success = await db_service.update_session(
            session_id=session_id,
            title=session_data.title,
            name=session_data.name,
            url=session_data.url
        )
        if not success:
            raise HTTPException(status_code=404, detail="Session not found")
        
        session = await db_service.get_session(session_id)
        return SessionResponse.model_validate(session)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update session: {e}")
        raise HTTPException(status_code=500, detail="Failed to update session")


@router.delete("/{session_id}")
async def delete_session(
    session_id: str,
    db_service: DatabaseService = Depends(get_database_service)
):
    """セッションを削除"""
    try:
        success = await db_service.delete_session(session_id)
        if not success:
            raise HTTPException(status_code=404, detail="Session not found")
        return {"message": "Session deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete session: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete session")


@router.post("/{session_id}/conversations", response_model=ConversationListResponse)
async def get_conversations(
    session_id: str,
    db_service: DatabaseService = Depends(get_database_service)
):
    """指定セッションの会話履歴を取得"""
    try:
        # セッションの存在確認
        session = await db_service.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        conversations = await db_service.get_conversations(session_id)
        return ConversationListResponse(
            conversations=[ConversationResponse.model_validate(conv) for conv in conversations],
            total=len(conversations)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get conversations: {e}")
        raise HTTPException(status_code=500, detail="Failed to get conversations")


@router.get("/{session_id}/conversations/{conversation_id}", response_model=ConversationResponse)
async def get_conversation(
    session_id: str,
    conversation_id: str,
    db_service: DatabaseService = Depends(get_database_service)
):
    """特定の会話を取得"""
    try:
        conversation = await db_service.get_conversation(conversation_id)
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        # セッションIDの一致確認
        if str(conversation.session_id) != session_id:
            raise HTTPException(status_code=404, detail="Conversation not found in this session")
        
        return ConversationResponse.model_validate(conversation)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get conversation: {e}")
        raise HTTPException(status_code=500, detail="Failed to get conversation") 