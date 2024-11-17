"""Gender-inclusive grammatical error correction module."""

import logging
from pathlib import Path
from typing import Optional, Tuple, List, Dict
import spacy
from spacy.tokens import Doc, Token

from ..utils import load_model
from .dictionary import DictionaryManager
from .correction_result import CorrectionResult
from .language_config import LanguageConfig, ProgrammingLanguage
from .code_analyzer import CodeAnalyzer

class GenderInclusiveCorrector:
    """Handles gender-inclusive grammatical error correction."""
    
    def __init__(self, dictionary_manager: DictionaryManager):
        """Initialize the gender-inclusive corrector.
        
        Args:
            dictionary_manager: Instance of DictionaryManager for word lookups
        """
        self.logger = logging.getLogger(__name__)
        self.dictionary_manager = dictionary_manager
        
        # Initialize components
        self.language_config = LanguageConfig()
        self.code_analyzer = CodeAnalyzer()
        
        # Load spacy model
        try:
            self.nlp = spacy.load('en_core_web_lg')
        except OSError:
            self.logger.info("Downloading spaCy model...")
            spacy.cli.download('en_core_web_lg')
            self.nlp = spacy.load('en_core_web_lg')
        
        # Add custom pipeline components
        self.add_custom_components()
        
    def add_custom_components(self):
        """Add custom pipeline components for gender-inclusive analysis."""
        
        @spacy.Language.component("gender_detector")
        def gender_detector(doc: Doc) -> Doc:
            """Detect gendered language in text."""
            lang_pattern = self.language_config.get_language_pattern("en")
            if not lang_pattern:
                return doc
                
            for token in doc:
                is_gendered = False
                neutral_form = None
                
                # Check pronouns
                for pronoun_type, terms in lang_pattern.pronouns.items():
                    if token.text.lower() in [terms.masculine, terms.feminine]:
                        is_gendered = True
                        neutral_form = terms.neutral
                        break
                        
                # Check possessives
                if not is_gendered:
                    for poss_type, terms in lang_pattern.possessives.items():
                        if token.text.lower() in [terms.masculine, terms.feminine]:
                            is_gendered = True
                            neutral_form = terms.neutral
                            break
                            
                # Check honorifics and role nouns
                if not is_gendered:
                    for category in [lang_pattern.honorifics, lang_pattern.role_nouns]:
                        for term_type, terms in category.items():
                            if token.text.lower() in [terms.masculine, terms.feminine]:
                                is_gendered = True
                                neutral_form = terms.neutral
                                break
                                
                token._.is_gendered = is_gendered
                token._.gender_neutral = neutral_form
                
            return doc
        
        # Register custom token extensions
        if not Token.has_extension("is_gendered"):
            Token.set_extension("is_gendered", default=False)
        if not Token.has_extension("gender_neutral"):
            Token.set_extension("gender_neutral", default=None)
            
        # Add component to pipeline
        if "gender_detector" not in self.nlp.pipe_names:
            self.nlp.add_pipe("gender_detector", last=True)

    def correct_text(self, text: str, context: Optional[Dict] = None) -> CorrectionResult:
        """Apply gender-inclusive corrections to the input text.
        
        Args:
            text: Input text to correct
            context: Optional context information (e.g., file path, language)
            
        Returns:
            CorrectionResult containing the corrected text and suggestions
        """
        try:
            corrections = []
            
            # Check if this is source code
            if context and 'file_path' in context:
                lang = self.code_analyzer.detect_language(context['file_path'])
                if lang:
                    corrected_code, code_corrections = self.code_analyzer.correct_code(text, lang)
                    return CorrectionResult(
                        original_text=text,
                        corrected_text=corrected_code,
                        corrections=code_corrections,
                        confidence=0.9 if code_corrections else 1.0
                    )
            
            # Process natural language text
            doc = self.nlp(text)
            lang_pattern = self.language_config.get_language_pattern("en")
            
            if not lang_pattern:
                return CorrectionResult(
                    original_text=text,
                    corrected_text=text,
                    corrections=[],
                    confidence=1.0
                )
            
            # Process each sentence
            for sent in doc.sents:
                # Track verb adjustments needed
                verb_adjustments = []
                
                # First pass: identify gendered pronouns and needed verb adjustments
                for token in sent:
                    if token._.is_gendered:
                        # Get the gender-neutral alternative
                        neutral_form = token._.gender_neutral
                        
                        # Check for verb agreement
                        next_token = token.nbor() if token.i + 1 < len(doc) else None
                        if next_token and next_token.text.lower() in lang_pattern.verb_agreements:
                            verb_adjustments.append((next_token, lang_pattern.verb_agreements[next_token.text.lower()]))
                            corrections.append({
                                'original': f"{token.text} {next_token.text}",
                                'suggestion': f"{neutral_form} {lang_pattern.verb_agreements[next_token.text.lower()]}",
                                'start': token.idx,
                                'end': next_token.idx + len(next_token.text),
                                'confidence': 0.9,
                                'type': 'gender_inclusive'
                            })
                        else:
                            corrections.append({
                                'original': token.text,
                                'suggestion': neutral_form,
                                'start': token.idx,
                                'end': token.idx + len(token.text),
                                'confidence': 0.9,
                                'type': 'gender_inclusive'
                            })
            
            # Create corrected text
            if corrections:
                corrected_text = text
                offset = 0
                for corr in sorted(corrections, key=lambda x: x['start']):
                    start = corr['start'] + offset
                    end = corr['end'] + offset
                    corrected_text = corrected_text[:start] + corr['suggestion'] + corrected_text[end:]
                    offset += len(corr['suggestion']) - (end - start)
            else:
                corrected_text = text
                
            return CorrectionResult(
                original_text=text,
                corrected_text=corrected_text,
                corrections=corrections,
                confidence=0.9 if corrections else 1.0
            )
            
        except Exception as e:
            self.logger.error(f"Error in gender-inclusive correction: {str(e)}")
            return CorrectionResult(
                original_text=text,
                corrected_text=text,
                corrections=[],
                confidence=1.0
            )
            
    def get_correction_suggestions(self, text: str, context: Optional[Dict] = None) -> List[Dict]:
        """Get gender-inclusive correction suggestions without applying them.
        
        Args:
            text: Input text to analyze
            context: Optional context information (e.g., file path, language)
            
        Returns:
            List of correction suggestions
        """
        result = self.correct_text(text, context)
        return result.corrections
