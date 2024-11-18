import enchant
import logging
from typing import List, Dict, Set
import json
import os
from collections import Counter

class WordSuggestionEngine:
    """
    Provides word suggestions and auto-completion functionality.
    """
    
    def __init__(self, language: str = 'en_US'):
        """
        Initialize the WordSuggestionEngine.
        
        :param language: str - Language code for spell checking.
        """
        self.language = language
        self.dictionary = enchant.Dict(language)
        self.user_dictionary: Set[str] = set()
        self.word_frequency: Dict[str, int] = Counter()
        self.load_user_dictionary()
        logging.info(f"WordSuggestionEngine initialized with language: {language}")
    
    def get_suggestions(self, word: str, max_suggestions: int = 5) -> List[str]:
        """
        Get spelling suggestions for a word.
        
        :param word: str - Word to get suggestions for.
        :param max_suggestions: int - Maximum number of suggestions to return.
        :return: List[str] - List of suggested words.
        """
        if not word:
            return []
            
        suggestions = []
        
        # Check user dictionary first
        user_suggestions = [w for w in self.user_dictionary 
                          if w.startswith(word) or w.lower().startswith(word.lower())]
        suggestions.extend(sorted(user_suggestions, 
                                key=lambda x: self.word_frequency.get(x, 0),
                                reverse=True))
        
        # Add dictionary suggestions
        if len(suggestions) < max_suggestions:
            dict_suggestions = self.dictionary.suggest(word)
            suggestions.extend([s for s in dict_suggestions 
                             if s not in suggestions])
        
        return suggestions[:max_suggestions]
    
    def is_word_valid(self, word: str) -> bool:
        """
        Check if a word is valid.
        
        :param word: str - Word to check.
        :return: bool - True if word is valid, False otherwise.
        """
        return word in self.user_dictionary or self.dictionary.check(word)
    
    def add_to_user_dictionary(self, word: str) -> None:
        """
        Add a word to the user dictionary.
        
        :param word: str - Word to add.
        """
        if word and word not in self.user_dictionary:
            self.user_dictionary.add(word)
            self.word_frequency[word] += 1
            self.save_user_dictionary()
            logging.info(f"Added '{word}' to user dictionary.")
    
    def remove_from_user_dictionary(self, word: str) -> None:
        """
        Remove a word from the user dictionary.
        
        :param word: str - Word to remove.
        """
        if word in self.user_dictionary:
            self.user_dictionary.remove(word)
            self.word_frequency.pop(word, None)
            self.save_user_dictionary()
            logging.info(f"Removed '{word}' from user dictionary.")
    
    def update_word_frequency(self, word: str) -> None:
        """
        Update the frequency count for a word.
        
        :param word: str - Word to update frequency for.
        """
        if word:
            self.word_frequency[word] += 1
            self.save_user_dictionary()
    
    def load_user_dictionary(self) -> None:
        """Load the user dictionary and word frequencies from file."""
        dict_file = os.path.join(os.path.dirname(__file__), f'user_dictionary_{self.language}.json')
        if os.path.exists(dict_file):
            try:
                with open(dict_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.user_dictionary = set(data.get('words', []))
                    self.word_frequency = Counter(data.get('frequencies', {}))
                logging.info("User dictionary loaded successfully.")
            except Exception as e:
                logging.error(f"Failed to load user dictionary: {e}")
                self.user_dictionary = set()
                self.word_frequency = Counter()
    
    def save_user_dictionary(self) -> None:
        """Save the user dictionary and word frequencies to file."""
        dict_file = os.path.join(os.path.dirname(__file__), f'user_dictionary_{self.language}.json')
        try:
            data = {
                'words': list(self.user_dictionary),
                'frequencies': dict(self.word_frequency)
            }
            with open(dict_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            logging.info("User dictionary saved successfully.")
        except Exception as e:
            logging.error(f"Failed to save user dictionary: {e}")
    
    def change_language(self, language: str) -> None:
        """
        Change the dictionary language.
        
        :param language: str - New language code.
        """
        try:
            self.dictionary = enchant.Dict(language)
            self.language = language
            self.user_dictionary = set()
            self.word_frequency = Counter()
            self.load_user_dictionary()
            logging.info(f"Language changed to {language}")
        except enchant.Error as e:
            logging.error(f"Failed to change language: {e}")
    
    def get_completion_suggestions(self, partial_word: str, max_suggestions: int = 5) -> List[str]:
        """
        Get auto-completion suggestions for a partial word.
        
        :param partial_word: str - Partial word to complete.
        :param max_suggestions: int - Maximum number of suggestions to return.
        :return: List[str] - List of completion suggestions.
        """
        if not partial_word:
            return []
            
        # Get suggestions from user dictionary first
        suggestions = [word for word in self.user_dictionary 
                      if word.lower().startswith(partial_word.lower())]
        
        # Sort by frequency
        suggestions.sort(key=lambda x: self.word_frequency.get(x, 0), reverse=True)
        
        return suggestions[:max_suggestions]
