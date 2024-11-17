"""Configuration for language-specific gender-inclusive corrections."""

from typing import Dict, List, Optional, Set
from dataclasses import dataclass
from enum import Enum

class ProgrammingLanguage(Enum):
    """Supported programming languages."""
    PYTHON = "python"
    JAVASCRIPT = "javascript"
    TYPESCRIPT = "typescript"
    JAVA = "java"
    CPP = "cpp"
    CSHARP = "csharp"
    GO = "go"
    RUST = "rust"
    RUBY = "ruby"
    PHP = "php"
    SWIFT = "swift"
    KOTLIN = "kotlin"

@dataclass
class GenderTerms:
    """Gender-specific terms and their neutral alternatives."""
    masculine: str
    feminine: str
    neutral: str
    context: Optional[str] = None

@dataclass
class LanguagePattern:
    """Language-specific patterns for gender detection and correction."""
    pronouns: Dict[str, GenderTerms]
    possessives: Dict[str, GenderTerms]
    honorifics: Dict[str, GenderTerms]
    role_nouns: Dict[str, GenderTerms]
    verb_agreements: Dict[str, str]
    
class CodePattern:
    """Patterns for gender-inclusive code corrections."""
    def __init__(self, lang: ProgrammingLanguage):
        self.language = lang
        self.patterns = self._init_patterns()
        
    def _init_patterns(self) -> Dict[str, List[str]]:
        """Initialize language-specific code patterns."""
        common_patterns = {
            "variable_names": [
                (r"(?i)(he|him|his|she|her|hers)([A-Z]|$)", "they$2"),
                (r"(?i)man([A-Z]|$)", "person$1"),
                (r"(?i)woman([A-Z]|$)", "person$1"),
            ],
            "comments": [
                (r"(?i)\b(he|him|his|she|her|hers)\b", "they"),
                (r"(?i)\b(man|woman)\b", "person"),
                (r"(?i)\b(mankind)\b", "humankind"),
            ],
            "string_literals": [
                (r'(?i)"([^"]*)(he|him|his|she|her|hers)([^"]*)"', r'"$1they$3"'),
                (r"(?i)'([^']*)(he|him|his|she|her|hers)([^']*)'", r"'$1they$3'"),
            ],
        }
        
        # Language-specific patterns
        lang_patterns = {
            ProgrammingLanguage.PYTHON: {
                "docstrings": [
                    (r'"""([^"]*)"""', self._process_docstring),
                    (r"'''([^']*)'''", self._process_docstring),
                ],
                **common_patterns
            },
            ProgrammingLanguage.JAVASCRIPT: {
                "jsdoc": [
                    (r"/\*\*([^*]*)\*/", self._process_jsdoc),
                ],
                **common_patterns
            },
            # Add more language-specific patterns here
        }
        
        return lang_patterns.get(self.language, common_patterns)
    
    def _process_docstring(self, match: str) -> str:
        """Process Python docstrings for gender-inclusive language."""
        content = match.group(1)
        # Apply gender-inclusive transformations
        return f'"""{content}"""'
    
    def _process_jsdoc(self, match: str) -> str:
        """Process JSDoc comments for gender-inclusive language."""
        content = match.group(1)
        # Apply gender-inclusive transformations
        return f"/**{content}*/"

class LanguageConfig:
    """Configuration for natural language processing and correction."""
    def __init__(self):
        self.patterns = {
            "en": LanguagePattern(
                pronouns={
                    "subject": GenderTerms("he", "she", "they"),
                    "object": GenderTerms("him", "her", "them"),
                    "reflexive": GenderTerms("himself", "herself", "themself"),
                },
                possessives={
                    "determiner": GenderTerms("his", "her", "their"),
                    "pronoun": GenderTerms("his", "hers", "theirs"),
                },
                honorifics={
                    "formal": GenderTerms("Mr.", "Ms.", "Mx."),
                    "professional": GenderTerms("chairman", "chairwoman", "chairperson"),
                },
                role_nouns={
                    "professional": GenderTerms("businessman", "businesswoman", "businessperson"),
                    "academic": GenderTerms("freshman", "freshwoman", "first-year student"),
                },
                verb_agreements={
                    "is": "are",
                    "was": "were",
                    "has": "have",
                    "'s": "'re",
                }
            ),
            # Add more languages here
        }
        
    def get_language_pattern(self, lang_code: str) -> Optional[LanguagePattern]:
        """Get language-specific patterns."""
        return self.patterns.get(lang_code)
