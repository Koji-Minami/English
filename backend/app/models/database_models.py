from sqlalchemy import Column, String, Integer, DateTime, Text, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.config.database import Base
import uuid


class Session(Base):
    __tablename__ = "sessions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=True)  # ユーザー名（シンプルな文字列）
    title = Column(Text, nullable=False)
    url = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # リレーションシップ
    conversations = relationship("Conversation", back_populates="session", cascade="all, delete-orphan")


class Conversation(Base):
    __tablename__ = "conversations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey("sessions.id"), nullable=False)
    conversation_number = Column(Integer, nullable=False)
    transcription = Column(Text, nullable=True)
    analysis_type = Column(String(20), nullable=False)  # 'transcript' or 'audio'
    
    # 分析結果のカラム
    advice = Column(Text, nullable=True)  # 音声分析用
    speechflaws = Column(Text, nullable=True)
    nuanceinquiry = Column(JSONB, nullable=True)  # list[string]
    alternativeexpressions = Column(JSONB, nullable=True)  # list[list[string, string]]
    suggestion = Column(JSONB, nullable=True)  # list[string], 音声分析用
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # リレーションシップ
    session = relationship("Session", back_populates="conversations") 