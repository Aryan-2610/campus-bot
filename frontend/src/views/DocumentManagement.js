import React, { useState, useEffect, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import {
  Box,
  Paper,
  Typography,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  LinearProgress,
  IconButton,
  Alert,
} from '@mui/material';
import { getDocuments, uploadDocument, deleteDocument } from '../services/api';
import { format } from 'date-fns';
import { formatBytes } from '../utils/helpers';
import ArticleIcon from '@mui/icons-material/Article';
import DeleteIcon from '@mui/icons-material/Delete';
import UploadFileIcon from '@mui/icons-material/UploadFile';
import PageTitle from '../components/common/PageTitle';
import ConfirmationDialog from '../components/common/ConfirmationDialog';

/**
 * A view for uploading, viewing, and deleting documents for the RAG model.
 */
const DocumentManagement = () => {
  const [documents, setDocuments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [uploadError, setUploadError] = useState(null);
  
  const [dialogOpen, setDialogOpen] = useState(false);
  const [docToDelete, setDocToDelete] = useState(null);

  const fetchDocuments = useCallback(async () => {
    try {
      setLoading(true);
      const response = await getDocuments();
      setDocuments(response.data);
      setError(null);
    } catch (err) {
      console.error("Failed to fetch documents:", err);
      setError("Could not load documents. Please try again later.");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchDocuments();
  }, [fetchDocuments]);

  const onDrop = useCallback(async (acceptedFiles) => {
    const file = acceptedFiles[0];
    if (!file) return;
    
    setUploadProgress(0);
    setUploadError(null);

    try {
      await uploadDocument(file, (progressEvent) => {
        const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total);
        setUploadProgress(percentCompleted);
      });
      fetchDocuments();
    } catch (err) {
      console.error("Upload failed:", err);
      setUploadError(`Failed to upload ${file.name}. Please try again.`);
    } finally {
      setTimeout(() => setUploadProgress(0), 1500);
    }
  }, [fetchDocuments]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'text/plain': ['.txt'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
      'application/msword': ['.doc'],
    },
    multiple: false,
  });

  const handleDeleteClick = (filename) => {
    setDocToDelete(filename);
    setDialogOpen(true);
  };

  const handleConfirmDelete = async () => {
    if (!docToDelete) return;
    try {
      await deleteDocument(docToDelete);
      fetchDocuments();
    } catch (err) {
      console.error("Delete failed:", err);
      setError("Failed to delete the document.");
    } finally {
      setDialogOpen(false);
      setDocToDelete(null);
    }
  };

  return (
    <Box>
      <PageTitle
        title="Document Management"
        subtitle="Upload and manage the knowledge base for your chatbot"
      />
      <Paper
        {...getRootProps()}
        sx={{
          p: 4,
          mt: 3,
          mb: 2,
          border: '2px dashed',
          borderColor: isDragActive ? 'primary.main' : 'divider',
          textAlign: 'center',
          cursor: 'pointer',
          backgroundColor: isDragActive ? 'action.hover' : 'background.paper',
        }}
      >
        <input {...getInputProps()} />
        <UploadFileIcon sx={{ fontSize: 48, color: 'text.secondary', mb: 1 }} />
        <Typography>
          {isDragActive
            ? "Drop the file here ..."
            : "Drag 'n' drop a PDF, DOCX, or TXT file here, or click to select"}
        </Typography>
      </Paper>

      {uploadProgress > 0 && <LinearProgress variant="determinate" value={uploadProgress} sx={{ mb: 2 }} />}
      {uploadError && <Alert severity="error" sx={{ mb: 2 }}>{uploadError}</Alert>}
      
      <Paper>
        {loading ? (
          <Box sx={{ p: 3, textAlign: 'center' }}><Typography>Loading documents...</Typography></Box>
        ) : error ? (
          <Alert severity="error" sx={{ m: 2 }}>{error}</Alert>
        ) : (
          <List>
            {documents.map((doc) => (
              <ListItem
                key={doc.filename}
                divider
                secondaryAction={
                  <IconButton edge="end" aria-label="delete" onClick={() => handleDeleteClick(doc.filename)}>
                    <DeleteIcon />
                  </IconButton>
                }
              >
                <ListItemIcon><ArticleIcon /></ListItemIcon>
                <ListItemText
                  primary={doc.filename}
                  secondary={`Size: ${formatBytes(doc.size)} - Last Modified: ${format(new Date(doc.modified * 1000), 'Pp')}`}
                />
              </ListItem>
            ))}
            {documents.length === 0 && (
                <Typography sx={{ p: 3, textAlign: 'center', color: 'text.secondary' }}>
                    No documents found. Upload one to get started.
                </Typography>
            )}
          </List>
        )}
      </Paper>

      <ConfirmationDialog
        open={dialogOpen}
        onClose={() => setDialogOpen(false)}
        onConfirm={handleConfirmDelete}
        title="Delete Document?"
        message={`Are you sure you want to permanently delete "${docToDelete}"? This action cannot be undone.`}
      />
    </Box>
  );
};

export default DocumentManagement;

