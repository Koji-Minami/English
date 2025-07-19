from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Union
from datetime import datetime
from uuid import UUID


class SessionCreate(BaseModel):
    name: Optional[str] = Field(None, description="ユーザー名")
    title: str = Field(..., description="セッションのタイトル")
    url: Optional[str] = Field(None, description="WebページのURL")


class SessionUpdate(BaseModel):
    name: Optional[str] = Field(None, description="ユーザー名")
    title: Optional[str] = Field(None, description="セッションのタイトル")
    url: Optional[str] = Field(None, description="WebページのURL")


class SessionResponse(BaseModel):
    id: UUID
    name: Optional[str]
    title: str
    url: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ConversationCreate(BaseModel):
    conversation_number: int = Field(..., description="会話番号")
    transcription: Optional[str] = Field(None, description="書き起こしテキスト")
    analysis_type: str = Field(..., description="分析タイプ（transcript/audio）")
    analysis_result: Optional[Dict[str, Any]] = Field(None, description="分析結果")


class ConversationResponse(BaseModel):
    id: UUID
    session_id: UUID
    conversation_number: int
    transcription: Optional[str]
    analysis_type: str
    advice: Optional[str] = Field(None, description="音声分析用のアドバイス")
    speechflaws: Optional[str] = Field(None, description="発話の欠点")
    nuanceinquiry: Optional[Union[List[str], str]] = Field(None, description="ニュアンスの質問")
    alternativeexpressions: Optional[Union[List[List[str]], str]] = Field(None, description="代替表現")
    suggestion: Optional[Union[List[str], str]] = Field(None, description="提案")
    created_at: datetime

    class Config:
        from_attributes = True


class SessionListResponse(BaseModel):
    sessions: List[SessionResponse] = Field(..., description="セッション一覧")
    total: int = Field(..., description="総数")


class ConversationListResponse(BaseModel):
    conversations: List[ConversationResponse] = Field(..., description="会話履歴")
    total: int = Field(..., description="総数") 