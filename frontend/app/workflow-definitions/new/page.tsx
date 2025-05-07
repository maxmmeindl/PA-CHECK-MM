'use client';

import React from 'react';
import { Box, Container, Paper, Typography } from '@mui/material';
import { useRouter } from 'next/navigation';
import Navigation from '../../components/Navigation';
import WorkflowDefinitionForm, { WorkflowDefinitionFormData } from '../components/WorkflowDefinitionForm';
import { useCreateWorkflowDefinition } from '../../hooks/useWorkflow';
import { Snackbar, Alert } from '@mui/material';

export default function NewWorkflowDefinitionPage() {
  const router = useRouter();
  const createWorkflowDefinition = useCreateWorkflowDefinition();
  const [snackbar, setSnackbar] = React.useState({
    open: false,
    message: '',
    severity: 'success' as 'success' | 'error',
  });

  const handleSubmit = async (data: WorkflowDefinitionFormData) => {
    try {
      // Map state indices to IDs for new transitions
      const stateIdMap = new Map<string, number>();
      data.states.forEach((_, index) => {
        stateIdMap.set(index.toString(), index);
      });

      // Update transition state references
      const updatedTransitions = data.transitions.map(transition => ({
        ...transition,
        from_state_id: stateIdMap.get(transition.from_state_id)?.toString() || transition.from_state_id,
        to_state_id: stateIdMap.get(transition.to_state_id)?.toString() || transition.to_state_id,
      }));

      await createWorkflowDefinition.mutateAsync({
        ...data,
        transitions: updatedTransitions,
      });

      setSnackbar({
        open: true,
        message: 'Workflow definition created successfully',
        severity: 'success',
      });

      // Navigate back to the list after successful creation
      setTimeout(() => {
        router.push('/workflow-definitions');
      }, 1500);
    } catch (error) {
      console.error('Error creating workflow definition:', error);
      setSnackbar({
        open: true,
        message: 'Failed to create workflow definition',
        severity: 'error',
      });
    }
  };

  const handleSnackbarClose = () => {
    setSnackbar({ ...snackbar, open: false });
  };

  return (
    <main>
      <Navigation />
      <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
        <Paper sx={{ p: 3, mb: 4 }}>
          <Typography variant="h4" component="h1" gutterBottom>
            Create New Workflow Definition
          </Typography>
          <Typography variant="body1" color="textSecondary" paragraph>
            Define the states and transitions for your new workflow.
          </Typography>
        </Paper>

        <WorkflowDefinitionForm
          onSubmit={handleSubmit}
          isSubmitting={createWorkflowDefinition.isPending}
        />

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
