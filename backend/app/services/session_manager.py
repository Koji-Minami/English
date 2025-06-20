from typing import Dict, Optional, List
from app.config.settings import get_settings
import uuid
from loguru import logger

class SessionManagerService:
    _instance = None
    _sessions: Dict[str, List[List[str]]] = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def create_session(self) -> str:
        try:
            session_id = str(uuid.uuid4())
            self._sessions[session_id] = []
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

    def delete_session(self, session_id: str) -> None:
        try:
            if session_id in self._sessions:
                del self._sessions[session_id]
                logger.debug(f"Deleted session: {session_id}")
            else:
                logger.warning(f"Session {session_id} not found")
        except Exception as e:
            logger.error(f"Failed to delete session: {e}")
            raise


class SessionManagerServiceFactory:
    _instance = None

    @classmethod
    def create(cls) -> SessionManagerService:
        if cls._instance is None:
            cls._instance = SessionManagerService()
        return cls._instance