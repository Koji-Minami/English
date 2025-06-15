import pytest
from app.services.gemini_service import GeminiService, GeminiServiceFactory
from unittest.mock import Mock, patch

@pytest.fixture
def mock_genai_client():
    with patch('app.services.gemini_service.genai.Client') as mock:
        yield mock

@pytest.fixture
def gemini_service(mock_genai_client):
    return GeminiServiceFactory.create()

def test_gemini_service_initialization(mock_genai_client):
    service = GeminiServiceFactory.create()
    assert service is not None
    mock_genai_client.assert_called_once()

def test_generate_text_success(gemini_service, mock_genai_client):
    # モックの設定
    mock_response = Mock()
    mock_response.text = "This is a test response"
    mock_genai_client.return_value.models.generate_content.return_value = mock_response

    # テスト実行
    result = gemini_service.generate_text("Test prompt")
    
    # 検証
    assert result == "This is a test response"
    mock_genai_client.return_value.models.generate_content.assert_called_once()

def test_generate_text_error(gemini_service, mock_genai_client):
    # モックの設定
    mock_genai_client.return_value.models.generate_content.side_effect = Exception("API Error")

    # テスト実行と検証
    with pytest.raises(Exception) as exc_info:
        gemini_service.generate_text("Test prompt")
    
    assert str(exc_info.value) == "API Error" 