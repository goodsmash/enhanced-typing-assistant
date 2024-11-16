import enchant
import logging

class SpellChecker:
    """
    Implements spell checking using PyEnchant.
    """
    
    def __init__(self, language: str = 'en_US'):
        """
        Initialize the SpellChecker with the specified language.
        
        :param language: str - Language code for spell checking.
        """
        if enchant:
            try:
                self.dictionary = enchant.Dict(language)
                logging.info(f"SpellChecker initialized for language: {language}")
            except enchant.errors.DictNotFoundError:
                logging.error(f"Dictionary for language '{language}' not found.")
                self.dictionary = None
        else:
            logging.error("PyEnchant is not installed.")
            self.dictionary = None
    
    def correct_spelling(self, text: str) -> str:
        """
        Correct the spelling of the provided text.
        
        :param text: str - The text to be spell-checked.
        :return: str - Text with corrected spelling.
        """
        if not self.dictionary:
            logging.warning("SpellChecker dictionary not initialized.")
            return text
        
        words = text.split()
        corrected_words = []
        for word in words:
            try:
                if not self.dictionary.check(word):
                    suggestions = self.dictionary.suggest(word)
                    if suggestions:
                        corrected_words.append(suggestions[0])
                    else:
                        corrected_words.append(word)
                else:
                    corrected_words.append(word)
            except Exception as e:
                logging.error(f"Error checking word '{word}': {e}")
                corrected_words.append(word)  # Append the original word if an error occurs
        
        corrected_text = ' '.join(corrected_words)
        logging.info("Spelling corrected successfully.")
        return corrected_text
