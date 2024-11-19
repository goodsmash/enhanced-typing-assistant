import os
import time
import asyncio
from openai import OpenAI
from dotenv import load_dotenv
import re
from typing import Dict, List, Optional, Tuple
import enchant
from collections import defaultdict
import logging

# Load environment variables
load_dotenv()

# Initialize logger
logger = logging.getLogger(__name__)

class TextCorrector:
    def __init__(self):
        self.client = OpenAI()
        self.assistant_id = "asst_tXilod6dvj2WtdMO3u6zpDLj"
        
        # LRU Cache for correction results
        self.correction_cache = {}
        self.max_cache_size = 1000
        self.cache_hits = 0
        self.cache_misses = 0
        
        # Performance monitoring
        self.total_corrections = 0
        self.total_processing_time = 0
        self.error_count = 0
        self.last_performance_check = time.time()
        
        # Initialize keyboard layout and patterns
        self.keyboard_layout = {
            'q': ['w', 'a', '1'], 'w': ['q', 'e', 's', '2'], 'e': ['w', 'r', 'd', '3'],
            'r': ['e', 't', 'f', '4'], 't': ['r', 'y', 'g', '5'], 'y': ['t', 'u', 'h', '6'],
            'u': ['y', 'i', 'j', '7'], 'i': ['u', 'o', 'k', '8'], 'o': ['i', 'p', 'l', '9'],
            'p': ['o', '[', ';', '0'], 'a': ['q', 's', 'z'], 's': ['w', 'a', 'd', 'x'],
            'd': ['e', 's', 'f', 'c'], 'f': ['r', 'd', 'g', 'v'], 'g': ['t', 'f', 'h', 'b'],
            'h': ['y', 'g', 'j', 'n'], 'j': ['u', 'h', 'k', 'm'], 'k': ['i', 'j', 'l', ','],
            'l': ['o', 'k', ';', '.'], 'z': ['a', 'x'], 'x': ['s', 'z', 'c'],
            'c': ['d', 'x', 'v'], 'v': ['f', 'c', 'b'], 'b': ['g', 'v', 'n'],
            'n': ['h', 'b', 'm'], 'm': ['j', 'n', ','], ',': ['k', 'm', '.'],
            '.': ['l', ',', '/'], '/': ['.', "'"]
        }
        
        # Common cognitive-related typing patterns
        self.cognitive_patterns = {
            'letter_swaps': [('ie', 'ei'), ('ou', 'uo'), ('th', 'ht'), ('ch', 'hc')],
            'phonetic_errors': {
                'f': ['ph'], 'i': ['ee', 'ea'], 'a': ['ay', 'ai'],
                'k': ['c', 'ch'], 's': ['c', 'ss'], 'shun': ['tion', 'sion']
            },
            'common_substitutions': {
                'their': ['thier', 'thear', 'ther'],
                'because': ['becuase', 'becasue', 'becouse'],
                'would': ['wuold', 'wold', 'whould'],
                'should': ['shuold', 'shoud', 'shold'],
                'could': ['cuold', 'coud', 'chold'],
                'were': ['wer', 'where', 'whre'],
                'have': ['hve', 'hav', 'ahve'],
                'want': ['wnat', 'watn', 'wnat'],
                'going': ['goin', 'goign', 'ggoing'],
                'with': ['wiht', 'whit', 'whit'],
                'computer': ['compter', 'computr', 'conputer'],
                'mental': ['mantal', 'mentl', 'mentel'],
                'health': ['helth', 'healht', 'heatlh'],
                'focus': ['focsu', 'foucs', 'focuse'],
                'months': ['monthes', 'mounths', 'monts'],
                'accident': ['accidnet', 'acident', 'axident'],
                'trouble': ['truoble', 'truble', 'troble']
            }
        }
        
        # Initialize spell checker
        self.spell_checker = enchant.Dict("en_US")
        
    async def correct_text(self, text: str, mode: str = "comprehensive", severity: str = "medium", language: str = "English") -> str:
        """
        Correct text using the OpenAI Assistant with improved caching and performance monitoring.
        """
        try:
            start_time = time.time()
            self.total_corrections += 1
            
            # Check cache first
            cache_key = f"{text}:{mode}:{severity}:{language}"
            if cache_key in self.correction_cache:
                self.cache_hits += 1
                return self.correction_cache[cache_key]
            
            self.cache_misses += 1
            
            # Input validation with detailed error messages
            if not text or not isinstance(text, str):
                raise ValueError("Invalid input text: Text must be a non-empty string")
                
            if mode not in ["spelling", "grammar", "clarity", "comprehensive"]:
                logger.warning(f"Invalid mode '{mode}', defaulting to comprehensive")
                mode = "comprehensive"
                
            if severity not in ["low", "medium", "high"]:
                logger.warning(f"Invalid severity '{severity}', defaulting to medium")
                severity = "medium"
            
            # Create a thread with timeout handling
            try:
                thread = await asyncio.wait_for(
                    self.client.beta.threads.create(),
                    timeout=10.0
                )
            except asyncio.TimeoutError:
                raise TimeoutError("Thread creation timed out")
            
            # Add message with improved error handling
            try:
                message = await asyncio.wait_for(
                    self.client.beta.threads.messages.create(
                        thread_id=thread.id,
                        role="user",
                        content=self._build_correction_prompt(text, mode, severity, language)
                    ),
                    timeout=10.0
                )
            except asyncio.TimeoutError:
                raise TimeoutError("Message creation timed out")
            
            # Run assistant with monitoring
            try:
                run = await asyncio.wait_for(
                    self.client.beta.threads.runs.create(
                        thread_id=thread.id,
                        assistant_id=self.assistant_id
                    ),
                    timeout=30.0
                )
                
                # Monitor run status with timeout
                start_wait = time.time()
                while True:
                    if time.time() - start_wait > 60:  # 1 minute timeout
                        raise TimeoutError("Assistant run timed out")
                        
                    run_status = await self.client.beta.threads.runs.retrieve(
                        thread_id=thread.id,
                        run_id=run.id
                    )
                    
                    if run_status.status == 'completed':
                        break
                    elif run_status.status in ['failed', 'cancelled']:
                        raise RuntimeError(f"Assistant run failed with status: {run_status.status}")
                        
                    await asyncio.sleep(1)
                
                # Get messages with timeout
                messages = await asyncio.wait_for(
                    self.client.beta.threads.messages.list(thread_id=thread.id),
                    timeout=10.0
                )
                
                # Process result
                corrected_text = messages.data[0].content[0].text.value
                
                # Update cache with LRU eviction
                if len(self.correction_cache) >= self.max_cache_size:
                    self.correction_cache.pop(next(iter(self.correction_cache)))
                self.correction_cache[cache_key] = corrected_text
                
                # Update performance metrics
                end_time = time.time()
                self.total_processing_time += (end_time - start_time)
                
                # Log performance stats periodically
                if end_time - self.last_performance_check > 3600:  # Every hour
                    self._log_performance_metrics()
                    self.last_performance_check = end_time
                
                return corrected_text
                
            except asyncio.TimeoutError:
                raise TimeoutError("Assistant processing timed out")
                
        except Exception as e:
            self.error_count += 1
            logger.error(f"Text correction error: {str(e)}")
            raise
            
    def _build_correction_prompt(self, text: str, mode: str, severity: str, language: str) -> str:
        """Build a detailed correction prompt based on mode and severity."""
        return (
            f"Please correct this {language} text with the following parameters:\n"
            f"Mode: {mode} - Focus on {self._get_mode_description(mode)}\n"
            f"Severity: {severity} - {self._get_severity_description(severity)}\n\n"
            f"Text to correct: {text}"
        )
        
    def _get_mode_description(self, mode: str) -> str:
        """Get detailed description for correction mode."""
        descriptions = {
            "spelling": "basic spelling corrections while preserving original structure",
            "grammar": "grammatical improvements and sentence structure",
            "clarity": "clarity and readability improvements",
            "comprehensive": "complete text improvement including spelling, grammar, and clarity"
        }
        return descriptions.get(mode, descriptions["comprehensive"])
        
    def _get_severity_description(self, severity: str) -> str:
        """Get detailed description for correction severity."""
        descriptions = {
            "low": "make minimal necessary corrections",
            "medium": "balance between correction and preserving original style",
            "high": "thorough correction with significant improvements"
        }
        return descriptions.get(severity, descriptions["medium"])
        
    def _log_performance_metrics(self):
        """Log performance metrics for monitoring."""
        if self.total_corrections > 0:
            avg_time = self.total_processing_time / self.total_corrections
            cache_hit_rate = (self.cache_hits / self.total_corrections) * 100
            error_rate = (self.error_count / self.total_corrections) * 100
            
            logger.info(
                f"Performance Metrics:\n"
                f"Total Corrections: {self.total_corrections}\n"
                f"Average Processing Time: {avg_time:.2f}s\n"
                f"Cache Hit Rate: {cache_hit_rate:.1f}%\n"
                f"Error Rate: {error_rate:.1f}%"
            )
            
    async def cleanup(self):
        """Clean up any resources"""
        pass  # Add cleanup code if needed
        
    def split_preserve_spacing(self, text: str) -> List[Tuple[str, str]]:
        """Split text into words while preserving spacing"""
        words = []
        current_word = ""
        current_space = ""
        
        for char in text:
            if char.isspace():
                if current_word:
                    words.append((current_word, current_space))
                    current_word = ""
                current_space += char
            else:
                if current_space and not current_word:
                    words.append(("", current_space))
                    current_space = ""
                current_word += char
                
        if current_word or current_space:
            words.append((current_word, current_space))
            
        return words
        
    def post_tbi_correction(self, word: str) -> str:
        """
        Specialized correction for post-traumatic brain injury typing patterns
        """
        if not word:
            return ""
            
        # Check common substitutions first
        lower_word = word.lower()
        if lower_word in self.cognitive_patterns['common_substitutions']:
            return word
            
        # Look for repeated characters (common in TBI typing)
        word = re.sub(r'(.)\1{2,}', r'\1\1', word)
        
        # Check for adjacent key hits (spatial awareness issues)
        corrected = self.check_adjacent_keys(word)
        if corrected != word:
            return corrected
            
        # Apply cognitive correction patterns
        corrected = self.cognitive_correction(word)
        
        return corrected
        
    def motor_difficulty_correction(self, word: str) -> str:
        """
        Correct common motor difficulty typing patterns
        """
        if not word:
            return ""
            
        # Remove unintended repeated characters
        word = re.sub(r'(.)\1{2,}', r'\1', word)
        
        # Check for adjacent key errors
        candidates = self.generate_adjacent_candidates(word)
        
        # Find the most likely correct word
        best_candidate = word
        best_score = float('inf')
        
        for candidate in candidates:
            if self.spell_checker.check(candidate):
                # Use Levenshtein distance to score candidates
                score = self.levenshtein_distance(candidate, word)
                if score < best_score:
                    best_score = score
                    best_candidate = candidate
                    
        return best_candidate
        
    def cognitive_correction(self, word: str) -> str:
        """
        Apply cognitive-specific correction patterns
        """
        if not word:
            return ""
            
        # Check common substitutions
        lower_word = word.lower()
        for correct, variants in self.cognitive_patterns['common_substitutions'].items():
            if lower_word in variants:
                return correct
                
        # Apply letter swap corrections
        for swap_from, swap_to in self.cognitive_patterns['letter_swaps']:
            if swap_from in word:
                word = word.replace(swap_from, swap_to)
                
        # Apply phonetic corrections
        for sound, variants in self.cognitive_patterns['phonetic_errors'].items():
            for variant in variants:
                if variant in word:
                    word = word.replace(variant, sound)
                    
        return word
        
    def generate_adjacent_candidates(self, word: str) -> List[str]:
        """
        Generate possible corrections based on adjacent keyboard keys
        """
        candidates = set()
        
        # For each position in the word
        for i in range(len(word)):
            # Get adjacent keys for the current letter
            if word[i].lower() in self.keyboard_layout:
                adjacent_keys = self.keyboard_layout[word[i].lower()]
                
                # Create variations with each adjacent key
                for adj_key in adjacent_keys:
                    candidate = word[:i] + adj_key + word[i+1:]
                    candidates.add(candidate)
                    
        return list(candidates)
        
    def levenshtein_distance(self, s1: str, s2: str) -> int:
        """
        Calculate the Levenshtein distance between two strings
        """
        if len(s1) < len(s2):
            return self.levenshtein_distance(s2, s1)
            
        if len(s2) == 0:
            return len(s1)
            
        previous_row = range(len(s2) + 1)
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row
            
        return previous_row[-1]
        
    def standard_correction(self, word: str) -> str:
        """
        Apply standard spell checking correction
        """
        if not word or not word.strip():
            return word
            
        if self.spell_checker.check(word):
            return word
            
        suggestions = self.spell_checker.suggest(word)
        return suggestions[0] if suggestions else word
        
    def check_adjacent_keys(self, word: str) -> str:
        """
        Check for adjacent key hits (spatial awareness issues)
        """
        # For each position in the word
        for i in range(len(word)):
            # Get adjacent keys for the current letter
            if word[i].lower() in self.keyboard_layout:
                adjacent_keys = self.keyboard_layout[word[i].lower()]
                
                # Check if any adjacent key is present in the word
                for adj_key in adjacent_keys:
                    if adj_key in word[i+1:]:
                        # Replace the adjacent key with the correct letter
                        word = word.replace(adj_key, word[i])
                        
        return word
