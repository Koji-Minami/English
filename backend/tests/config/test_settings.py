import pytest
from app.config.settings import Settings, get_settings

def test_settings_default_values():
    settings = Settings()
    assert settings.APP_NAME == "Speech to Text API"
    assert settings.DEBUG is True
    assert "http://localhost:3000" in settings.CORS_ORIGINS
    assert settings.AUDIO_SAMPLE_RATE == 48000
    assert settings.AUDIO_ENCODING == "MP3"
    assert settings.LANGUAGE_CODE == "en-US"

def test_settings_custom_values():
    settings = Settings(
        APP_NAME="Custom App",
        DEBUG=False,
        CORS_ORIGINS=["http://custom-origin.com"],
        AUDIO_SAMPLE_RATE=44100,
        AUDIO_ENCODING="LINEAR16",
        LANGUAGE_CODE="ja-JP"
    )
    assert settings.APP_NAME == "Custom App"
    assert settings.DEBUG is False
    assert settings.CORS_ORIGINS == ["http://custom-origin.com"]
    assert settings.AUDIO_SAMPLE_RATE == 44100
    assert settings.AUDIO_ENCODING == "LINEAR16"
    assert settings.LANGUAGE_CODE == "ja-JP"

def test_get_settings_caching():
    settings1 = get_settings()
    settings2 = get_settings()
    assert settings1 is settings2  # 同じインスタンスが返されることを確認 