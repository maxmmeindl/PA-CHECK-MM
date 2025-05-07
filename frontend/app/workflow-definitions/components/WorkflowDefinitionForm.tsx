'use client';

import React, { useState } from 'react';
import {
  Box,
  Button,
  Card,
  CardContent,
  Chip,
  Divider,
  FormControl,
  FormControlLabel,
  FormHelperText,
  Grid,
  IconButton,
  InputLabel,
  MenuItem,
  Paper,
  Select,
  Switch,
  TextField,
  Typography,
} from '@mui/material';
import AddIcon from '@mui/icons-material/Add';
import DeleteIcon from '@mui/icons-material/Delete';
import { useForm, Controller, useFieldArray } from 'react-hook-form';
import { yupResolver } from '@hookform/resolvers/yup';
import * as yup from 'yup';
import { WorkflowDefinition, WorkflowState, WorkflowTransition } from '../../api/apiService';
import StateDiagram from './StateDiagram';

// Form validation schema
const schema = yup.object({
  name: yup.string().required('Name is required'),
  description: yup.string(),
  version: yup.string().required('Version is required'),
  states: yup.array().of(
    yup.object({
      name: yup.string().required('State name is required'),
      description: yup.string(),
      is_initial: yup.boolean(),
      is_final: yup.boolean(),
    })
  ).min(1, 'At least one state is required'),
  transitions: yup.array().of(
    yup.object({
      name: yup.string().required('Transition name is required'),
      description: yup.string(),
      from_state_id: yup.string().required('From state is required'),
      to_state_id: yup.string().required('To state is required'),
    })
  ),
});

// Form data type
export type WorkflowDefinitionFormData = {
  name: string;
  description: string;
  version: string;
  states: Array<{
    id?: string;
    name: string;
    description: string;
    is_initial: boolean;
    is_final: boolean;
  }>;
  transitions: Array<{
    id?: string;
    name: string;
    description: string;
    from_state_id: string;
    to_state_id: string;
  }>;
};

interface WorkflowDefinitionFormProps {
  initialData?: WorkflowDefinition;
  onSubmit: (data: WorkflowDefinitionFormData) => void;
  isSubmitting: boolean;
}

