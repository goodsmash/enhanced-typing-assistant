# Enhanced Typing Assistant with Multi-Model AI Support

A comprehensive typing assistance tool that leverages multiple AI models for advanced text correction, style enhancement, and cognitive support. This enhanced version includes intelligent model selection, usage tracking, and accessibility features.

## Features

### Advanced AI Integration
- Multiple AI Model Support:
  - OpenAI GPT-4 Turbo and GPT-3.5 Turbo
  - Anthropic Claude-3 Opus and Sonnet
- Task-Specific Model Selection
- Intelligent Cost Management
- Usage Statistics and Analytics

### Task Support
- Grammar Correction
- Spelling Check
- Style Enhancement
- Text Rewriting
- Content Analysis
- Text Summarization

### Accessibility Features
- High Contrast Mode
- Large Text Support
- Dyslexic-Friendly Font
- Screen Reader Compatibility

### User Interface
- Modern, Intuitive Design
- Real-time Model Information
- Usage Statistics Dashboard
- Task-Specific Controls

## Technical Requirements

### Dependencies
```
openai>=1.0.0
anthropic>=0.3.0
PyQt5>=5.15.0
tiktoken>=0.5.0
thefuzz>=0.19.0
python-dotenv>=0.19.0
```

### API Keys Required
- OpenAI API Key
- Anthropic API Key

## Installation

1. Clone the repository:
```bash
git clone [repository-url]
cd typing-assistant
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
# Create .env file
OPENAI_API_KEY=your_openai_key_here
ANTHROPIC_API_KEY=your_anthropic_key_here
```

4. Run the application:
```bash
python main.py
```

## Usage

1. Select your task type (Grammar, Style, Rewrite, etc.)
2. Choose your preferred AI model or let the system recommend one
3. Type or paste your text
4. Enable auto-correct for real-time corrections
5. Monitor usage and costs in the Statistics tab

## Model Selection Guide

### GPT-4 Turbo
- Best for: Complex analysis, technical writing
- Strengths: Advanced reasoning, context understanding
- Cost: Premium pricing

### GPT-3.5 Turbo
- Best for: Quick corrections, basic tasks
- Strengths: Fast, cost-effective
- Cost: Budget-friendly

### Claude-3 Opus
- Best for: Long documents, research writing
- Strengths: Large context window, analytical tasks
- Cost: Premium pricing

### Claude-3 Sonnet
- Best for: General writing tasks
- Strengths: Good balance of quality and speed
- Cost: Moderate pricing

## Contributing

Contributions are welcome! Please feel free to submit pull requests.

## License

This project is licensed under the MIT License - see the LICENSE file for details.