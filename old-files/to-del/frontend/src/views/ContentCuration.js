import React from 'react';
import { Box, Typography, Paper } from '@mui/material';
import AutoFixHighIcon from '@mui/icons-material/AutoFixHigh';
import PageTitle from '../components/common/PageTitle';

/**
 * A placeholder view for the Content Curation page.
 * It informs the user that this feature is under development.
 */
const ContentCuration = () => {
  return (
    <Box>
      <PageTitle
        title="Content Curation"
        subtitle="Review and manage AI-powered content suggestions"
      />
      <Paper
        sx={{
          p: 4,
          mt: 3,
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          textAlign: 'center',
          minHeight: '60vh',
          backgroundColor: (theme) =>
            theme.palette.mode === 'dark' ? 'rgba(255, 255, 255, 0.05)' : 'rgba(0, 0, 0, 0.02)',
          border: '1px dashed',
          borderColor: 'divider',
        }}
      >
        <AutoFixHighIcon sx={{ fontSize: 60, color: 'text.secondary', mb: 2 }} />
        <Typography variant="h5" component="h2" gutterBottom>
          AI Curation Tools Coming Soon
        </Typography>
        <Typography color="text.secondary">
          This section will allow you to review, approve, edit, or discard AI-generated suggestions for new FAQs and document improvements to enhance the bot's knowledge base.
        </Typography>
      </Paper>
    </Box>
  );
};

export default ContentCuration;

