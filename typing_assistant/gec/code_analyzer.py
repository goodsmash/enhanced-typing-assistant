"""Code analysis and correction for gender-inclusive language."""

import re
from typing import Dict, List, Optional, Tuple
from pathlib import Path
import logging

from .language_config import ProgrammingLanguage, CodePattern

class CodeAnalyzer:
    """Analyzes and corrects gender-specific language in code."""
    
    def __init__(self):
        """Initialize the code analyzer."""
        self.logger = logging.getLogger(__name__)
        self.patterns: Dict[ProgrammingLanguage, CodePattern] = {}
        
    def get_pattern(self, lang: ProgrammingLanguage) -> CodePattern:
        """Get or create pattern for a programming language."""
        if lang not in self.patterns:
            self.patterns[lang] = CodePattern(lang)
        return self.patterns[lang]
        
    def detect_language(self, file_path: str) -> Optional[ProgrammingLanguage]:
        """Detect programming language from file extension."""
        ext_map = {
            '.py': ProgrammingLanguage.PYTHON,
            '.js': ProgrammingLanguage.JAVASCRIPT,
            '.ts': ProgrammingLanguage.TYPESCRIPT,
            '.java': ProgrammingLanguage.JAVA,
            '.cpp': ProgrammingLanguage.CPP,
            '.cs': ProgrammingLanguage.CSHARP,
            '.go': ProgrammingLanguage.GO,
            '.rs': ProgrammingLanguage.RUST,
            '.rb': ProgrammingLanguage.RUBY,
            '.php': ProgrammingLanguage.PHP,
            '.swift': ProgrammingLanguage.SWIFT,
            '.kt': ProgrammingLanguage.KOTLIN,
        }
        ext = Path(file_path).suffix.lower()
        return ext_map.get(ext)

    def analyze_code(self, code: str, lang: ProgrammingLanguage) -> List[Dict]:
        """Analyze code for gender-specific language.
        
        Args:
            code: Source code to analyze
            lang: Programming language of the code
            
        Returns:
            List of suggestions for gender-inclusive alternatives
        """
        suggestions = []
        pattern = self.get_pattern(lang)
        
        for category, rules in pattern.patterns.items():
            for rule in rules:
                if callable(rule):
                    # Handle custom processors (e.g., docstring processors)
                    continue
                    
                regex, replacement = rule
                for match in re.finditer(regex, code):
                    suggestions.append({
                        'start': match.start(),
                        'end': match.end(),
                        'original': match.group(),
                        'suggestion': re.sub(regex, replacement, match.group()),
                        'category': category,
                        'confidence': 0.9
                    })
        
        return suggestions
        
    def correct_code(self, code: str, lang: ProgrammingLanguage) -> Tuple[str, List[Dict]]:
        """Apply gender-inclusive corrections to code.
        
        Args:
            code: Source code to correct
            lang: Programming language of the code
            
        Returns:
            Tuple of (corrected code, list of applied corrections)
        """
        suggestions = self.analyze_code(code, lang)
        corrected = code
        
        # Apply corrections from end to start to maintain correct positions
        for suggestion in sorted(suggestions, key=lambda x: x['start'], reverse=True):
            start = suggestion['start']
            end = suggestion['end']
            corrected = corrected[:start] + suggestion['suggestion'] + corrected[end:]
            
        return corrected, suggestions
        
    def analyze_file(self, file_path: str) -> Optional[List[Dict]]:
        """Analyze a source code file for gender-specific language.
        
        Args:
            file_path: Path to the source code file
            
        Returns:
            List of suggestions for gender-inclusive alternatives, or None if language not supported
        """
        try:
            lang = self.detect_language(file_path)
            if not lang:
                self.logger.warning(f"Unsupported file type: {file_path}")
                return None
                
            with open(file_path, 'r', encoding='utf-8') as f:
                code = f.read()
                
            return self.analyze_code(code, lang)
            
        except Exception as e:
            self.logger.error(f"Error analyzing file {file_path}: {str(e)}")
            return None
            
    def correct_file(self, file_path: str) -> Optional[Tuple[str, List[Dict]]]:
        """Apply gender-inclusive corrections to a source code file.
        
        Args:
            file_path: Path to the source code file
            
        Returns:
            Tuple of (corrected code, list of applied corrections), or None if language not supported
        """
        try:
            lang = self.detect_language(file_path)
            if not lang:
                self.logger.warning(f"Unsupported file type: {file_path}")
                return None
                
            with open(file_path, 'r', encoding='utf-8') as f:
                code = f.read()
                
            return self.correct_code(code, lang)
            
        except Exception as e:
            self.logger.error(f"Error correcting file {file_path}: {str(e)}")
            return None
