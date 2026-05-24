import React from 'react';
import { Box, Typography, Paper } from '@mui/material';
import AccountTreeIcon from '@mui/icons-material/AccountTree';
import PageTitle from '../components/common/PageTitle';

/**
 * A placeholder view for the conversation Flow Builder.
 * This component informs the user that the feature is under development.
 */
const FlowBuilder = () => {
  return (
    <Box>
      <PageTitle
        title="Flow Builder"
        subtitle="Visually design and manage conversation flows"
      />
      
      <Paper
        sx={{
          mt: 3,
          p: 4,
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          height: '60vh',
          backgroundColor: 'action.hover',
        }}
      >
        <AccountTreeIcon sx={{ fontSize: 64, color: 'text.secondary', mb: 2 }} />
        <Typography variant="h5" component="h2" gutterBottom>
          Coming Soon!
        </Typography>
        <Typography color="text.secondary" sx={{ maxWidth: '400px', textAlign: 'center' }}>
          We're working on a powerful drag-and-drop editor to help you create dynamic and engaging conversation flows. Stay tuned!
        </Typography>
      </Paper>
    </Box>
  );
};

export default FlowBuilder;

