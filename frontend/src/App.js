import React, { useState } from 'react';
import axios from 'axios';
import { 
  Container, 
  TextField, 
  Button, 
  Typography, 
  Paper, 
  Box, 
  CircularProgress,
  IconButton,
  ThemeProvider,
  createTheme
} from '@mui/material';
import ContentCopyIcon from '@mui/icons-material/ContentCopy';

// Create a theme instance
const theme = createTheme();

function App() {
  const [message, setMessage] = useState('');
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const generateQuery = async () => {
    if (!message.trim()) {
      setError('Please enter your request');
      return;
    }

    setLoading(true);
    setError('');
    
    try {
      const response = await axios.post('http://localhost:5000/generate-query', {
        message: message
      });
      setQuery(response.data.query);
    } catch (err) {
      setError('Failed to generate query. Please try again.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const copyToClipboard = () => {
    navigator.clipboard.writeText(query);
  };

  return (
    <ThemeProvider theme={theme}>
      <Container maxWidth="md" sx={{ my: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Generador de Query de SQL
        </Typography>
        <Typography variant="body1" gutterBottom>
          Describe que necesitas en lenguaje natural para obtener una consulta SQL generada.
        </Typography>

        <TextField
          fullWidth
          multiline
          rows={8}
          variant="outlined"
          label="Describe la Query de SQL que necesitas"
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          placeholder="Ejemplo: Yo tengo la llamada llamada 'usuarios' con las columnas id, nombre, correo y fecha de creacion. 
          Me gustaria obtener los usuarios que se registraron en la ultima semana."
          sx={{ mb: 2 }}
        />

        {error && (
          <Typography color="error" gutterBottom>
            {error}
          </Typography>
        )}

        <Button
          variant="contained"
          color="primary"
          onClick={generateQuery}
          disabled={loading}
        >
          {loading ? <CircularProgress size={24} /> : 'Genera la query de SQL'}
        </Button>

        {query && (
          <Paper elevation={3} sx={{ p: 3, mt: 3, backgroundColor: 'grey.100' }}>
            <Box display="flex" justifyContent="space-between" alignItems="center">
              <Typography variant="h6" gutterBottom>
                Query de SQL generada:
              </Typography>
              <IconButton onClick={copyToClipboard} title="Copy to clipboard">
                <ContentCopyIcon />
              </IconButton>
            </Box>
            <Box 
              component="pre" 
              sx={{ 
                backgroundColor: 'white', 
                p: 2, 
                borderRadius: 1,
                overflowX: 'auto'
              }}
            >
              {query}
            </Box>
          </Paper>
        )}
      </Container>
    </ThemeProvider>
  );
}

export default App;