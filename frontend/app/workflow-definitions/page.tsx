'use client';

import React from 'react';
import {
  Box,
  Button,
  Container,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Typography,
  Fab,
  IconButton,
  Tooltip,
  Chip,
} from '@mui/material';
import AddIcon from '@mui/icons-material/Add';
import EditIcon from '@mui/icons-material/Edit';
import DeleteIcon from '@mui/icons-material/Delete';
import VisibilityIcon from '@mui/icons-material/Visibility';
import PlayArrowIcon from '@mui/icons-material/PlayArrow';
import { useRouter } from 'next/navigation';
import Navigation from '../components/Navigation';
import AsyncBoundary from '../components/AsyncBoundary';
import { useWorkflowDefinitions, useDeleteWorkflowDefinition } from '../hooks/useWorkflow';
import { formatDistanceToNow } from 'date-fns';
import { useState } from 'react';
import { 
  Dialog, 
  DialogActions, 
  DialogContent, 
  DialogContentText, 
  DialogTitle,
  Snackbar,
  Alert
} from '@mui/material';

export default function WorkflowDefinitionsPage() {
  const router = useRouter();
  const { data: definitions, isLoading, isError, error, refetch } = useWorkflowDefinitions();
  const deleteWorkflowDefinition = useDeleteWorkflowDefinition();
  
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [definitionToDelete, setDefinitionToDelete] = useState<string | null>(null);
  const [snackbar, setSnackbar] = useState<{ open: boolean; message: string; severity: 'success' | 'error' }>({
    open: false,
    message: '',
    severity: 'success',
  });

  const handleCreateNew = () => {
    router.push('/workflow-definitions/new');
  };

  const handleEdit = (id: string) => {
    router.push(`/workflow-definitions/${id}/edit`);
  };

  const handleView = (id: string) => {
    router.push(`/workflow-definitions/${id}`);
  };

  const handleStartWorkflow = (id: string) => {
    router.push(`/workflow-instances/new?definitionId=${id}`);
  };

  const handleDeleteClick = (id: string) => {
    setDefinitionToDelete(id);
    setDeleteDialogOpen(true);
  };

  const handleDeleteConfirm = async () => {
    if (definitionToDelete) {
      try {
        await deleteWorkflowDefinition.mutateAsync(definitionToDelete);
        setSnackbar({
          open: true,
          message: 'Workflow definition deleted successfully',
          severity: 'success',
        });
        refetch();
      } catch (err) {
        setSnackbar({
          open: true,
          message: 'Failed to delete workflow definition',
          severity: 'error',
        });
      }
    }
    setDeleteDialogOpen(false);
    setDefinitionToDelete(null);
  };

  const handleDeleteCancel = () => {
    setDeleteDialogOpen(false);
    setDefinitionToDelete(null);
  };

  const handleSnackbarClose = () => {
    setSnackbar({ ...snackbar, open: false });
  };

  return (
    <main>
      <Navigation />
      <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={4}>
          <Typography variant="h4" component="h1" gutterBottom>
            Workflow Definitions
          </Typography>
          <Button
            variant="contained"
            color="primary"
            startIcon={<AddIcon />}
            onClick={handleCreateNew}
          >
            Create New Definition
          </Button>
        </Box>

        <AsyncBoundary isLoading={isLoading} isError={isError} error={error as Error}>
          {definitions && definitions.length > 0 ? (
            <TableContainer component={Paper}>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Name</TableCell>
                    <TableCell>Version</TableCell>
                    <TableCell>States</TableCell>
                    <TableCell>Transitions</TableCell>
                    <TableCell>Last Updated</TableCell>
                    <TableCell align="right">Actions</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {definitions.map((definition) => (
                    <TableRow key={definition.id}>
                      <TableCell>{definition.name}</TableCell>
                      <TableCell>{definition.version}</TableCell>
                      <TableCell>{definition.states.length}</TableCell>
                      <TableCell>{definition.transitions.length}</TableCell>
                      <TableCell>
                        {formatDistanceToNow(new Date(definition.updated_at), { addSuffix: true })}
                      </TableCell>
                      <TableCell align="right">
                        <Tooltip title="View">
                          <IconButton onClick={() => handleView(definition.id)}>
                            <VisibilityIcon />
                          </IconButton>
                        </Tooltip>
                        <Tooltip title="Edit">
                          <IconButton onClick={() => handleEdit(definition.id)}>
                            <EditIcon />
                          </IconButton>
                        </Tooltip>
                        <Tooltip title="Start Workflow">
                          <IconButton onClick={() => handleStartWorkflow(definition.id)} color="primary">
                            <PlayArrowIcon />
                          </IconButton>
                        </Tooltip>
                        <Tooltip title="Delete">
                          <IconButton onClick={() => handleDeleteClick(definition.id)} color="error">
                            <DeleteIcon />
                          </IconButton>
                        </Tooltip>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          ) : (
            <Paper sx={{ p: 4, textAlign: 'center' }}>
              <Typography variant="h6" gutterBottom>
                No workflow definitions found
              </Typography>
              <Typography variant="body1" color="textSecondary" paragraph>
                Create your first workflow definition to get started
              </Typography>
              <Button
                variant="contained"
                color="primary"
                startIcon={<AddIcon />}
                onClick={handleCreateNew}
              >
                Create New Definition
              </Button>
            </Paper>
          )}
        </AsyncBoundary>

        <Fab
          color="primary"
          aria-label="add"
          sx={{ position: 'fixed', bottom: 16, right: 16 }}
          onClick={handleCreateNew}
        >
          <AddIcon />
        </Fab>

        {/* Delete Confirmation Dialog */}
        <Dialog
          open={deleteDialogOpen}
          onClose={handleDeleteCancel}
        >
          <DialogTitle>Delete Workflow Definition</DialogTitle>
          <DialogContent>
            <DialogContentText>
              Are you sure you want to delete this workflow definition? This action cannot be undone.
            </DialogContentText>
          </DialogContent>
          <DialogActions>
            <Button onClick={handleDeleteCancel}>Cancel</Button>
            <Button onClick={handleDeleteConfirm} color="error" autoFocus>
              Delete
            </Button>
          </DialogActions>
        </Dialog>

        {/* Snackbar for notifications */}
        <Snackbar
          open={snackbar.open}
          autoHideDuration={6000}
          onClose={handleSnackbarClose}
          anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
        >
          <Alert onClose={handleSnackbarClose} severity={snackbar.severity}>
            {snackbar.message}
          </Alert>
        </Snackbar>
      </Container>
    </main>
  );
}
