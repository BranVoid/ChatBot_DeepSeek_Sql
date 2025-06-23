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
  createTheme,
  List,
  ListItem,
  ListItemText,
  Divider
} from '@mui/material';
import ContentCopyIcon from '@mui/icons-material/ContentCopy';
import ArrowForwardIcon from '@mui/icons-material/ArrowForward';

// Create a theme instance
const theme = createTheme();

function App() {
  const [message, setMessage] = useState('');
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [history, setHistory] = useState([]); // Historial de mensajes

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
      const generatedQuery = response.data.query;

      // Actualizar el historial con el mensaje y la respuesta
      setHistory((prevHistory) => [
        ...prevHistory,
        { user: message, system: generatedQuery }
      ]);

      setQuery(generatedQuery);
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
      <Box display="flex" height="100vh">
        {/* Historial de mensajes en la columna izquierda */}
        <Box 
          flex={1} 
          bgcolor="grey.100" 
          p={2} 
          overflow="auto" 
          borderRight="1px solid grey"
          maxWidth="200px" // Limitar el ancho de la columna izquierda
        >
          <Typography variant="h6" gutterBottom>
            Historial de Consultas
          </Typography>
          <List>
            {history.map((entry, index) => (
              <React.Fragment key={index}>
                <ListItem alignItems="flex-start">
                  <ListItemText
                    primary={`Usuario: ${entry.user}`}
                    secondary={`Sistema: ${entry.system}`}
                  />
                </ListItem>
                <Divider />
              </React.Fragment>
            ))}
          </List>
        </Box>

        {/* Contenido principal en la columna derecha */}
        <Box flex={2} p={2} bgcolor="white" maxWidth="700px" mx="auto">
          <Typography variant="body1" gutterBottom>
            Describe que necesitas en lenguaje natural para obtener una consulta SQL generada.
          </Typography>

          <Box display="flex" alignItems="flex-start" gap={2}>
            <TextField
              fullWidth
              multiline
              rows={4}
              variant="outlined"
              label="Describe la Query de SQL que necesitas"
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              placeholder="Ejemplo: Yo tengo la llamada llamada 'usuarios' con las columnas id, nombre, correo y fecha de creacion. 
              Me gustaria obtener los usuarios que se registraron en la ultima semana."
              sx={{ mb: 2 }}
            />

            <IconButton
              color="primary"
              onClick={generateQuery}
              disabled={loading}
              sx={{ height: 'fit-content', mt: 1 }}
            >
              {loading ? <CircularProgress size={24} /> : <ArrowForwardIcon />}
            </IconButton>
          </Box>

          {error && (
            <Typography color="error" gutterBottom>
              {error}
            </Typography>
          )}

          {query && (
            <Box mt={2}>
              <Typography variant="body1" gutterBottom>
                Query generada:
              </Typography>
              <Paper elevation={1} sx={{ p: 2 }}>
                <Typography variant="body2">{query}</Typography>
                <IconButton onClick={copyToClipboard} sx={{ mt: 1 }}>
                  <ContentCopyIcon />
                </IconButton>
              </Paper>
            </Box>
          )}
        </Box>
      </Box>
    </ThemeProvider>
  );
}

export default App;