import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  Switch,
  FormControlLabel,
  TextField,
  Button,
  Grid,
  Snackbar,
  Alert,
  Tooltip,
  IconButton,
  Stack,
  Divider,
  CircularProgress,
} from '@mui/material';
import ContentCopyIcon from '@mui/icons-material/ContentCopy';
import PageTitle from '../components/common/PageTitle';
import { getBotConfig, updateBotConfig, getEmbedCode } from '../services/api';

/**
 * A view for managing the chatbot's configuration settings.
 * All fields are now enabled for frontend interaction.
 */
const BotConfiguration = () => {
  // --- THIS IS THE FIX: Added fallback_message to the initial state ---
  const [config, setConfig] = useState({
    enable_website: true,
    enable_whatsapp: false,
    enable_telegram: false,
    fallback_message: "Sorry, I couldn't find an answer to your question.",
  });
  const [embedCode, setEmbedCode] = useState('');
  const [loading, setLoading] = useState(true);
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'success' });

  // This hook still fetches the initial config, which is good practice.
  useEffect(() => {
    const fetchConfig = async () => {
      try {
        setLoading(true);
        const configRes = await getBotConfig();
        // Ensure fetched config includes the new field to prevent errors
        setConfig(prev => ({ ...prev, ...configRes.data })); 
        const embedRes = await getEmbedCode();
        setEmbedCode(embedRes.data.code);
      } catch (error) {
        console.error('Failed to fetch configuration:', error);
        setSnackbar({ open: true, message: 'Failed to load configuration', severity: 'error' });
      } finally {
        setLoading(false);
      }
    };
    fetchConfig();
  }, []);

  // --- THIS IS THE FIX: A generic handler for both switches and text fields ---
  const handleConfigChange = (event) => {
    const { name, value, checked, type } = event.target;
    setConfig((prevConfig) => ({
      ...prevConfig,
      [name]: type === 'checkbox' ? checked : value,
    }));
  };

  const handleSaveChanges = async () => {
    // This function will send the current state to the backend, including the new fields.
    try {
      await updateBotConfig(config);
      setSnackbar({ open: true, message: 'Configuration saved successfully!', severity: 'success' });
    } catch (error) {
      console.error('Failed to save configuration:', error);
      setSnackbar({ open: true, message: 'Failed to save configuration', severity: 'error' });
    }
  };

  const handleCopyToClipboard = () => {
    const textArea = document.createElement('textarea');
    textArea.value = embedCode;
    document.body.appendChild(textArea);
    textArea.focus();
    textArea.select();
    try {
      document.execCommand('copy');
      setSnackbar({ open: true, message: 'Embed code copied to clipboard!', severity: 'info' });
    } catch (err) {
      console.error('Failed to copy text: ', err);
      setSnackbar({ open: true, message: 'Failed to copy code', severity: 'error' });
    }
    document.body.removeChild(textArea);
  };
  
  const handleCloseSnackbar = (event, reason) => {
    if (reason === 'clickaway') {
      return;
    }
    setSnackbar({ ...snackbar, open: false });
  };

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box>
      <PageTitle
        title="Bot Configuration"
        subtitle="Manage chatbot settings, channels, and integrations"
      />

      <Grid container spacing={4} mt={1}>
        {/* Left Column: Core Settings */}
        <Grid item xs={12} lg={7}>
          <Stack spacing={3}>
            {/* Active Channels Card */}
            <Paper component="section" variant="outlined">
              <Box sx={{ p: 2 }}>
                <Typography variant="h6">Active Channels</Typography>
              </Box>
              <Divider />
              <Box sx={{ p: 2 }}>
                {/* --- THIS IS THE FIX: "disabled" prop removed and labels updated --- */}
                <FormControlLabel
                  control={<Switch checked={config.enable_website} onChange={handleConfigChange} name="enable_website" />}
                  label="Website Widget"
                />
                <FormControlLabel
                  control={<Switch checked={config.enable_whatsapp} onChange={handleConfigChange} name="enable_whatsapp" />}
                  label="WhatsApp"
                />
                <FormControlLabel
                  control={<Switch checked={config.enable_telegram} onChange={handleConfigChange} name="enable_telegram" />}
                  label="Telegram"
                />
              </Box>
            </Paper>

            {/* Behavior Settings Card */}
            <Paper component="section" variant="outlined">
              <Box sx={{ p: 2 }}>
                <Typography variant="h6">Behavior Settings</Typography>
              </Box>
              <Divider />
              <Box sx={{ p: 2 }}>
                {/* --- THIS IS THE FIX: Field is now enabled, controlled, and named --- */}
                <TextField
                  fullWidth
                  multiline
                  rows={3}
                  label="Fallback Message"
                  name="fallback_message"
                  value={config.fallback_message}
                  onChange={handleConfigChange}
                  helperText="The message sent when the bot cannot find an answer."
                />
              </Box>
            </Paper>
          </Stack>
        </Grid>

        {/* Right Column: Embed Code */}
        <Grid item xs={12} lg={5}>
          <Paper component="aside" variant="outlined">
            <Box sx={{ p: 2 }}>
              <Typography variant="h6">Embed Website Widget</Typography>
              <Typography variant="body2" color="text.secondary" mt={1}>
                Paste this snippet before the closing <code>&lt;/body&gt;</code> tag on your website.
              </Typography>
            </Box>
            <Divider />
            <Box sx={{ p: 2, position: 'relative' }}>
              <Box
                sx={{
                  backgroundColor: 'background.default',
                  p: 2,
                  borderRadius: 1,
                  fontFamily: 'monospace',
                  whiteSpace: 'pre-wrap',
                  wordBreak: 'break-all',
                  border: '1px solid',
                  borderColor: 'divider',
                }}
              >
                <code>{embedCode}</code>
              </Box>
              <Tooltip title="Copy to Clipboard">
                <IconButton
                  size="small"
                  onClick={handleCopyToClipboard}
                  sx={{ position: 'absolute', top: 24, right: 24 }}
                >
                  <ContentCopyIcon fontSize="small" />
                </IconButton>
              </Tooltip>
            </Box>
          </Paper>
        </Grid>
      </Grid>

      {/* Save Button */}
      <Box sx={{ mt: 3, display: 'flex' }}>
        <Button
          variant="contained"
          color="primary"
          onClick={handleSaveChanges}
        >
          Save Changes
        </Button>
      </Box>

      <Snackbar
        open={snackbar.open}
        autoHideDuration={4000}
        onClose={handleCloseSnackbar}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
      >
        <Alert onClose={handleCloseSnackbar} severity={snackbar.severity} sx={{ width: '100%' }}>
          {snackbar.message}
        </Alert>
      </Snackbar>
    </Box>
  );
};

export default BotConfiguration;