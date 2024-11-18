const express = require('express');
const cors = require('cors');
const { createServer } = require('http');
const { Server } = require('socket.io');
const { spawn } = require('child_process');
const path = require('path');

const app = express();
const httpServer = createServer(app);
const io = new Server(httpServer, {
  cors: {
    origin: 'http://localhost:3000',
    methods: ['GET', 'POST'],
  },
});

app.use(cors());
app.use(express.json());

// Start Python backend process
const pythonProcess = spawn('python', ['../app.py'], {
  stdio: ['pipe', 'pipe', 'pipe'],
});

pythonProcess.stdout.on('data', (data) => {
  console.log(`Python stdout: ${data}`);
});

pythonProcess.stderr.on('data', (data) => {
  console.error(`Python stderr: ${data}`);
});

// WebSocket connection handling
io.on('connection', (socket) => {
  console.log('Client connected');

  socket.on('text_update', async (data) => {
    try {
      // Send text to Python backend
      pythonProcess.stdin.write(JSON.stringify({
        type: 'text_update',
        data: data.text,
      }) + '\n');

      // Mock response for now (replace with actual Python backend response)
      socket.emit('suggestions', {
        suggestions: ['Suggestion 1', 'Suggestion 2'],
      });
    } catch (error) {
      console.error('Error processing text update:', error);
    }
  });

  socket.on('disconnect', () => {
    console.log('Client disconnected');
  });
});

// API endpoints
app.post('/translate', async (req, res) => {
  try {
    const { text, targetLang } = req.body;
    
    // Send translation request to Python backend
    pythonProcess.stdin.write(JSON.stringify({
      type: 'translate',
      data: { text, targetLang },
    }) + '\n');

    // Mock response for now (replace with actual Python backend response)
    res.json({
      translation: `Translated: ${text}`,
    });
  } catch (error) {
    console.error('Translation error:', error);
    res.status(500).json({ error: 'Translation failed' });
  }
});

// Serve static files in production
if (process.env.NODE_ENV === 'production') {
  app.use(express.static(path.join(__dirname, '../frontend/build')));
  app.get('*', (req, res) => {
    res.sendFile(path.join(__dirname, '../frontend/build/index.html'));
  });
}

const PORT = process.env.PORT || 5000;
httpServer.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});
