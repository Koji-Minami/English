from google.cloud import texttospeech
from loguru import logger
from typing import Optional
import tempfile
import os

class TextToSpeechService:
    def __init__(self):
        self.client = texttospeech.TextToSpeechClient()

    def text_to_speech(self, text: str, language_code: str) -> bytes:
        try:
            synthesis_input = texttospeech.SynthesisInput(text=text)

            # Build the voice request, select the language code and the ssml voice gender
            voice = texttospeech.VoiceSelectionParams(
                language_code=language_code,
                ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL
            )

            # Select the type of audio file you want returned
            audio_config = texttospeech.AudioConfig(
                audio_encoding=texttospeech.AudioEncoding.MP3
            )

            # Perform the text-to-speech request
            response = self.client.synthesize_speech(
                input=synthesis_input,
                voice=voice,
                audio_config=audio_config
            )

            # The response's audio_content is binary.
            with open("output.mp3", "wb") as out:
                # Write the response to the output file.
                out.write(response.audio_content)
                print('Audio content written to file "output.mp3"')
                        # Return the audio content directly
            return response.audio_content

        except Exception as e:
            logger.error(f"Error in text to speech: {str(e)}")
            raise

class TextToSpeechServiceFactory:
    @staticmethod
    def create() -> TextToSpeechService:
        return TextToSpeechService() 