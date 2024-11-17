"""Text correction module with gender-inclusive support."""

import sys
import json
import argparse
import logging
from typing import List, Dict, Optional
from dictionary import DictionaryManager
from gender_inclusive import GenderInclusiveCorrector
from correction_result import CorrectionResult

class TextCorrector:
    """Handles text correction including gender-inclusive suggestions."""
    
    def __init__(self):
        """Initialize the text corrector with necessary components."""
        self.logger = logging.getLogger(__name__)
        self.dictionary_manager = DictionaryManager()
        self.gender_corrector = GenderInclusiveCorrector(self.dictionary_manager)
        
    def correct_text(self, text: str) -> CorrectionResult:
        """Apply all corrections to the input text.
        
        Args:
            text: Input text to correct
            
        Returns:
            CorrectionResult containing corrections and suggestions
        """
        try:
            # Get standard corrections
            base_result = self.dictionary_manager.correct_text(text)
            
            # Get gender-inclusive corrections
            gender_result = self.gender_corrector.correct_text(text)
            
            # Merge corrections, prioritizing gender-inclusive ones
            all_corrections = []
            used_spans = set()
            
            # Add gender-inclusive corrections first
            for corr in gender_result.corrections:
                span = (corr['start'], corr['end'])
                used_spans.add(span)
                all_corrections.append(corr)
            
            # Add non-overlapping standard corrections
            for corr in base_result.corrections:
                span = (corr['start'], corr['end'])
                if span not in used_spans:
                    all_corrections.append(corr)
            
            # Apply all corrections
            if all_corrections:
                corrected_text = text
                offset = 0
                for corr in sorted(all_corrections, key=lambda x: x['start']):
                    start = corr['start'] + offset
                    end = corr['end'] + offset
                    corrected_text = corrected_text[:start] + corr['suggestion'] + corrected_text[end:]
                    offset += len(corr['suggestion']) - (end - start)
            else:
                corrected_text = text
            
            return CorrectionResult(
                original_text=text,
                corrected_text=corrected_text,
                corrections=all_corrections,
                confidence=min(base_result.confidence, gender_result.confidence)
            )
            
        except Exception as e:
            self.logger.error(f"Error in text correction: {str(e)}")
            return CorrectionResult(
                original_text=text,
                corrected_text=text,
                corrections=[],
                confidence=1.0
            )
    
    def get_correction_suggestions(self, text: str) -> List[Dict]:
        """Get all correction suggestions without applying them.
        
        Args:
            text: Input text to analyze
            
        Returns:
            List of correction suggestions
        """
        result = self.correct_text(text)
        return result.corrections

def parse_args():
    parser = argparse.ArgumentParser(description='Text correction service')
    parser.add_argument('--text', required=True, help='Text to correct')
    parser.add_argument('--domain', default='general', help='Domain for correction')
    return parser.parse_args()

def main():
    args = parse_args()
    
    # Initialize text corrector
    corrector = TextCorrector()
    
    # Get corrections
    corrections = corrector.get_correction_suggestions(args.text)
    
    # Format corrections for JSON output
    formatted_corrections = [
        {
            'correction': corr['suggestion'],
            'confidence': corr.get('confidence', 1.0),
            'original': args.text[corr['start']:corr['end']]
        }
        for corr in corrections
    ]
    
    # Output as JSON
    print(json.dumps(formatted_corrections))

if __name__ == '__main__':
    main()
