import os
import time
import asyncio
from openai import OpenAI
from dotenv import load_dotenv
import re
from typing import Dict, List, Optional, Tuple
import enchant
from collections import defaultdict

# Load environment variables
load_dotenv()

class TextCorrector:
    def __init__(self):
        self.client = OpenAI()
        self.assistant_id = "asst_tXilod6dvj2WtdMO3u6zpDLj"
        
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
        Correct text using the OpenAI Assistant.
        
        Args:
            text (str): The text to correct
            mode (str): One of ["spelling", "grammar", "clarity", "comprehensive"]
            severity (str): One of ["low", "medium", "high"]
            language (str): The language of the text
            
        Returns:
            str: The corrected text
        """
        try:
            # Input validation
            if not text or not isinstance(text, str):
                raise ValueError("Invalid input text")
                
            if mode not in ["spelling", "grammar", "clarity", "comprehensive"]:
                mode = "comprehensive"
                
            if severity not in ["low", "medium", "high"]:
                severity = "medium"
            
            # Create a thread
            thread = await self.client.beta.threads.create()
            
            # Add the message to the thread
            message = await self.client.beta.threads.messages.create(
                thread_id=thread.id,
                role="user",
                content=f"Please correct this {language} text. Mode: {mode}, Severity: {severity}\n\nText: {text}"
            )
            
            # Run the assistant
            run = await self.client.beta.threads.runs.create(
                thread_id=thread.id,
                assistant_id=self.assistant_id
            )
            
            # Wait for completion with timeout
            timeout = 30  # 30 seconds timeout
            start_time = time.time()
            while True:
                run = await self.client.beta.threads.runs.retrieve(
                    thread_id=thread.id,
                    run_id=run.id
                )
                
                if run.status == "completed":
                    break
                elif run.status in ["failed", "cancelled", "expired"]:
                    raise Exception(f"Assistant run failed with status: {run.status}")
                elif time.time() - start_time > timeout:
                    await self.client.beta.threads.runs.cancel(
                        thread_id=thread.id,
                        run_id=run.id
                    )
                    raise TimeoutError("Assistant response timed out")
                    
                await asyncio.sleep(1)  # Wait 1 second before checking again
            
            # Get the assistant's response
            messages = await self.client.beta.threads.messages.list(
                thread_id=thread.id
            )
            
            if not messages.data:
                raise Exception("No response from assistant")
                
            # Return the corrected text from the assistant's last message
            corrected_text = messages.data[0].content[0].text.value
            
            # Clean up the thread
            await self.client.beta.threads.delete(thread.id)
            
            return corrected_text
            
        except Exception as e:
            print(f"Error in text correction: {str(e)}")
            return text  # Return original text if correction fails
            
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
