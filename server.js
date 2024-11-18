const express = require('express');
const cors = require('cors');
const { PythonShell } = require('python-shell');
const path = require('path');
const bodyParser = require('body-parser');
const app = express();
const http = require('http').createServer(app);
const io = require('socket.io')(http, {
    cors: {
        origin: "http://localhost:3000",
        methods: ["GET", "POST"]
    }
});

// Middleware
app.use(cors());
app.use(bodyParser.json());
app.use(express.static(path.join(__dirname, 'client/build')));

// Python shell options
const pythonOptions = {
    pythonPath: 'python',
    scriptPath: path.join(__dirname, 'typing_assistant/gec')
};

// WebSocket connection handling
io.on('connection', (socket) => {
    console.log('Client connected');

    socket.on('text-correction', async (data) => {
        try {
            const options = {
                ...pythonOptions,
                args: [
                    '--text', data.text,
                    '--domain', data.domain || 'general'
                ]
            };

            PythonShell.run('correct_text.py', options).then(results => {
                const corrections = JSON.parse(results[0]);
                socket.emit('correction-result', corrections);
            }).catch(err => {
                console.error('Error running Python script:', err);
                socket.emit('correction-error', { error: 'Correction failed' });
            });
        } catch (error) {
            console.error('Error processing correction:', error);
            socket.emit('correction-error', { error: 'Processing failed' });
        }
    });

    socket.on('disconnect', () => {
        console.log('Client disconnected');
    });
});

// API Routes
app.post('/api/correct', async (req, res) => {
    try {
        const { text, domain } = req.body;
        const options = {
            ...pythonOptions,
            args: [
                '--text', text,
                '--domain', domain || 'general'
            ]
        };

        PythonShell.run('correct_text.py', options).then(results => {
            const corrections = JSON.parse(results[0]);
            res.json(corrections);
        }).catch(err => {
            console.error('Error running Python script:', err);
            res.status(500).json({ error: 'Correction failed' });
        });
    } catch (error) {
        console.error('Error processing correction:', error);
        res.status(500).json({ error: 'Processing failed' });
    }
});

// Serve React app in production
if (process.env.NODE_ENV === 'production') {
    app.get('*', (req, res) => {
        res.sendFile(path.join(__dirname, 'client/build/index.html'));
    });
}

const PORT = process.env.PORT || 5000;
http.listen(PORT, () => {
    console.log(`Server running on port ${PORT}`);
});
