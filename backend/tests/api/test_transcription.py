import pytest
from unittest.mock import Mock, patch
from fastapi import UploadFile
from io import BytesIO

@pytest.mark.asyncio
async def test_transcribe_endpoint_success(test_client, mock_speech_service, sample_audio_content):
    # モックの設定
    mock_speech_service.transcribe_audio.return_value = "Hello, this is a test."
    
    # テスト用のファイルオブジェクトを作成
    file = UploadFile(
        filename="test.wav",
        file=BytesIO(sample_audio_content)
    )
    
    # テスト実行
    response = test_client.post(
        "/api/v1/transcribe",
        files={"audio_file": ("test.wav", sample_audio_content, "audio/wav")}
    )
    
    # アサーション
    assert response.status_code == 200
    assert response.json() == {"transcript": "Hello, this is a test."}
    mock_speech_service.transcribe_audio.assert_called_once()

@pytest.mark.asyncio
async def test_transcribe_endpoint_error(test_client, mock_speech_service, sample_audio_content):
    # モックの設定
    mock_speech_service.transcribe_audio.side_effect = Exception("API Error")
    
    # テスト実行
    response = test_client.post(
        "/api/v1/transcribe",
        files={"audio_file": ("test.wav", sample_audio_content, "audio/wav")}
    )
    
    # アサーション
    assert response.status_code == 500
    mock_speech_service.transcribe_audio.assert_called_once() 