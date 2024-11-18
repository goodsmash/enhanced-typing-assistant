import React, { useState, useEffect } from 'react';
import {
  ThemeProvider,
  CssBaseline,
  createTheme,
  Box,
  AppBar,
  Toolbar,
  IconButton,
  Typography,
  Container,
  Paper,
  TextField,
  Button,
  Menu,
  MenuItem,
  Switch,
} from '@mui/material';
import {
  Brightness4,
  Brightness7,
  Settings,
  Translate,
  AccessibilityNew,
  VolumeUp,
} from '@mui/icons-material';
import { motion, AnimatePresence } from 'framer-motion';
import axios from 'axios';
import io from 'socket.io-client';

// Create theme with light and dark mode
const getTheme = (mode) =>
  createTheme({
    palette: {
      mode,
      primary: {
        main: '#2196f3',
      },
      secondary: {
        main: '#f50057',
      },
    },
    typography: {
      fontFamily: '"Roboto", "Helvetica", "Arial", sans-serif',
    },
    components: {
      MuiTextField: {
        defaultProps: {
          variant: 'outlined',
        },
      },
    },
  });

function App() {
  const [darkMode, setDarkMode] = useState(false);
  const [text, setText] = useState('');
  const [suggestions, setSuggestions] = useState([]);
  const [translatedText, setTranslatedText] = useState('');
  const [liveTranslation, setLiveTranslation] = useState(false);
  const [anchorEl, setAnchorEl] = useState(null);
  const [socket, setSocket] = useState(null);
  const [settings, setSettings] = useState({
    language: 'en',
    accessibility: {
      highContrast: false,
      textToSpeech: false,
      cognitiveSupport: false,
    },
  });

  // Initialize WebSocket connection
  useEffect(() => {
    const newSocket = io('http://localhost:5000');
    setSocket(newSocket);

    newSocket.on('suggestions', (data) => {
      setSuggestions(data.suggestions);
    });

    newSocket.on('translation', (data) => {
      setTranslatedText(data.translation);
    });

    return () => newSocket.close();
  }, []);

  // Handle text changes
  const handleTextChange = async (e) => {
    const newText = e.target.value;
    setText(newText);

    if (socket) {
      socket.emit('text_update', { text: newText });
    }

    if (liveTranslation) {
      try {
        const response = await axios.post('http://localhost:5000/translate', {
          text: newText,
          targetLang: settings.language,
        });
        setTranslatedText(response.data.translation);
      } catch (error) {
        console.error('Translation error:', error);
      }
    }
  };

  // Settings menu
  const handleSettingsClick = (event) => {
    setAnchorEl(event.currentTarget);
  };

  const handleSettingsClose = () => {
    setAnchorEl(null);
  };

  const toggleSetting = (setting) => {
    setSettings((prev) => ({
      ...prev,
      accessibility: {
        ...prev.accessibility,
        [setting]: !prev.accessibility[setting],
      },
    }));
  };

  return (
    <ThemeProvider theme={getTheme(darkMode ? 'dark' : 'light')}>
      <CssBaseline />
      <Box sx={{ flexGrow: 1, minHeight: '100vh' }}>
        <AppBar position="static">
          <Toolbar>
            <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
              Enhanced Typing Assistant
            </Typography>
            <IconButton onClick={() => setDarkMode(!darkMode)} color="inherit">
              {darkMode ? <Brightness7 /> : <Brightness4 />}
            </IconButton>
            <IconButton onClick={handleSettingsClick} color="inherit">
              <Settings />
            </IconButton>
          </Toolbar>
        </AppBar>

        <Container maxWidth="md" sx={{ mt: 4 }}>
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
          >
            <Paper elevation={3} sx={{ p: 3 }}>
              <TextField
                fullWidth
                multiline
                rows={6}
                value={text}
                onChange={handleTextChange}
                placeholder="Start typing here..."
                sx={{ mb: 2 }}
              />

              <AnimatePresence>
                {liveTranslation && translatedText && (
                  <motion.div
                    initial={{ opacity: 0, height: 0 }}
                    animate={{ opacity: 1, height: 'auto' }}
                    exit={{ opacity: 0, height: 0 }}
                  >
                    <Paper
                      elevation={1}
                      sx={{ p: 2, mb: 2, bgcolor: 'background.default' }}
                    >
                      <Typography variant="body1">{translatedText}</Typography>
                    </Paper>
                  </motion.div>
                )}
              </AnimatePresence>

              {suggestions.length > 0 && (
                <Box sx={{ mt: 2 }}>
                  {suggestions.map((suggestion, index) => (
                    <Button
                      key={index}
                      variant="outlined"
                      size="small"
                      sx={{ mr: 1, mb: 1 }}
                      onClick={() => setText(suggestion)}
                    >
                      {suggestion}
                    </Button>
                  ))}
                </Box>
              )}
            </Paper>
          </motion.div>
        </Container>

        <Menu
          anchorEl={anchorEl}
          open={Boolean(anchorEl)}
          onClose={handleSettingsClose}
        >
          <MenuItem>
            <Translate sx={{ mr: 1 }} />
            <Typography>Live Translation</Typography>
            <Switch
              checked={liveTranslation}
              onChange={() => setLiveTranslation(!liveTranslation)}
            />
          </MenuItem>
          <MenuItem>
            <AccessibilityNew sx={{ mr: 1 }} />
            <Typography>High Contrast</Typography>
            <Switch
              checked={settings.accessibility.highContrast}
              onChange={() => toggleSetting('highContrast')}
            />
          </MenuItem>
          <MenuItem>
            <VolumeUp sx={{ mr: 1 }} />
            <Typography>Text to Speech</Typography>
            <Switch
              checked={settings.accessibility.textToSpeech}
              onChange={() => toggleSetting('textToSpeech')}
            />
          </MenuItem>
        </Menu>
      </Box>
    </ThemeProvider>
  );
}

export default App;
