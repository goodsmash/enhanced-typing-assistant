import os
import asyncio
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class SpeechTranscriber:
    def __init__(self):
        self.client = OpenAI()
        
    async def transcribe_audio(self, audio_file_path: str, language: str = None) -> str:
        """
        Transcribe audio file to text using OpenAI's transcription API.
        
        Args:
            audio_file_path (str): Path to the audio file
            language (str): Optional ISO-639-1 language code
            
        Returns:
            str: The transcribed text
        """
        try:
            # Input validation
            if not os.path.exists(audio_file_path):
                raise FileNotFoundError(f"Audio file not found: {audio_file_path}")
                
            # Validate file size (max 25MB for OpenAI API)
            file_size = os.path.getsize(audio_file_path) / (1024 * 1024)  # Convert to MB
            if file_size > 25:
                raise ValueError(f"Audio file too large: {file_size:.1f}MB (max 25MB)")
            
            async def transcribe():
                with open(audio_file_path, "rb") as audio_file:
                    response = await self.client.audio.transcriptions.create(
                        model="whisper-1",
                        file=audio_file,
                        language=language
                    )
                return response.text
                
            return await asyncio.to_thread(transcribe)
            
        except Exception as e:
            print(f"Error in transcription: {str(e)}")
            return None
            
    async def translate_audio(self, audio_file_path: str) -> str:
        """
        Translate non-English audio to English text.
        
        Args:
            audio_file_path (str): Path to the audio file
            
        Returns:
            str: The translated English text
        """
        try:
            # Input validation
            if not os.path.exists(audio_file_path):
                raise FileNotFoundError(f"Audio file not found: {audio_file_path}")
                
            # Validate file size (max 25MB for OpenAI API)
            file_size = os.path.getsize(audio_file_path) / (1024 * 1024)  # Convert to MB
            if file_size > 25:
                raise ValueError(f"Audio file too large: {file_size:.1f}MB (max 25MB)")
            
            async def translate():
                with open(audio_file_path, "rb") as audio_file:
                    response = await self.client.audio.translations.create(
                        model="whisper-1",
                        file=audio_file
                    )
                return response.text
                
            return await asyncio.to_thread(translate)
            
        except Exception as e:
            print(f"Error in translation: {str(e)}")
            return None
            
    async def cleanup(self):
        """Clean up any resources"""
        pass  # Add cleanup code if needed
