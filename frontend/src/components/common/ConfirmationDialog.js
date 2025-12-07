import React from 'react';
import {
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogContentText,
  DialogTitle,
} from '@mui/material';

/**
 * A reusable confirmation dialog component.
 * @param {object} props - The component props.
 * @param {boolean} props.open - If true, the dialog is open.
 * @param {function} props.onClose - Function to call when the dialog is closed (e.g., clicking cancel or outside).
 * @param {function} props.onConfirm - Function to call when the confirm button is clicked.
 * @param {string} props.title - The title of the dialog window.
 * @param {string} props.message - The main text/message within the dialog.
 */
const ConfirmationDialog = ({ open, onClose, onConfirm, title, message }) => {
  return (
    <Dialog
      open={open}
      onClose={onClose}
      aria-labelledby="confirmation-dialog-title"
      aria-describedby="confirmation-dialog-description"
    >
      <DialogTitle id="confirmation-dialog-title">{title}</DialogTitle>
      <DialogContent>
        <DialogContentText id="confirmation-dialog-description">
          {message}
        </DialogContentText>
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose} color="primary">
          Cancel
        </Button>
        <Button onClick={onConfirm} color="secondary" variant="contained" autoFocus>
          Confirm
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default ConfirmationDialog;

