import pytest
from unittest.mock import Mock, patch
from app.services.speech_service import SpeechService
from google.cloud import speech

@pytest.mark.asyncio
async def test_transcribe_audio_success():
    # モックの設定
    mock_client = Mock()
    mock_response = Mock()
    mock_result = Mock()
    mock_alternative = Mock()
    mock_alternative.transcript = "Hello, this is a test."
    mock_result.alternatives = [mock_alternative]
    mock_response.results = [mock_result]
    mock_client.recognize.return_value = mock_response

    # SpeechServiceのインスタンス化とモックの注入
    with patch('google.cloud.speech.SpeechClient', return_value=mock_client):
        service = SpeechService()
        
        # テスト実行
        result = await service.transcribe_audio(
            audio_content=b"test audio",
            sample_rate=48000,
            encoding="WEBM_OPUS",
            language_code="en-US"
        )

        # アサーション
        assert result == "Hello, this is a test."
        mock_client.recognize.assert_called_once()

@pytest.mark.asyncio
async def test_transcribe_audio_error():
    # モックの設定
    mock_client = Mock()
    mock_client.recognize.side_effect = Exception("API Error")

    # SpeechServiceのインスタンス化とモックの注入
    with patch('google.cloud.speech.SpeechClient', return_value=mock_client):
        service = SpeechService()
        
        # テスト実行とエラー確認
        with pytest.raises(Exception) as exc_info:
            await service.transcribe_audio(
                audio_content=b"test audio",
                sample_rate=48000,
                encoding="WEBM_OPUS",
                language_code="en-US"
            )
        
        assert str(exc_info.value) == "API Error" 