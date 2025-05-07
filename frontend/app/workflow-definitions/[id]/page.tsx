'use client';

import React from 'react';
import {
  Box,
  Button,
  Card,
  CardContent,
  Chip,
  Container,
  Divider,
  Grid,
  IconButton,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Tooltip,
  Typography,
} from '@mui/material';
import { useRouter } from 'next/navigation';
import Navigation from '../../../components/Navigation';
import AsyncBoundary from '../../../components/AsyncBoundary';
import { useWorkflowDefinition } from '../../../hooks/useWorkflow';
import EditIcon from '@mui/icons-material/Edit';
import DeleteIcon from '@mui/icons-material/Delete';
import PlayArrowIcon from '@mui/icons-material/PlayArrow';
import ArrowBackIcon from '@mui/icons-material/ArrowBack';
import { formatDistanceToNow } from 'date-fns';
import StateDiagram from '../../components/StateDiagram';

interface WorkflowDefinitionDetailPageProps {
  params: {
    id: string;
  };
}

export default function WorkflowDefinitionDetailPage({ params }: WorkflowDefinitionDetailPageProps) {
  const { id } = params;
  const router = useRouter();
  const { data: definition, isLoading, isError, error } = useWorkflowDefinition(id);

  const handleBack = () => {
    router.push('/workflow-definitions');
  };

  const handleEdit = () => {
    router.push(`/workflow-definitions/${id}/edit`);
  };

  const handleStartWorkflow = () => {
    router.push(`/workflow-instances/new?definitionId=${id}`);
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
            Back to List
          </Button>
          <Typography variant="h4" component="h1">
            Workflow Definition Details
          </Typography>
        </Box>

        <AsyncBoundary isLoading={isLoading} isError={isError} error={error as Error}>
          {definition && (
            <>
              <Paper sx={{ p: 3, mb: 4 }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                  <Box>
                    <Typography variant="h5" gutterBottom>
                      {definition.name}
                    </Typography>
                    <Typography variant="body1" color="textSecondary" paragraph>
                      {definition.description || 'No description provided'}
                    </Typography>
                    <Box sx={{ display: 'flex', gap: 1, mb: 2 }}>
                      <Chip label={`Version: ${definition.version}`} color="primary" variant="outlined" />
                      <Chip label={`States: ${definition.states.length}`} color="secondary" variant="outlined" />
                      <Chip label={`Transitions: ${definition.transitions.length}`} color="info" variant="outlined" />
                    </Box>
                    <Typography variant="body2" color="textSecondary">
                      Last updated: {formatDistanceToNow(new Date(definition.updated_at), { addSuffix: true })}
                    </Typography>
                  </Box>
                  <Box>
                    <Button
                      variant="contained"
                      color="primary"
                      startIcon={<PlayArrowIcon />}
                      onClick={handleStartWorkflow}
                      sx={{ mr: 1 }}
                    >
                      Start Workflow
                    </Button>
                    <Button
                      variant="outlined"
                      startIcon={<EditIcon />}
                      onClick={handleEdit}
                    >
                      Edit
                    </Button>
                  </Box>
                </Box>
              </Paper>

              <Grid container spacing={4}>
                <Grid item xs={12} md={6}>
                  <Paper sx={{ p: 3, mb: 4 }}>
                    <Typography variant="h6" gutterBottom>
                      States
                    </Typography>
                    <TableContainer>
                      <Table>
                        <TableHead>
                          <TableRow>
                            <TableCell>Name</TableCell>
                            <TableCell>Type</TableCell>
                            <TableCell>Description</TableCell>
                          </TableRow>
                        </TableHead>
                        <TableBody>
                          {definition.states.map((state) => (
                            <TableRow key={state.id}>
                              <TableCell>{state.name}</TableCell>
                              <TableCell>
                                {state.is_initial && state.is_final ? (
                                  <Chip label="Initial & Final" color="warning" size="small" />
                                ) : state.is_initial ? (
                                  <Chip label="Initial" color="success" size="small" />
                                ) : state.is_final ? (
                                  <Chip label="Final" color="error" size="small" />
                                ) : (
                                  <Chip label="Normal" color="default" size="small" />
                                )}
                              </TableCell>
                              <TableCell>{state.description || '-'}</TableCell>
                            </TableRow>
                          ))}
                        </TableBody>
                      </Table>
                    </TableContainer>
                  </Paper>
                </Grid>

                <Grid item xs={12} md={6}>
                  <Paper sx={{ p: 3, mb: 4 }}>
                    <Typography variant="h6" gutterBottom>
                      Transitions
                    </Typography>
                    <TableContainer>
                      <Table>
                        <TableHead>
                          <TableRow>
                            <TableCell>Name</TableCell>
                            <TableCell>From</TableCell>
                            <TableCell>To</TableCell>
                            <TableCell>Description</TableCell>
                          </TableRow>
                        </TableHead>
                        <TableBody>
                          {definition.transitions.map((transition) => {
                            const fromState = definition.states.find(
                              (s) => s.id === transition.from_state_id
                            );
                            const toState = definition.states.find(
                              (s) => s.id === transition.to_state_id
                            );

                            return (
                              <TableRow key={transition.id}>
                                <TableCell>{transition.name}</TableCell>
                                <TableCell>{fromState?.name || '-'}</TableCell>
                                <TableCell>{toState?.name || '-'}</TableCell>
                                <TableCell>{transition.description || '-'}</TableCell>
                              </TableRow>
                            );
                          })}
                        </TableBody>
                      </Table>
                    </TableContainer>
                  </Paper>
                </Grid>
              </Grid>

              <Paper sx={{ p: 3, mb: 4 }}>
                <Typography variant="h6" gutterBottom>
                  Workflow Diagram
                </Typography>
                <Box sx={{ height: 500, border: '1px solid #ddd', borderRadius: 1 }}>
                  <StateDiagram states={definition.states} transitions={definition.transitions} />
                </Box>
              </Paper>
            </>
          )}
        </AsyncBoundary>
      </Container>
    </main>
  );
}
