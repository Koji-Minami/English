from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from sqlalchemy.orm import selectinload
from app.models.database_models import Session, Conversation
from app.config.database import get_async_db
from loguru import logger
import uuid


class DatabaseService:
    def __init__(self, db_session: AsyncSession):
        self.db = db_session

    async def create_session(self, title: str, name: Optional[str] = None, url: Optional[str] = None) -> Session:
        """新しいセッションを作成"""
        try:
            session = Session(
                id=uuid.uuid4(),
                title=title,
                name=name,
                url=url
            )
            self.db.add(session)
            await self.db.commit()
            await self.db.refresh(session)
            logger.debug(f"Created session: {session.id}")
            return session
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Failed to create session: {e}")
            raise

    async def get_session(self, session_id: str) -> Optional[Session]:
        """セッションを取得"""
        try:
            result = await self.db.execute(
                select(Session).where(Session.id == uuid.UUID(session_id))
            )
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Failed to get session: {e}")
            return None

    async def get_all_sessions(self, name: Optional[str] = None) -> List[Session]:
        """全てのセッションを取得"""
        try:
            query = select(Session)
            if name:
                query = query.where(Session.name == name)
            query = query.order_by(Session.updated_at.desc())
            
            result = await self.db.execute(query)
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Failed to get all sessions: {e}")
            return []

    async def update_session(self, session_id: str, title: Optional[str] = None, name: Optional[str] = None, url: Optional[str] = None) -> bool:
        """セッションを更新"""
        try:
            update_data = {}
            if title is not None:
                update_data["title"] = title
            if name is not None:
                update_data["name"] = name
            if url is not None:
                update_data["url"] = url
            
            if update_data:
                result = await self.db.execute(
                    update(Session)
                    .where(Session.id == uuid.UUID(session_id))
                    .values(**update_data)
                )
                await self.db.commit()
                return result.rowcount > 0
            return True
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Failed to update session: {e}")
            return False

    async def delete_session(self, session_id: str) -> bool:
        """セッションを削除（関連するconversationsも削除される）"""
        try:
            # まず関連するconversationsを削除
            await self.db.execute(
                delete(Conversation).where(Conversation.session_id == uuid.UUID(session_id))
            )
            
            # 次にセッションを削除
            result = await self.db.execute(
                delete(Session).where(Session.id == uuid.UUID(session_id))
            )
            await self.db.commit()
            return result.rowcount > 0
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Failed to delete session: {e}")
            return False

    async def create_conversation(
        self,
        session_id: str,
        conversation_number: int,
        transcription: Optional[str] = None,
        analysis_type: str = "transcript",
        analysis_result: Optional[Dict[str, Any]] = None
    ) -> Conversation:
        """新しい会話を作成"""
        try:
            conversation = Conversation(
                id=uuid.uuid4(),
                session_id=uuid.UUID(session_id),
                conversation_number=conversation_number,
                transcription=transcription,
                analysis_type=analysis_type,
                **self._extract_analysis_fields(analysis_result) if analysis_result else {}
            )
            self.db.add(conversation)
            await self.db.commit()
            await self.db.refresh(conversation)
            logger.debug(f"Created conversation: {conversation.id}")
            return conversation
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Failed to create conversation: {e}")
            raise

    async def get_conversations(self, session_id: str) -> List[Conversation]:
        """セッションの全ての会話を取得"""
        try:
            result = await self.db.execute(
                select(Conversation)
                .where(Conversation.session_id == uuid.UUID(session_id))
                .order_by(Conversation.conversation_number)
            )
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Failed to get conversations: {e}")
            return []

    async def get_conversation(self, conversation_id: str) -> Optional[Conversation]:
        """特定の会話を取得"""
        try:
            result = await self.db.execute(
                select(Conversation).where(Conversation.id == uuid.UUID(conversation_id))
            )
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Failed to get conversation: {e}")
            return None

    async def update_conversation_analysis(
        self,
        conversation_id: str,
        analysis_result: Dict[str, Any]
    ) -> bool:
        """会話の分析結果を更新"""
        try:
            update_data = self._extract_analysis_fields(analysis_result)
            result = await self.db.execute(
                update(Conversation)
                .where(Conversation.id == uuid.UUID(conversation_id))
                .values(**update_data)
            )
            await self.db.commit()
            return result.rowcount > 0
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Failed to update conversation analysis: {e}")
            return False

    def _extract_analysis_fields(self, analysis_result: Dict[str, Any]) -> Dict[str, Any]:
        """分析結果からデータベースフィールドを抽出"""
        fields = {}
        if "advice" in analysis_result:
            fields["advice"] = analysis_result["advice"]
        if "speechflaws" in analysis_result:
            fields["speechflaws"] = analysis_result["speechflaws"]
        if "nuanceinquiry" in analysis_result:
            fields["nuanceinquiry"] = analysis_result["nuanceinquiry"]
        if "alternativeexpressions" in analysis_result:
            fields["alternativeexpressions"] = analysis_result["alternativeexpressions"]
        if "suggestion" in analysis_result:
            fields["suggestion"] = analysis_result["suggestion"]
        return fields

    async def get_next_conversation_number(self, session_id: str) -> int:
        """次の会話番号を取得"""
        try:
            result = await self.db.execute(
                select(Conversation.conversation_number)
                .where(Conversation.session_id == uuid.UUID(session_id))
                .order_by(Conversation.conversation_number.desc())
                .limit(1)
            )
            last_number = result.scalar_one_or_none()
            return (last_number or 0) + 1
        except Exception as e:
            logger.error(f"Failed to get next conversation number: {e}")
            return 1 