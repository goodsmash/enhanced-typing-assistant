"""Text processing and correction functionality with enhanced support for severe typing difficulties."""

import re
import os
import logging
import json
from typing import List, Optional, Tuple, Dict, Set, Any
from pathlib import Path
from collections import defaultdict
import time

import openai
import enchant
from nltk.tokenize import word_tokenize
from nltk.corpus import words
from thefuzz import fuzz

logger = logging.getLogger(__name__)

class TextProcessor:
    """Handles text processing, correction, and enhancement with focus on accessibility."""

    def __init__(self, api_key: Optional[str] = None, language: str = "en_US", model: str = "gpt-3.5-turbo"):
        """Initialize text processor with enhanced correction capabilities."""
        try:
            # Basic setup
            self.keyboard_layout = self._load_keyboard_layout()
            self.dictionary = enchant.Dict(language)
            self.word_set = set(words.words())
            self.common_patterns = self._load_common_patterns()
            self.user_dictionary = defaultdict(int)
            
            # AI settings
            self.api_key = api_key
            self.model = model
            if api_key:
                openai.api_key = api_key
            self.last_ai_call = 0
            self.ai_cooldown = 2.0  # Seconds between AI calls
            
            # Correction settings
            self.correction_mode = "standard"  # standard, strict, creative, ai
            self.correction_severity = 0.5  # 0.0 to 1.0
            self.context_window = []  # Store recent text for context
            self.max_context_length = 100
            
            # Advanced settings
            self.learning_enabled = True  # Enable learning from corrections
            self.confidence_threshold = 0.7  # Minimum confidence for suggestions
            self.max_suggestions = 5  # Maximum number of suggestions to return
            self.preserve_case = True  # Preserve original case when correcting
            self.preserve_formatting = True  # Preserve text formatting
            
            # Performance optimization
            self.cache = {}  # Cache for frequent corrections
            self.cache_size = 1000
            self.cache_hits = 0
            self.total_corrections = 0
            
            logger.info("Text processor initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing text processor: {e}", exc_info=True)
            raise RuntimeError("Failed to initialize text processor") from e

    def _load_keyboard_layout(self, layout: str = 'qwerty') -> Dict[str, List[str]]:
        """Load the specified keyboard layout."""
        layouts = {
            'qwerty': {
                'q': ['w', 'a', '1'],
                'w': ['q', 'e', 's', 'a', '2'],
                'e': ['w', 'r', 'd', 's', '3'],
                'r': ['e', 't', 'f', 'd', '4'],
                't': ['r', 'y', 'g', 'f', '5'],
                'y': ['t', 'u', 'h', 'g', '6'],
                'u': ['y', 'i', 'j', 'h', '7'],
                'i': ['u', 'o', 'k', 'j', '8'],
                'o': ['i', 'p', 'l', 'k', '9'],
                'p': ['o', '[', ';', 'l', '0'],
                'a': ['q', 'w', 's', 'z'],
                's': ['w', 'e', 'd', 'x', 'a'],
                'd': ['e', 'r', 'f', 'c', 's'],
                'f': ['r', 't', 'g', 'v', 'd'],
                'g': ['t', 'y', 'h', 'b', 'f'],
                'h': ['y', 'u', 'j', 'n', 'g'],
                'j': ['u', 'i', 'k', 'm', 'h'],
                'k': ['i', 'o', 'l', ',', 'j'],
                'l': ['o', 'p', ';', '.', 'k'],
                'z': ['a', 's', 'x'],
                'x': ['s', 'd', 'c', 'z'],
                'c': ['d', 'f', 'v', 'x'],
                'v': ['f', 'g', 'b', 'c'],
                'b': ['g', 'h', 'n', 'v'],
                'n': ['h', 'j', 'm', 'b'],
                'm': ['j', 'k', ',', 'n'],
                ',': ['k', 'l', '.', 'm'],
                '.': ['l', ';', '/', ','],
                '/': ['.', ';', "'"],
                "'": [';', '/', '"'],
                ';': ['p', "'", '/', 'l'],
                '[': ['p', ']', "'"],
                ']': ['[', '\\'],
                '\\': [']']
            }
        }
        return layouts.get(layout.lower(), layouts['qwerty'])

    def _load_common_patterns(self) -> Dict[str, str]:
        """Load common typing patterns and mistakes."""
        return {
            "teh": "the",
            "adn": "and",
            "cant": "can't",
            "dont": "don't",
            "didnt": "didn't",
            "wouldnt": "wouldn't",
            "couldnt": "couldn't",
            "shouldnt": "shouldn't",
            "im": "I'm",
            "youre": "you're",
            "theyre": "they're",
            "weve": "we've",
            "thats": "that's",
            "isnt": "isn't",
            "wasnt": "wasn't",
            "werent": "weren't",
            "hasnt": "hasn't",
            "havent": "haven't",
            "wont": "won't"
        }

    def enhance_text(self, text: str) -> str:
        """Enhance text with corrections based on current mode and severity."""
        if not text:
            return text

        try:
            # Check cache first
            cache_key = (text, self.correction_mode, self.correction_severity)
            if cache_key in self.cache:
                self.cache_hits += 1
                return self.cache[cache_key]
            
            self.total_corrections += 1

            # Use AI for severe typing difficulties in creative or ai mode
            if (self.correction_mode in ["creative", "ai"] and 
                self.api_key and 
                self._should_use_ai(text)):
                corrected = self._ai_enhance_text(text)
            else:
                # Standard correction
                corrected = self._standard_enhance_text(text)
            
            # Update cache
            if len(self.cache) >= self.cache_size:
                # Remove oldest entries
                while len(self.cache) >= self.cache_size * 0.9:
                    self.cache.pop(next(iter(self.cache)))
            self.cache[cache_key] = corrected
            
            return corrected
            
        except Exception as e:
            logger.error(f"Error enhancing text: {e}", exc_info=True)
            return text

    def _standard_enhance_text(self, text: str) -> str:
        """Standard text enhancement without AI."""
        words = text.split()
        corrected_words = []

        for word in words:
            # Skip correction for certain patterns
            if any(char.isdigit() for char in word) or len(word) <= 1:
                corrected_words.append(word)
                continue

            # Check common patterns first
            lower_word = word.lower()
            if lower_word in self.common_patterns:
                corrected = self.common_patterns[lower_word]
                corrected_words.append(self._preserve_case(word, corrected))
                continue

            # Check if word needs correction
            if self.dictionary.check(word) or word in self.user_dictionary:
                corrected_words.append(word)
                continue

            # Get suggestions using fuzzy matching
            suggestions = self._get_best_suggestion(word)
            if suggestions:
                # Apply correction based on severity and mode
                if self.correction_mode == "strict" or self.correction_severity > 0.8:
                    corrected = suggestions[0]
                elif self.correction_severity > 0.4:
                    # Only correct if we're reasonably confident
                    similarity = fuzz.ratio(word.lower(), suggestions[0].lower())
                    if similarity > 65:
                        corrected = suggestions[0]
                    else:
                        corrected = word
                else:
                    corrected = word
                
                corrected_words.append(self._preserve_case(word, corrected))
            else:
                corrected_words.append(word)

        corrected_text = " ".join(corrected_words)
        
        # Update context window
        self._update_context(corrected_text)
        
        return corrected_text

    def _should_use_ai(self, text: str) -> bool:
        """Determine if AI should be used based on text complexity."""
        # Check time since last AI call
        if time.time() - self.last_ai_call < self.ai_cooldown:
            return False
            
        # Check for severe typing issues
        word_count = len(text.split())
        misspelled_count = sum(1 for word in text.split() 
                             if len(word) > 1 and not self.dictionary.check(word))
        
        # Use AI if more than 40% of words are misspelled
        return (word_count >= 3 and 
                misspelled_count / word_count > 0.4)

    def _ai_enhance_text(self, text: str) -> str:
        """Use AI to enhance severely mistyped text."""
        try:
            # Update last AI call time
            self.last_ai_call = time.time()
            
            # Prepare context
            context = " ".join(self.context_window[-3:])  # Last 3 entries
            
            # Create prompt based on correction mode
            if self.correction_mode == "creative":
                prompt = f"""Please enhance this text while maintaining its meaning. 
                Consider the writer's style and add clarity where needed.
                Previous context: {context}
                Text to enhance: {text}"""
            else:
                prompt = f"""Please correct this text, which was typed by someone with motor control difficulties. 
                Maintain the original meaning but fix spelling and grammar.
                Previous context: {context}
                Text to correct: {text}"""
            
            # Call GPT with specified model
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that corrects text while preserving meaning."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=150
            )
            
            corrected_text = response.choices[0].message.content.strip()
            
            # Learn from the correction if enabled
            if self.learning_enabled:
                self._learn_from_correction(text, corrected_text)
            
            logger.info(f"AI correction: '{text}' -> '{corrected_text}'")
            return corrected_text
            
        except Exception as e:
            logger.error(f"Error in AI text enhancement: {e}", exc_info=True)
            return text

    def _learn_from_correction(self, original: str, corrected: str) -> None:
        """Learn from corrections to improve future suggestions."""
        original_words = original.lower().split()
        corrected_words = corrected.lower().split()
        
        # Only learn if the words are similar enough
        for orig, corr in zip(original_words, corrected_words):
            if orig != corr and fuzz.ratio(orig, corr) > 60:
                self.user_dictionary[corr] += 1

    def _preserve_case(self, original: str, corrected: str) -> str:
        """Preserve the case pattern of the original word."""
        if not self.preserve_case:
            return corrected
            
        if original.isupper():
            return corrected.upper()
        elif original.islower():
            return corrected.lower()
        elif original[0].isupper():
            return corrected.capitalize()
        return corrected

    def get_correction_stats(self) -> Dict[str, Any]:
        """Get statistics about the correction process."""
        return {
            "total_corrections": self.total_corrections,
            "cache_hits": self.cache_hits,
            "cache_hit_ratio": self.cache_hits / max(1, self.total_corrections),
            "dictionary_size": len(self.user_dictionary),
            "context_size": len(self.context_window)
        }

    def set_model(self, model: str) -> None:
        """Set the OpenAI model to use for corrections."""
        self.model = model

    def set_learning_enabled(self, enabled: bool) -> None:
        """Enable or disable learning from corrections."""
        self.learning_enabled = enabled

    def set_confidence_threshold(self, threshold: float) -> None:
        """Set the confidence threshold for suggestions."""
        self.confidence_threshold = max(0.0, min(1.0, threshold))

    def clear_cache(self) -> None:
        """Clear the correction cache."""
        self.cache.clear()
        self.cache_hits = 0
        self.total_corrections = 0

    def _get_best_suggestion(self, word: str) -> List[str]:
        """Get the best spelling suggestions using multiple methods."""
        suggestions = []
        
        # Get enchant suggestions
        enchant_suggestions = self.dictionary.suggest(word)
        if enchant_suggestions:
            suggestions.extend(enchant_suggestions[:3])
            
        # Add keyboard proximity suggestions
        proximity_suggestions = self._get_proximity_suggestions(word)
        if proximity_suggestions:
            suggestions.extend(proximity_suggestions[:2])
            
        # Sort by similarity to original word
        return sorted(set(suggestions), 
                     key=lambda x: fuzz.ratio(word.lower(), x.lower()),
                     reverse=True)

    def _get_proximity_suggestions(self, word: str) -> List[str]:
        """Get suggestions based on keyboard proximity."""
        suggestions = set()
        
        # Generate variations based on keyboard layout
        for i, char in enumerate(word):
            if char.lower() in self.keyboard_layout:
                for nearby in self.keyboard_layout[char.lower()]:
                    variation = word[:i] + nearby + word[i+1:]
                    if self.dictionary.check(variation):
                        suggestions.add(variation)
                        
        return list(suggestions)

    def _update_context(self, text: str):
        """Update the context window with new text."""
        self.context_window.append(text)
        if len(self.context_window) > self.max_context_length:
            self.context_window.pop(0)

    def set_correction_mode(self, mode: str):
        """Set the correction mode."""
        try:
            if mode in ["standard", "strict", "creative", "ai"]:
                self.correction_mode = mode
                logger.info(f"Correction mode set to {mode}")
        except Exception as e:
            logger.error(f"Error setting correction mode: {e}", exc_info=True)
            raise

    def set_correction_severity(self, severity: float):
        """Set the correction severity."""
        try:
            if not 0 <= severity <= 1:
                raise ValueError("Severity must be between 0 and 1")
            self.correction_severity = severity
            logger.info(f"Correction severity set to {severity}")
        except Exception as e:
            logger.error(f"Error setting correction severity: {e}", exc_info=True)
            raise
