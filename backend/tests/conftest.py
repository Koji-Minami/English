import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch
from app.main import create_app
from app.services.speech_service import SpeechService

@pytest.fixture
def test_client():
    app = create_app()
    return TestClient(app)

@pytest.fixture
def mock_speech_service():
    with patch('app.services.speech_service.SpeechService') as mock:
        service = Mock(spec=SpeechService)
        mock.return_value = service
        yield service

@pytest.fixture
def sample_audio_content():
    return b"fake audio content" 