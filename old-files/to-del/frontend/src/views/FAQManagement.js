import React, { useState, useEffect, useMemo, useCallback } from 'react';
import {
  Box,
  Paper,
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TextField,
  Typography,
  CircularProgress,
  IconButton,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  Toolbar,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Grid,
} from '@mui/material';
import AddIcon from '@mui/icons-material/Add';
import EditIcon from '@mui/icons-material/Edit';
import DeleteIcon from '@mui/icons-material/Delete';
import PageTitle from '../components/common/PageTitle';
import ConfirmationDialog from '../components/common/ConfirmationDialog';
import { getFaqs, createFaq, updateFaq, deleteFaq } from '../services/api';
import { truncateText } from '../utils/helpers';

const emptyFaq = { question: '', answer: '', category: 'General', language: 'en' };

/**
 * A view for CRUD operations on FAQs.
 */
const FAQManagement = () => {
  const [faqs, setFaqs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  const [filters, setFilters] = useState({ searchTerm: '', category: 'All', language: 'All' });
  
  const [dialogOpen, setDialogOpen] = useState(false);
  const [isEditing, setIsEditing] = useState(false);
  const [currentFaq, setCurrentFaq] = useState(emptyFaq);

  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [faqToDelete, setFaqToDelete] = useState(null);

  const fetchFaqs = useCallback(async () => {
    try {
      setLoading(true);
      const response = await getFaqs();
      setFaqs(response.data);
      setError(null);
    } catch (err) {
      console.error("Failed to fetch FAQs:", err);
      setError("Could not load FAQs. Please try again.");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchFaqs();
  }, [fetchFaqs]);

  const handleFilterChange = (event) => {
    const { name, value } = event.target;
    setFilters(prev => ({ ...prev, [name]: value }));
  };

  const filteredFaqs = useMemo(() => {
    return faqs.filter(faq => {
      const searchTermMatch = faq.question.toLowerCase().includes(filters.searchTerm.toLowerCase()) ||
                              faq.answer.toLowerCase().includes(filters.searchTerm.toLowerCase());
      const categoryMatch = filters.category === 'All' || faq.category === filters.category;
      const languageMatch = filters.language === 'All' || faq.language === filters.language;
      return searchTermMatch && categoryMatch && languageMatch;
    });
  }, [faqs, filters]);
  
  const categories = useMemo(() => ['All', ...new Set(faqs.map(f => f.category))], [faqs]);
  const languages = useMemo(() => ['All', ...new Set(faqs.map(f => f.language))], [faqs]);

  // --- Dialog and CRUD Handlers ---

  const handleAddNew = () => {
    setIsEditing(false);
    setCurrentFaq(emptyFaq);
    setDialogOpen(true);
  };

  const handleEdit = (faq) => {
    setIsEditing(true);
    setCurrentFaq(faq);
    setDialogOpen(true);
  };

  const handleDialogClose = () => {
    setDialogOpen(false);
  };

  const handleSave = async () => {
    try {
      if (isEditing) {
        await updateFaq(currentFaq.id, currentFaq);
      } else {
        await createFaq(currentFaq);
      }
      fetchFaqs(); // Refresh data
      handleDialogClose();
    } catch (err) {
      console.error("Failed to save FAQ:", err);
      // You might want to show an error toast here
    }
  };

  const handleDelete = (faq) => {
    setFaqToDelete(faq);
    setDeleteDialogOpen(true);
  };

  const handleConfirmDelete = async () => {
    if (!faqToDelete) return;
    try {
      await deleteFaq(faqToDelete.id);
      fetchFaqs(); // Refresh data
    } catch (err) {
      console.error("Failed to delete FAQ:", err);
    } finally {
      setDeleteDialogOpen(false);
      setFaqToDelete(null);
    }
  };


  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '80vh' }}>
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box>
      <PageTitle title="FAQ Management" subtitle="Create, edit, and manage frequently asked questions" />
      
      <Paper sx={{ mt: 3 }}>
        <Toolbar sx={{ p: 2, display: 'flex', justifyContent: 'space-between' }}>
          <Box sx={{ display: 'flex', gap: 2 }}>
            <TextField
              name="searchTerm"
              variant="outlined"
              size="small"
              placeholder="Search questions..."
              value={filters.searchTerm}
              onChange={handleFilterChange}
              sx={{ width: '300px' }}
            />
            {/* Add Category and Language filters */}
          </Box>
          <Button variant="contained" startIcon={<AddIcon />} onClick={handleAddNew}>
            Add New FAQ
          </Button>
        </Toolbar>
        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Question</TableCell>
                <TableCell>Category</TableCell>
                <TableCell>Language</TableCell>
                <TableCell align="right">Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {filteredFaqs.map((faq) => (
                <TableRow key={faq.id} hover>
                  <TableCell>{truncateText(faq.question, 60)}</TableCell>
                  <TableCell>{faq.category}</TableCell>
                  <TableCell>{faq.language.toUpperCase()}</TableCell>
                  <TableCell align="right">
                    <IconButton size="small" onClick={() => handleEdit(faq)}><EditIcon /></IconButton>
                    <IconButton size="small" onClick={() => handleDelete(faq)}><DeleteIcon /></IconButton>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      </Paper>

      {/* Add/Edit Dialog */}
      <Dialog open={dialogOpen} onClose={handleDialogClose} fullWidth maxWidth="md">
        <DialogTitle>{isEditing ? 'Edit FAQ' : 'Add New FAQ'}</DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12}>
              <TextField
                label="Question"
                fullWidth
                value={currentFaq.question}
                onChange={(e) => setCurrentFaq({...currentFaq, question: e.target.value})}
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                label="Answer"
                fullWidth
                multiline
                rows={4}
                value={currentFaq.answer}
                onChange={(e) => setCurrentFaq({...currentFaq, answer: e.target.value})}
              />
            </Grid>
            <Grid item xs={6}>
               <TextField
                label="Category"
                fullWidth
                value={currentFaq.category}
                onChange={(e) => setCurrentFaq({...currentFaq, category: e.target.value})}
              />
            </Grid>
            <Grid item xs={6}>
              <TextField
                label="Language"
                fullWidth
                value={currentFaq.language}
                onChange={(e) => setCurrentFaq({...currentFaq, language: e.target.value})}
                helperText="Use 2-letter code (e.g., en, es, fr)"
              />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleDialogClose}>Cancel</Button>
          <Button onClick={handleSave} variant="contained">Save</Button>
        </DialogActions>
      </Dialog>
      
      {/* Delete Confirmation */}
      <ConfirmationDialog
        open={deleteDialogOpen}
        onClose={() => setDeleteDialogOpen(false)}
        onConfirm={handleConfirmDelete}
        title="Delete FAQ?"
        message={`Are you sure you want to delete the question: "${faqToDelete?.question}"?`}
      />
    </Box>
  );
};

export default FAQManagement;

