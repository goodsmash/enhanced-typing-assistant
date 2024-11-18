import pytest
from modules.translation_manager import TranslationManager

@pytest.fixture
def translation_manager():
    return TranslationManager()

def test_translate_text(translation_manager):
    """Test text translation."""
    # Test basic translation
    result = translation_manager.translate_text("Hello", "es")
    assert result == "Hola"
    
    # Test with source language
    result = translation_manager.translate_text("Hello", "es", "en")
    assert result == "Hola"
    
    # Test with invalid target language
    with pytest.raises(ValueError):
        translation_manager.translate_text("Hello", "invalid_lang")

def test_detect_language(translation_manager):
    """Test language detection."""
    # Test English detection
    lang = translation_manager.detect_language("Hello world")
    assert lang == "en"
    
    # Test Spanish detection
    lang = translation_manager.detect_language("Hola mundo")
    assert lang == "es"
    
    # Test empty text
    with pytest.raises(ValueError):
        translation_manager.detect_language("")

def test_get_supported_languages(translation_manager):
    """Test getting supported languages."""
    languages = translation_manager.get_supported_languages()
    assert isinstance(languages, dict)
    assert len(languages) > 0
    assert "en" in languages
    assert "es" in languages
    assert "fr" in languages

def test_translation_cache(translation_manager):
    """Test translation caching."""
    # First translation (not cached)
    result1 = translation_manager.translate_text("Hello", "es")
    assert result1 == "Hola"
    
    # Second translation (should use cache)
    result2 = translation_manager.translate_text("Hello", "es")
    assert result2 == "Hola"
    assert translation_manager.cache_hits > 0

def test_clear_cache(translation_manager):
    """Test clearing translation cache."""
    # Add something to cache
    translation_manager.translate_text("Hello", "es")
    
    # Clear cache
    translation_manager.clear_cache()
    assert len(translation_manager.translation_cache) == 0
    assert translation_manager.cache_hits == 0
