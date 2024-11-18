import pytest
from modules.word_suggestion import WordSuggestion

@pytest.fixture
def word_suggestion():
    return WordSuggestion()

def test_get_spelling_suggestions(word_suggestion):
    """Test getting spelling suggestions."""
    # Test basic misspelling
    suggestions = word_suggestion.get_spelling_suggestions("helllo")
    assert "hello" in suggestions
    
    # Test with correct word
    suggestions = word_suggestion.get_spelling_suggestions("hello")
    assert len(suggestions) == 0
    
    # Test with empty string
    suggestions = word_suggestion.get_spelling_suggestions("")
    assert len(suggestions) == 0

def test_add_to_user_dictionary(word_suggestion):
    """Test adding words to user dictionary."""
    # Add custom word
    word_suggestion.add_to_user_dictionary("pythonista")
    
    # Verify word is accepted
    assert word_suggestion.is_word_valid("pythonista")
    
    # Test suggestions include custom word
    suggestions = word_suggestion.get_spelling_suggestions("pythonist")
    assert "pythonista" in suggestions

def test_track_word_frequency(word_suggestion):
    """Test word frequency tracking."""
    # Track some words
    word_suggestion.track_word("hello")
    word_suggestion.track_word("hello")
    word_suggestion.track_word("world")
    
    # Check frequencies
    assert word_suggestion.get_word_frequency("hello") == 2
    assert word_suggestion.get_word_frequency("world") == 1
    assert word_suggestion.get_word_frequency("unknown") == 0

def test_get_auto_complete_suggestions(word_suggestion):
    """Test auto-completion suggestions."""
    # Train with some text
    word_suggestion.train_with_text("The quick brown fox jumps over the lazy dog")
    
    # Test basic completion
    suggestions = word_suggestion.get_auto_complete_suggestions("qu")
    assert "quick" in suggestions
    
    # Test with empty prefix
    suggestions = word_suggestion.get_auto_complete_suggestions("")
    assert len(suggestions) == 0
    
    # Test with full word
    suggestions = word_suggestion.get_auto_complete_suggestions("quick")
    assert len(suggestions) == 0

def test_clear_user_dictionary(word_suggestion):
    """Test clearing user dictionary."""
    # Add some words
    word_suggestion.add_to_user_dictionary("customword1")
    word_suggestion.add_to_user_dictionary("customword2")
    
    # Clear dictionary
    word_suggestion.clear_user_dictionary()
    
    # Verify words are removed
    assert not word_suggestion.is_word_valid("customword1")
    assert not word_suggestion.is_word_valid("customword2")
