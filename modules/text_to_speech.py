import pyttsx3
import logging

class TextToSpeech:
    """
    Converts text to speech using pyttsx3.
    """
    
    def __init__(self, speech_rate: int = 150, voice_id: str = None):
        """
        Initialize the TextToSpeech with optional speech rate and voice.
        
        :param speech_rate: int - Speech rate in words per minute.
        :param voice_id: str - Specific voice ID to use.
        """
        try:
            self.engine = pyttsx3.init()
            self.engine.setProperty('rate', speech_rate)
            if voice_id:
                self.engine.setProperty('voice', voice_id)
            logging.info(f"TextToSpeech initialized with rate: {speech_rate}, voice_id: {voice_id}")
        except Exception as e:
            logging.error(f"Failed to initialize TextToSpeech: {e}")
            self.engine = None
    
    def speak(self, text: str) -> None:
        """
        Speak the provided text aloud.
        
        :param text: str - The text to speak.
        """
        if not self.engine:
            logging.error("Text-to-speech engine not initialized.")
            return
        
        try:
            self.engine.say(text)
            self.engine.runAndWait()
            logging.info("Text spoken successfully.")
        except Exception as e:
            logging.error(f"Failed to speak text: {e}")
    
    def set_speech_rate(self, rate: int) -> None:
        """
        Set the speech rate.
        
        :param rate: int - New speech rate in words per minute.
        """
        if not self.engine:
            logging.error("Text-to-speech engine not initialized.")
            return
        try:
            self.engine.setProperty('rate', rate)
            logging.info(f"Speech rate set to: {rate}")
        except Exception as e:
            logging.error(f"Failed to set speech rate: {e}")
    
    def set_voice(self, voice_id: str) -> None:
        """
        Set the voice by ID.
        
        :param voice_id: str - The voice ID to set.
        """
        if not self.engine:
            logging.error("Text-to-speech engine not initialized.")
            return
        try:
            self.engine.setProperty('voice', voice_id)
            logging.info(f"Voice set to: {voice_id}")
        except Exception as e:
            logging.error(f"Failed to set voice: {e}")
