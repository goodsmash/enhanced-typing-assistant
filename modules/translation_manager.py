from typing import Dict, Optional
import json
import os
import logging
from googletrans import Translator, LANGUAGES

class TranslationManager:
    """
    Manages text translation using Google Translate API.
    """
    
    def __init__(self):
        """Initialize the TranslationManager."""
        self.translator = Translator()
        self.languages = LANGUAGES
        self.current_language = 'en'
        self.translations_cache: Dict[str, Dict[str, str]] = {}
        self.load_cache()
        logging.info("TranslationManager initialized.")
    
    def translate_text(self, text: str, target_lang: str, source_lang: Optional[str] = None) -> str:
        """
        Translate text to the target language.
        
        :param text: str - Text to translate.
        :param target_lang: str - Target language code.
        :param source_lang: Optional[str] - Source language code. If None, will be auto-detected.
        :return: str - Translated text.
        """
        if not text:
            return text
            
        # Check cache first
        cache_key = f"{text}:{source_lang or 'auto'}:{target_lang}"
        if cache_key in self.translations_cache.get(target_lang, {}):
            logging.info("Translation found in cache.")
            return self.translations_cache[target_lang][cache_key]
            
        try:
            translation = self.translator.translate(
                text,
                dest=target_lang,
                src=source_lang or 'auto'
            )
            translated_text = translation.text
            
            # Cache the translation
            if target_lang not in self.translations_cache:
                self.translations_cache[target_lang] = {}
            self.translations_cache[target_lang][cache_key] = translated_text
            self.save_cache()
            
            logging.info(f"Text translated to {target_lang} successfully.")
            return translated_text
            
        except Exception as e:
            logging.error(f"Translation failed: {e}")
            return text
    
    def get_available_languages(self) -> Dict[str, str]:
        """
        Get a dictionary of available languages.
        
        :return: Dict[str, str] - Dictionary of language codes and names.
        """
        return self.languages
    
    def set_current_language(self, language_code: str) -> None:
        """
        Set the current language for translations.
        
        :param language_code: str - Language code to set as current.
        """
        if language_code in self.languages:
            self.current_language = language_code
            logging.info(f"Current language set to {language_code}")
        else:
            logging.warning(f"Invalid language code: {language_code}")
    
    def load_cache(self) -> None:
        """Load the translation cache from file."""
        cache_file = os.path.join(os.path.dirname(__file__), 'translation_cache.json')
        if os.path.exists(cache_file):
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    self.translations_cache = json.load(f)
                logging.info("Translation cache loaded successfully.")
            except Exception as e:
                logging.error(f"Failed to load translation cache: {e}")
                self.translations_cache = {}
    
    def save_cache(self) -> None:
        """Save the translation cache to file."""
        cache_file = os.path.join(os.path.dirname(__file__), 'translation_cache.json')
        try:
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(self.translations_cache, f, ensure_ascii=False, indent=2)
            logging.info("Translation cache saved successfully.")
        except Exception as e:
            logging.error(f"Failed to save translation cache: {e}")
    
    def clear_cache(self) -> None:
        """Clear the translation cache."""
        self.translations_cache = {}
        self.save_cache()
        logging.info("Translation cache cleared.")
