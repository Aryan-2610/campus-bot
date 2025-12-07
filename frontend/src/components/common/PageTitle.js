import React from 'react';
import { Typography, Box } from '@mui/material';

/**
 * A component to display a standardized page title and optional subtitle.
 * This ensures a consistent heading style across all pages of the application.
 *
 * @param {object} props - The component props.
 * @param {string} props.title - The main title of the page. This is required.
 * @param {string} [props.subtitle] - An optional subtitle or description displayed below the main title.
 */
const PageTitle = ({ title, subtitle }) => {
  return (
    <Box sx={{ mb: 4 }}>
      <Typography 
        variant="h4" 
        component="h1" 
        fontWeight="600" 
        gutterBottom
      >
        {title}
      </Typography>
      {subtitle && (
        <Typography 
          variant="subtitle1" 
          color="text.secondary"
        >
          {subtitle}
        </Typography>
      )}
    </Box>
  );
};

export default PageTitle;

