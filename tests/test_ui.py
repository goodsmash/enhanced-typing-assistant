import pytest
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtTest import QTest
from PyQt5.QtWidgets import (
    QMainWindow, QTextEdit, QMenuBar,
    QStatusBar, QApplication, QMessageBox
)
from typing_assistant.ui.main_window import MainWindow
from typing_assistant.ui.theme_manager import ThemeManager
from typing_assistant.config import (
    DEFAULT_WINDOW_SIZE, DEFAULT_FONT_SIZE,
    MIN_FONT_SIZE, MAX_FONT_SIZE
)

@pytest.fixture
def main_window(qapp):
    """Create a MainWindow instance for testing."""
    window = MainWindow()
    window.show()
    return window

def test_window_initialization(main_window):
    """Test window initialization and basic properties."""
    assert isinstance(main_window, QMainWindow)
    assert main_window.windowTitle() == "Enhanced Typing Assistant"
    assert main_window.size().width() == DEFAULT_WINDOW_SIZE[0]
    assert main_window.size().height() == DEFAULT_WINDOW_SIZE[1]

def test_text_editor(main_window):
    """Test text editor widget functionality."""
    editor = main_window.text_editor
    assert isinstance(editor, QTextEdit)
    
    # Test text input
    QTest.keyClicks(editor, "Test input")
    assert editor.toPlainText() == "Test input"
    
    # Test text selection
    editor.selectAll()
    assert editor.textCursor().selectedText() == "Test input"

def test_menu_bar(main_window):
    """Test menu bar and actions."""
    menu_bar = main_window.menuBar()
    assert isinstance(menu_bar, QMenuBar)
    
    # Test File menu
    file_menu = menu_bar.actions()[0]
    assert file_menu.text() == "&File"
    
    # Test Edit menu
    edit_menu = menu_bar.actions()[1]
    assert edit_menu.text() == "&Edit"

def test_status_bar(main_window):
    """Test status bar functionality."""
    status_bar = main_window.statusBar()
    assert isinstance(status_bar, QStatusBar)
    
    # Test status message
    main_window.show_status_message("Test status")
    assert status_bar.currentMessage() == "Test status"

def test_font_size_adjustment(main_window):
    """Test font size adjustment functionality."""
    editor = main_window.text_editor
    initial_size = editor.font().pointSize()
    
    # Test increase font size
    main_window.increase_font_size()
    assert editor.font().pointSize() == min(initial_size + 1, MAX_FONT_SIZE)
    
    # Test decrease font size
    main_window.decrease_font_size()
    assert editor.font().pointSize() == initial_size

def test_theme_switching(main_window):
    """Test theme switching functionality."""
    theme_manager = ThemeManager()
    
    # Test light theme
    theme_manager.apply_theme(main_window, "light")
    assert main_window.palette().color(main_window.backgroundRole()).name() != "#2b2b2b"
    
    # Test dark theme
    theme_manager.apply_theme(main_window, "dark")
    assert main_window.palette().color(main_window.backgroundRole()).name() == "#2b2b2b"

def test_keyboard_shortcuts(main_window):
    """Test keyboard shortcuts."""
    editor = main_window.text_editor
    
    # Test copy/paste
    editor.setText("Test text")
    editor.selectAll()
    QTest.keyClick(editor, Qt.Key_C, Qt.ControlModifier)
    editor.clear()
    QTest.keyClick(editor, Qt.Key_V, Qt.ControlModifier)
    assert editor.toPlainText() == "Test text"
    
    # Test undo/redo
    editor.clear()
    QTest.keyClicks(editor, "Test undo")
    QTest.keyClick(editor, Qt.Key_Z, Qt.ControlModifier)
    assert editor.toPlainText() == ""
    QTest.keyClick(editor, Qt.Key_Y, Qt.ControlModifier)
    assert editor.toPlainText() == "Test undo"

def test_context_menu(main_window):
    """Test context menu functionality."""
    editor = main_window.text_editor
    editor.setText("Right click test")
    
    # Simulate right click
    menu = editor.createStandardContextMenu()
    assert len(menu.actions()) > 0
    assert any(action.text() == "Cut" for action in menu.actions())
    assert any(action.text() == "Copy" for action in menu.actions())
    assert any(action.text() == "Paste" for action in menu.actions())

def test_drag_and_drop(main_window, tmp_path):
    """Test drag and drop functionality."""
    # Create a test file
    test_file = tmp_path / "test.txt"
    test_file.write_text("Drag and drop test content")
    
    # Test file drop handling
    main_window.handle_file_drop([str(test_file)])
    assert "Drag and drop test content" in main_window.text_editor.toPlainText()

def test_window_state_persistence(main_window, tmp_path):
    """Test window state saving and loading."""
    # Modify window state
    new_pos = QPoint(100, 100)
    main_window.move(new_pos)
    main_window.resize(800, 600)
    
    # Save state
    main_window.save_window_state()
    
    # Create new window and load state
    new_window = MainWindow()
    new_window.load_window_state()
    
    assert new_window.pos() == new_pos
    assert new_window.size().width() == 800
    assert new_window.size().height() == 600

def test_error_handling(main_window, monkeypatch):
    """Test error handling and user notifications."""
    def mock_critical(*args, **kwargs):
        assert "Error" in args[2]
    
    monkeypatch.setattr(QMessageBox, "critical", mock_critical)
    main_window.show_error("Test error message")

def test_accessibility_features(main_window):
    """Test accessibility features."""
    editor = main_window.text_editor
    
    # Test text scaling
    initial_scale = editor.font().pointSize()
    QTest.keyClick(editor, Qt.Key_Plus, Qt.ControlModifier)
    assert editor.font().pointSize() > initial_scale
    
    # Test high contrast mode
    main_window.toggle_high_contrast_mode()
    palette = editor.palette()
    assert palette.color(palette.Base).lightness() in (0, 255)  # Either black or white

def test_performance(main_window):
    """Test UI performance with large text."""
    editor = main_window.text_editor
    large_text = "Test line\n" * 1000
    
    # Measure time to insert text
    start_time = QApplication.instance().processEvents()
    editor.setText(large_text)
    end_time = QApplication.instance().processEvents()
    
    # Should handle large text without significant delay
    assert (end_time - start_time) < 1000  # Less than 1 second
