from PyQt5.QtWidgets import (
    QMenu, QAction, QShortcut, QTextEdit, QWidget
)
from PyQt5.QtCore import Qt, QSettings
from PyQt5.QtGui import QKeySequence, QTextCursor, QFont
import json
import pyttsx3
import threading
import logging

# Configure logging
logger = logging.getLogger(__name__)

class AccessibilityManager:
    def __init__(self, parent):
        self.parent = parent
        self.settings = QSettings('EnhancedTypingAssistant', 'Settings')
        self.tts_lock = threading.Lock()
        self.tts_thread = None
        
        # Initialize components
        try:
            self.text_to_speech = pyttsx3.init()
        except Exception as e:
            logger.error(f"Failed to initialize text-to-speech: {e}")
            self.text_to_speech = None
        
        # Load settings
        self.settings_dict = {
            'word_prediction': self.settings.value('accessibility/word_prediction', True, type=bool),
            'audio_feedback': self.settings.value('accessibility/audio_feedback', True, type=bool),
            'hover_select': self.settings.value('accessibility/hover_select', False, type=bool),
            'text_spacing': self.settings.value('accessibility/text_spacing', 1.5, type=float),
            'simplified_mode': self.settings.value('accessibility/simplified_mode', False, type=bool),
            'auto_correction': self.settings.value('accessibility/auto_correction', True, type=bool),
            'content_moderation': self.settings.value('accessibility/content_moderation', True, type=bool),
            'voice_input': self.settings.value('accessibility/voice_input', True, type=bool),
            'voice_output': self.settings.value('accessibility/voice_output', True, type=bool),
            'preferred_voice': self.settings.value('accessibility/preferred_voice', 'alloy', type=str)
        }
        
        # Initialize word prediction
        self.word_predictor = WordPredictor()
        
        # Set up shortcuts
        self.setup_shortcuts()

    def setup_shortcuts(self):
        """Set up keyboard shortcuts for accessibility features."""
        self.shortcuts = {
            'Ctrl+Space': self.show_word_predictions,
            'Ctrl+B': self.increase_text_size,
            'Ctrl+S': self.decrease_text_size,
            'F1': self.toggle_simplified_mode,
            'Ctrl+H': self.toggle_hover_select,
            'Ctrl+M': self.toggle_voice_output,
            'Ctrl+V': self.toggle_voice_input,
            'Ctrl+R': self.read_selected_text
        }
        
        for shortcut, func in self.shortcuts.items():
            QShortcut(QKeySequence(shortcut), self.parent).activated.connect(func)

    def create_accessibility_menu(self, menubar):
        """Create the accessibility menu."""
        accessibility_menu = menubar.addMenu('&Accessibility')
        
        # Add menu items
        features = [
            ('&Word Prediction', 'word_prediction', 'Ctrl+Space'),
            ('&Audio Feedback', 'audio_feedback', 'Ctrl+M'),
            ('&Hover Select', 'hover_select', 'Ctrl+H'),
            ('&Simplified Mode', 'simplified_mode', 'F1'),
            ('&Voice Input', 'voice_input', 'Ctrl+V'),
            ('&Voice Output', 'voice_output', 'Ctrl+M')
        ]
        
        for name, setting, shortcut in features:
            action = QAction(name, self.parent)
            action.setCheckable(True)
            action.setChecked(self.settings_dict[setting])
            if shortcut:
                action.setShortcut(shortcut)
            action.triggered.connect(lambda checked, s=setting: self.toggle_setting(s))
            accessibility_menu.addAction(action)
        
        return accessibility_menu

    def toggle_setting(self, setting):
        """Toggle an accessibility setting."""
        try:
            self.settings_dict[setting] = not self.settings_dict[setting]
            self.settings.setValue(f'accessibility/{setting}', self.settings_dict[setting])
            
            # Apply changes
            if setting == 'simplified_mode':
                self.toggle_simplified_mode()
            elif setting == 'hover_select':
                self.toggle_hover_select()
            elif setting == 'audio_feedback':
                self.play_audio_feedback('toggle')
            elif setting == 'voice_input':
                self.toggle_voice_input()
            elif setting == 'voice_output':
                self.toggle_voice_output()
                
            logger.info(f"Accessibility setting '{setting}' changed to: {self.settings_dict[setting]}")
        except Exception as e:
            logger.error(f"Error toggling setting '{setting}': {str(e)}")
            self.play_audio_feedback('error')

    def show_word_predictions(self):
        """Show word predictions for the current word."""
        try:
            if not self.settings_dict['word_prediction']:
                return
                
            text_edit = self.parent.findChild(QTextEdit)
            if not text_edit:
                logger.warning("No QTextEdit found in parent widget")
                return
                
            cursor = text_edit.textCursor()
            cursor.select(QTextCursor.WordUnderCursor)
            current_word = cursor.selectedText()
            
            if len(current_word) >= 2:
                predictions = self.word_predictor.predict(current_word)
                if predictions:
                    self.show_prediction_menu(text_edit, predictions)
        except Exception as e:
            logger.error(f"Error in word prediction: {str(e)}")
            self.play_audio_feedback('error')

    def show_prediction_menu(self, text_edit, predictions):
        """Show a menu with word predictions."""
        try:
            cursor = text_edit.textCursor()
            rect = text_edit.cursorRect(cursor)
            pos = text_edit.mapToGlobal(rect.bottomRight())
            
            menu = QMenu(self.parent)
            for word in predictions[:5]:
                action = menu.addAction(word)
                action.triggered.connect(lambda _, w=word: self.insert_prediction(text_edit, w))
            
            menu.popup(pos)
        except Exception as e:
            logger.error(f"Error showing prediction menu: {str(e)}")

    def insert_prediction(self, text_edit, word):
        """Insert the selected prediction."""
        cursor = text_edit.textCursor()
        cursor.select(QTextCursor.WordUnderCursor)
        cursor.insertText(word + ' ')
        if self.settings_dict['audio_feedback']:
            self.play_audio_feedback('prediction')

    def play_audio_feedback(self, text=None):
        """Play audio feedback in a thread-safe manner."""
        if not self.text_to_speech or not self.settings_dict['audio_feedback']:
            return

        def speak_text():
            try:
                with self.tts_lock:
                    if text:
                        self.text_to_speech.say(text)
                    self.text_to_speech.runAndWait()
            except Exception as e:
                logger.error(f"Error in text-to-speech: {e}")
                # Try to reinitialize TTS engine
                try:
                    self.text_to_speech = pyttsx3.init()
                except Exception as reinit_error:
                    logger.error(f"Failed to reinitialize TTS: {reinit_error}")

        # Cancel any existing TTS thread
        if self.tts_thread and self.tts_thread.is_alive():
            self.text_to_speech.stop()
            self.tts_thread.join(timeout=1.0)

        # Start new TTS thread
        self.tts_thread = threading.Thread(target=speak_text)
        self.tts_thread.daemon = True
        self.tts_thread.start()

    def toggle_simplified_mode(self):
        """Toggle between simplified and full interface."""
        simplified = self.settings_dict['simplified_mode']
        for widget in self.parent.findChildren(QWidget):
            if hasattr(widget, 'simplified_hidden'):
                widget.setVisible(not simplified)

    def toggle_hover_select(self):
        """Toggle hover-to-select functionality."""
        hover = self.settings_dict['hover_select']
        text_edit = self.parent.findChild(QTextEdit)
        if text_edit:
            text_edit.setMouseTracking(hover)

    def toggle_voice_input(self):
        """Toggle voice input feature."""
        self.settings_dict['voice_input'] = not self.settings_dict['voice_input']
        self.settings.setValue('accessibility/voice_input', self.settings_dict['voice_input'])
        self.play_audio_feedback("Voice input " + ("enabled" if self.settings_dict['voice_input'] else "disabled"))

    def toggle_voice_output(self):
        """Toggle voice output feature."""
        self.settings_dict['voice_output'] = not self.settings_dict['voice_output']
        self.settings.setValue('accessibility/voice_output', self.settings_dict['voice_output'])
        self.play_audio_feedback("Voice output " + ("enabled" if self.settings_dict['voice_output'] else "disabled"))

    async def read_selected_text(self):
        """Read the selected text using the preferred voice."""
        if not self.settings_dict['voice_output']:
            return

        text_edit = self.parent.focusWidget()
        if isinstance(text_edit, QTextEdit):
            selected_text = text_edit.textCursor().selectedText()
            if selected_text:
                try:
                    voice = self.settings_dict['preferred_voice']
                    await self.parent.speech_generator.generate_speech(selected_text, voice=voice)
                except Exception as e:
                    logger.error(f"Error in text-to-speech: {e}")
                    self.play_audio_feedback("Error reading text")

    def increase_text_size(self):
        """Increase text size."""
        self.change_text_size(1.1)

    def decrease_text_size(self):
        """Decrease text size."""
        self.change_text_size(0.9)

    def change_text_size(self, factor):
        """Change text size by a factor."""
        text_edit = self.parent.findChild(QTextEdit)
        if text_edit:
            font = text_edit.font()
            size = font.pointSize()
            font.setPointSize(int(size * factor))
            text_edit.setFont(font)

    def cleanup(self):
        """Clean up resources before closing."""
        try:
            if self.text_to_speech:
                self.text_to_speech.stop()
                if self.tts_thread and self.tts_thread.is_alive():
                    self.tts_thread.join(timeout=1.0)
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")


