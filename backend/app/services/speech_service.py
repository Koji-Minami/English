from google.cloud import speech
from loguru import logger
from typing import Optional
import tempfile
import os

class SpeechService:
    def __init__(self):
        self.client = speech.SpeechClient()

    async def transcribe_audio(self, audio_content: bytes, sample_rate: int, encoding: str, language_code: str) -> Optional[str]:
        try:
            # 音声認識の設定
            audio = speech.RecognitionAudio(content=audio_content)
            config = speech.RecognitionConfig(
                encoding=getattr(speech.RecognitionConfig.AudioEncoding, encoding),
                sample_rate_hertz=sample_rate,
                language_code=language_code,
            )

            # 音声認識の実行
            response = self.client.recognize(config=config, audio=audio)

            # 結果の取得
            transcript = ""
            for result in response.results:
                transcript += result.alternatives[0].transcript

            return transcript

        except Exception as e:
            logger.error(f"Error in speech recognition: {str(e)}")
            raise

class SpeechServiceFactory:
    @staticmethod
    def create() -> SpeechService:
        return SpeechService() 