import os
from PyQt5.QtWidgets import (
    QMenu, QAction, QShortcut, QTextEdit, QWidget, QComboBox,
    QLabel, QVBoxLayout, QHBoxLayout
)
from PyQt5.QtCore import Qt, QSettings, pyqtSignal, QObject, QThread
from PyQt5.QtGui import QKeySequence, QTextCursor, QFont, QPalette
import json
import pyttsx3
import threading
import logging
import openai
from dotenv import load_dotenv
import asyncio
import tiktoken
from concurrent.futures import ThreadPoolExecutor
import time
import numpy as np
from sklearn.preprocessing import StandardScaler
from cognitive_support import CognitiveSupportManager, CognitiveProfile
import asyncio
import tiktoken

# Load environment variables
load_dotenv()
openai.api_key = os.getenv('OPENAI_API_KEY')

# Configure logging
logger = logging.getLogger(__name__)

class TranslationWorker(QObject):
    """Worker class for handling real-time translations."""
    translation_ready = pyqtSignal(str, str)  # (original_text, translated_text)
    error_occurred = pyqtSignal(str)

    def __init__(self, target_language='en'):
        super().__init__()
        self.target_language = target_language
        self.last_request_time = 0
        self.min_request_interval = 1.0  # Minimum time between requests
        self.translation_cache = {}
        self.executor = ThreadPoolExecutor(max_workers=1)

    async def translate_text(self, text):
        """Translate text using GPT-4."""
        try:
            current_time = time.time()
            if current_time - self.last_request_time < self.min_request_interval:
                await asyncio.sleep(self.min_request_interval)

            # Check cache first
            cache_key = f"{text}_{self.target_language}"
            if cache_key in self.translation_cache:
                self.translation_ready.emit(text, self.translation_cache[cache_key])
                return

            response = await openai.ChatCompletion.acreate(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": f"You are a real-time translator. Translate to {self.target_language}."},
                    {"role": "user", "content": text}
                ],
                max_tokens=100,
                temperature=0.3
            )

            translated_text = response.choices[0].message['content'].strip()
            self.translation_cache[cache_key] = translated_text
            self.last_request_time = time.time()
            self.translation_ready.emit(text, translated_text)

        except Exception as e:
            logger.error(f"Translation error: {str(e)}")
            self.error_occurred.emit(f"Translation error: {str(e)}")

