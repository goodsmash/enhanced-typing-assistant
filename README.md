# Enhanced Typing Assistant

A Python-based typing assistant with advanced accessibility features, designed to help users with motor control challenges and typing difficulties.

## Features

- Real-time spelling correction and grammar improvement
- Word prediction with motor control pattern recognition
- Text-to-speech feedback with multiple voice options
- Speech-to-text transcription and translation
- Content moderation for safe text input
- High contrast and color-blind friendly themes
- Adjustable text size and spacing
- Simplified interface mode
- Keyboard shortcuts for all features
- Multiple language support

## Requirements

- Python 3.8 or higher
- PyQt5
- OpenAI API key (for advanced features)
- Windows, macOS, or Linux
- Microphone (for speech input)
- Speakers (for text-to-speech)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/typing_assistant.git
cd typing_assistant
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up your OpenAI API key:
```bash
python set_api_key.py
```

## Usage

1. Start the application:
```bash
python app.py
```

2. Register a new account or login with existing credentials

3. Basic Usage:
   - Type or paste text in the input area
   - Use voice input with the microphone button
   - Enable auto-correct for real-time corrections
   - Adjust font size and voice speed as needed
   - Use the theme selector for different visual modes

4. Keyboard Shortcuts:
   - Ctrl+C: Copy text
   - Ctrl+V: Paste text
   - Ctrl+Z: Undo
   - Ctrl+Y: Redo
   - F1: Show help
   - Ctrl+Q: Quit

## Configuration

- `.env`: Environment variables and API keys
- `config.py`: Application settings
- `styles.py`: UI themes and styling

## Accessibility Features

1. Visual Accessibility:
   - High contrast theme
   - Adjustable font sizes
   - Color-blind friendly design
   - Custom font support for dyslexia

2. Motor Control Support:
   - Voice input
   - Word prediction
   - Auto-correction
   - Simplified interface mode

3. Auditory Support:
   - Text-to-speech
   - Voice speed control
   - Multiple language voices

## Debug Mode

The application includes a comprehensive debug panel (press Ctrl+D to open) that provides:

1. Component Status:
   - Text Processor status
   - Speech Handler status
   - API Connection status
   - Spell Check status
   - Grammar Check status

2. Real-time Statistics:
   - Memory usage
   - CPU usage
   - Active threads
   - API calls
   - Text processing metrics

3. Logging:
   - Configurable log levels (DEBUG, INFO, WARNING, ERROR)
   - Color-coded log entries
   - Log file export
   - Component-specific logging

## Application Architecture

1. Core Components:
   - `text_processor.py`: Handles text analysis and correction
   - `speech_handler.py`: Manages speech input/output
   - `accessibility.py`: Controls accessibility features
   - `config_manager.py`: Manages application settings
   - `debug_panel.py`: Provides debugging interface

2. User Interface:
   - Modern PyQt5-based interface
   - Responsive design
   - Theme support
   - Accessibility-first approach

3. Data Flow:
   - Input Processing → Text Analysis → Correction Suggestions
   - Speech Input → Text Conversion → Processing
   - Configuration → Feature Enablement → UI Updates

## Advanced Features

1. Text Processing:
   - Multiple correction modes (Standard, Strict, Creative)
   - Pattern recognition for common mistakes
   - Context-aware corrections
   - Custom dictionary support

2. Speech Features:
   - Multiple voice options
   - Voice speed control
   - Custom pronunciation rules
   - Background noise filtering

3. Accessibility Options:
   - Screen reader compatibility
   - Keyboard navigation
   - Focus indicators
   - Motion reduction

## Troubleshooting

1. Application Issues:
   - Check the debug panel (Ctrl+D) for component status
   - Review logs for error messages
   - Verify API key configuration
   - Check system requirements

2. Text Processing Issues:
   - Verify correction mode settings
   - Check language configuration
   - Review custom dictionary entries
   - Monitor CPU usage in debug panel

3. Speech Issues:
   - Check microphone/speaker settings
   - Verify voice package installation
   - Review speech rate settings
   - Check audio device permissions

4. Database Issues:
   - Delete `typing_assistant.db` and restart the app
   - Check file permissions

5. Audio Problems:
   - Verify microphone/speaker connections
   - Check system audio settings
   - Update audio drivers

6. API Key Issues:
   - Rerun `set_api_key.py`
   - Check internet connection
   - Verify API key validity

## Security

- Passwords are hashed using SHA-256
- API keys are encrypted
- Input is sanitized
- Content moderation enabled

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support, please:
1. Check the documentation
2. Search existing issues
3. Create a new issue with:
   - System details
   - Error messages
   - Steps to reproduce