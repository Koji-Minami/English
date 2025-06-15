import pytest
from app.services.gemini_audio_service import GeminiAudioService, GeminiAudioServiceFactory
from unittest.mock import Mock, patch

@pytest.fixture
def mock_genai_client():
    with patch('app.services.gemini_audio_service.genai.Client') as mock:
        yield mock

@pytest.fixture
def gemini_audio_service(mock_genai_client):
    return GeminiAudioServiceFactory.create()

def test_gemini_audio_service_initialization(mock_genai_client):
    """Test if the service is properly initialized."""
    service = GeminiAudioServiceFactory.create()
    assert service is not None, "Service should be initialized"
    mock_genai_client.assert_called_once()

def test_generate_text_success(gemini_audio_service, mock_genai_client):
    """Test successful text generation from audio."""
    # モックの設定
    mock_response = Mock()
    mock_response.text = "This is a test response"
    mock_genai_client.return_value.models.generate_content.return_value = mock_response

    # テスト実行
    result = gemini_audio_service.generate_text(b"test audio")
    
    # 検証
    assert result == "This is a test response", "Should return the expected response"
    mock_genai_client.return_value.models.generate_content.assert_called_once()

def test_generate_text_error(gemini_audio_service, mock_genai_client):
    """Test error handling when API call fails."""
    # モックの設定
    mock_genai_client.return_value.models.generate_content.side_effect = Exception("API Error")

    # テスト実行と検証
    with pytest.raises(Exception) as exc_info:
        gemini_audio_service.generate_text(b"test audio")
    
    assert str(exc_info.value) == "API Error", "Should raise the expected error"

def test_generate_text_with_invalid_audio(gemini_audio_service, mock_genai_client):
    """Test handling of invalid audio data."""
    # モックの設定
    mock_genai_client.return_value.models.generate_content.side_effect = ValueError("Invalid audio format")

    # テスト実行と検証
    with pytest.raises(ValueError) as exc_info:
        gemini_audio_service.generate_text(b"invalid audio data")
    
    assert "Invalid audio format" in str(exc_info.value), "Should raise format error"

def test_generate_text_with_empty_audio(gemini_audio_service, mock_genai_client):
    """Test handling of empty audio data."""
    # テスト実行と検証
    with pytest.raises(ValueError) as exc_info:
        gemini_audio_service.generate_text(b"")
    
    assert "Empty audio data" in str(exc_info.value), "Should raise empty data error"