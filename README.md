# Enhanced Typing Assistant

A modern, accessible typing assistant with AI-powered features and real-time translation support.

## Features

- Real-time text suggestions using GPT-4
- Live translation support for multiple languages
- Cognitive accessibility features
- Dark/Light mode support
- Text-to-speech capabilities
- High contrast mode for visual accessibility
- WebSocket-based real-time updates
- Modern, responsive UI built with React and Material-UI

## Architecture

The application uses a three-tier architecture:

1. Frontend (React)
   - Material-UI components
   - Framer Motion animations
   - WebSocket communication
   - Responsive design
   - Accessibility features

2. Node.js Backend
   - Express.js server
   - Socket.IO for real-time communication
   - API endpoints for translation
   - Proxy to Python backend

3. Python Backend
   - GPT-4 integration
   - Translation services
   - Cognitive support features
   - Text analysis

## Setup

### Prerequisites

- Node.js 16+
- Python 3.12+
- OpenAI API key

### Installation

1. Install frontend dependencies:
```bash
cd frontend
npm install
```

2. Install backend dependencies:
```bash
cd backend
npm install
```

3. Install Python dependencies:
```bash
pip install -r requirements.txt
```

4. Create a .env file in the root directory:
```
OPENAI_API_KEY=your_api_key_here
```

### Running the Application

1. Start the Python backend:
```bash
python app.py
```

2. Start the Node.js backend:
```bash
cd backend
npm start
```

3. Start the React frontend:
```bash
cd frontend
npm start
```

The application will be available at http://localhost:3000

## Development

- Frontend development server runs on port 3000
- Node.js backend runs on port 5000
- Python backend communicates through stdin/stdout

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a new Pull Request

## License

MIT