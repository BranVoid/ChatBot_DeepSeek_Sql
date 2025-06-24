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
  Divider,
  Chip,
  Tooltip
} from '@mui/material';
import ContentCopyIcon from '@mui/icons-material/ContentCopy';
import AssistantIcon from '@mui/icons-material/Assistant';
import PersonIcon from '@mui/icons-material/Person';
import DeleteIcon from '@mui/icons-material/Delete';

// Create a theme instance
const theme = createTheme({
  palette: {
    primary: {
      main: '#2e7d32', // verde financiero
    },
    secondary: {
      main: '#1565c0', // azul confianza
    },
  },
});

function App() {
  const [inputMessage, setInputMessage] = useState('');
  const [conversation, setConversation] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const generateQuery = async () => {
    if (!inputMessage.trim()) {
      setError('Por favor escribe tu solicitud');
      return;
    }

    setLoading(true);
    setError('');
    
    try {
      // Agregar mensaje de usuario a la conversación
      const userMessage = { role: 'user', content: inputMessage };
      const updatedConversation = [...conversation, userMessage];
      setConversation(updatedConversation);
      setInputMessage('');

      // Enviar todo el historial de conversación al backend
      const response = await axios.post('http://localhost:5000/generate-query', {
        message: inputMessage,
        history: updatedConversation.filter(msg => msg.role !== 'system')
      });

      // Agregar respuesta del asistente a la conversación
      setConversation(prev => [
        ...prev, 
        { role: 'assistant', content: response.data.response }
      ]);
    } catch (err) {
      setError('Error al generar la respuesta. Por favor intenta nuevamente.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text);
  };

  const clearConversation = () => {
    setConversation([]);
  };

  // Extraer la última consulta SQL generada
  const lastSqlQuery = conversation.length > 0 && 
                        conversation[conversation.length - 1].role === 'assistant' ?
                        conversation[conversation.length - 1].content : '';

  // Función para formatear el contenido del asistente
  const formatAssistantContent = (content) => {
    // Si contiene un bloque de código SQL
    if (content.includes('```sql')) {
      const parts = content.split('```sql');
      const explanation = parts[0];
      const sqlPart = parts[1] ? parts[1].split('```')[0] : '';
      
      return (
        <Box>
          <Typography variant="body1" component="div" sx={{ whiteSpace: 'pre-line', mb: 2 }}>
            {explanation}
          </Typography>
          {sqlPart && (
            <Box 
              component="pre" 
              sx={{ 
                backgroundColor: '#f5f5f5', 
                p: 2, 
                borderRadius: 1,
                overflowX: 'auto'
              }}
            >
              {sqlPart}
            </Box>
          )}
        </Box>
      );
    }
    
    // Si es una respuesta normal
    return (
      <Typography variant="body1" component="div" sx={{ whiteSpace: 'pre-line' }}>
        {content}
      </Typography>
    );
  };

  return (
    <ThemeProvider theme={theme}>
      <Container maxWidth="md" sx={{ my: 4 }}>
        <Box display="flex" justifyContent="space-between" alignItems="center">
          <Typography variant="h4" component="h1" gutterBottom>
            Asistente SQL Financiero
          </Typography>
          <Button 
            variant="outlined" 
            color="secondary" 
            startIcon={<DeleteIcon />}
            onClick={clearConversation}
            disabled={conversation.length === 0}
          >
            Limpiar Conversación
          </Button>
        </Box>
        
        <Typography variant="subtitle1" gutterBottom color="primary">
          Experto en SQL, finanzas, microfinanzas y análisis comercial
        </Typography>

        {/* Historial de conversación */}
        <Paper elevation={2} sx={{ p: 2, mb: 2, maxHeight: '400px', overflowY: 'auto' }}>
          {conversation.length === 0 ? (
            <Typography variant="body2" color="textSecondary" sx={{ textAlign: 'center', py: 4 }}>
              Describe tu necesidad financiera o SQL para comenzar la conversación...
            </Typography>
          ) : (
            <List>
              {conversation.map((msg, index) => (
                <React.Fragment key={index}>
                  <ListItem alignItems="flex-start">
                    {msg.role === 'user' ? (
                      <PersonIcon color="primary" sx={{ mr: 1 }} />
                    ) : (
                      <AssistantIcon color="secondary" sx={{ mr: 1 }} />
                    )}
                    <ListItemText
                      primary={
                        <Box>
                          <Typography variant="subtitle2" component="span">
                            {msg.role === 'user' ? 'Tú' : 'Asistente SQL'}
                          </Typography>
                          {msg.role === 'assistant' && msg.content.includes('```sql') && (
                            <Tooltip title="Copiar SQL">
                              <IconButton 
                                size="small" 
                                onClick={() => {
                                  const sqlPart = msg.content.split('```sql')[1]?.split('```')[0] || '';
                                  copyToClipboard(sqlPart);
                                }}
                                sx={{ ml: 1 }}
                              >
                                <ContentCopyIcon fontSize="small" />
                              </IconButton>
                            </Tooltip>
                          )}
                        </Box>
                      }
                      secondary={
                        msg.role === 'assistant' ? (
                          formatAssistantContent(msg.content)
                        ) : (
                          <Typography variant="body1" sx={{ whiteSpace: 'pre-line' }}>
                            {msg.content}
                          </Typography>
                        )
                      }
                      secondaryTypographyProps={{ component: 'div' }}
                    />
                  </ListItem>
                  {index < conversation.length - 1 && <Divider component="li" />}
                </React.Fragment>
              ))}
            </List>
          )}
        </Paper>

        {/* Entrada de mensaje */}
        <TextField
          fullWidth
          multiline
          minRows={3}
          maxRows={6}
          variant="outlined"
          label="Describe tu necesidad financiera o SQL"
          value={inputMessage}
          onChange={(e) => setInputMessage(e.target.value)}
          placeholder="Ejemplo: Necesito calcular la morosidad (PAR) de una cartera de microcréditos con una tabla llamada 'prestamos' que tiene las columnas: id, cliente_id, monto, fecha_desembolso, estado, dias_mora"
          disabled={loading}
          sx={{ mb: 2 }}
          onKeyDown={(e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
              e.preventDefault();
              generateQuery();
            }
          }}
        />

        {error && (
          <Typography color="error" gutterBottom>
            {error}
          </Typography>
        )}

        <Box display="flex" justifyContent="space-between">
          <Chip 
            label="Finanzas" 
            color="primary" 
            variant="outlined" 
            size="small" 
            sx={{ mr: 1 }}
          />
          <Chip 
            label="Microfinanzas" 
            color="primary" 
            variant="outlined" 
            size="small" 
            sx={{ mr: 1 }}
          />
          <Chip 
            label="Comercial" 
            color="primary" 
            variant="outlined" 
            size="small" 
            sx={{ mr: 1 }}
          />
          <Button
            variant="contained"
            color="primary"
            onClick={generateQuery}
            disabled={loading || !inputMessage.trim()}
            sx={{ ml: 'auto' }}
          >
            {loading ? <CircularProgress size={24} /> : 'Enviar'}
          </Button>
        </Box>

        {/* Última query SQL destacada */}
        {lastSqlQuery.includes('```sql') && (
          <Paper elevation={3} sx={{ p: 3, mt: 3, backgroundColor: 'grey.50' }}>
            <Box display="flex" justifyContent="space-between" alignItems="center">
              <Typography variant="h6" gutterBottom>
                Consulta SQL Generada:
              </Typography>
              <IconButton 
                onClick={() => {
                  const sqlPart = lastSqlQuery.split('```sql')[1]?.split('```')[0] || '';
                  copyToClipboard(sqlPart);
                }} 
                title="Copiar SQL"
              >
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
              {lastSqlQuery.split('```sql')[1]?.split('```')[0] || lastSqlQuery}
            </Box>
          </Paper>
        )}
      </Container>
    </ThemeProvider>
  );
}

export default App;