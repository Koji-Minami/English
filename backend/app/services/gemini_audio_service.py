from google import genai
from google.genai import types
from app.config.settings import get_settings
from app.prompts.audio_prompts import AudioPrompt
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

# class ResponseSchema(BaseModel):
#     transcription: str
#     response: str
#     feedback: str

#     def _parse_json_field(self, field: str, key: str = "text") -> str:
#         """
#         JSONフィールドをパースする共通メソッド
        
#         Args:
#             field: パースするフィールド名
#             key: 取得するJSONのキー
            
#         Returns:
#             str: パースされたテキスト
#         """
#         try:
#             value = getattr(self, field)
#             return json.loads(value)[key]
#         except (json.JSONDecodeError, KeyError, AttributeError):
#             return value  # フォールバック: 生のテキストを返す

#     @property
#     def transcription_text(self) -> str:
#         return self._parse_json_field("transcription")

#     @property
#     def response_text(self) -> str:
#         return self._parse_json_field("response")

#     @property
#     def feedback_text(self) -> str:
#         return self._parse_json_field("feedback")

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

    def generate_text(self, audio_content: bytes, session_id: str, session_manager: SessionManagerService):
        """
        音声データからテキストを生成するメソッド
        
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
            history = session_manager.get_history(session_id)
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
            conversation = [f'"user":{response_json[0].transcription}', 
                            f'"model":{response_json[0].response}']
            session_manager.add_to_history(session_id, conversation)
            return response_json
            
        except Exception as e:
            logger.error(f"Error generating text: {e}")
            raise e

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
