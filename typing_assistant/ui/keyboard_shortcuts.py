"""Keyboard shortcuts manager for the typing assistant."""

from typing import Callable, Dict, Optional

from PyQt5.QtCore import Qt, QObject
from PyQt5.QtGui import QKeySequence
from PyQt5.QtWidgets import QWidget, QShortcut


class KeyboardShortcutsManager(QObject):
    """Manages keyboard shortcuts and their actions."""

    def __init__(self, parent: QWidget):
        """Initialize keyboard shortcuts manager.
        
        Args:
            parent: Parent widget to attach shortcuts to
        """
        super().__init__(parent)
        self._shortcuts: Dict[str, QShortcut] = {}
        self._parent = parent
        self._setup_default_shortcuts()

    def _setup_default_shortcuts(self) -> None:
        """Set up default keyboard shortcuts."""
        # Navigation shortcuts
        self.add_shortcut("focus_text_area", "Alt+T", 
                         lambda: self._parent.text_edit.setFocus())
        self.add_shortcut("focus_controls", "Alt+C", 
                         lambda: self._parent.correction_mode.setFocus())
        
        # Text size shortcuts
        self.add_shortcut("increase_text_size", "Ctrl++", 
                         lambda: self._parent.font_size.setValue(
                             self._parent.font_size.value() + 2))
        self.add_shortcut("decrease_text_size", "Ctrl+-", 
                         lambda: self._parent.font_size.setValue(
                             self._parent.font_size.value() - 2))
        
        # Accessibility shortcuts
        self.add_shortcut("toggle_high_contrast", "Ctrl+Alt+H", 
                         lambda: self._parent.high_contrast.toggle())
        self.add_shortcut("toggle_screen_reader", "Ctrl+Alt+S", 
                         lambda: self._parent.toggle_screen_reader())
        
        # Speech shortcuts
        self.add_shortcut("speak_selected", "Ctrl+Space", 
                         lambda: self._parent.speak_text())
        self.add_shortcut("speak_all", "Ctrl+Shift+Space", 
                         lambda: self._parent.speak_all_text())
        
        # Text correction shortcuts
        self.add_shortcut("accept_correction", "Alt+Enter", 
                         lambda: self._parent.accept_correction())
        self.add_shortcut("reject_correction", "Alt+Backspace", 
                         lambda: self._parent.reject_correction())
        
        # Mode shortcuts
        self.add_shortcut("cycle_correction_mode", "Ctrl+M", 
                         lambda: self._cycle_correction_mode())

    def add_shortcut(self, name: str, key_sequence: str, 
                    callback: Callable[[], None]) -> None:
        """Add a new keyboard shortcut.
        
        Args:
            name: Unique identifier for the shortcut
            key_sequence: Key combination (e.g., "Ctrl+S")
            callback: Function to call when shortcut is triggered
        """
        if name in self._shortcuts:
            self._shortcuts[name].setEnabled(False)
            self._shortcuts[name].deleteLater()
        
        shortcut = QShortcut(QKeySequence(key_sequence), self._parent)
        shortcut.activated.connect(callback)
        self._shortcuts[name] = shortcut

    def remove_shortcut(self, name: str) -> None:
        """Remove a keyboard shortcut.
        
        Args:
            name: Identifier of the shortcut to remove
        """
        if name in self._shortcuts:
            self._shortcuts[name].setEnabled(False)
            self._shortcuts[name].deleteLater()
            del self._shortcuts[name]

    def get_shortcut(self, name: str) -> Optional[QShortcut]:
        """Get a keyboard shortcut by name.
        
        Args:
            name: Identifier of the shortcut
            
        Returns:
            The shortcut object if found, None otherwise
        """
        return self._shortcuts.get(name)

    def enable_shortcut(self, name: str) -> None:
        """Enable a keyboard shortcut.
        
        Args:
            name: Identifier of the shortcut to enable
        """
        if name in self._shortcuts:
            self._shortcuts[name].setEnabled(True)

    def disable_shortcut(self, name: str) -> None:
        """Disable a keyboard shortcut.
        
        Args:
            name: Identifier of the shortcut to disable
        """
        if name in self._shortcuts:
            self._shortcuts[name].setEnabled(False)

    def _cycle_correction_mode(self) -> None:
        """Cycle through available correction modes."""
        current_index = self._parent.correction_mode.currentIndex()
        next_index = (current_index + 1) % self._parent.correction_mode.count()
        self._parent.correction_mode.setCurrentIndex(next_index)

    def get_shortcut_descriptions(self) -> Dict[str, str]:
        """Get descriptions of all keyboard shortcuts.
        
        Returns:
            Dictionary mapping shortcut names to their key sequences
        """
        return {
            name: shortcut.key().toString()
            for name, shortcut in self._shortcuts.items()
        }

    def show_shortcuts_help(self) -> None:
        """Display help information about available shortcuts."""
        descriptions = {
            "focus_text_area": "Focus the main text editing area",
            "focus_controls": "Focus the control panel",
            "increase_text_size": "Increase text size",
            "decrease_text_size": "Decrease text size",
            "toggle_high_contrast": "Toggle high contrast mode",
            "toggle_screen_reader": "Toggle screen reader",
            "speak_selected": "Speak selected text",
            "speak_all": "Speak all text",
            "accept_correction": "Accept current correction",
            "reject_correction": "Reject current correction",
            "cycle_correction_mode": "Cycle through correction modes",
        }
        
        shortcuts = self.get_shortcut_descriptions()
        help_text = "Keyboard Shortcuts:\n\n"
        
        for name, desc in descriptions.items():
            if name in shortcuts:
                help_text += f"{shortcuts[name]}: {desc}\n"
        
        # Show help text in a dialog or status bar
        self._parent.show_help_dialog("Keyboard Shortcuts", help_text)
