'use client';

import React, { useState } from 'react';
import {
  Box,
  Button,
  Card,
  CardContent,
  Chip,
  Container,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  Divider,
  FormControl,
  Grid,
  InputLabel,
  MenuItem,
  Paper,
  Select,
  Snackbar,
  Alert,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TextField,
  Typography,
} from '@mui/material';
import { useRouter } from 'next/navigation';
import Navigation from '../../../components/Navigation';
import AsyncBoundary from '../../../components/AsyncBoundary';
import {
  useWorkflowInstance,
  useWorkflowDefinition,
  useWorkflowInstanceHistory,
  useTransitionWorkflowInstance,
} from '../../../hooks/useWorkflow';
import ArrowBackIcon from '@mui/icons-material/ArrowBack';
import { formatDistanceToNow, format } from 'date-fns';
import { useForm, Controller } from 'react-hook-form';
import { yupResolver } from '@hookform/resolvers/yup';
import * as yup from 'yup';

interface WorkflowInstanceDetailPageProps {
  params: {
    id: string;
  };
}

// Form validation schema for transition
const transitionSchema = yup.object({
  transition_id: yup.string().required('Transition is required'),
  data: yup.string().test('is-valid-json', 'Invalid JSON format', function (value) {
    if (!value) return true;
    try {
      JSON.parse(value);
      return true;
    } catch (error) {
      return false;
    }
  }),
});

type TransitionFormData = {
  transition_id: string;
  data: string;
};

