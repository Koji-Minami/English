from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, BackgroundTasks, Query, Form
from pydantic import BaseModel
from loguru import logger
from ..services.speech_service import SpeechService, SpeechServiceFactory
from ..services.gemini_service import GeminiService, GeminiServiceFactory
from ..services.gemini_audio_service import GeminiAudioService, GeminiAudioServiceFactory
from ..services.text2speech_service import TextToSpeechService, TextToSpeechServiceFactory
from ..services.postgres_session_manager import PostgresSessionManagerService, PostgresSessionManagerServiceFactory
from ..services.web_scraper_service import WebScraperService, WebScraperServiceFactory
from ..config.settings import Settings, get_settings
import tempfile
import os
import base64


class WebpageUrlRequest(BaseModel):
    url: str

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
    
@router.get("/gemini_audio")
async def create_session(
    session_manager_service: PostgresSessionManagerService = Depends(PostgresSessionManagerServiceFactory.create)
):
    """
    新しいセッションを作成し、セッションIDを返すエンドポイント
    
    Returns:
        dict: セッションIDを含むレスポンス
    """
    session_id = await session_manager_service.create_session()
    return {"session_id": session_id}


@router.post("/gemini_audio/{session_id}/webpage")
async def add_webpage_to_session(
    session_id: str,
    webpage_request: WebpageUrlRequest,
    session_manager_service: PostgresSessionManagerService = Depends(PostgresSessionManagerServiceFactory.create),
    web_scraper_service: WebScraperService = Depends(WebScraperServiceFactory.create)
):
    """
    WebページのURLをPOSTし、内容をセッションのhistoryに追加するエンドポイント
    
    Args:
        session_id (str): セッションID
        webpage_request (WebpageUrlRequest): WebページURLリクエスト
        session_manager_service (PostgresSessionManagerService): セッション管理サービス
        web_scraper_service (WebScraperService): Webスクレイピングサービス
        
    Returns:
        dict: 処理結果を含むレスポンス
        
    Raises:
        HTTPException: 処理中にエラーが発生した場合
    """
    try:
        # URLの検証
        if not web_scraper_service.validate_url(webpage_request.url):
            raise HTTPException(
                status_code=400,
                detail="Invalid URL format"
            )
        
        # Webページのスクレイピング
        webpage_data = web_scraper_service.scrape_url(webpage_request.url)
        if not webpage_data:
            raise HTTPException(
                status_code=500,
                detail="Failed to scrape webpage content"
            )
        
        # セッションにWebページデータを保存
        await session_manager_service.save_webpage_data(session_id, webpage_data)
        
        # 会話履歴にWebページの内容を追加
        webpage_content = f"Webpage: {webpage_data['title']}\nContent: {webpage_data['content']}..."  # 最初の1000文字のみ
        conversation = [f'"user":I have loaded the webpage content. Let\'s discuss about it. # loaded webpage content{webpage_content}']
        print(conversation)
        await session_manager_service.add_to_history(session_id, conversation)
        logger.info(f"Successfully added webpage content to session: {session_id}, url: {webpage_request.url}")
        
        return {
            "status": "success",
            "message": "Webpage content added to session",
            "webpage_data": {
                "url": webpage_data['url'],
                "title": webpage_data['title'],
                "content_length": len(webpage_data['content'])
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error adding webpage to session: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error adding webpage to session: {str(e)}"
        )


    
@router.post("/gemini_audio/{session_id}")
async def gemini_audio(
    session_id: str,
    background_tasks: BackgroundTasks,
    audio_file: UploadFile = File(...),
    gemini_audio_service: GeminiAudioService = Depends(GeminiAudioServiceFactory.create),
    text_to_speech_service: TextToSpeechService = Depends(TextToSpeechServiceFactory.create),
    session_manager_service: PostgresSessionManagerService = Depends(PostgresSessionManagerServiceFactory.create),
    settings: Settings = Depends(get_settings)
):
    """
    音声ファイルをGemini APIに送信し、即座のレスポンス（書き起こしと返事）を返すエンドポイント
    文法分析はバックグラウンドで非同期実行される
    
    Args:
        session_id (str): セッションID
        audio_file (UploadFile): アップロードされた音声ファイル
        background_tasks (BackgroundTasks): FastAPIのバックグラウンドタスク
        gemini_audio_service (GeminiAudioService): 音声処理サービス
        text_to_speech_service (TextToSpeechService): 音声合成サービス
        session_manager_service (PostgresSessionManagerService): セッション管理サービス
        settings (Settings): アプリケーション設定
        
    Returns:
        dict: 即座のレスポンス（書き起こし、返事、音声データ）を含むレスポンス
        
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
            # 即座のレスポンス（書き起こしと返事）を生成
            immediate_response = await gemini_audio_service.generate_immediate_response(
                audio_content=content,
                session_id=session_id,
                session_manager=session_manager_service
            )

            # バックグラウンドで文法分析を実行
            # background_tasks.add_task(
            #     gemini_audio_service.analyze_transcription_background,
            #     transcription=immediate_response.transcription,
            #     session_id=session_id,
            #     session_manager=session_manager_service
            # )

            current_conversation_id = await session_manager_service.get_next_conversation_id(session_id)
            print(f'current_conversation_id: {current_conversation_id}')
            background_tasks.add_task(
                gemini_audio_service.analyze_audio_background,
                audio_content=content,
                session_id=session_id,
                conversation_id=current_conversation_id,
                session_manager=session_manager_service
            )

            # テキストを音声に変換
            audio_content = text_to_speech_service.text_to_speech(
                text=immediate_response.response,
                language_code=settings.LANGUAGE_CODE
            )

            # Base64エンコード
            audio_base64 = base64.b64encode(audio_content).decode('utf-8')

            return {
                "transcription": {
                    "id": current_conversation_id,
                    "content": immediate_response.transcription
                },
                "response": {
                    "id": await session_manager_service.get_next_conversation_id(session_id),
                    "content": immediate_response.response
                },
                "audio_content": audio_base64,
                "analysis_status": "processing"  # 文法分析が進行中であることを示す
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

@router.get("/analysis/{session_id}")
async def get_analysis_results(
    session_id: str,
    session_manager_service: PostgresSessionManagerService = Depends(PostgresSessionManagerServiceFactory.create),
    conversation_id: str = Query(default="", description="特定の会話ID（指定しない場合は全て取得）")
):
    """
    文法分析結果を取得するエンドポイント
    
    Args:
        session_id (str): セッションID
        transcription (str, optional): 特定の書き起こしテキスト（指定しない場合は全て取得）
        session_manager_service (PostgresSessionManagerService): セッション管理サービス
        
    Returns:
        dict: 文法分析結果を含むレスポンス
    """
    try:
        if conversation_id:
            # 特定の書き起こしテキストの分析結果を取得
            analysis_result = await session_manager_service.get_analysis_result(session_id, conversation_id)
            if analysis_result is None:
                return {
                    "status": "not_found",
                    "message": "Analysis result not found for the specified transcription"
                }
            return {
                "status": "completed",
                "analysis_result": analysis_result
            }
        else:
            # セッションの全ての分析結果を取得
            return {"status": "error", "message": "Conversation ID is required"}
            all_results = await session_manager_service.get_all_analysis_results(session_id)
            return {
                "status": "completed",
                "all_analysis_results": all_results
            }
            
    except Exception as e:
        logger.error(f"Error getting analysis results: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error getting analysis results: {str(e)}"
        )

@router.post("/finish_session/{session_id}")
async def finish_session(
    session_id: str,
    session_manager_service: PostgresSessionManagerService = Depends(PostgresSessionManagerServiceFactory.create)
):
    await session_manager_service.delete_session(session_id)
    return {"message": "Session finished"}

@router.post("/gemini_audio_legacy/{session_id}")
async def gemini_audio_legacy(
    session_id: str,
    audio_file: UploadFile = File(...),
    gemini_audio_service: GeminiAudioService = Depends(GeminiAudioServiceFactory.create),
    text_to_speech_service: TextToSpeechService = Depends(TextToSpeechServiceFactory.create),
    session_manager_service: PostgresSessionManagerService = Depends(PostgresSessionManagerServiceFactory.create),
    settings: Settings = Depends(get_settings)
):
    """
    従来の統合版エンドポイント（後方互換性のため）
    音声ファイルをGemini APIに送信し、全ての処理（書き起こし、返事、文法分析）を同時に実行する
    
    Args:
        session_id (str): セッションID
        audio_file (UploadFile): アップロードされた音声ファイル
        gemini_audio_service (GeminiAudioService): 音声処理サービス
        text_to_speech_service (TextToSpeechService): 音声合成サービス
        session_manager_service (PostgresSessionManagerService): セッション管理サービス
        settings (Settings): アプリケーション設定
        
    Returns:
        dict: 全ての処理結果を含むレスポンス
        
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
            # 統合版の処理を実行
            gemini_response = await gemini_audio_service.generate_text(
                audio_content=content,
                session_id=session_id,
                session_manager=session_manager_service
            )

            # テキストを音声に変換
            audio_content = text_to_speech_service.text_to_speech(
                text=gemini_response[0].response,
                language_code=settings.LANGUAGE_CODE
            )

            # Base64エンコード
            audio_base64 = base64.b64encode(audio_content).decode('utf-8')

            return {
                "gemini_response": gemini_response,
                "audio_content": audio_base64
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
    

@router.get("/get_analysis_result/{session_id}/{conversation_id}")
async def get_analysis_result(
    session_id: str,
    conversation_id: str,
    session_manager_service: PostgresSessionManagerService = Depends(PostgresSessionManagerServiceFactory.create)
):
    analysis_result = await session_manager_service.get_analysis_result(session_id, conversation_id)
    return {"analysis_result": analysis_result}