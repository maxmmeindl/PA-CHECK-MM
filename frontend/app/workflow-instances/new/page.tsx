'use client';

import React, { useState, useEffect } from 'react';
import {
  Box,
  Button,
  Container,
  FormControl,
  FormHelperText,
  InputLabel,
  MenuItem,
  Paper,
  Select,
  TextField,
  Typography,
  Snackbar,
  Alert,
} from '@mui/material';
import { useRouter, useSearchParams } from 'next/navigation';
import Navigation from '../../components/Navigation';
import AsyncBoundary from '../../components/AsyncBoundary';
import { useWorkflowDefinitions, useCreateWorkflowInstance } from '../../hooks/useWorkflow';
import ArrowBackIcon from '@mui/icons-material/ArrowBack';
import { useForm, Controller } from 'react-hook-form';
import { yupResolver } from '@hookform/resolvers/yup';
import * as yup from 'yup';

// Form validation schema
const schema = yup.object({
  workflow_definition_id: yup.string().required('Workflow definition is required'),
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

type FormData = {
  workflow_definition_id: string;
  data: string;
};

export default function NewWorkflowInstancePage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const definitionId = searchParams.get('definitionId');
  const { data: definitions, isLoading, isError, error } = useWorkflowDefinitions();
  const createWorkflowInstance = useCreateWorkflowInstance();
  const [snackbar, setSnackbar] = useState({
    open: false,
    message: '',
    severity: 'success' as 'success' | 'error',
  });

  const {
    control,
    handleSubmit,
    setValue,
    formState: { errors },
  } = useForm<FormData>({
    resolver: yupResolver(schema),
    defaultValues: {
      workflow_definition_id: definitionId || '',
      data: '{\n  \n}',
    },
  });

  // Set definition ID from URL parameter if available
  useEffect(() => {
    if (definitionId) {
      setValue('workflow_definition_id', definitionId);
    }
  }, [definitionId, setValue]);

  const handleFormSubmit = async (data: FormData) => {
    try {
      const parsedData = data.data ? JSON.parse(data.data) : {};
      
      await createWorkflowInstance.mutateAsync({
        workflow_definition_id: data.workflow_definition_id,
        data: parsedData,
      });

      setSnackbar({
        open: true,
        message: 'Workflow instance created successfully',
        severity: 'success',
      });

      // Navigate to the instances list after successful creation
      setTimeout(() => {
        router.push('/workflow-instances');
      }, 1500);
    } catch (error) {
      console.error('Error creating workflow instance:', error);
      setSnackbar({
        open: true,
        message: 'Failed to create workflow instance',
        severity: 'error',
      });
    }
  };

  const handleBack = () => {
    router.push('/workflow-instances');
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
            Start New Workflow
          </Typography>
        </Box>

        <AsyncBoundary isLoading={isLoading} isError={isError} error={error as Error}>
          {definitions && (
            <Paper sx={{ p: 3 }}>
              <form onSubmit={handleSubmit(handleFormSubmit)}>
                <Box sx={{ mb: 3 }}>
                  <Controller
                    name="workflow_definition_id"
                    control={control}
                    render={({ field }) => (
                      <FormControl fullWidth error={!!errors.workflow_definition_id}>
                        <InputLabel id="workflow-definition-label">Workflow Definition</InputLabel>
                        <Select
                          {...field}
                          labelId="workflow-definition-label"
                          label="Workflow Definition"
                        >
                          {definitions.map((definition) => (
                            <MenuItem key={definition.id} value={definition.id}>
                              {definition.name} (v{definition.version})
                            </MenuItem>
                          ))}
                        </Select>
                        {errors.workflow_definition_id && (
                          <FormHelperText>{errors.workflow_definition_id.message}</FormHelperText>
                        )}
                      </FormControl>
                    )}
                  />
                </Box>

                <Box sx={{ mb: 3 }}>
                  <Typography variant="subtitle1" gutterBottom>
                    Initial Data (JSON)
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

                <Box sx={{ display: 'flex', justifyContent: 'flex-end', mt: 3 }}>
                  <Button
                    type="submit"
                    variant="contained"
                    color="primary"
                    size="large"
                    disabled={createWorkflowInstance.isPending}
                  >
                    {createWorkflowInstance.isPending ? 'Starting...' : 'Start Workflow'}
                  </Button>
                </Box>
              </form>
            </Paper>
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
