# tests/test_text_correction.py

import pytest
from typing_assistant.core.text_processor import TextProcessor
from typing_assistant.config import FEATURES, MAX_TEXT_LENGTH

@pytest.fixture
def text_processor(mock_openai):
    """Create a TextProcessor instance with mocked OpenAI."""
    return TextProcessor()

def test_text_correction_basic(text_processor):
    """Test basic text correction functionality."""
    input_text = "This is a tst of the text processor."
    corrected = text_processor.correct_text(input_text)
    assert isinstance(corrected, str)
    assert len(corrected) > 0
    assert corrected != input_text

def test_text_correction_empty(text_processor):
    """Test correction with empty text."""
    assert text_processor.correct_text("") == ""
    assert text_processor.correct_text(None) == ""
    assert text_processor.correct_text("   ") == ""

def test_text_correction_max_length(text_processor):
    """Test text correction with maximum length handling."""
    long_text = "a" * (MAX_TEXT_LENGTH + 100)
    with pytest.raises(ValueError):
        text_processor.correct_text(long_text)

def test_spell_check(text_processor):
    """Test spell checking functionality."""
    misspelled = "teh quik brwn fox"
    suggestions = text_processor.get_spelling_suggestions(misspelled)
    assert isinstance(suggestions, dict)
    assert "teh" in suggestions
    assert "quik" in suggestions
    assert "brwn" in suggestions

def test_grammar_check(text_processor):
    """Test grammar checking functionality."""
    text = "They was going to the store."
    issues = text_processor.check_grammar(text)
    assert isinstance(issues, list)
    assert len(issues) > 0
    assert any("agreement" in str(issue).lower() for issue in issues)

def test_style_suggestions(text_processor):
    """Test style improvement suggestions."""
    text = "The thing was very good and nice."
    suggestions = text_processor.get_style_suggestions(text)
    assert isinstance(suggestions, list)
    assert len(suggestions) > 0

@pytest.mark.asyncio
async def test_async_correction(text_processor):
    """Test asynchronous text correction."""
    text = "This is an async tst."
    result = await text_processor.correct_text_async(text)
    assert isinstance(result, str)
    assert len(result) > 0
    assert result != text

def test_correction_with_context(text_processor):
    """Test text correction with context awareness."""
    context = {
        "style": "formal",
        "domain": "academic",
        "language": "en-US"
    }
    text = "gonna do this thing"
    corrected = text_processor.correct_text(text, context=context)
    assert "going to" in corrected.lower()
    assert "thing" not in corrected.lower()

def test_feature_flags(text_processor):
    """Test feature flag handling in text processor."""
    text = "teh cat sleeps"
    
    # Test with spell check disabled
    with pytest.MonkeyPatch() as mp:
        mp.setitem(FEATURES, "spell_check", False)
        result = text_processor.correct_text(text)
        assert "teh" in result

    # Test with grammar check disabled
    with pytest.MonkeyPatch() as mp:
        mp.setitem(FEATURES, "grammar_check", False)
        result = text_processor.correct_text("they was sleeping")
        assert "they was" in result

def test_correction_batch_processing(text_processor):
    """Test batch processing of text corrections."""
    texts = [
        "This is tst one.",
        "This is tst two.",
        "This is tst three."
    ]
    results = text_processor.correct_texts_batch(texts)
    assert len(results) == len(texts)
    assert all(isinstance(r, str) for r in results)
    assert all(r != t for r, t in zip(results, texts))