export default function WorkflowDefinitionForm({
  initialData,
  onSubmit,
  isSubmitting,
}: WorkflowDefinitionFormProps) {
  const [showDiagram, setShowDiagram] = useState(true);

  // Initialize form with default values or existing data
  const defaultValues: WorkflowDefinitionFormData = {
    name: initialData?.name || '',
    description: initialData?.description || '',
    version: initialData?.version || '1.0.0',
    states: initialData?.states || [
      {
        name: 'Initial',
        description: 'Starting state',
        is_initial: true,
        is_final: false,
      },
    ],
    transitions: initialData?.transitions || [],
  };

  const {
    control,
    handleSubmit,
    formState: { errors },
    watch,
    setValue,
  } = useForm<WorkflowDefinitionFormData>({
    resolver: yupResolver(schema),
    defaultValues,
  });

  // Field arrays for states and transitions
  const {
    fields: stateFields,
    append: appendState,
    remove: removeState,
  } = useFieldArray({
    control,
    name: 'states',
  });

  const {
    fields: transitionFields,
    append: appendTransition,
    remove: removeTransition,
  } = useFieldArray({
    control,
    name: 'transitions',
  });

  // Watch states for transition dropdowns
  const states = watch('states');

  // Handle form submission
  const handleFormSubmit = (data: WorkflowDefinitionFormData) => {
    onSubmit(data);
  };

  // Add a new state
  const handleAddState = () => {
    appendState({
      name: `State ${stateFields.length + 1}`,
      description: '',
      is_initial: false,
      is_final: false,
    });
  };

  // Add a new transition
  const handleAddTransition = () => {
    if (states.length < 2) {
      alert('You need at least two states to create a transition');
      return;
    }

    appendTransition({
      name: `Transition ${transitionFields.length + 1}`,
      description: '',
      from_state_id: states[0].id || '0',
      to_state_id: states[1].id || '1',
    });
  };

  // Toggle diagram view
  const toggleDiagram = () => {
    setShowDiagram(!showDiagram);
  };

  return (
    <form onSubmit={handleSubmit(handleFormSubmit)}>
      <Paper sx={{ p: 3, mb: 4 }}>
        <Typography variant="h6" gutterBottom>
          Basic Information
        </Typography>
        <Grid container spacing={3}>
          <Grid item xs={12} md={6}>
            <Controller
              name="name"
              control={control}
              render={({ field }) => (
                <TextField
                  {...field}
                  label="Workflow Name"
                  fullWidth
                  error={!!errors.name}
                  helperText={errors.name?.message}
                />
              )}
            />
          </Grid>
          <Grid item xs={12} md={6}>
            <Controller
              name="version"
              control={control}
              render={({ field }) => (
                <TextField
                  {...field}
                  label="Version"
                  fullWidth
                  error={!!errors.version}
                  helperText={errors.version?.message}
                />
              )}
            />
          </Grid>
          <Grid item xs={12}>
            <Controller
              name="description"
              control={control}
              render={({ field }) => (
                <TextField
                  {...field}
                  label="Description"
                  fullWidth
                  multiline
                  rows={3}
                  error={!!errors.description}
                  helperText={errors.description?.message}
                />
              )}
            />
          </Grid>
        </Grid>
      </Paper>

      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
        <Typography variant="h6">States</Typography>
        <Button
          variant="outlined"
          startIcon={<AddIcon />}
          onClick={handleAddState}
        >
          Add State
        </Button>
      </Box>

      {stateFields.length === 0 ? (
        <Paper sx={{ p: 3, mb: 4, textAlign: 'center' }}>
          <Typography color="textSecondary">No states defined yet</Typography>
          <Button
            variant="outlined"
            startIcon={<AddIcon />}
            onClick={handleAddState}
            sx={{ mt: 2 }}
          >
            Add State
          </Button>
        </Paper>
      ) : (
        <Grid container spacing={3} sx={{ mb: 4 }}>
          {stateFields.map((field, index) => (
            <Grid item xs={12} md={6} key={field.id}>
              <Card variant="outlined">
                <CardContent>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
                    <Typography variant="subtitle1">State {index + 1}</Typography>
                    <IconButton
                      color="error"
                      onClick={() => removeState(index)}
                      size="small"
                    >
                      <DeleteIcon />
                    </IconButton>
                  </Box>
                  <Grid container spacing={2}>
                    <Grid item xs={12}>
                      <Controller
                        name={`states.${index}.name`}
                        control={control}
                        render={({ field }) => (
                          <TextField
                            {...field}
                            label="State Name"
                            fullWidth
                            error={!!errors.states?.[index]?.name}
                            helperText={errors.states?.[index]?.name?.message}
                          />
                        )}
                      />
                    </Grid>
                    <Grid item xs={12}>
                      <Controller
                        name={`states.${index}.description`}
                        control={control}
                        render={({ field }) => (
                          <TextField
                            {...field}
                            label="Description"
                            fullWidth
                            multiline
                            rows={2}
                          />
                        )}
                      />
                    </Grid>
                    <Grid item xs={6}>
                      <Controller
                        name={`states.${index}.is_initial`}
                        control={control}
                        render={({ field }) => (
                          <FormControlLabel
                            control={
                              <Switch
                                checked={field.value}
                                onChange={(e) => {
                                  field.onChange(e.target.checked);
                                  // If this is set to initial, unset others
                                  if (e.target.checked) {
                                    states.forEach((_, i) => {
                                      if (i !== index) {
                                        setValue(`states.${i}.is_initial`, false);
                                      }
                                    });
                                  }
                                }}
                              />
                            }
                            label="Initial State"
                          />
                        )}
                      />
                    </Grid>
                    <Grid item xs={6}>
                      <Controller
                        name={`states.${index}.is_final`}
                        control={control}
                        render={({ field }) => (
                          <FormControlLabel
                            control={<Switch checked={field.value} onChange={(e) => field.onChange(e.target.checked)} />}
                            label="Final State"
                          />
                        )}
                      />
                    </Grid>
                  </Grid>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      )}

      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
        <Typography variant="h6">Transitions</Typography>
        <Button
          variant="outlined"
          startIcon={<AddIcon />}
          onClick={handleAddTransition}
          disabled={states.length < 2}
        >
          Add Transition
        </Button>
      </Box>

      {transitionFields.length === 0 ? (
        <Paper sx={{ p: 3, mb: 4, textAlign: 'center' }}>
          <Typography color="textSecondary">
            {states.length < 2
              ? 'You need at least two states to create transitions'
              : 'No transitions defined yet'}
          </Typography>
          {states.length >= 2 && (
            <Button
              variant="outlined"
              startIcon={<AddIcon />}
              onClick={handleAddTransition}
              sx={{ mt: 2 }}
            >
              Add Transition
            </Button>
          )}
        </Paper>
      ) : (
        <Grid container spacing={3} sx={{ mb: 4 }}>
          {transitionFields.map((field, index) => (
            <Grid item xs={12} md={6} key={field.id}>
              <Card variant="outlined">
                <CardContent>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
                    <Typography variant="subtitle1">Transition {index + 1}</Typography>
                    <IconButton
                      color="error"
                      onClick={() => removeTransition(index)}
                      size="small"
                    >
                      <DeleteIcon />
                    </IconButton>
                  </Box>
                  <Grid container spacing={2}>
                    <Grid item xs={12}>
                      <Controller
                        name={`transitions.${index}.name`}
                        control={control}
                        render={({ field }) => (
                          <TextField
                            {...field}
                            label="Transition Name"
                            fullWidth
                            error={!!errors.transitions?.[index]?.name}
                            helperText={errors.transitions?.[index]?.name?.message}
                          />
                        )}
                      />
                    </Grid>
                    <Grid item xs={12}>
                      <Controller
                        name={`transitions.${index}.description`}
                        control={control}
                        render={({ field }) => (
                          <TextField
                            {...field}
                            label="Description"
                            fullWidth
                            multiline
                            rows={2}
                          />
                        )}
                      />
                    </Grid>
                    <Grid item xs={12} md={6}>
                      <Controller
                        name={`transitions.${index}.from_state_id`}
                        control={control}
                        render={({ field }) => (
                          <FormControl fullWidth error={!!errors.transitions?.[index]?.from_state_id}>
                            <InputLabel>From State</InputLabel>
                            <Select {...field} label="From State">
                              {states.map((state, stateIndex) => (
                                <MenuItem key={state.id || stateIndex} value={state.id || stateIndex.toString()}>
                                  {state.name}
                                </MenuItem>
                              ))}
                            </Select>
                            {errors.transitions?.[index]?.from_state_id && (
                              <FormHelperText>{errors.transitions?.[index]?.from_state_id?.message}</FormHelperText>
                            )}
                          </FormControl>
                        )}
                      />
                    </Grid>
                    <Grid item xs={12} md={6}>
                      <Controller
                        name={`transitions.${index}.to_state_id`}
                        control={control}
                        render={({ field }) => (
                          <FormControl fullWidth error={!!errors.transitions?.[index]?.to_state_id}>
                            <InputLabel>To State</InputLabel>
                            <Select {...field} label="To State">
                              {states.map((state, stateIndex) => (
                                <MenuItem key={state.id || stateIndex} value={state.id || stateIndex.toString()}>
                                  {state.name}
                                </MenuItem>
                              ))}
                            </Select>
                            {errors.transitions?.[index]?.to_state_id && (
                              <FormHelperText>{errors.transitions?.[index]?.to_state_id?.message}</FormHelperText>
                            )}
                          </FormControl>
                        )}
                      />
                    </Grid>
                  </Grid>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      )}

      {states.length > 0 && (
        <Paper sx={{ p: 3, mb: 4 }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
            <Typography variant="h6">Workflow Diagram</Typography>
            <Button variant="outlined" onClick={toggleDiagram}>
              {showDiagram ? 'Hide Diagram' : 'Show Diagram'}
            </Button>
          </Box>
          {showDiagram && (
            <Box sx={{ height: 400, border: '1px solid #ddd', borderRadius: 1 }}>
              <StateDiagram states={states} transitions={watch('transitions')} />
            </Box>
          )}
        </Paper>
      )}

      <Box sx={{ display: 'flex', justifyContent: 'flex-end', mt: 4 }}>
        <Button
          type="submit"
          variant="contained"
          color="primary"
          size="large"
          disabled={isSubmitting}
        >
          {isSubmitting ? 'Saving...' : initialData ? 'Update Workflow' : 'Create Workflow'}
        </Button>
      </Box>
    </form>
  );
}
