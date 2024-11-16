"""Speech recognition and synthesis functionality."""

import threading
from typing import Callable, Optional

import pyttsx3
import speech_recognition as sr


class SpeechHandler:
    """Handles text-to-speech and speech-to-text functionality."""

    def __init__(self):
        """Initialize speech handler with TTS and STT engines."""
        self.engine = pyttsx3.init()
        self.recognizer = sr.Recognizer()
        self.speaking = False
        self.recording = False
        self._speech_thread: Optional[threading.Thread] = None
        self._record_thread: Optional[threading.Thread] = None

    def set_voice(self, voice_id: Optional[str] = None) -> None:
        """Set the text-to-speech voice."""
        voices = self.engine.getProperty('voices')
        if voice_id:
            self.engine.setProperty('voice', voice_id)
        else:
            # Default to first available voice
            self.engine.setProperty('voice', voices[0].id)

    def set_rate(self, rate: int) -> None:
        """Set the speech rate (words per minute)."""
        if 50 <= rate <= 400:
            self.engine.setProperty('rate', rate)
        else:
            raise ValueError("Rate must be between 50 and 400 words per minute")

    def set_volume(self, volume: float) -> None:
        """Set the speech volume (0.0 to 1.0)."""
        if 0.0 <= volume <= 1.0:
            self.engine.setProperty('volume', volume)
        else:
            raise ValueError("Volume must be between 0.0 and 1.0")

    def speak(self, text: str, callback: Optional[Callable[[], None]] = None) -> None:
        """Speak the given text asynchronously."""
        if self.speaking:
            self.stop_speaking()

        def speak_thread():
            self.speaking = True
            self.engine.say(text)
            self.engine.runAndWait()
            self.speaking = False
            if callback:
                callback()

        self._speech_thread = threading.Thread(target=speak_thread)
        self._speech_thread.start()

    def stop_speaking(self) -> None:
        """Stop current speech output."""
        if self.speaking:
            self.engine.stop()
            self.speaking = False
            if self._speech_thread:
                self._speech_thread.join()

    def start_recording(self, callback: Callable[[str], None]) -> None:
        """Start recording audio for speech recognition."""
        if self.recording:
            return

        def record_thread():
            self.recording = True
            with sr.Microphone() as source:
                try:
                    print("Listening...")
                    audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=10)
                    text = self.recognizer.recognize_google(audio)
                    callback(text)
                except sr.WaitTimeoutError:
                    callback("")
                    print("No speech detected")
                except sr.UnknownValueError:
                    callback("")
                    print("Could not understand audio")
                except sr.RequestError as e:
                    callback("")
                    print(f"Could not request results: {e}")
                finally:
                    self.recording = False

        self._record_thread = threading.Thread(target=record_thread)
        self._record_thread.start()

    def stop_recording(self) -> None:
        """Stop current audio recording."""
        self.recording = False
        if self._record_thread:
            self._record_thread.join()

    def get_available_voices(self) -> list:
        """Get list of available voices."""
        return self.engine.getProperty('voices')

    def get_current_rate(self) -> int:
        """Get current speech rate."""
        return self.engine.getProperty('rate')

    def get_current_volume(self) -> float:
        """Get current volume."""
        return self.engine.getProperty('volume')
