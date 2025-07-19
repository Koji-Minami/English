from typing import Dict, Optional, List, Any
from app.config.settings import get_settings
from app.services.database_service import DatabaseService
from app.config.database import get_async_db
from loguru import logger
import uuid


class PostgresSessionManagerService:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    async def create_session(self, title: str = "New Session", name: Optional[str] = None, url: Optional[str] = None) -> str:
        """新しいセッションを作成"""
        try:
            async for db in get_async_db():
                db_service = DatabaseService(db)
                session = await db_service.create_session(title=title, name=name, url=url)
                logger.debug(f"Created session: {session.id}")
                return str(session.id)
        except Exception as e:
            logger.error(f"Failed to create session: {e}")
            raise

    async def get_history(self, session_id: str) -> List[List[str]]:
        """セッションの会話履歴を取得（従来の形式に変換）"""
        try:
            async for db in get_async_db():
                db_service = DatabaseService(db)
                conversations = await db_service.get_conversations(session_id)
                
                # 従来の形式に変換
                history = []
                for conv in conversations:
                    if conv.transcription:
                        history.append([f'"user":{conv.transcription}', f'"model":""'])
                
                return history if history else ""
        except Exception as e:
            logger.error(f"Failed to get history: {e}")
            return []

    async def add_to_history(self, session_id: str, content: List[str]) -> None:
        """会話履歴に追加（従来の形式から変換）"""
        try:
            async for db in get_async_db():
                db_service = DatabaseService(db)
                
                # 従来の形式からtranscriptionを抽出
                transcription = ""
                for item in content:
                    if item.startswith('"user":'):
                        transcription = item.replace('"user":', '').strip()
                        break
                
                if transcription:
                    conversation_number = await db_service.get_next_conversation_number(session_id)
                    await db_service.create_conversation(
                        session_id=session_id,
                        conversation_number=conversation_number,
                        transcription=transcription,
                        analysis_type="transcript"
                    )
                    logger.debug(f"Added to history for session: {session_id}")
        except Exception as e:
            logger.error(f"Failed to add to history: {e}")
            raise

    async def save_analysis_result(
        self, 
        session_id: str, 
        conversation_id: str, 
        transcription: str, 
        analysis_result: Dict[str, Any]
    ) -> None:
        """文法分析結果を保存"""
        try:
            async for db in get_async_db():
                db_service = DatabaseService(db)
                
                # conversation_idが数値の場合は、その番号の会話を更新
                try:
                    conv_number = int(conversation_id)
                    conversations = await db_service.get_conversations(session_id)
                    target_conversation = None
                    
                    for conv in conversations:
                        if conv.conversation_number == conv_number:
                            target_conversation = conv
                            break
                    
                    if target_conversation:
                        await db_service.update_conversation_analysis(
                            conversation_id=str(target_conversation.id),
                            analysis_result=analysis_result
                        )
                        logger.debug(f"Saved analysis result for session: {session_id}, conversation_id: {conversation_id}")
                    else:
                        # 会話が存在しない場合は新規作成
                        await db_service.create_conversation(
                            session_id=session_id,
                            conversation_number=conv_number,
                            transcription=transcription,
                            analysis_type="audio" if "advice" in analysis_result else "transcript",
                            analysis_result=analysis_result
                        )
                        logger.debug(f"Created conversation with analysis for session: {session_id}, conversation_id: {conversation_id}")
                        
                except ValueError:
                    # conversation_idがUUIDの場合は直接更新
                    await db_service.update_conversation_analysis(
                        conversation_id=conversation_id,
                        analysis_result=analysis_result
                    )
                    logger.debug(f"Saved analysis result for session: {session_id}, conversation_id: {conversation_id}")
                    
        except Exception as e:
            logger.error(f"Failed to save analysis result: {e}")
            raise

    async def get_analysis_result(self, session_id: str, conversation_id: str) -> Optional[Dict[str, Any]]:
        """指定された会話IDの文法分析結果を取得"""
        try:
            async for db in get_async_db():
                db_service = DatabaseService(db)
                
                # conversation_idが数値の場合は、その番号の会話を検索
                try:
                    conv_number = int(conversation_id)
                    conversations = await db_service.get_conversations(session_id)
                    
                    for conv in conversations:
                        if conv.conversation_number == conv_number:
                            return {
                                "advice": conv.advice,
                                "speechflaws": conv.speechflaws,
                                "nuanceinquiry": conv.nuanceinquiry,
                                "alternativeexpressions": conv.alternativeexpressions,
                                "suggestion": conv.suggestion
                            }
                    return None
                    
                except ValueError:
                    # conversation_idがUUIDの場合は直接取得
                    conversation = await db_service.get_conversation(conversation_id)
                    if conversation:
                        return {
                            "advice": conversation.advice,
                            "speechflaws": conversation.speechflaws,
                            "nuanceinquiry": conversation.nuanceinquiry,
                            "alternativeexpressions": conversation.alternativeexpressions,
                            "suggestion": conversation.suggestion
                        }
                    return None
                    
        except Exception as e:
            logger.error(f"Failed to get analysis result: {e}")
            return None

    async def get_all_analysis_results(self, session_id: str) -> Dict[str, Any]:
        """セッションの全ての文法分析結果を取得"""
        try:
            async for db in get_async_db():
                db_service = DatabaseService(db)
                conversations = await db_service.get_conversations(session_id)
                
                results = {}
                for conv in conversations:
                    results[str(conv.conversation_number)] = {
                        "transcription": conv.transcription,
                        "analysis_result": {
                            "advice": conv.advice,
                            "speechflaws": conv.speechflaws,
                            "nuanceinquiry": conv.nuanceinquiry,
                            "alternativeexpressions": conv.alternativeexpressions,
                            "suggestion": conv.suggestion
                        }
                    }
                return results
        except Exception as e:
            logger.error(f"Failed to get all analysis results: {e}")
            return {}

    async def delete_session(self, session_id: str) -> None:
        """セッションを削除"""
        try:
            async for db in get_async_db():
                db_service = DatabaseService(db)
                success = await db_service.delete_session(session_id)
                if success:
                    logger.debug(f"Deleted session: {session_id}")
                else:
                    logger.warning(f"Session {session_id} not found")
        except Exception as e:
            logger.error(f"Failed to delete session: {e}")
            raise

    async def save_webpage_data(self, session_id: str, webpage_data: Dict[str, str]) -> None:
        """Webページデータをセッションに保存"""
        try:
            async for db in get_async_db():
                db_service = DatabaseService(db)
                success = await db_service.update_session(
                    session_id=session_id,
                    url=webpage_data.get('url')
                )
                if success:
                    logger.debug(f"Saved webpage data for session: {session_id}, url: {webpage_data.get('url', 'unknown')}")
        except Exception as e:
            logger.error(f"Failed to save webpage data: {e}")
            raise

    async def get_webpage_data(self, session_id: str) -> Optional[Dict[str, str]]:
        """セッションのWebページデータを取得"""
        try:
            async for db in get_async_db():
                db_service = DatabaseService(db)
                session = await db_service.get_session(session_id)
                if session and session.url:
                    return {"url": session.url}
                return None
        except Exception as e:
            logger.error(f"Failed to get webpage data: {e}")
            return None

    async def get_next_conversation_id(self, session_id: str) -> str:
        """次の会話IDを取得"""
        try:
            async for db in get_async_db():
                db_service = DatabaseService(db)
                next_number = await db_service.get_next_conversation_number(session_id)
                conversation_id = str(next_number)
                logger.info(f"Generated conversation_id: {conversation_id} for session: {session_id}")
                return conversation_id
        except Exception as e:
            logger.error(f"Failed to get next conversation id: {e}")
            return "1"


class PostgresSessionManagerServiceFactory:
    _instance = None

    @classmethod
    def create(cls) -> PostgresSessionManagerService:
        if cls._instance is None:
            cls._instance = PostgresSessionManagerService()
        return cls._instance 