export default function WorkflowInstanceDetailPage({ params }: WorkflowInstanceDetailPageProps) {
  const { id } = params;
  const router = useRouter();
  const { data: instance, isLoading: instanceLoading, isError: instanceError, error: instanceErrorData } = useWorkflowInstance(id);
  const { data: history, isLoading: historyLoading, isError: historyError, error: historyErrorData } = useWorkflowInstanceHistory(id);
  
  const [transitionDialogOpen, setTransitionDialogOpen] = useState(false);
  const [snackbar, setSnackbar] = useState({
    open: false,
    message: '',
    severity: 'success' as 'success' | 'error',
  });

  // Get the workflow definition if we have an instance
  const { data: definition, isLoading: definitionLoading } = useWorkflowDefinition(
    instance?.workflow_definition_id || '',
    { enabled: !!instance?.workflow_definition_id }
  );

  const transitionWorkflowInstance = useTransitionWorkflowInstance(id);

  const {
    control,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<TransitionFormData>({
    resolver: yupResolver(transitionSchema),
    defaultValues: {
      transition_id: '',
      data: '{\n  \n}',
    },
  });

  const handleBack = () => {
    router.push('/workflow-instances');
  };

  const handleTransitionClick = () => {
    setTransitionDialogOpen(true);
  };

  const handleTransitionDialogClose = () => {
    setTransitionDialogOpen(false);
    reset();
  };

  const handleTransitionSubmit = async (data: TransitionFormData) => {
    try {
      const parsedData = data.data ? JSON.parse(data.data) : {};
      
      await transitionWorkflowInstance.mutateAsync({
        transition_id: data.transition_id,
        data: parsedData,
      });

      setSnackbar({
        open: true,
        message: 'Workflow transitioned successfully',
        severity: 'success',
      });

      setTransitionDialogOpen(false);
    } catch (error) {
      console.error('Error transitioning workflow:', error);
      setSnackbar({
        open: true,
        message: 'Failed to transition workflow',
        severity: 'error',
      });
    }
  };

  const handleSnackbarClose = () => {
    setSnackbar({ ...snackbar, open: false });
  };

  // Helper function to get state name by ID
  const getStateName = (stateId: string) => {
    const state = definition?.states.find((s) => s.id === stateId);
    return state?.name || 'Unknown State';
  };

  // Helper function to get transition name by ID
  const getTransitionName = (transitionId: string) => {
    const transition = definition?.transitions.find((t) => t.id === transitionId);
    return transition?.name || 'System Transition';
  };

  // Get available transitions from current state
  const getAvailableTransitions = () => {
    if (!definition || !instance) return [];
    
    return definition.transitions.filter(
      (transition) => transition.from_state_id === instance.current_state_id
    );
  };

  // Determine if the instance can be transitioned
  const canTransition = () => {
    if (!instance || instance.status !== 'active') return false;
    return getAvailableTransitions().length > 0;
  };

  // Format JSON data for display
  const formatJsonData = (data: Record<string, any>) => {
    return JSON.stringify(data, null, 2);
  };

  const isLoading = instanceLoading || historyLoading || definitionLoading;
  const isError = instanceError || historyError;
  const error = instanceErrorData || historyErrorData;

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
            Back to List
          </Button>
          <Typography variant="h4" component="h1">
            Workflow Instance Details
          </Typography>
        </Box>

        <AsyncBoundary isLoading={isLoading} isError={isError} error={error as Error}>
          {instance && definition && (
            <>
              <Paper sx={{ p: 3, mb: 4 }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                  <Box>
                    <Typography variant="h5" gutterBottom>
                      {definition.name} (v{definition.version})
                    </Typography>
                    <Typography variant="body1" color="textSecondary" paragraph>
                      Instance ID: {instance.id}
                    </Typography>
                    <Box sx={{ display: 'flex', gap: 1, mb: 2 }}>
                      <Chip
                        label={`Status: ${instance.status}`}
                        color={
                          instance.status === 'active'
                            ? 'primary'
                            : instance.status === 'completed'
                            ? 'success'
                            : 'error'
                        }
                      />
                      <Chip
                        label={`Current State: ${getStateName(instance.current_state_id)}`}
                        color="secondary"
                        variant="outlined"
                      />
                    </Box>
                    <Typography variant="body2" color="textSecondary">
                      Created: {formatDistanceToNow(new Date(instance.created_at), { addSuffix: true })}
                    </Typography>
                    <Typography variant="body2" color="textSecondary">
                      Last updated: {formatDistanceToNow(new Date(instance.updated_at), { addSuffix: true })}
                    </Typography>
                  </Box>
                  <Box>
                    {canTransition() && (
                      <Button
                        variant="contained"
                        color="primary"
                        onClick={handleTransitionClick}
                      >
                        Transition Workflow
                      </Button>
                    )}
                  </Box>
                </Box>
              </Paper>

              <Grid container spacing={4}>
                <Grid item xs={12} md={6}>
                  <Paper sx={{ p: 3, mb: 4 }}>
                    <Typography variant="h6" gutterBottom>
                      Current Data
                    </Typography>
                    <Box
                      component="pre"
                      sx={{
                        p: 2,
                        borderRadius: 1,
                        bgcolor: 'grey.100',
                        overflow: 'auto',
                        maxHeight: '300px',
                        fontFamily: 'monospace',
                      }}
                    >
                      {formatJsonData(instance.data)}
                    </Box>
                  </Paper>
                </Grid>

                <Grid item xs={12} md={6}>
                  <Paper sx={{ p: 3, mb: 4 }}>
                    <Typography variant="h6" gutterBottom>
                      Available Transitions
                    </Typography>
                    {getAvailableTransitions().length > 0 ? (
                      <TableContainer>
                        <Table>
                          <TableHead>
                            <TableRow>
                              <TableCell>Transition</TableCell>
                              <TableCell>To State</TableCell>
                              <TableCell>Description</TableCell>
                            </TableRow>
                          </TableHead>
                          <TableBody>
                            {getAvailableTransitions().map((transition) => {
                              const toState = definition.states.find(
                                (s) => s.id === transition.to_state_id
                              );
                              return (
                                <TableRow key={transition.id}>
                                  <TableCell>{transition.name}</TableCell>
                                  <TableCell>{toState?.name || 'Unknown'}</TableCell>
                                  <TableCell>{transition.description || '-'}</TableCell>
                                </TableRow>
                              );
                            })}
                          </TableBody>
                        </Table>
                      </TableContainer>
                    ) : (
                      <Typography color="textSecondary" align="center" sx={{ py: 2 }}>
                        {instance.status === 'active'
                          ? 'No available transitions from current state'
                          : `Workflow is ${instance.status}`}
                      </Typography>
                    )}
                  </Paper>
                </Grid>
              </Grid>

              <Paper sx={{ p: 3, mb: 4 }}>
                <Typography variant="h6" gutterBottom>
                  Workflow History
                </Typography>
                {history && history.length > 0 ? (
                  <TableContainer>
                    <Table>
                      <TableHead>
                        <TableRow>
                          <TableCell>Timestamp</TableCell>
                          <TableCell>From State</TableCell>
                          <TableCell>To State</TableCell>
                          <TableCell>Transition</TableCell>
                          <TableCell>Data</TableCell>
                        </TableRow>
                      </TableHead>
                      <TableBody>
                        {history.map((entry) => (
                          <TableRow key={entry.id}>
                            <TableCell>
                              {format(new Date(entry.timestamp), 'MMM d, yyyy HH:mm:ss')}
                            </TableCell>
                            <TableCell>
                              {entry.from_state_id
                                ? getStateName(entry.from_state_id)
                                : 'Initial'}
                            </TableCell>
                            <TableCell>{getStateName(entry.to_state_id)}</TableCell>
                            <TableCell>
                              {entry.transition_id
                                ? getTransitionName(entry.transition_id)
                                : 'Initialization'}
                            </TableCell>
                            <TableCell>
                              <Button
                                size="small"
                                onClick={() => {
                                  alert(JSON.stringify(entry.data, null, 2));
                                }}
                              >
                                View Data
                              </Button>
                            </TableCell>
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  </TableContainer>
                ) : (
                  <Typography color="textSecondary" align="center" sx={{ py: 2 }}>
                    No history entries found
                  </Typography>
                )}
              </Paper>

              {/* Transition Dialog */}
              <Dialog
                open={transitionDialogOpen}
                onClose={handleTransitionDialogClose}
                maxWidth="md"
                fullWidth
              >
                <form onSubmit={handleSubmit(handleTransitionSubmit)}>
                  <DialogTitle>Transition Workflow</DialogTitle>
                  <DialogContent>
                    <Box sx={{ mt: 2 }}>
                      <Controller
                        name="transition_id"
                        control={control}
                        render={({ field }) => (
                          <FormControl fullWidth error={!!errors.transition_id} sx={{ mb: 3 }}>
                            <InputLabel id="transition-label">Select Transition</InputLabel>
                            <Select
                              {...field}
                              labelId="transition-label"
                              label="Select Transition"
                            >
                              {getAvailableTransitions().map((transition) => {
                                const toState = definition.states.find(
                                  (s) => s.id === transition.to_state_id
                                );
                                return (
                                  <MenuItem key={transition.id} value={transition.id}>
                                    {transition.name} (to {toState?.name})
                                  </MenuItem>
                                );
                              })}
                            </Select>
                            {errors.transition_id && (
                              <Typography color="error" variant="caption">
                                {errors.transition_id.message}
                              </Typography>
                            )}
                          </FormControl>
                        )}
                      />

                      <Typography variant="subtitle1" gutterBottom>
                        Transition Data (JSON)
                      </Typography>
                      <Controller
                        name="data"
                        control={control}
                        render={({ field }) => (
                          <TextField
                            {...field}
                            multiline
                            rows={10}
                            fullWidth
                            variant="outlined"
                            placeholder="Enter JSON data"
                            error={!!errors.data}
                            helperText={errors.data?.message}
                            sx={{ fontFamily: 'monospace' }}
                          />
                        )}
                      />
                    </Box>
                  </DialogContent>
                  <DialogActions>
                    <Button onClick={handleTransitionDialogClose}>Cancel</Button>
                    <Button
                      type="submit"
                      variant="contained"
                      color="primary"
                      disabled={transitionWorkflowInstance.isPending}
                    >
                      {transitionWorkflowInstance.isPending ? 'Processing...' : 'Execute Transition'}
                    </Button>
                  </DialogActions>
                </form>
              </Dialog>
            </>
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
