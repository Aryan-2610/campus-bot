import React from 'react';
import { Card, CardContent, Typography, Box } from '@mui/material';

const StatCard = ({ title, value, icon }) => {
  return (
    <Card variant="outlined">
      <CardContent>
        <Box sx={{ display: 'flex', alignItems: 'center' }}>
          <Box sx={{ color: 'action.active', mr: 2 }}>{icon}</Box>
          <Box>
            <Typography variant="h6" component="div">
              {value}
            </Typography>
            <Typography sx={{ color: 'text.secondary' }}>
              {title}
            </Typography>
          </Box>
        </Box>
      </CardContent>
    </Card>
  );
};

export default StatCard;