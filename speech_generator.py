import os
import asyncio
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class SpeechGenerator:
    def __init__(self):
        self.client = OpenAI()
        
    async def generate_speech(self, text: str, voice: str = "alloy", speed: float = 1.0) -> bytes:
        """
        Convert text to speech using OpenAI's text-to-speech API.
        
        Args:
            text (str): The text to convert to speech
            voice (str): One of 'alloy', 'echo', 'fable', 'onyx', 'nova', or 'shimmer'
            speed (float): Speed of speech, between 0.25 and 4.0
            
        Returns:
            bytes: The audio data
        """
        try:
            # Input validation
            if not text or not isinstance(text, str):
                raise ValueError("Invalid input text")
                
            if voice not in ["alloy", "echo", "fable", "onyx", "nova", "shimmer"]:
                voice = "alloy"
                
            speed = max(0.25, min(4.0, float(speed)))  # Clamp speed between 0.25 and 4.0
            
            response = await asyncio.to_thread(
                self.client.audio.speech.create,
                model="tts-1",
                voice=voice,
                input=text,
                speed=speed
            )
            
            # Get the audio data
            audio_data = response.content
            return audio_data
            
        except Exception as e:
            print(f"Error in speech generation: {str(e)}")
            return None
            
    async def save_audio(self, audio_data: bytes, filename: str):
        """Save audio data to a file asynchronously"""
        if audio_data:
            try:
                await asyncio.to_thread(self._write_audio_file, audio_data, filename)
            except Exception as e:
                print(f"Error saving audio file: {str(e)}")
                
    def _write_audio_file(self, audio_data: bytes, filename: str):
        """Helper method to write audio data to file"""
        with open(filename, 'wb') as f:
            f.write(audio_data)
            
    async def cleanup(self):
        """Clean up any resources"""
        pass  # Add cleanup code if needed