class AccessibilityManager:
    def __init__(self, parent):
        self.parent = parent
        self.settings = QSettings('EnhancedTypingAssistant', 'Settings')
        self.tts_lock = threading.Lock()
        self.tts_thread = None
        
        # Initialize translation components
        self.translation_worker = TranslationWorker()
        self.translation_worker.translation_ready.connect(self.update_translation)
        self.translation_worker.error_occurred.connect(self.handle_translation_error)
        self.current_language = self.settings.value('accessibility/target_language', 'en')
        
        # Initialize GPT-4 components
        try:
            self.sentiment_analyzer = pipeline("sentiment-analysis")
            self.encoding = tiktoken.encoding_for_model("gpt-4")
            self.interaction_history = []
            self.token_usage = {'prompt_tokens': 0, 'completion_tokens': 0}
            self.last_suggestion_time = 0
            self.suggestion_cache = {}
        except Exception as e:
            logger.error(f"Failed to initialize AI components: {e}")
        
        # Initialize text-to-speech
        try:
            self.text_to_speech = pyttsx3.init()
        except Exception as e:
            logger.error(f"Failed to initialize text-to-speech: {e}")
            self.text_to_speech = None
        
        # Initialize cognitive support with AI
        self.cognitive_support = CognitiveSupportManager(parent)
        
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
            'preferred_voice': self.settings.value('accessibility/preferred_voice', 'alloy', type=str),
            'cognitive_assist': self.settings.value('accessibility/cognitive_assist', False, type=bool),
            'post_concussion_mode': self.settings.value('accessibility/post_concussion_mode', False, type=bool),
            'ai_adaptation': self.settings.value('accessibility/ai_adaptation', True, type=bool),
            'smart_suggestions': self.settings.value('accessibility/smart_suggestions', True, type=bool),
            'gpt4_enhanced': self.settings.value('accessibility/gpt4_enhanced', True, type=bool),
            'live_translation': self.settings.value('accessibility/live_translation', True, type=bool)
        }
        
        # Set up translation UI
        self.setup_translation_ui()
        
        # Initialize AI-powered components
        self.setup_ai_components()
        
        # Initialize word prediction
        self.word_predictor = WordPredictor()
        
        # Set up shortcuts
        self.setup_shortcuts()
        
        # Initialize start time for user behavior analysis
        self.start_time = time.time()

    async def get_gpt4_suggestions(self, current_text, context=None):
        """Get context-aware suggestions using GPT-4."""
        try:
            if not self.settings_dict['smart_suggestions'] or not self.settings_dict['gpt4_enhanced']:
                return []
                
            # Rate limiting and caching
            current_time = time.time()
            if current_time - self.last_suggestion_time < 1.0:  # Rate limit to 1 request per second
                if current_text in self.suggestion_cache:
                    return self.suggestion_cache[current_text]
                return []
                
            self.last_suggestion_time = current_time
            
            # Prepare context-aware prompt
            system_prompt = """You are an AI writing assistant specializing in cognitive accessibility.
            Consider the user's cognitive needs and provide clear, helpful suggestions.
            Focus on completing thoughts and maintaining coherence."""
            
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Context: {context}\nCurrent text: {current_text}\nProvide 3 natural continuations:"}
            ]
            
            response = await openai.ChatCompletion.acreate(
                model="gpt-4",
                messages=messages,
                max_tokens=100,
                temperature=0.7,
                presence_penalty=0.6,
                frequency_penalty=0.5
            )
            
            # Update token usage
            self.token_usage['prompt_tokens'] += response.usage.prompt_tokens
            self.token_usage['completion_tokens'] += response.usage.completion_tokens
            
            suggestions = response.choices[0].message['content'].split('\n')
            suggestions = [s.strip() for s in suggestions if s.strip()]
            
            # Cache the results
            self.suggestion_cache[current_text] = suggestions
            
            return suggestions
            
        except Exception as e:
            logger.error(f"Error getting GPT-4 suggestions: {e}")
            return []
            
    async def analyze_text_complexity(self, text):
        """Analyze text complexity using GPT-4."""
        try:
            response = await openai.ChatCompletion.acreate(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "Analyze the following text for cognitive complexity and accessibility."},
                    {"role": "user", "content": text}
                ],
                max_tokens=100
            )
            
            analysis = response.choices[0].message['content']
            return self.parse_complexity_analysis(analysis)
            
        except Exception as e:
            logger.error(f"Error analyzing text complexity: {e}")
            return None
            
    def parse_complexity_analysis(self, analysis):
        """Parse GPT-4's complexity analysis into actionable metrics."""
        try:
            # Extract key metrics from the analysis
            metrics = {
                'complexity_score': 0.0,
                'readability_level': 'medium',
                'suggested_improvements': []
            }
            
            # Add parsing logic here based on GPT-4's output format
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error parsing complexity analysis: {e}")
            return None
            
    async def get_cognitive_assistance(self, text, user_profile):
        """Get personalized cognitive assistance using GPT-4."""
        try:
            profile_context = json.dumps(user_profile)
            
            response = await openai.ChatCompletion.acreate(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a cognitive accessibility assistant."},
                    {"role": "user", "content": f"User Profile: {profile_context}\nText: {text}\nProvide assistance:"}
                ],
                max_tokens=150
            )
            
            assistance = response.choices[0].message['content']
            return self.parse_cognitive_assistance(assistance)
            
        except Exception as e:
            logger.error(f"Error getting cognitive assistance: {e}")
            return None
            
    def parse_cognitive_assistance(self, assistance):
        """Parse GPT-4's cognitive assistance response."""
        try:
            # Extract actionable suggestions and adaptations
            suggestions = {
                'text_modifications': [],
                'interface_adjustments': [],
                'cognitive_supports': []
            }
            
            # Add parsing logic here
            
            return suggestions
            
        except Exception as e:
            logger.error(f"Error parsing cognitive assistance: {e}")
            return None
            
    def setup_ai_components(self):
        """Initialize AI components for enhanced accessibility."""
        try:
            # Setup GPT-4 configuration
            self.completion_model = "gpt-4"
            self.max_context_length = 8192  # GPT-4's context window
            
            # Initialize user behavior tracking
            self.user_metrics = {
                'typing_speed': [],
                'error_rate': [],
                'pause_patterns': [],
                'correction_patterns': [],
                'complexity_scores': [],
                'assistance_effectiveness': []
            }
            
            # Load personalized ML model if exists
            self.load_personalized_model()
            
        except Exception as e:
            logger.error(f"Error setting up AI components: {e}")
            
    def get_ai_suggestions(self, current_text):
        """Get AI-powered suggestions based on user's writing context."""
        try:
            if not self.settings_dict['smart_suggestions']:
                return []
                
            response = openai.ChatCompletion.create(
                model=self.completion_model,
                messages=[
                    {"role": "system", "content": "You are an AI writing assistant helping with word and phrase suggestions."},
                    {"role": "user", "content": f"Suggest next words or phrases for: {current_text}"}
                ],
                max_tokens=50,
                temperature=0.7
            )
            
            suggestions = response.choices[0].message['content'].split('\n')
            return [s.strip() for s in suggestions if s.strip()]
            
        except Exception as e:
            logger.error(f"Error getting AI suggestions: {e}")
            return []
            
    def analyze_user_behavior(self, text_edit):
        """Analyze user's typing behavior for adaptive assistance."""
        try:
            current_text = text_edit.toPlainText()
            
            # Calculate metrics
            typing_speed = len(current_text) / (time.time() - self.start_time)
            error_rate = self.calculate_error_rate(current_text)
            
            # Update user metrics
            self.user_metrics['typing_speed'].append(typing_speed)
            self.user_metrics['error_rate'].append(error_rate)
            
            # Adapt interface based on metrics
            self.adapt_interface(text_edit)
            
        except Exception as e:
            logger.error(f"Error analyzing user behavior: {e}")
            
    def adapt_interface(self, text_edit):
        """Dynamically adapt interface based on user behavior."""
        try:
            if not self.settings_dict['ai_adaptation']:
                return
                
            # Calculate average metrics
            avg_speed = np.mean(self.user_metrics['typing_speed'][-10:])
            avg_error = np.mean(self.user_metrics['error_rate'][-10:])
            
            # Adjust text size and spacing
            if avg_error > 0.2:  # High error rate
                self.increase_text_size(1.1)
                self.settings_dict['text_spacing'] = min(2.0, self.settings_dict['text_spacing'] * 1.1)
            
            # Adjust cognitive support
            if avg_speed < 20:  # Slow typing speed
                self.cognitive_support.increase_assistance_level()
            
            # Save adaptations
            self.save_adaptations()
            
        except Exception as e:
            logger.error(f"Error adapting interface: {e}")
            
    def calculate_error_rate(self, text):
        """Calculate typing error rate using ML model."""
        try:
            words = text.split()
            if not words:
                return 0.0
                
            # Use sentiment analysis as a proxy for text quality
            sentiment = self.sentiment_analyzer(text)[0]
            
            # Complex error detection logic here
            error_rate = 1.0 - (sentiment['score'] if sentiment['label'] == 'POSITIVE' else 0.5)
            return error_rate
            
        except Exception as e:
            logger.error(f"Error calculating error rate: {e}")
            return 0.0
            
    def save_adaptations(self):
        """Save personalized adaptations to file."""
        try:
            adaptations = {
                'metrics': self.user_metrics,
                'settings': self.settings_dict
            }
            
            with open('user_adaptations.json', 'w') as f:
                json.dump(adaptations, f)
                
        except Exception as e:
            logger.error(f"Error saving adaptations: {e}")
            
    def setup_translation_ui(self):
        """Set up the translation interface."""
        try:
            # Create translation widget
            self.translation_widget = QWidget(self.parent)
            layout = QVBoxLayout()
            
            # Language selection
            lang_layout = QHBoxLayout()
            lang_label = QLabel("Target Language:")
            self.language_combo = QComboBox()
            self.language_combo.addItems(['English', 'Spanish', 'French', 'German', 'Chinese', 'Japanese'])
            self.language_combo.currentTextChanged.connect(self.change_target_language)
            lang_layout.addWidget(lang_label)
            lang_layout.addWidget(self.language_combo)
            
            # Translation display
            self.translation_display = QTextEdit()
            self.translation_display.setReadOnly(True)
            self.translation_display.setPlaceholderText("Translation will appear here...")
            
            layout.addLayout(lang_layout)
            layout.addWidget(self.translation_display)
            self.translation_widget.setLayout(layout)
            
        except Exception as e:
            logger.error(f"Error setting up translation UI: {e}")
            
    def change_target_language(self, language):
        """Change the target language for translation."""
        try:
            language_codes = {
                'English': 'en',
                'Spanish': 'es',
                'French': 'fr',
                'German': 'de',
                'Chinese': 'zh',
                'Japanese': 'ja'
            }
            self.current_language = language_codes.get(language, 'en')
            self.translation_worker.target_language = self.current_language
            self.settings.setValue('accessibility/target_language', self.current_language)
            
        except Exception as e:
            logger.error(f"Error changing language: {e}")
            
    def update_translation(self, original_text, translated_text):
        """Update the translation display."""
        try:
            self.translation_display.setText(translated_text)
        except Exception as e:
            logger.error(f"Error updating translation: {e}")
            
    def handle_translation_error(self, error_message):
        """Handle translation errors."""
        logger.error(error_message)
        self.translation_display.setText(f"Translation Error: {error_message}")
        
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
            'Ctrl+R': self.read_selected_text,
            'Ctrl+G': self.toggle_cognitive_assist,
            'Ctrl+P': self.toggle_post_concussion_mode
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
            ('&Voice Output', 'voice_output', 'Ctrl+M'),
            ('&Cognitive Assist', 'cognitive_assist', 'Ctrl+G'),
            ('&Post-Concussion Mode', 'post_concussion_mode', 'Ctrl+P'),
            ('&AI Adaptation', 'ai_adaptation', ''),
            ('&Smart Suggestions', 'smart_suggestions', ''),
            ('&GPT-4 Enhanced', 'gpt4_enhanced', ''),
            ('&Live Translation', 'live_translation', '')
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
            elif setting == 'cognitive_assist':
                self.toggle_cognitive_assist()
            elif setting == 'post_concussion_mode':
                self.toggle_post_concussion_mode()
                
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

    def toggle_cognitive_assist(self):
        """Toggle cognitive assistance features."""
        if self.settings_dict['cognitive_assist']:
            self.cognitive_support.profile.focus_assist = True
            self.cognitive_support.profile.memory_assist = True
            self.cognitive_support.enable_focus_mode(self.parent.findChild(QTextEdit))
            self.cognitive_support.apply_memory_assists(self.parent.findChild(QTextEdit))
        else:
            self.cognitive_support.profile.focus_assist = False
            self.cognitive_support.profile.memory_assist = False
            
    def toggle_post_concussion_mode(self):
        """Toggle post-concussion syndrome support mode."""
        if self.settings_dict['post_concussion_mode']:
            self.cognitive_support.adjust_for_post_concussion()
        else:
            # Reset to default settings
            self.cognitive_support.profile = CognitiveProfile()
            text_edit = self.parent.findChild(QTextEdit)
            if text_edit:
                # Reset text display
                font = text_edit.font()
                font.setPointSize(12)  # Default size
                text_edit.setFont(font)
                
                # Reset colors
                palette = text_edit.palette()
                palette.setColor(QPalette.Base, Qt.white)
                palette.setColor(QPalette.Text, Qt.black)
                text_edit.setPalette(palette)
                
                # Reset line spacing
                format = text_edit.document().defaultTextOption()
                format.setLineHeight(100, format.ProportionalHeight)
                text_edit.document().setDefaultTextOption(format)

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
