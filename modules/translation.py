from googletrans import Translator, LANGUAGES
import logging

class TextTranslator:
    """
    Provides translation services using Googletrans.
    """
    
    def __init__(self):
        """
        Initialize the TextTranslator.
        """
        try:
            self.translator = Translator()
            logging.info("TextTranslator initialized successfully.")
        except Exception as e:
            logging.error(f"Failed to initialize TextTranslator: {e}")
            self.translator = None
    
    def translate_text(self, text: str, dest_language: str = 'en') -> str:
        """
        Translate text to the desired language.
        
        :param text: str - Text to translate.
        :param dest_language: str - Destination language code (e.g., 'en', 'es').
        :return: str - Translated text.
        """
        if not self.translator:
            logging.error("Translator not initialized.")
            return "Translation service not available."
        
        try:
            translation = self.translator.translate(text, dest=dest_language)
            logging.info(f"Text translated to {dest_language}.")
            return translation.text
        except Exception as e:
            logging.error(f"Failed to translate text: {e}")
            return "An error occurred during translation."
    
    def get_available_languages(self) -> dict:
        """
        Get available languages for translation.
        
        :return: dict - Dictionary of language codes and names.
        """
        return LANGUAGES
