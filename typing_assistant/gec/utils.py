"""Utility functions for GEC module"""

import os
import torch
import logging
from typing import Dict, List, Optional, Tuple
from transformers import AutoTokenizer
import numpy as np
from .constants import ERROR_TYPES, CONFIDENCE_THRESHOLDS

logger = logging.getLogger(__name__)

def load_pretrained_model(
    model_path: str,
    device: str = "cuda" if torch.cuda.is_available() else "cpu"
) -> Tuple[torch.nn.Module, AutoTokenizer]:
    """Load a pretrained GECToR model and tokenizer.
    
    Args:
        model_path: Path to pretrained model
        device: Device to load model on
        
    Returns:
        Tuple of (model, tokenizer)
    """
    try:
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model path not found: {model_path}")
            
        # Load model and tokenizer
        model = torch.load(model_path, map_location=device)
        tokenizer = AutoTokenizer.from_pretrained(model.config._name_or_path)
        
        model.eval()
        return model, tokenizer
        
    except Exception as e:
        logger.error(f"Error loading pretrained model: {e}")
        raise

def apply_confidence_thresholds(
    predictions: Dict[str, float],
    error_type: str
) -> Optional[str]:
    """Apply confidence thresholds to model predictions.
    
    Args:
        predictions: Dictionary of prediction probabilities
        error_type: Type of error being corrected
        
    Returns:
        Selected prediction or None if below threshold
    """
    threshold = CONFIDENCE_THRESHOLDS.get(error_type, 0.9)
    
    # Get prediction with highest probability
    pred_type = max(predictions.items(), key=lambda x: x[1])
    
    if pred_type[1] >= threshold:
        return pred_type[0]
    return None

def get_error_corrections(
    token: str,
    error_type: str
) -> List[str]:
    """Get possible corrections for a given error type.
    
    Args:
        token: Token to correct
        error_type: Type of error
        
    Returns:
        List of possible corrections
    """
    corrections = ERROR_TYPES.get(error_type, [])
    
    if error_type == 'SPELL':
        # TODO: Implement spell check suggestions
        pass
    elif error_type == 'WO':
        # Word order handled by sequence labeling
        pass
        
    return corrections

def calculate_edit_distance(
    source: str,
    target: str
) -> int:
    """Calculate Levenshtein edit distance between strings."""
    if len(source) < len(target):
        return calculate_edit_distance(target, source)

    # Convert str2 to previous row.
    previous_row = range(len(target) + 1)
    for i, c1 in enumerate(source):
        current_row = [i + 1]
        for j, c2 in enumerate(target):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row
    
    return previous_row[-1]

def merge_corrections(
    corrections: List[Dict],
    max_distance: int = 2
) -> List[Dict]:
    """Merge nearby corrections to avoid overlapping edits.
    
    Args:
        corrections: List of correction dictionaries
        max_distance: Maximum token distance to merge
        
    Returns:
        List of merged corrections
    """
    if not corrections:
        return []
        
    # Sort by start position
    corrections = sorted(corrections, key=lambda x: x['start'])
    
    merged = []
    current = corrections[0]
    
    for next_corr in corrections[1:]:
        if next_corr['start'] - current['start'] <= max_distance:
            # Merge corrections
            current['end'] = next_corr['end']
            current['confidence'] = max(
                current['confidence'],
                next_corr['confidence']
            )
        else:
            merged.append(current)
            current = next_corr
            
    merged.append(current)
    return merged
