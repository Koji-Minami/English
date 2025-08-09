from google import genai
from google.genai import types
from app.config.settings import get_settings
from app.prompts.audio_prompts import AudioPrompt, AudioImmediatePrompt, AudioAnalysisPrompt, TranscriptAnalysisPrompt
from app.services.session_manager import SessionManagerService
from loguru import logger
from pydantic import BaseModel
import json
from fastapi import Depends 


class ResponseSchema(BaseModel):
    transcription: str
    response: str
    speechflaws: str
    nuanceinquiry: list
    alternativeexpressions: list

class ImmediateResponseSchema(BaseModel):
    transcription: str
    response: str

class AnalysisResponseSchema(BaseModel):
    speechflaws: str
    nuanceinquiry: list
    alternativeexpressions: list

class AudioAnalysisResponseSchema(BaseModel):
    advice: str
    speechflaws: str
    nuanceinquiry: list
    alternativeexpressions: list
    suggestion: str

class GeminiAudioService:
    """
    Gemini APIを使用して音声データを処理するサービス
    """
    def __init__(self):
        """
        初期化メソッド
        Gemini APIクライアントとプロンプトを設定します
        """
        # Gemini APIクライアントの初期化
        self.client = genai.Client(api_key=get_settings().GEMINI_API_KEY)
        self.model_name = get_settings().GEMINI_MODEL_NAME
            
        # プロンプトの初期化
        self.prompt = AudioPrompt()
        self.immediate_prompt = AudioImmediatePrompt()
        self.transcript_analysis_prompt = TranscriptAnalysisPrompt()
        self.audio_analysis_prompt = AudioAnalysisPrompt()

    async def generate_text(self, audio_content: bytes, session_id: str, session_manager: SessionManagerService):
        """
        音声データからテキストを生成するメソッド（従来の統合版）
        
        Args:
            audio_content (bytes): 音声データ
            
        Returns:
            dict: 生成されたテキスト（transcription と response を含む）
            
        Raises:
            ValueError: 音声データが空の場合
            Exception: API呼び出しでエラーが発生した場合
        """
        # 入力値のバリデーション
        if not audio_content:
            raise ValueError("Empty audio data")
        
        try:
            history = await session_manager.get_history(session_id)
            print(history)
            # プロンプトの取得
            prompt = self.prompt.format()
            
            # Gemini APIに音声データとプロンプトを送信
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=[
                    prompt,
                    str(history),
                    types.Part.from_bytes(data=audio_content, mime_type='audio/wav')
                ],
                config={
                    "response_mime_type": "application/json",
                    "response_schema": list[ResponseSchema]
                }
            )
            response_json: list[ResponseSchema] = response.parsed
            if not response_json:
                logger.error("Empty parsed response for generate_text")
                raise ValueError("Empty parsed response")
            conversation = [f'"user":{response_json[0].transcription}', 
                            f'"model":{response_json[0].response}']
            await session_manager.add_to_history(session_id, conversation)
            return response_json
            
        except Exception as e:
            logger.error(f"Error generating text: {e}")
            raise e

    async def generate_immediate_response(self, audio_content: bytes, session_id: str, session_manager: SessionManagerService):
        """
        音声データから即座のレスポンス（書き起こしと返事）を生成するメソッド
        
        Args:
            audio_content (bytes): 音声データ
            session_id (str): セッションID
            session_manager (SessionManagerService): セッション管理サービス
            
        Returns:
            ImmediateResponseSchema: 書き起こしと返事を含むレスポンス
            
        Raises:
            ValueError: 音声データが空の場合
            Exception: API呼び出しでエラーが発生した場合
        """
        # 入力値のバリデーション
        if not audio_content:
            raise ValueError("Empty audio data")
        
        try:
            history = await session_manager.get_history(session_id)
            print(history)
            
            # Webページデータがあるかチェック
            webpage_data = await session_manager.get_webpage_data(session_id)
            webpage_context = ""
            if webpage_data and isinstance(webpage_data, dict):
                title = webpage_data.get('title', 'Unknown Title')
                url = webpage_data.get('url', 'Unknown URL')
                content = webpage_data.get('content', '')
                webpage_context = f"\n\nReference Webpage:\nTitle: {title}\nURL: {url}\nContent: {content[:2000]}..."  # 最初の2000文字
            
            # プロンプトの取得
            prompt = self.immediate_prompt.format()
            
            # Gemini APIに音声データとプロンプトを送信
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=[
                    prompt,
                    str(history),
                    webpage_context,  # Webページのコンテキストを追加
                    types.Part.from_bytes(data=audio_content, mime_type='audio/wav')
                ],
                config={
                    "response_mime_type": "application/json",
                    "response_schema": list[ImmediateResponseSchema]
                }
            )
            response_json: list[ImmediateResponseSchema] = response.parsed
            if not response_json:
                logger.error("Empty parsed response for generate_immediate_response")
                raise ValueError("Empty parsed response")
            
            # セッション履歴に追加
            conversation = [f'"user":{response_json[0].transcription}', 
                            f'"model":{response_json[0].response}']
            await session_manager.add_to_history(session_id, conversation)
            
            return response_json[0]
            
        except Exception as e:
            logger.error(f"Error generating immediate response: {e}")
            raise e

    async def generate_transcript_analysis(self, transcription: str):
        """
        書き起こしテキストから文法分析を生成するメソッド
        
        Args:
            transcription (str): 分析対象の書き起こしテキスト
            
        Returns:
            AnalysisResponseSchema: 文法分析結果を含むレスポンス
            
        Raises:
            ValueError: 書き起こしテキストが空の場合
            Exception: API呼び出しでエラーが発生した場合
        """
        # 入力値のバリデーション
        if not transcription:
            raise ValueError("Empty transcription text")
        
        try:
            # プロンプトの取得
            prompt = self.transcript_analysis_prompt.format(transcription=transcription)
            
            # Gemini APIにプロンプトを送信
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=[prompt],
                config={
                    "response_mime_type": "application/json",
                    "response_schema": list[AnalysisResponseSchema]
                }
            )
            response_json: list[AnalysisResponseSchema] = response.parsed
            if not response_json:
                logger.error("Empty parsed response for generate_transcript_analysis")
                raise ValueError("Empty parsed response")
            
            return response_json[0]
            
        except Exception as e:
            logger.error(f"Error generating analysis: {e}")
            raise e

    async def analyze_transcription_background(
        self,
        transcription: str,
        session_id: str,
        conversation_id: str,
        session_manager: SessionManagerService
    ):
        """
        バックグラウンドで文法分析を実行するメソッド
        
        Args:
            transcription (str): 分析対象の書き起こしテキスト
            session_id (str): セッションID
            session_manager (SessionManagerService): セッション管理サービス
        """
        try:
            logger.info(f"Starting background analysis for session: {session_id}")
            analysis_result = await self.generate_transcript_analysis(transcription)
            
            # 分析結果をセッションに保存
            await session_manager.save_analysis_result(
                session_id=session_id,
                conversation_id=conversation_id,
                transcription=transcription,
                analysis_result=analysis_result.dict()
            )
            logger.info(f"Completed background analysis for session: {session_id}")
            
        except Exception as e:
            logger.error(f"Error in background analysis for session {session_id}: {str(e)}")
            # エラーが発生した場合も空の結果を保存
            await session_manager.save_analysis_result(
                session_id=session_id,
                conversation_id=conversation_id,
                transcription=transcription,
                analysis_result={
                    "speechflaws": "",
                    "nuanceinquiry": [],
                    "alternativeexpressions": []
                }
            )

    async def generate_audio_analysis(self, audio_content: bytes):
        """
        バックグラウンドで音声データを分析するメソッド
        """
        # 入力値のバリデーション
        if not audio_content:
            raise ValueError("Empty audio data")
        
        try:

            prompt = self.audio_analysis_prompt.format()
            
            # Gemini APIに音声データとプロンプトを送信
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=[
                    prompt, 
                    types.Part.from_bytes(data=audio_content, mime_type='audio/wav')
                ],
                config={
                    "response_mime_type": "application/json",
                    "response_schema": list[AudioAnalysisResponseSchema]
                }
            )
            response_json: list[AudioAnalysisResponseSchema] = response.parsed
            if not response_json:
                logger.error("Empty parsed response for generate_audio_analysis")
                raise ValueError("Empty parsed response")
            
            return response_json[0]
            
        except Exception as e:
            logger.error(f"Error generating immediate response: {e}")
            raise e
    async def analyze_audio_background (self, audio_content: bytes, session_id: str, conversation_id: str, session_manager: SessionManagerService):
        """
        バックグラウンドで文法分析を実行するメソッド
        
        Args:
            transcription (str): 分析対象の書き起こしテキスト
            session_id (str): セッションID
            session_manager (SessionManagerService): セッション管理サービス
        """
        try:
            logger.info(f"Starting background analysis for session: {session_id}")
            analysis_result = await self.generate_audio_analysis(audio_content)
            
            # 分析結果をセッションに保存
            await session_manager.save_analysis_result(
                session_id=session_id,
                conversation_id=conversation_id,
                transcription="",  # 音声分析なので空文字列
                analysis_result=analysis_result.dict()
            )
            logger.info(f"Completed background analysis for session: {session_id}")
            
        except Exception as e:
            logger.error(f"Error in background analysis for session {session_id}: {str(e)}")
            # エラーが発生した場合も空の結果を保存
            await session_manager.save_analysis_result(
                session_id=session_id,
                conversation_id=conversation_id,
                transcription="",
                analysis_result={
                    "advice": "",
                    "speechflaws": "",
                    "nuanceinquiry": [],
                    "alternativeexpressions": [],
                    "suggestion": ""
                }
            )
        


class GeminiAudioServiceFactory:
    """
    GeminiAudioServiceのファクトリークラス
    """
    @staticmethod
    def create() -> GeminiAudioService:
        """
        GeminiAudioServiceのインスタンスを作成するメソッド
        
        Returns:
            GeminiAudioService: 新しいサービスインスタンス
        """
        return GeminiAudioService() 
