import pytest
import os
from modules.user_preferences import UserPreferences

@pytest.fixture
def user_prefs():
    prefs = UserPreferences()
    yield prefs
    # Cleanup after tests
    if os.path.exists(prefs.settings_file):
        os.remove(prefs.settings_file)

def test_default_preferences(user_prefs):
    """Test default preferences are set correctly."""
    assert user_prefs.get_preference('theme') == 'Light'
    assert user_prefs.get_preference('font_size') == 12
    assert user_prefs.get_preference('spell_check_enabled') is True
    assert user_prefs.get_preference('auto_correct_enabled') is True
    assert user_prefs.get_preference('language') == 'en'

def test_set_get_preference(user_prefs):
    """Test setting and getting preferences."""
    # Set new values
    user_prefs.set_preference('theme', 'Dark')
    user_prefs.set_preference('font_size', 14)
    user_prefs.set_preference('spell_check_enabled', False)
    
    # Verify values
    assert user_prefs.get_preference('theme') == 'Dark'
    assert user_prefs.get_preference('font_size') == 14
    assert user_prefs.get_preference('spell_check_enabled') is False
    
    # Test invalid preference
    with pytest.raises(KeyError):
        user_prefs.get_preference('invalid_pref')

def test_save_load_preferences(user_prefs):
    """Test saving and loading preferences."""
    # Modify some preferences
    user_prefs.set_preference('theme', 'Dark')
    user_prefs.set_preference('font_size', 14)
    
    # Save preferences
    user_prefs.save_preferences()
    
    # Create new instance and load
    new_prefs = UserPreferences()
    new_prefs.load_preferences()
    
    # Verify loaded values match
    assert new_prefs.get_preference('theme') == 'Dark'
    assert new_prefs.get_preference('font_size') == 14

def test_export_import_preferences(user_prefs, tmp_path):
    """Test exporting and importing preferences."""
    # Set some preferences
    user_prefs.set_preference('theme', 'Dark')
    user_prefs.set_preference('font_size', 14)
    
    # Export to temporary file
    export_file = tmp_path / "prefs_export.json"
    user_prefs.export_preferences(str(export_file))
    
    # Create new instance and import
    new_prefs = UserPreferences()
    new_prefs.import_preferences(str(export_file))
    
    # Verify imported values match
    assert new_prefs.get_preference('theme') == 'Dark'
    assert new_prefs.get_preference('font_size') == 14

def test_reset_preferences(user_prefs):
    """Test resetting preferences to defaults."""
    # Modify some preferences
    user_prefs.set_preference('theme', 'Dark')
    user_prefs.set_preference('font_size', 14)
    
    # Reset to defaults
    user_prefs.reset_preferences()
    
    # Verify reset to defaults
    assert user_prefs.get_preference('theme') == 'Light'
    assert user_prefs.get_preference('font_size') == 12
