import React from 'react';
import { Box, Typography, Paper } from '@mui/material';
import BarChartIcon from '@mui/icons-material/BarChart';
import PageTitle from '../components/common/PageTitle';

/**
 * A placeholder view for the Analytics page.
 * It informs the user that this feature is under development.
 */
const Analytics = () => {
  return (
    <Box>
      <PageTitle
        title="Analytics"
        subtitle="Insights into bot performance and user engagement"
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
        <BarChartIcon sx={{ fontSize: 60, color: 'text.secondary', mb: 2 }} />
        <Typography variant="h5" component="h2" gutterBottom>
          Analytics Dashboard Coming Soon
        </Typography>
        <Typography color="text.secondary">
          We are currently developing this section to bring you detailed charts and reports on daily conversations, user metrics, and overall performance.
        </Typography>
      </Paper>
    </Box>
  );
};

export default Analytics;

