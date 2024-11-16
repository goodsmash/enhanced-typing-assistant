"""Dictionary management for text correction"""

import os
import logging
import re
from typing import Dict, List, Optional, Set, Tuple, Any
from pathlib import Path
import json
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from functools import lru_cache
from rapidfuzz import fuzz, process
from .utils import calculate_edit_distance

logger = logging.getLogger(__name__)

class CorrectionResult:
    """Structured class for correction results"""
    def __init__(self, original: str, correction: str, confidence: float):
        self.original = original
        self.correction = correction
        self.confidence = confidence

class DictionaryManager:
    def __init__(
        self,
        dict_dir: str = "resources/dictionaries",
        min_confidence: float = 0.8,
        max_suggestions: int = 5,
        use_cache: bool = True,
        domain: Optional[str] = None,
        max_workers: int = 4
    ):
        """Initialize dictionary manager.
        
        Args:
            dict_dir: Directory containing dictionary files
            min_confidence: Minimum confidence score for suggestions
            max_suggestions: Maximum number of suggestions per word
            use_cache: Whether to cache corrections
            domain: Optional domain for specialized corrections
            max_workers: Maximum number of worker threads for parallel processing
        """
        self.dict_dir = Path(dict_dir)
        self.min_confidence = min_confidence
        self.max_suggestions = max_suggestions
        self.use_cache = use_cache
        self.domain = domain
        self.max_workers = max_workers
        
        # Initialize thread pool
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        
        # Initialize dictionaries with type hints
        self.corrections: Dict[str, Tuple[str, float]] = {}
        self.word_forms: Dict[str, Set[str]] = defaultdict(set)
        self.domain_corrections: Dict[str, Dict[str, Tuple[str, float]]] = {}
        self.cache: Dict[str, List[Tuple[str, float]]] = {}
        self.context_patterns: Dict[str, List[str]] = defaultdict(list)
        
        # Security settings
        self.max_word_length = 50
        self.min_confidence_threshold = 0.5
        self.blocked_patterns = [
            r'[<>]',  # HTML/XML tags
            r'[{}]',  # Code blocks
            r'[$`]',  # Shell commands
            r'^/',    # File paths
            r'^http', # URLs
            r'^!',    # Command prefixes
            r'^\s*#', # Comments/directives
            r'[\x00-\x1F\x7F]',  # Control characters
            r'(?i)(?:javascript|vbscript):', # Script injection
            r'(?i)(?:data|file):', # Protocol injection
        ]
        
        # Advanced features
        self.use_contextual_boost = True
        self.context_boost_factor = 0.1
        self.domain_boost_factor = 0.15
        self.frequency_weight = 0.7
        self.similarity_weight = 0.3
        
        # Performance optimization
        self._init_caches()
        
        # Load dictionaries
        self._load_dictionaries()
    
    def _init_caches(self):
        """Initialize LRU caches for frequently used methods"""
        self.get_correction = lru_cache(maxsize=10000)(self.get_correction)
        self.get_suggestions = lru_cache(maxsize=5000)(self.get_suggestions)
        self._get_contextual_confidence = lru_cache(maxsize=1000)(self._get_contextual_confidence)
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any):
        self.cleanup()
    
    def cleanup(self):
        """Clean up resources"""
        if hasattr(self, 'executor'):
            self.executor.shutdown(wait=True)
        self.clear_cache()
    
    def _load_dictionaries(self):
        """Load all dictionary files."""
        try:
            # Parallel dictionary loading
            dict_files = [
                ("common_misspellings.txt", self._load_dict_file),
                ("internet_slang.txt", self._load_dict_file)
            ]
            
            # Add domain-specific dictionaries
            domain_dir = self.dict_dir / "domain_specific"
            if domain_dir.exists():
                for dict_file in domain_dir.glob("*.txt"):
                    dict_files.append((dict_file.name, 
                                     lambda f: self._load_domain_dict(dict_file.stem, dict_file)))
            
            # Load dictionaries in parallel
            futures = []
            for filename, load_func in dict_files:
                futures.append(self.executor.submit(load_func, filename))
            
            # Wait for all loading to complete
            for future in futures:
                future.result()
            
            logger.info(f"Loaded {len(self.corrections)} corrections and {len(self.word_forms)} word forms")
            logger.info(f"Loaded domain dictionaries: {list(self.domain_corrections.keys())}")
            
        except Exception as e:
            logger.error(f"Error loading dictionaries: {e}")
            raise
    
    def _load_domain_dict(self, domain: str, filepath: Path):
        """Load a domain-specific dictionary.
        
        Args:
            domain: Domain name
            filepath: Path to dictionary file
        """
        try:
            domain_dict = {}
            with open(filepath, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue
                        
                    parts = line.split('\t')
                    if len(parts) >= 2:
                        word = parts[0].lower()
                        correction = parts[1].lower()
                        confidence = float(parts[2]) if len(parts) > 2 else 1.0
                        
                        domain_dict[word] = (correction, confidence)
                        
            self.domain_corrections[domain] = domain_dict
            logger.info(f"Loaded {len(domain_dict)} corrections for domain: {domain}")
            
        except Exception as e:
            logger.error(f"Error loading domain dictionary {filepath}: {e}")
            
    def _load_dict_file(self, filename: str):
        """Load a single dictionary file.
        
        Args:
            filename: Name of dictionary file
        """
        filepath = self.dict_dir / filename
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue
                        
                    parts = line.split('\t')
                    if len(parts) >= 2:
                        word = parts[0].lower()
                        correction = parts[1].lower()
                        confidence = float(parts[2]) if len(parts) > 2 else 1.0
                        
                        # Add to corrections dictionary
                        self.corrections[word] = (correction, confidence)
                        
                        # Add to word forms
                        self.word_forms[correction].add(word)
                        
        except Exception as e:
            logger.error(f"Error loading dictionary file {filename}: {e}")
            
    def _is_safe_text(self, text: str) -> bool:
        """Check if text is safe for correction.
        
        Args:
            text: Text to check
            
        Returns:
            bool: True if text is safe, False otherwise
        """
        # Length check
        if len(text) > self.max_word_length:
            logger.warning(f"Text exceeds maximum length: {text}")
            return False
            
        # Pattern checks
        for pattern in self.blocked_patterns:
            if re.search(pattern, text):
                logger.warning(f"Text matches blocked pattern: {text}")
                return False
                
        # Character set check
        if not text.isprintable():
            logger.warning(f"Text contains non-printable characters: {text}")
            return False
            
        return True
        
    def _sanitize_text(self, text: str) -> str:
        """Sanitize text for safe processing.
        
        Args:
            text: Text to sanitize
            
        Returns:
            str: Sanitized text
        """
        # Convert to lowercase
        text = text.lower()
        
        # Remove excess whitespace
        text = ' '.join(text.split())
        
        # Remove special characters
        text = re.sub(r'[^a-z0-9\s\-]', '', text)
        
        return text
        
    def _get_domain_correction(
        self,
        word: str,
        domain: Optional[str] = None
    ) -> Optional[Tuple[str, float]]:
        """Get domain-specific correction for a word.
        
        Args:
            word: Word to correct
            domain: Optional domain override
            
        Returns:
            Tuple of (correction, confidence) or None
        """
        target_domain = domain or self.domain
        if not target_domain or target_domain not in self.domain_corrections:
            return None
            
        domain_dict = self.domain_corrections[target_domain]
        if word in domain_dict:
            correction, confidence = domain_dict[word]
            # Apply domain boost
            confidence = min(1.0, confidence + self.domain_boost_factor)
            return correction, confidence
            
        return None
        
    def _get_contextual_confidence(
        self,
        word: str,
        correction: str,
        context: Optional[str] = None
    ) -> float:
        """Calculate contextual confidence boost.
        
        Args:
            word: Original word
            correction: Proposed correction
            context: Optional context string
            
        Returns:
            float: Confidence boost factor
        """
        if not context or not self.use_contextual_boost:
            return 0.0
            
        boost = 0.0
        context = context.lower()
        
        # Check for domain-specific context patterns
        if self.domain and self.domain in self.context_patterns:
            for pattern in self.context_patterns[self.domain]:
                if pattern in context:
                    boost += self.context_boost_factor
                    
        # Check for correction-specific context
        if correction in self.word_forms:
            related_forms = self.word_forms[correction]
            for form in related_forms:
                if form in context:
                    boost += self.context_boost_factor
                    
        return min(self.context_boost_factor, boost)
        
    def get_correction(
        self,
        word: str,
        context: Optional[str] = None,
        domain: Optional[str] = None
    ) -> Optional[CorrectionResult]:
        """Get the correction for a word with improved error handling and validation.
        
        Args:
            word: Word to correct
            context: Optional context string
            domain: Optional domain override
            
        Returns:
            CorrectionResult object or None if no correction found
        
        Raises:
            ValueError: If word is invalid or unsafe
        """
        try:
            # Input validation
            if not word or not isinstance(word, str):
                raise ValueError("Invalid word input")
            
            # Security checks
            if not self._is_safe_text(word):
                raise ValueError("Unsafe word input")
            
            word = self._sanitize_text(word)
            
            # Check cache first
            cache_key = f"{word}:{domain or self.domain}"
            if self.use_cache and cache_key in self.cache:
                correction, confidence = self.cache[cache_key][0]
                return CorrectionResult(word, correction, confidence)
            
            # Get domain-specific correction
            domain_result = self._get_domain_correction(word, domain)
            if domain_result:
                correction, base_confidence = domain_result
                
                # Apply contextual boost
                if context and self.use_contextual_boost:
                    boost = self._get_contextual_confidence(word, correction, context)
                    confidence = min(1.0, base_confidence + boost)
                else:
                    confidence = base_confidence
                
                # Cache result
                if self.use_cache:
                    self.cache[cache_key] = [(correction, confidence)]
                
                return CorrectionResult(word, correction, confidence)
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting correction for word '{word}': {e}")
            return None
        
    def get_suggestions(
        self,
        word: str,
        context: Optional[str] = None,
        domain: Optional[str] = None,
        max_distance: int = 2
    ) -> List[Tuple[str, float]]:
        """Get suggested corrections for a word.
        
        Args:
            word: Word to get suggestions for
            context: Optional context string
            domain: Optional domain override
            max_distance: Maximum edit distance for suggestions
            
        Returns:
            List of (correction, confidence) tuples
        """
        word = word.lower()
        suggestions = []
        
        # Check cache
        cache_key = f"{word}:{domain or self.domain}"
        if self.use_cache and cache_key in self.cache:
            return self.cache[cache_key]
            
        # Try domain-specific suggestions first
        if domain or self.domain:
            target_domain = domain or self.domain
            if target_domain in self.domain_corrections:
                domain_dict = self.domain_corrections[target_domain]
                for correct_word, (_, base_confidence) in domain_dict.items():
                    distance = calculate_edit_distance(word, correct_word)
                    if distance <= max_distance:
                        similarity = 1.0 - (distance / max(len(word), len(correct_word)))
                        similarity *= fuzz.ratio(word, correct_word) / 100.0
                        
                        # Combine frequency and similarity scores
                        confidence = (
                            self.frequency_weight * base_confidence +
                            self.similarity_weight * similarity +
                            self.domain_boost_factor
                        )
                        
                        if confidence >= self.min_confidence_threshold:
                            suggestions.append((correct_word, confidence))
                            
        # Find general corrections
        for correct_word in self.word_forms.keys():
            distance = calculate_edit_distance(word, correct_word)
            if distance <= max_distance:
                # Calculate base similarity score
                similarity = 1.0 - (distance / max(len(word), len(correct_word)))
                similarity *= fuzz.ratio(word, correct_word) / 100.0
                
                # Get base confidence from corrections dict
                base_confidence = 0.8  # Default if not in corrections
                for form in self.word_forms[correct_word]:
                    if form in self.corrections:
                        base_confidence = self.corrections[form][1]
                        break
                        
                # Apply contextual boost
                context_boost = self._get_contextual_confidence(word, correct_word, context)
                
                # Combine all scores
                confidence = (
                    self.frequency_weight * base_confidence +
                    self.similarity_weight * similarity +
                    context_boost
                )
                
                if confidence >= self.min_confidence_threshold:
                    suggestions.append((correct_word, confidence))
                    
        # Sort by confidence and limit results
        suggestions.sort(key=lambda x: x[1], reverse=True)
        suggestions = suggestions[:self.max_suggestions]
        
        if self.use_cache:
            self.cache[cache_key] = suggestions
            
        return suggestions
        
    def add_correction(
        self,
        word: str,
        correction: str,
        confidence: float = 1.0
    ):
        """Add a new correction to the dictionary.
        
        Args:
            word: Incorrect word
            correction: Correct word
            confidence: Confidence score
        """
        word = word.lower()
        correction = correction.lower()
        
        self.corrections[word] = (correction, confidence)
        self.word_forms[correction].add(word)
        
        if self.use_cache and word in self.cache:
            del self.cache[word]
            
    def save_custom_corrections(
        self,
        filepath: str
    ):
        """Save custom corrections to file.
        
        Args:
            filepath: Path to save corrections
        """
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                for word, (correction, confidence) in self.corrections.items():
                    f.write(f"{word}\t{correction}\t{confidence:.2f}\n")
                    
            logger.info(f"Saved {len(self.corrections)} corrections to {filepath}")
            
        except Exception as e:
            logger.error(f"Error saving corrections: {e}")
            
    def load_custom_corrections(
        self,
        filepath: str
    ):
        """Load custom corrections from file.
        
        Args:
            filepath: Path to corrections file
        """
        try:
            self._load_dict_file(filepath)
            logger.info(f"Loaded custom corrections from {filepath}")
            
        except Exception as e:
            logger.error(f"Error loading custom corrections: {e}")
            
    def clear_cache(self):
        """Clear the correction cache."""
        self.cache.clear()
