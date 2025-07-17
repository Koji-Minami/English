from typing import Dict, Optional, List, Any
from app.config.settings import get_settings
import uuid
from loguru import logger

class SessionManagerService:
    _instance = None
    _sessions: Dict[str, List[List[str]]] = {}
    _analysis_results: Dict[str, Dict[str, Any]] = {}
    _webpage_data: Dict[str, Dict[str, str]] = {}  # セッションごとのWebページデータ
    _conversation_ids: Dict[str, int] = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def create_session(self) -> str:
        try:
            session_id = str(uuid.uuid4())
            self._sessions[session_id] = []
            self._analysis_results[session_id] = {}
            self._webpage_data[session_id] = {}
            logger.debug(f"Created session: {session_id}")
            return session_id
        except Exception as e:
            logger.error(f"Failed to create session: {e}")
            raise

    def get_history(self, session_id: str) -> List[List[str]]:
        try:
            if self._sessions.get(session_id, []) == []:
                return ""
            else:
                return self._sessions.get(session_id, [])
        except Exception as e:
            logger.error(f"Failed to get history: {e}")
            return []

    def add_to_history(self, session_id: str, content: List[str]) -> None:
        try:
            if session_id in self._sessions:
                self._sessions[session_id].append(content)
                logger.debug(f"Added to history for session: {session_id}")
        except Exception as e:
            logger.error(f"Failed to add to history: {e}")
            raise

    def save_analysis_result(self, session_id: str, conversation_id: str, transcription: str, analysis_result: Dict[str, Any]) -> None:
        """
        文法分析結果をセッションに保存するメソッド
        
        Args:
            session_id (str): セッションID
            conversation_id (str): 会話ID
            transcription (str): 書き起こしテキスト
            analysis_result (Dict[str, Any]): 文法分析結果
        """
        try:
            if session_id in self._analysis_results:
                # conversation_idをキーとして使用し、transcriptionとanalysis_resultを含む辞書を保存
                self._analysis_results[session_id][conversation_id] = {
                    "transcription": transcription,
                    "analysis_result": analysis_result
                }
                logger.debug(f"Saved analysis result for session: {session_id}, conversation_id: {conversation_id}, transcription: {transcription[:50]}...")
                print(self._analysis_results)
        except Exception as e:
            logger.error(f"Failed to save analysis result: {e}")
            raise

    def get_analysis_result(self, session_id: str, conversation_id: str) -> Optional[Dict[str, Any]]:
        """
        指定された会話IDの文法分析結果を取得するメソッド
        
        Args:
            session_id (str): セッションID
            conversation_id (str): 会話ID
            
        Returns:
            Optional[Dict[str, Any]]: 文法分析結果（存在しない場合はNone）
        """
        try:
            if session_id in self._analysis_results:
                conversation_data = self._analysis_results[session_id].get(conversation_id)
                print(f"conversation_data: {conversation_data}")
                if conversation_data:
                    print(f"conversation_data: {conversation_data}")
                    return conversation_data.get("analysis_result")
            return None
        except Exception as e:
            logger.error(f"Failed to get analysis result: {e}")
            return None

    def get_all_analysis_results(self, session_id: str) -> Dict[str, Any]:
        """
        セッションの全ての文法分析結果を取得するメソッド
        
        Args:
            session_id (str): セッションID
            
        Returns:
            Dict[str, Any]: 全ての文法分析結果（conversation_idをキーとした辞書）
        """
        try:
            if session_id in self._analysis_results:
                return self._analysis_results[session_id]
            return {}
        except Exception as e:
            logger.error(f"Failed to get all analysis results: {e}")
            return {}

    def delete_session(self, session_id: str) -> None:
        try:
            if session_id in self._sessions:
                del self._sessions[session_id]
                logger.debug(f"Deleted session: {session_id}")
            else:
                logger.warning(f"Session {session_id} not found")
                
            if session_id in self._analysis_results:
                del self._analysis_results[session_id]
                logger.debug(f"Deleted analysis results for session: {session_id}")
                
            if session_id in self._webpage_data:
                del self._webpage_data[session_id]
                logger.debug(f"Deleted webpage data for session: {session_id}")
        except Exception as e:
            logger.error(f"Failed to delete session: {e}")
            raise

    def save_webpage_data(self, session_id: str, webpage_data: Dict[str, str]) -> None:
        """
        Webページデータをセッションに保存するメソッド
        
        Args:
            session_id (str): セッションID
            webpage_data (Dict[str, str]): Webページデータ（url, title, content）
        """
        try:
            if session_id in self._webpage_data:
                self._webpage_data[session_id] = webpage_data
                logger.debug(f"Saved webpage data for session: {session_id}, url: {webpage_data.get('url', 'unknown')}")
        except Exception as e:
            logger.error(f"Failed to save webpage data: {e}")
            raise

    def get_webpage_data(self, session_id: str) -> Optional[Dict[str, str]]:
        """
        セッションのWebページデータを取得するメソッド
        
        Args:
            session_id (str): セッションID
            
        Returns:
            Optional[Dict[str, str]]: Webページデータ（存在しない場合はNone）
        """
        try:
            if session_id in self._webpage_data:
                return self._webpage_data[session_id]
            return None
        except Exception as e:
            logger.error(f"Failed to get webpage data: {e}")
            return None
        
    def get_next_conversation_id(self, session_id: str) -> str:
        try:
            if session_id not in self._conversation_ids:
                self._conversation_ids[session_id] = 0
            self._conversation_ids[session_id] += 1
            conversation_id = str(self._conversation_ids[session_id])
            logger.info(f"Generated conversation_id: {conversation_id} for session: {session_id}")
            return conversation_id
        except Exception as e:
            logger.error(f"Failed to get next conversation id: {e}")
            return None


class SessionManagerServiceFactory:
    _instance = None

    @classmethod

    def create(cls) -> SessionManagerService:
        if cls._instance is None:
            cls._instance = SessionManagerService()
        return cls._instance