from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from loguru import logger
from ..services.speech_service import SpeechService, SpeechServiceFactory
from ..services.gemini_service import GeminiService, GeminiServiceFactory
from ..services.gemini_audio_service import GeminiAudioService, GeminiAudioServiceFactory
from ..services.text2speech_service import TextToSpeechService, TextToSpeechServiceFactory
from ..config.settings import Settings, get_settings
import tempfile
import os

router = APIRouter()

@router.post("/transcribe")
async def transcribe_audio(
    audio_file: UploadFile = File(...),
    speech_service: SpeechService = Depends(SpeechServiceFactory.create),
    gemini_service: GeminiService = Depends(GeminiServiceFactory.create),
    settings: Settings = Depends(get_settings)
):
    try:
        # 一時ファイルとして保存
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_file:
            content = await audio_file.read()
            temp_file.write(content)
            temp_file_path = temp_file.name

        try:
            # 音声認識の実行
            transcript = await speech_service.transcribe_audio(
                audio_content=content,
                sample_rate=settings.AUDIO_SAMPLE_RATE,
                encoding=settings.AUDIO_ENCODING,
                language_code=settings.LANGUAGE_CODE
            )

            # Gemini APIに送信
            gemini_response = gemini_service.generate_text(transcript)

            return {
                "transcript": transcript,
                "gemini_response": gemini_response
            }

        finally:
            # 一時ファイルの削除
            os.unlink(temp_file_path)

    except Exception as e:
        logger.error(f"Error processing audio file: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error processing audio file: {str(e)}"
        ) 
    
@router.post("/gemini_audio")
async def gemini_audio(
    audio_file: UploadFile = File(...),
    gemini_audio_service: GeminiAudioService = Depends(GeminiAudioServiceFactory.create),
    text_to_speech_service: TextToSpeechService = Depends(TextToSpeechServiceFactory.create),
    settings: Settings = Depends(get_settings)
):
    """
    音声ファイルをGemini APIに送信し、指定されたコンテキストに基づいて分析結果を返すエンドポイント
    
    Args:
        audio_file (UploadFile): アップロードされた音声ファイル
        context (str, optional): 分析のコンテキスト（例：「発音の改善点」）
        gemini_audio_service (GeminiAudioService): 音声処理サービス
        settings (Settings): アプリケーション設定
        
    Returns:
        dict: 分析結果を含むレスポンス
        
    Raises:
        HTTPException: 処理中にエラーが発生した場合
    """
    try:
        # 一時ファイルとして保存
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_file:
            content = await audio_file.read()
            temp_file.write(content)
            temp_file_path = temp_file.name

        try:
            # 音声認識の実行
            gemini_response = gemini_audio_service.generate_text(
                audio_content=content
            )

            # text_to_speech_service.text_to_speech(
            #     text=gemini_response[0].response,
            #     language_code=settings.LANGUAGE_CODE
            # )

            return {
                "gemini_response": gemini_response
            }

        finally:
            # 一時ファイルの削除
            os.unlink(temp_file_path)

    except Exception as e:
        logger.error(f"Error processing audio file: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error processing audio file: {str(e)}"
        ) 
