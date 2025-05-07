'use client';

import React from 'react';
import { Box, Container, Paper, Typography, Button } from '@mui/material';
import { useRouter } from 'next/navigation';
import Navigation from '../../../components/Navigation';
import WorkflowDefinitionForm, { WorkflowDefinitionFormData } from '../../components/WorkflowDefinitionForm';
import { useWorkflowDefinition, useUpdateWorkflowDefinition } from '../../../hooks/useWorkflow';
import AsyncBoundary from '../../../components/AsyncBoundary';
import ArrowBackIcon from '@mui/icons-material/ArrowBack';
import { Snackbar, Alert } from '@mui/material';

interface EditWorkflowDefinitionPageProps {
  params: {
    id: string;
  };
}

export default function EditWorkflowDefinitionPage({ params }: EditWorkflowDefinitionPageProps) {
  const { id } = params;
  const router = useRouter();
  const { data: definition, isLoading, isError, error } = useWorkflowDefinition(id);
  const updateWorkflowDefinition = useUpdateWorkflowDefinition(id);
  const [snackbar, setSnackbar] = React.useState({
    open: false,
    message: '',
    severity: 'success' as 'success' | 'error',
  });

  const handleSubmit = async (data: WorkflowDefinitionFormData) => {
    try {
      await updateWorkflowDefinition.mutateAsync(data);
      
      setSnackbar({
        open: true,
        message: 'Workflow definition updated successfully',
        severity: 'success',
      });

      // Navigate back to the details page after successful update
      setTimeout(() => {
        router.push(`/workflow-definitions/${id}`);
      }, 1500);
    } catch (error) {
      console.error('Error updating workflow definition:', error);
      setSnackbar({
        open: true,
        message: 'Failed to update workflow definition',
        severity: 'error',
      });
    }
  };

  const handleBack = () => {
    router.push(`/workflow-definitions/${id}`);
  };

  const handleSnackbarClose = () => {
    setSnackbar({ ...snackbar, open: false });
  };

  return (
    <main>
      <Navigation />
      <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
          <Button
            startIcon={<ArrowBackIcon />}
            onClick={handleBack}
            sx={{ mr: 2 }}
          >
            Back
          </Button>
          <Typography variant="h4" component="h1">
            Edit Workflow Definition
          </Typography>
        </Box>

        <AsyncBoundary isLoading={isLoading} isError={isError} error={error as Error}>
          {definition && (
            <WorkflowDefinitionForm
              initialData={definition}
              onSubmit={handleSubmit}
              isSubmitting={updateWorkflowDefinition.isPending}
            />
          )}
        </AsyncBoundary>

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
