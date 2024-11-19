"""Text correction worker module."""

import logging
from typing import Dict, Any
from PyQt5.QtCore import QObject, pyqtSignal
import enchant
from thefuzz import fuzz
import re

logger = logging.getLogger(__name__)

class TextCorrectionWorker(QObject):
    """Worker class for text correction."""

    result_ready = pyqtSignal(str)
    error_occurred = pyqtSignal(str)

    def __init__(self):
        """Initialize the text correction worker."""
        super().__init__()
        self.dictionary = enchant.Dict("en_US")
        self.settings = {
            'language': 'english',
            'severity': 'medium',
            'auto_correct': True
        }

    def update_settings(self, settings: Dict[str, Any]) -> None:
        """Update worker settings."""
        self.settings.update(settings)
        # Update dictionary based on language
        lang_codes = {
            'english': 'en_US',
            'spanish': 'es',
            'french': 'fr',
            'german': 'de'
        }
        try:
            if self.settings['language'] in lang_codes:
                self.dictionary = enchant.Dict(lang_codes[self.settings['language']])
        except enchant.errors.DictNotFoundError:
            logger.warning(f"Dictionary not found for {self.settings['language']}, falling back to en_US")
            self.dictionary = enchant.Dict("en_US")

    def correct_text(self, text: str) -> None:
        """Perform text correction."""
        try:
            if not text.strip():
                self.result_ready.emit("")
                return

            # Split text into words
            words = re.findall(r'\b\w+\b|\W+', text)
            corrected_words = []

            for word in words:
                if re.match(r'\W+', word):  # Keep punctuation and whitespace
                    corrected_words.append(word)
                    continue

                if not self.dictionary.check(word):
                    suggestions = self.dictionary.suggest(word)
                    if suggestions:
                        # Use fuzzy matching to find the best suggestion
                        best_match = max(suggestions, key=lambda x: fuzz.ratio(word, x))
                        if fuzz.ratio(word, best_match) > 70:  # Only correct if confidence is high
                            corrected_words.append(best_match)
                        else:
                            corrected_words.append(word)
                    else:
                        corrected_words.append(word)
                else:
                    corrected_words.append(word)

            corrected_text = ''.join(corrected_words)
            self.result_ready.emit(corrected_text)

        except Exception as e:
            logger.error(f"Error in text correction: {e}")
            self.error_occurred.emit(str(e))
