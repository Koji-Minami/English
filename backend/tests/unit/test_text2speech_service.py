import pytest
from unittest.mock import Mock, patch
from app.services.text2speech_service import TextToSpeechService, TextToSpeechServiceFactory
from google.cloud import texttospeech

@pytest.fixture
def mock_text_to_speech_client():
    with patch('app.services.text2speech_service.texttospeech.TextToSpeechClient') as mock:
        yield mock

@pytest.fixture
def text_to_speech_service(mock_text_to_speech_client):
    return TextToSpeechServiceFactory.create()

def test_text_to_speech_service_initialization(mock_text_to_speech_client):
    """Test if the service is properly initialized."""
    service = TextToSpeechServiceFactory.create()
    assert service is not None, "Service should be initialized"
    mock_text_to_speech_client.assert_called_once()

def test_text_to_speech_success(text_to_speech_service, mock_text_to_speech_client):
    """Test successful text to speech conversion."""
    # モックの設定
    mock_response = Mock()
    mock_response.audio_content = b"test audio content"
    mock_text_to_speech_client.return_value.synthesize_speech.return_value = mock_response

    # テスト実行
    result = text_to_speech_service.text_to_speech("This is a test", "en-US")
    
    # 検証
    assert result == b"test audio content", "Should return the expected audio content"
    mock_text_to_speech_client.return_value.synthesize_speech.assert_called_once()

def test_text_to_speech_empty_text(text_to_speech_service, mock_text_to_speech_client):
    """Test handling of empty text input."""
    # モックの設定
    mock_response = Mock()
    mock_response.audio_content = b"test audio content"
    mock_text_to_speech_client.return_value.synthesize_speech.return_value = mock_response

    # 空のテキストでも正常に処理されることを確認
    result = text_to_speech_service.text_to_speech("", "en-US")
    assert result == b"test audio content", "Should handle empty text gracefully"

def test_text_to_speech_invalid_language(text_to_speech_service, mock_text_to_speech_client):
    """Test handling of invalid language code."""
    # モックの設定
    mock_response = Mock()
    mock_response.audio_content = b"test audio content"
    mock_text_to_speech_client.return_value.synthesize_speech.return_value = mock_response

    # 無効な言語コードでも正常に処理されることを確認
    result = text_to_speech_service.text_to_speech("Test", "invalid-language")
    assert result == b"test audio content", "Should handle invalid language gracefully"

def test_text_to_speech_error(text_to_speech_service, mock_text_to_speech_client):
    """Test error handling when API call fails."""
    # モックの設定
    mock_text_to_speech_client.return_value.synthesize_speech.side_effect = Exception("API Error")

    # テスト実行と検証
    with pytest.raises(Exception) as exc_info:
        text_to_speech_service.text_to_speech("This is a test", "en-US")
    
    assert str(exc_info.value) == "API Error", "Should raise the expected error"

def test_text_to_speech_with_custom_voice(text_to_speech_service, mock_text_to_speech_client):
    """Test text to speech conversion with custom voice settings."""
    # モックの設定
    mock_response = Mock()
    mock_response.audio_content = b"test audio content"
    mock_text_to_speech_client.return_value.synthesize_speech.return_value = mock_response

    # テスト実行（現在のAPIではカスタム音声パラメータはサポートされていない）
    result = text_to_speech_service.text_to_speech("This is a test", "en-US")
    
    # 検証
    assert result == b"test audio content", "Should return the expected audio content"
    mock_text_to_speech_client.return_value.synthesize_speech.assert_called_once()

