"""
Text processor using GECToR for real-time grammatical error correction
"""

import asyncio
from typing import List, Dict, Optional, Tuple
import logging
from .model import GECToRModel

logger = logging.getLogger(__name__)

class GECProcessor:
    def __init__(
        self,
        model_name: str = "roberta-base",
        batch_size: int = 32,
        max_length: int = 128,
        confidence_bias: float = 0.2,
        min_error_prob: float = 0.5,
        cache_size: int = 1000
    ):
        """Initialize GEC processor for real-time text correction.
        
        Args:
            model_name: Name of the pretrained transformer model
            batch_size: Batch size for processing
            max_length: Maximum sequence length
            confidence_bias: Confidence bias for error detection
            min_error_prob: Minimum probability threshold for error detection
            cache_size: Size of correction cache
        """
        self.batch_size = batch_size
        self.max_length = max_length
        self._cache = {}
        self._cache_size = cache_size
        
        try:
            self.model = GECToRModel(
                model_name=model_name,
                confidence_bias=confidence_bias,
                min_error_prob=min_error_prob
            )
            logger.info("Initialized GEC processor")
        except Exception as e:
            logger.error(f"Failed to initialize GEC processor: {e}")
            raise
    
    async def process_text(
        self,
        text: str,
        use_cache: bool = True
    ) -> Tuple[str, List[Dict]]:
        """Process text for grammatical errors asynchronously.
        
        Args:
            text: Input text to correct
            use_cache: Whether to use correction cache
            
        Returns:
            Tuple of (corrected_text, list of corrections)
        """
        try:
            # Check cache first
            if use_cache and text in self._cache:
                logger.debug("Using cached correction")
                return self._cache[text]
            
            # Process text in chunks for real-time correction
            chunks = self._split_into_chunks(text)
            corrected_chunks = []
            all_corrections = []
            
            for chunk in chunks:
                corrected_chunk, corrections = await self._process_chunk(chunk)
                corrected_chunks.append(corrected_chunk)
                all_corrections.extend(corrections)
            
            corrected_text = " ".join(corrected_chunks)
            
            # Update cache
            if use_cache:
                self._update_cache(text, (corrected_text, all_corrections))
            
            return corrected_text, all_corrections
            
        except Exception as e:
            logger.error(f"Error in text processing: {e}")
            return text, []
    
    async def _process_chunk(
        self,
        chunk: str
    ) -> Tuple[str, List[Dict]]:
        """Process a single chunk of text."""
        try:
            # Run model prediction in executor to avoid blocking
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                self.model.predict,
                chunk,
                self.batch_size,
                self.max_length
            )
            return result
        except Exception as e:
            logger.error(f"Error processing chunk: {e}")
            return chunk, []
    
    def _split_into_chunks(self, text: str) -> List[str]:
        """Split text into processable chunks."""
        # Simple sentence-based splitting for now
        # TODO: Implement more sophisticated splitting
        sentences = text.split('. ')
        chunks = []
        current_chunk = []
        current_length = 0
        
        for sentence in sentences:
            sentence_length = len(sentence.split())
            if current_length + sentence_length > self.max_length:
                if current_chunk:
                    chunks.append('. '.join(current_chunk) + '.')
                current_chunk = [sentence]
                current_length = sentence_length
            else:
                current_chunk.append(sentence)
                current_length += sentence_length
        
        if current_chunk:
            chunks.append('. '.join(current_chunk))
        
        return chunks
    
    def _update_cache(
        self,
        text: str,
        result: Tuple[str, List[Dict]]
    ):
        """Update the correction cache."""
        if len(self._cache) >= self._cache_size:
            # Remove oldest entry
            self._cache.pop(next(iter(self._cache)))
        self._cache[text] = result
