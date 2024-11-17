import React, { useState, useEffect, useCallback } from 'react';
import { Editor } from '@monaco-editor/react';
import { debounce } from 'lodash';
import {
  Box,
  Container,
  Paper,
  Typography,
  CircularProgress,
  Snackbar,
  Alert,
  Chip,
  Stack,
  IconButton,
  Tooltip,
} from '@mui/material';
import {
  Check as CheckIcon,
  ContentCopy as ContentCopyIcon,
  Refresh as RefreshIcon,
} from '@mui/icons-material';

interface Correction {
  original: string;
  suggestion: string;
  start: number;
  end: number;
  confidence: number;
  type: string;
}

interface CorrectionResponse {
  original_text: string;
  corrected_text: string;
  corrections: Correction[];
  confidence: number;
}

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const GenderInclusiveEditor: React.FC = () => {
  const [text, setText] = useState<string>('');
  const [correctedText, setCorrectedText] = useState<string>('');
  const [corrections, setCorrections] = useState<Correction[]>([]);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [copied, setCopied] = useState<boolean>(false);

  const fetchCorrections = useCallback(
    debounce(async (inputText: string) => {
      if (!inputText.trim()) {
        setCorrectedText('');
        setCorrections([]);
        return;
      }

      try {
        setLoading(true);
        const response = await fetch(`${API_URL}/correct`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            text: inputText,
            context: {
              file_path: 'input.txt',
            },
          }),
        });

        if (!response.ok) {
          throw new Error('Failed to fetch corrections');
        }

        const data: CorrectionResponse = await response.json();
        setCorrectedText(data.corrected_text);
        setCorrections(data.corrections);
        setError(null);
      } catch (err) {
        setError((err as Error).message);
      } finally {
        setLoading(false);
      }
    }, 500),
    []
  );

  useEffect(() => {
    fetchCorrections(text);
  }, [text, fetchCorrections]);

  const handleCopy = () => {
    navigator.clipboard.writeText(correctedText);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleReset = () => {
    setText('');
    setCorrectedText('');
    setCorrections([]);
  };

  return (
    <Container maxWidth="lg">
      <Box sx={{ my: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Gender-Inclusive Language Editor
        </Typography>

        <Stack direction="row" spacing={2} sx={{ mb: 2 }}>
          <Chip
            label={`${corrections.length} suggestions`}
            color="primary"
            variant="outlined"
          />
          <IconButton
            onClick={handleCopy}
            color={copied ? 'success' : 'default'}
            title="Copy corrected text"
          >
            {copied ? <CheckIcon /> : <ContentCopyIcon />}
          </IconButton>
          <IconButton onClick={handleReset} title="Reset">
            <RefreshIcon />
          </IconButton>
        </Stack>

        <Paper elevation={3} sx={{ mb: 4, p: 2 }}>
          <Typography variant="h6" gutterBottom>
            Original Text
          </Typography>
          <Editor
            height="200px"
            defaultLanguage="text"
            value={text}
            onChange={(value) => setText(value || '')}
            options={{
              minimap: { enabled: false },
              lineNumbers: 'off',
              wordWrap: 'on',
              wrappingIndent: 'indent',
            }}
          />
        </Paper>

        <Paper elevation={3} sx={{ p: 2 }}>
          <Typography variant="h6" gutterBottom>
            Corrected Text
            {loading && (
              <CircularProgress
                size={20}
                sx={{ ml: 2, verticalAlign: 'middle' }}
              />
            )}
          </Typography>
          <Editor
            height="200px"
            defaultLanguage="text"
            value={correctedText}
            options={{
              readOnly: true,
              minimap: { enabled: false },
              lineNumbers: 'off',
              wordWrap: 'on',
              wrappingIndent: 'indent',
            }}
          />
        </Paper>

        {corrections.length > 0 && (
          <Paper elevation={3} sx={{ mt: 4, p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Suggestions
            </Typography>
            <Stack spacing={1}>
              {corrections.map((correction, index) => (
                <Box
                  key={index}
                  sx={{
                    p: 2,
                    border: 1,
                    borderColor: 'divider',
                    borderRadius: 1,
                  }}
                >
                  <Typography color="text.secondary" gutterBottom>
                    Original: <strong>{correction.original}</strong>
                  </Typography>
                  <Typography color="primary">
                    Suggestion: <strong>{correction.suggestion}</strong>
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    Confidence: {Math.round(correction.confidence * 100)}%
                  </Typography>
                </Box>
              ))}
            </Stack>
          </Paper>
        )}

        <Snackbar
          open={error !== null}
          autoHideDuration={6000}
          onClose={() => setError(null)}
        >
          <Alert severity="error" onClose={() => setError(null)}>
            {error}
          </Alert>
        </Snackbar>
      </Box>
    </Container>
  );
};

export default GenderInclusiveEditor;
