import React, { useEffect, useState, useMemo } from 'react';
import {
  Box,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Typography,
  CircularProgress,
  IconButton,
  Collapse,
  Alert,
  Stack,
  Divider,
} from '@mui/material';
import { format } from 'date-fns';
import { getConversations } from '../services/api';
import PageTitle from '../components/common/PageTitle';
import KeyboardArrowDownIcon from '@mui/icons-material/KeyboardArrowDown';
import KeyboardArrowUpIcon from '@mui/icons-material/KeyboardArrowUp';

/**
 * A component that displays a single user query and bot response pair
 * in a clean, professional log format.
 */
const LogEntry = ({ message }) => (
  <Paper variant="outlined" sx={{ p: 2 }}>
    {/* User Query Section */}
    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
      <Typography variant="body1" sx={{ fontWeight: 600, color: 'text.primary' }}>
        User Query
      </Typography>
      {/* --- TIMESTAMP FIX --- */}
      {/* The new Date() constructor automatically converts the UTC string from the server to the browser's local timezone. */}
      {/* 'Pp' format displays the full date and time (e.g., 09/07/2025, 2:11 PM) */}
      <Typography variant="caption" sx={{ color: 'text.secondary' }}>
        {format(new Date(message.timestamp), 'Pp')}
      </Typography>
      {/* ------------------- */}
    </Box>
    <Typography variant="body2" sx={{ mb: 2, pl: 1, color: 'text.secondary', whiteSpace: 'pre-wrap' }}>
      {message.query}
    </Typography>

    <Divider />

    {/* Bot Response Section */}
    <Box sx={{ mt: 1.5, mb: 1 }}>
      <Typography variant="body1" sx={{ fontWeight: 600, color: 'text.primary' }}>
        Bot Response
      </Typography>
    </Box>
    <Typography variant="body2" sx={{ pl: 1, color: 'text.secondary', whiteSpace: 'pre-wrap' }}>
      {message.response}
    </Typography>
  </Paper>
);

/**
 * A component that displays a single conversation session as an expandable row.
 * The expanded view now shows a series of structured log entries.
 */
const SessionRow = ({ sessionId, messages }) => {
  const [open, setOpen] = useState(false);
  const latestMessageTimestamp = messages[0].timestamp;
  const messageCount = messages.length;

  return (
    <React.Fragment>
      <TableRow sx={{ '& > *': { borderBottom: 'unset' }, cursor: 'pointer' }} onClick={() => setOpen(!open)}>
        <TableCell>
          <IconButton aria-label="expand session" size="small">
            {open ? <KeyboardArrowUpIcon /> : <KeyboardArrowDownIcon />}
          </IconButton>
        </TableCell>
        <TableCell component="th" scope="row">{sessionId}</TableCell>
        <TableCell>{messageCount}</TableCell>
        {/* --- TIMESTAMP FIX for the 'Last Activity' column --- */}
        <TableCell>{format(new Date(latestMessageTimestamp), 'Pp')}</TableCell>
        {/* ---------------------------------------------------- */}
      </TableRow>
      <TableRow>
        <TableCell style={{ paddingBottom: 0, paddingTop: 0 }} colSpan={4}>
          <Collapse in={open} timeout="auto" unmountOnExit>
            <Box sx={{ margin: 1, padding: 2, backgroundColor: 'background.default', borderRadius: 1 }}>
              <Typography variant="h6" gutterBottom component="div">
                Session Transcript
              </Typography>
              <Stack spacing={2} sx={{ mt: 2 }}>
                {/* Display messages in chronological order (oldest first) */}
                {[...messages].reverse().map((message) => (
                  <LogEntry key={message.id} message={message} />
                ))}
              </Stack>
            </Box>
          </Collapse>
        </TableCell>
      </TableRow>
    </React.Fragment>
  );
};

const ConversationLogs = () => {
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const groupedSessions = useMemo(() => {
    if (!logs || logs.length === 0) return {};
    return logs.reduce((acc, log) => {
      const { session_id } = log;
      if (!acc[session_id]) {
        acc[session_id] = [];
      }
      acc[session_id].push(log);
      return acc;
    }, {});
  }, [logs]);

  useEffect(() => {
    const fetchLogs = async () => {
      try {
        setLoading(true);
        setError(null);
        const response = await getConversations();
        setLogs(response.data.conversations || []);
      } catch (err) {
        console.error("Failed to fetch conversation logs:", err);
        setError("Failed to fetch conversation logs.");
      } finally {
        setLoading(false);
      }
    };
    fetchLogs();
  }, []);

  return (
    <Box>
      <PageTitle title="Conversation Logs" subtitle="Review all user sessions" />
      
      {loading && (
        <Box sx={{ display: 'flex', justifyContent: 'center', my: 3 }}>
          <CircularProgress />
        </Box>
      )}

      {error && <Alert severity="error" sx={{ my: 2 }}>{error}</Alert>}

      {!loading && !error && (
        <Paper sx={{ mt: 3 }}>
          <TableContainer>
            <Table aria-label="collapsible conversation sessions table">
              <TableHead>
                <TableRow>
                  <TableCell style={{ width: '5%' }} />
                  <TableCell>Session ID</TableCell>
                  <TableCell>Messages</TableCell>
                  <TableCell>Last Activity</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {Object.entries(groupedSessions).length > 0 ? (
                  Object.entries(groupedSessions).map(([sessionId, messages]) => (
                    <SessionRow key={sessionId} sessionId={sessionId} messages={messages} />
                  ))
                ) : (
                  <TableRow>
                    <TableCell colSpan={4} align="center">
                      <Typography sx={{ p: 4, color: 'text.secondary' }}>
                        No conversation logs found.
                      </Typography>
                    </TableCell>
                  </TableRow>
                )}
              </TableBody>
            </Table>
          </TableContainer>
        </Paper>
      )}
    </Box>
  );
};

export default ConversationLogs;