class WordPredictor:
    """Handles word prediction using various algorithms."""
    
    def __init__(self):
        self.word_frequencies = {}
        self.load_frequencies()
        
        # Common typing patterns for users with motor control challenges
        self.typing_patterns = {
            'doubles': {'tt': 't', 'ee': 'e', 'rr': 'r'},  # Common double letters
            'adjacents': {  # Common adjacent key presses
                'sd': 's', 'ds': 's',
                'jk': 'j', 'kj': 'j',
                'gh': 'h', 'hg': 'h'
            }
        }
    
    def load_frequencies(self):
        """Load word frequency dictionary."""
        try:
            with open('word_frequencies.json', 'r') as f:
                self.word_frequencies = json.load(f)
        except FileNotFoundError:
            # Initialize with some common words if file doesn't exist
            self.word_frequencies = {
                'the': 100, 'be': 90, 'to': 80, 'of': 70, 'and': 60,
                'a': 50, 'in': 40, 'that': 30, 'have': 20, 'i': 10
            }
    
    def predict(self, partial_word):
        """Predict words based on partial input."""
        if not partial_word:
            return []
            
        predictions = set()
        
        # Clean the input
        cleaned_word = self.clean_input(partial_word.lower())
        
        # Add exact prefix matches
        predictions.update(
            word for word in self.word_frequencies 
            if word.startswith(cleaned_word)
        )
        
        # Add common corrections
        corrections = self.get_corrections(cleaned_word)
        for correction in corrections:
            predictions.update(
                word for word in self.word_frequencies 
                if word.startswith(correction)
            )
        
        # Sort by frequency and relevance
        sorted_predictions = sorted(
            predictions,
            key=lambda x: (
                self.word_frequencies.get(x, 0),
                -self.levenshtein_distance(x, cleaned_word)
            ),
            reverse=True
        )
        
        return sorted_predictions[:10]
    
    def clean_input(self, word):
        """Clean input by handling common typing patterns."""
        result = word
        
        # Handle double letters
        for double, single in self.typing_patterns['doubles'].items():
            result = result.replace(double, single)
        
        # Handle adjacent key presses
        for adj, correct in self.typing_patterns['adjacents'].items():
            result = result.replace(adj, correct)
        
        return result
    
    def get_corrections(self, word):
        """Get possible corrections for the word."""
        corrections = set()
        
        # Add the original word
        corrections.add(word)
        
        # Handle transposed letters
        for i in range(len(word) - 1):
            transposed = list(word)
            transposed[i], transposed[i + 1] = transposed[i + 1], transposed[i]
            corrections.add(''.join(transposed))
        
        # Handle missing letters
        for i in range(len(word) + 1):
            for c in 'abcdefghijklmnopqrstuvwxyz':
                corrections.add(word[:i] + c + word[i:])
        
        return corrections
    
    @staticmethod
    def levenshtein_distance(s1, s2):
        """Calculate the Levenshtein distance between two strings."""
        if len(s1) < len(s2):
            return WordPredictor.levenshtein_distance(s2, s1)
        if len(s2) == 0:
            return len(s1)
        
        previous_row = range(len(s2) + 1)
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row
        
        return previous_row[-1]
