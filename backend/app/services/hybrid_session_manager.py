"""
ハイブリッドセッション管理サービス

メモリとデータベースを並行して管理し、段階的な移行を可能にする
"""

from typing import Dict, Optional, List, Any
from app.config.settings import get_settings
from app.services.session_manager import SessionManagerService
from app.services.postgres_session_manager import PostgresSessionManagerService
import uuid
from loguru import logger


class HybridSessionManagerService:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, '_initialized'):
            self._memory_manager = SessionManagerService()
            self._db_manager = PostgresSessionManagerService()
            self._use_database = True  # データベース使用フラグ
            self._initialized = True
            logger.info("HybridSessionManagerService initialized")
    
    async def create_session(self, title: str = "New Session", name: Optional[str] = None, url: Optional[str] = None) -> str:
        """セッションを作成（メモリとデータベースの両方に保存）"""
        try:
            # メモリに作成
            memory_session_id = self._memory_manager.create_session()
            
            # データベースにも作成
            if self._use_database:
                db_session_id = await self._db_manager.create_session(title, name, url)
                logger.info(f"Created session in both memory ({memory_session_id}) and database ({db_session_id})")
                return db_session_id  # データベースのIDを返す
            else:
                logger.info(f"Created session in memory only: {memory_session_id}")
                return memory_session_id
                
        except Exception as e:
            logger.error(f"Failed to create session: {e}")
            # データベースが失敗した場合はメモリのみを使用
            if self._use_database:
                logger.warning("Falling back to memory-only session creation")
                self._use_database = False
                return self._memory_manager.create_session()
            raise
    
    async def get_history(self, session_id: str) -> List[List[str]]:
        """履歴を取得（データベース優先、フォールバックでメモリ）"""
        try:
            if self._use_database:
                try:
                    return await self._db_manager.get_history(session_id)
                except Exception as e:
                    logger.warning(f"Database get_history failed, falling back to memory: {e}")
                    self._use_database = False
            
            return self._memory_manager.get_history(session_id)
            
        except Exception as e:
            logger.error(f"Failed to get history: {e}")
            return []
    
    async def add_to_history(self, session_id: str, content: List[str]) -> None:
        """履歴を追加（メモリとデータベースの両方に保存）"""
        try:
            # メモリに追加
            self._memory_manager.add_to_history(session_id, content)
            
            # データベースにも追加
            if self._use_database:
                try:
                    await self._db_manager.add_to_history(session_id, content)
                except Exception as e:
                    logger.warning(f"Database add_to_history failed: {e}")
                    self._use_database = False
                    
        except Exception as e:
            logger.error(f"Failed to add to history: {e}")
            raise
    
    async def save_analysis_result(self, session_id: str, conversation_id: str, transcription: str, analysis_result: Dict[str, Any]) -> None:
        """分析結果を保存（メモリとデータベースの両方に保存）"""
        try:
            # メモリに保存
            self._memory_manager.save_analysis_result(session_id, conversation_id, transcription, analysis_result)
            
            # データベースにも保存
            if self._use_database:
                try:
                    await self._db_manager.save_analysis_result(session_id, conversation_id, transcription, analysis_result)
                except Exception as e:
                    logger.warning(f"Database save_analysis_result failed: {e}")
                    self._use_database = False
                    
        except Exception as e:
            logger.error(f"Failed to save analysis result: {e}")
            raise
    
    async def get_analysis_result(self, session_id: str, conversation_id: str) -> Optional[Dict[str, Any]]:
        """分析結果を取得（データベース優先、フォールバックでメモリ）"""
        try:
            if self._use_database:
                try:
                    result = await self._db_manager.get_analysis_result(session_id, conversation_id)
                    if result is not None:
                        return result
                except Exception as e:
                    logger.warning(f"Database get_analysis_result failed, falling back to memory: {e}")
                    self._use_database = False
            
            return self._memory_manager.get_analysis_result(session_id, conversation_id)
            
        except Exception as e:
            logger.error(f"Failed to get analysis result: {e}")
            return None
    
    async def get_all_analysis_results(self, session_id: str) -> Dict[str, Any]:
        """全分析結果を取得（データベース優先、フォールバックでメモリ）"""
        try:
            if self._use_database:
                try:
                    return await self._db_manager.get_all_analysis_results(session_id)
                except Exception as e:
                    logger.warning(f"Database get_all_analysis_results failed, falling back to memory: {e}")
                    self._use_database = False
            
            return self._memory_manager.get_all_analysis_results(session_id)
            
        except Exception as e:
            logger.error(f"Failed to get all analysis results: {e}")
            return {}
    
    async def delete_session(self, session_id: str) -> None:
        """セッションを削除（メモリとデータベースの両方から削除）"""
        try:
            # メモリから削除
            self._memory_manager.delete_session(session_id)
            
            # データベースからも削除
            if self._use_database:
                try:
                    await self._db_manager.delete_session(session_id)
                except Exception as e:
                    logger.warning(f"Database delete_session failed: {e}")
                    self._use_database = False
                    
        except Exception as e:
            logger.error(f"Failed to delete session: {e}")
            raise
    
    async def save_webpage_data(self, session_id: str, webpage_data: Dict[str, str]) -> None:
        """Webページデータを保存（メモリとデータベースの両方に保存）"""
        try:
            # メモリに保存
            self._memory_manager.save_webpage_data(session_id, webpage_data)
            
            # データベースにも保存
            if self._use_database:
                try:
                    await self._db_manager.save_webpage_data(session_id, webpage_data)
                except Exception as e:
                    logger.warning(f"Database save_webpage_data failed: {e}")
                    self._use_database = False
                    
        except Exception as e:
            logger.error(f"Failed to save webpage data: {e}")
            raise
    
    async def get_webpage_data(self, session_id: str) -> Optional[Dict[str, str]]:
        """Webページデータを取得（データベース優先、フォールバックでメモリ）"""
        try:
            if self._use_database:
                try:
                    result = await self._db_manager.get_webpage_data(session_id)
                    if result is not None:
                        return result
                except Exception as e:
                    logger.warning(f"Database get_webpage_data failed, falling back to memory: {e}")
                    self._use_database = False
            
            return self._memory_manager.get_webpage_data(session_id)
            
        except Exception as e:
            logger.error(f"Failed to get webpage data: {e}")
            return None
    
    async def get_next_conversation_id(self, session_id: str) -> str:
        """次の会話IDを取得（データベース優先、フォールバックでメモリ）"""
        try:
            if self._use_database:
                try:
                    return await self._db_manager.get_next_conversation_id(session_id)
                except Exception as e:
                    logger.warning(f"Database get_next_conversation_id failed, falling back to memory: {e}")
                    self._use_database = False
            
            return self._memory_manager.get_next_conversation_id(session_id)
            
        except Exception as e:
            logger.error(f"Failed to get next conversation id: {e}")
            return "1"
    
    def get_status(self) -> Dict[str, Any]:
        """現在の状態を取得"""
        return {
            "use_database": self._use_database,
            "memory_sessions_count": len(self._memory_manager._sessions),
            "memory_analysis_results_count": len(self._memory_manager._analysis_results)
        }


class HybridSessionManagerServiceFactory:
    _instance = None

    @classmethod
    def create(cls) -> HybridSessionManagerService:
        if cls._instance is None:
            cls._instance = HybridSessionManagerService()
        return cls._instance 