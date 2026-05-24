// TicketManagement.js

import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Alert,
  Snackbar,
  Tabs,
  Tab,
  IconButton,
  Tooltip,
  CircularProgress,
  Stack,
  Divider
} from '@mui/material';
import { format } from 'date-fns';
import VisibilityIcon from '@mui/icons-material/Visibility';
import ReplyIcon from '@mui/icons-material/Reply';
import CloseIcon from '@mui/icons-material/Close';
import DeleteIcon from '@mui/icons-material/Delete';
import PageTitle from '../components/common/PageTitle';
import { getTickets, respondToTicket, closeTicket, deleteTicket } from '../services/api';

const TicketManagement = () => {
  const [tickets, setTickets] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedTab, setSelectedTab] = useState(0);
  const [selectedTicket, setSelectedTicket] = useState(null);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [responseText, setResponseText] = useState('');
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'success' });

  const tabLabels = ['All Tickets', 'Open', 'Answered', 'Closed'];
  const statusFilters = ['', 'open', 'answered', 'closed'];

  useEffect(() => {
    fetchTickets();
  }, [selectedTab]);

  const fetchTickets = async () => {
    try {
      setLoading(true);
      const statusFilter = statusFilters[selectedTab];
      const response = await getTickets(statusFilter);
      setTickets(response.data.tickets || []);
    } catch (error) {
      console.error('Failed to fetch tickets:', error);
      showSnackbar('Failed to fetch tickets', 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleTabChange = (event, newValue) => {
    setSelectedTab(newValue);
  };

  const handleViewTicket = (ticket) => {
    setSelectedTicket(ticket);
    setResponseText(ticket.admin_response || '');
    setDialogOpen(true);
  };

  const handleRespondToTicket = async () => {
    if (!responseText.trim()) {
      showSnackbar('Please enter a response', 'warning');
      return;
    }

    try {
      await respondToTicket(selectedTicket.id, { admin_response: responseText });
      showSnackbar('Response sent successfully', 'success');
      setDialogOpen(false);
      fetchTickets(); // Refresh the ticket list
    } catch (error) {
      console.error('Failed to respond to ticket:', error);
      showSnackbar('Failed to send response', 'error');
    }
  };

  const handleCloseTicket = async (ticketId) => {
    try {
      await closeTicket(ticketId);
      showSnackbar('Ticket closed successfully', 'success');
      fetchTickets(); // Refresh the ticket list
    } catch (error) {
      console.error('Failed to close ticket:', error);
      showSnackbar('Failed to close ticket', 'error');
    }
  };

  const handleDeleteTicket = async (ticketId) => {
    if (window.confirm('Are you sure you want to delete this ticket?')) {
      try {
        await deleteTicket(ticketId);
        showSnackbar('Ticket deleted successfully', 'success');
        fetchTickets(); // Refresh the ticket list
      } catch (error) {
        console.error('Failed to delete ticket:', error);
        showSnackbar('Failed to delete ticket', 'error');
      }
    }
  };

  const showSnackbar = (message, severity) => {
    setSnackbar({ open: true, message, severity });
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'open': return 'error';
      case 'answered': return 'warning';
      case 'closed': return 'success';
      default: return 'default';
    }
  };

  const getStatusCount = (status) => {
    return tickets.filter(ticket => ticket.status === status).length;
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box>
      <PageTitle title="Ticket Management" />
      
      {/* Stats Cards */}
      <Stack direction="row" spacing={2} sx={{ mb: 3 }}>
        <Paper sx={{ p: 2, flex: 1, textAlign: 'center' }}>
          <Typography variant="h4" color="error.main">{getStatusCount('open')}</Typography>
          <Typography variant="body2" color="text.secondary">Open Tickets</Typography>
        </Paper>
        <Paper sx={{ p: 2, flex: 1, textAlign: 'center' }}>
          <Typography variant="h4" color="warning.main">{getStatusCount('answered')}</Typography>
          <Typography variant="body2" color="text.secondary">Answered Tickets</Typography>
        </Paper>
        <Paper sx={{ p: 2, flex: 1, textAlign: 'center' }}>
          <Typography variant="h4" color="success.main">{getStatusCount('closed')}</Typography>
          <Typography variant="body2" color="text.secondary">Closed Tickets</Typography>
        </Paper>
        <Paper sx={{ p: 2, flex: 1, textAlign: 'center' }}>
          <Typography variant="h4">{tickets.length}</Typography>
          <Typography variant="body2" color="text.secondary">Total Tickets</Typography>
        </Paper>
      </Stack>

      <Paper sx={{ width: '100%' }}>
        {/* Tabs for filtering */}
        <Tabs value={selectedTab} onChange={handleTabChange} variant="fullWidth">
          {tabLabels.map((label, index) => (
            <Tab key={index} label={label} />
          ))}
        </Tabs>

        <Divider />

        {/* Ticket Table */}
        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Ticket ID</TableCell>
                <TableCell>Query</TableCell>
                <TableCell>Status</TableCell>
                <TableCell>Created</TableCell>
                <TableCell>Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {tickets.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={5} align="center">
                    <Typography variant="body2" color="text.secondary">
                      No tickets found
                    </Typography>
                  </TableCell>
                </TableRow>
              ) : (
                tickets.map((ticket) => (
                  <TableRow key={ticket.id} hover>
                    <TableCell>
                      <Typography variant="body2" fontWeight="medium">
                        {ticket.ticket_id.slice(0, 8)}...
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Typography 
                        variant="body2" 
                        sx={{ 
                          maxWidth: 300, 
                          overflow: 'hidden', 
                          textOverflow: 'ellipsis', 
                          whiteSpace: 'nowrap' 
                        }}
                      >
                        {ticket.query}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Chip 
                        label={ticket.status.toUpperCase()} 
                        color={getStatusColor(ticket.status)}
                        size="small"
                      />
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2">
                        {format(new Date(ticket.created_at), 'MMM dd, yyyy HH:mm')}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Stack direction="row" spacing={1}>
                        <Tooltip title="View Details">
                          <IconButton 
                            size="small" 
                            onClick={() => handleViewTicket(ticket)}
                          >
                            <VisibilityIcon fontSize="small" />
                          </IconButton>
                        </Tooltip>
                        
                        {ticket.status !== 'closed' && (
                          <Tooltip title="Close Ticket">
                            <IconButton 
                              size="small" 
                              onClick={() => handleCloseTicket(ticket.id)}
                              color="success"
                            >
                              <CloseIcon fontSize="small" />
                            </IconButton>
                          </Tooltip>
                        )}
                        
                        <Tooltip title="Delete Ticket">
                          <IconButton 
                            size="small" 
                            onClick={() => handleDeleteTicket(ticket.id)}
                            color="error"
                          >
                            <DeleteIcon fontSize="small" />
                          </IconButton>
                        </Tooltip>
                      </Stack>
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </TableContainer>
      </Paper>

      {/* Ticket Detail Dialog */}
      <Dialog 
        open={dialogOpen} 
        onClose={() => setDialogOpen(false)}
        maxWidth="md"
        fullWidth
      >
        {selectedTicket && (
          <>
            <DialogTitle>
              <Stack direction="row" justifyContent="space-between" alignItems="center">
                <Typography variant="h6">
                  Ticket Details - {selectedTicket.ticket_id.slice(0, 8)}...
                </Typography>
                <Chip 
                  label={selectedTicket.status.toUpperCase()} 
                  color={getStatusColor(selectedTicket.status)}
                  size="small"
                />
              </Stack>
            </DialogTitle>
            
            <DialogContent dividers>
              <Stack spacing={3}>
                {/* User Query Section */}
                <Box>
                  <Typography variant="subtitle2" gutterBottom color="primary">
                    User Query
                  </Typography>
                  <Paper variant="outlined" sx={{ p: 2, bgcolor: 'grey.50' }}>
                    <Typography variant="body2">
                      {selectedTicket.query}
                    </Typography>
                  </Paper>
                  <Typography variant="caption" color="text.secondary" sx={{ mt: 1, display: 'block' }}>
                    Created: {format(new Date(selectedTicket.created_at), 'MMM dd, yyyy HH:mm')}
                  </Typography>
                </Box>

                {/* Admin Response Section */}
                <Box>
                  <Typography variant="subtitle2" gutterBottom color="primary">
                    Admin Response
                  </Typography>
                  <TextField
                    multiline
                    rows={4}
                    fullWidth
                    variant="outlined"
                    placeholder="Enter your response to the user..."
                    value={responseText}
                    onChange={(e) => setResponseText(e.target.value)}
                    disabled={selectedTicket.status === 'closed'}
                  />
                </Box>

                {selectedTicket.closed_at && (
                  <Alert severity="info" sx={{ mt: 2 }}>
                    This ticket was closed on {format(new Date(selectedTicket.closed_at), 'MMM dd, yyyy HH:mm')}
                  </Alert>
                )}
              </Stack>
            </DialogContent>
            
            <DialogActions sx={{ p: 2 }}>
              <Button onClick={() => setDialogOpen(false)}>
                Cancel
              </Button>
              
              {selectedTicket.status !== 'closed' && (
                <>
                  <Button 
                    onClick={() => handleCloseTicket(selectedTicket.id)}
                    color="success"
                    variant="outlined"
                  >
                    Close Ticket
                  </Button>
                  
                  <Button 
                    onClick={handleRespondToTicket}
                    variant="contained"
                    startIcon={<ReplyIcon />}
                    disabled={!responseText.trim()}
                  >
                    Send Response
                  </Button>
                </>
              )}
            </DialogActions>
          </>
        )}
      </Dialog>

      {/* Snackbar for notifications */}
      <Snackbar
        open={snackbar.open}
        autoHideDuration={6000}
        onClose={() => setSnackbar({ ...snackbar, open: false })}
      >
        <Alert 
          onClose={() => setSnackbar({ ...snackbar, open: false })} 
          severity={snackbar.severity}
        >
          {snackbar.message}
        </Alert>
      </Snackbar>
    </Box>
  );
};

export default TicketManagement;