"""
GECToR model implementation for grammatical error correction
Based on the paper: GECToR – Grammatical Error Correction: Tag, Not Rewrite
"""

import torch
from transformers import AutoModel, AutoTokenizer, PreTrainedModel
from typing import List, Tuple, Dict, Optional, Union
import logging
from .constants import DEFAULT_MODEL_CONFIGS, ERROR_TYPES, CONFIDENCE_THRESHOLDS
from .utils import (
    load_pretrained_model,
    apply_confidence_thresholds,
    get_error_corrections,
    merge_corrections
)

logger = logging.getLogger(__name__)

class GECToRModel:
    def __init__(
        self,
        model_name: str = "roberta-base",
        pretrained_path: Optional[str] = None,
        device: str = "cuda" if torch.cuda.is_available() else "cpu",
        confidence_bias: float = 0.2,
        min_error_prob: float = 0.5,
    ):
        """Initialize GECToR model for grammatical error correction.
        
        Args:
            model_name: Name of the pretrained transformer model
            pretrained_path: Path to pretrained GECToR model (optional)
            device: Device to run the model on ('cuda' or 'cpu')
            confidence_bias: Confidence bias for error detection
            min_error_prob: Minimum probability threshold for error detection
        """
        self.device = device
        self.confidence_bias = confidence_bias
        self.min_error_prob = min_error_prob
        
        try:
            if pretrained_path:
                # Load pretrained GECToR model
                self.model, self.tokenizer = load_pretrained_model(
                    pretrained_path,
                    device
                )
                logger.info(f"Loaded pretrained GECToR model from {pretrained_path}")
            else:
                # Initialize from base transformer
                self.tokenizer = AutoTokenizer.from_pretrained(model_name)
                self.model = AutoModel.from_pretrained(model_name).to(device)
                logger.info(f"Initialized base model with {model_name}")
                
            # Get model config
            model_type = 'roberta' if 'roberta' in model_name else 'xlnet'
            self.config = DEFAULT_MODEL_CONFIGS[model_type]
            
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            raise
        
    def predict(
        self,
        text: str,
        batch_size: int = 32,
        max_length: int = 128
    ) -> Tuple[str, List[Dict]]:
        """Predict and apply corrections to input text.
        
        Args:
            text: Input text to correct
            batch_size: Batch size for processing
            max_length: Maximum sequence length
            
        Returns:
            Tuple of (corrected_text, list of corrections)
        """
        try:
            # Tokenize input
            tokens = self.tokenizer.tokenize(text)
            if len(tokens) > max_length:
                logger.warning(f"Input text truncated from {len(tokens)} to {max_length} tokens")
                tokens = tokens[:max_length]
            
            # Convert to model inputs
            inputs = self.tokenizer.encode_plus(
                tokens,
                return_tensors="pt",
                padding=True,
                truncation=True,
                max_length=max_length
            ).to(self.device)
            
            # Get model predictions
            with torch.no_grad():
                outputs = self.model(**inputs)
                
                # Get logits for error detection and correction
                error_logits = outputs[0]  # [batch_size, seq_len, num_error_types]
                correction_logits = outputs[1]  # [batch_size, seq_len, vocab_size]
                
                # Apply confidence thresholds
                error_probs = torch.softmax(error_logits, dim=-1)
                correction_probs = torch.softmax(correction_logits, dim=-1)
                
            # Decode predictions and get corrections
            corrections = self._decode_predictions(
                tokens,
                error_probs[0],
                correction_probs[0]
            )
            
            # Merge nearby corrections
            corrections = merge_corrections(corrections)
            
            # Apply corrections to text
            corrected_text = self._apply_corrections(text, corrections)
            
            return corrected_text, corrections
            
        except Exception as e:
            logger.error(f"Error in prediction: {e}")
            return text, []
            
    def _decode_predictions(
        self,
        tokens: List[str],
        error_probs: torch.Tensor,
        correction_probs: torch.Tensor
    ) -> List[Dict]:
        """Decode model predictions into edit operations."""
        corrections = []
        
        for idx, (token, err_probs, corr_probs) in enumerate(
            zip(tokens, error_probs, correction_probs)
        ):
            # Check if token needs correction
            if err_probs.max().item() < self.min_error_prob + self.confidence_bias:
                continue
                
            # Get error type
            error_type = list(ERROR_TYPES.keys())[err_probs.argmax().item()]
            
            # Get correction candidates
            candidates = get_error_corrections(token, error_type)
            
            # Get best correction
            if candidates:
                candidate_probs = {
                    cand: corr_probs[self.tokenizer.convert_tokens_to_ids(cand)].item()
                    for cand in candidates
                }
                
                correction = apply_confidence_thresholds(candidate_probs, error_type)
                if correction:
                    corrections.append({
                        'start': idx,
                        'token': token,
                        'correction': correction,
                        'error_type': error_type,
                        'confidence': err_probs.max().item()
                    })
        
        return corrections
    
    def _apply_corrections(
        self,
        text: str,
        corrections: List[Dict]
    ) -> str:
        """Apply corrections to the input text."""
        if not corrections:
            return text
            
        # Sort corrections in reverse order
        corrections.sort(key=lambda x: x['start'], reverse=True)
        
        # Convert text to list for easier editing
        chars = list(text)
        
        for correction in corrections:
            start = correction['start']
            orig_token = correction['token']
            new_token = correction['correction']
            
            # Find token boundaries
            token_start = text.find(orig_token, max(0, start - len(orig_token)))
            if token_start == -1:
                continue
                
            token_end = token_start + len(orig_token)
            
            # Apply correction
            chars[token_start:token_end] = list(new_token)
        
        return ''.join(chars)
        
    def train(
        self,
        train_data: List[Tuple[str, str]],
        epochs: int = 5,
        batch_size: int = 32,
        learning_rate: float = 2e-5,
        max_grad_norm: float = 1.0,
        save_path: Optional[str] = None
    ):
        """Train the model on parallel text data.
        
        Args:
            train_data: List of (incorrect, correct) text pairs
            epochs: Number of training epochs
            batch_size: Training batch size
            learning_rate: Learning rate
            max_grad_norm: Maximum gradient norm for clipping
            save_path: Path to save trained model
        """
        # Training implementation to be added
        raise NotImplementedError("Training functionality to be implemented")
