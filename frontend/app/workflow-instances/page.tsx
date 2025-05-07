'use client';

import React from 'react';
import {
  Box,
  Button,
  Chip,
  Container,
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
  Fab,
} from '@mui/material';
import AddIcon from '@mui/icons-material/Add';
import VisibilityIcon from '@mui/icons-material/Visibility';
import PlayArrowIcon from '@mui/icons-material/PlayArrow';
import { useRouter } from 'next/navigation';
import Navigation from '../components/Navigation';
import AsyncBoundary from '../components/AsyncBoundary';
import { useWorkflowInstances, useWorkflowDefinitions } from '../hooks/useWorkflow';
import { formatDistanceToNow } from 'date-fns';

export default function WorkflowInstancesPage() {
  const router = useRouter();
  const { data: instances, isLoading, isError, error } = useWorkflowInstances();
  const { data: definitions } = useWorkflowDefinitions();

  const handleCreateNew = () => {
    router.push('/workflow-instances/new');
  };

  const handleView = (id: string) => {
    router.push(`/workflow-instances/${id}`);
  };

  // Helper function to get definition name by ID
  const getDefinitionName = (definitionId: string) => {
    const definition = definitions?.find((d) => d.id === definitionId);
    return definition?.name || 'Unknown Definition';
  };

  // Helper function to get state name by ID
  const getStateName = (definitionId: string, stateId: string) => {
    const definition = definitions?.find((d) => d.id === definitionId);
    const state = definition?.states.find((s) => s.id === stateId);
    return state?.name || 'Unknown State';
  };

  // Helper function to determine chip color based on status
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active':
        return 'primary';
      case 'completed':
        return 'success';
      case 'terminated':
        return 'error';
      default:
        return 'default';
    }
  };

  return (
    <main>
      <Navigation />
      <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={4}>
          <Typography variant="h4" component="h1" gutterBottom>
            Workflow Instances
          </Typography>
          <Button
            variant="contained"
            color="primary"
            startIcon={<AddIcon />}
            onClick={handleCreateNew}
          >
            Start New Workflow
          </Button>
        </Box>

        <AsyncBoundary isLoading={isLoading} isError={isError} error={error as Error}>
          {instances && instances.length > 0 ? (
            <TableContainer component={Paper}>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>ID</TableCell>
                    <TableCell>Workflow Definition</TableCell>
                    <TableCell>Current State</TableCell>
                    <TableCell>Status</TableCell>
                    <TableCell>Created</TableCell>
                    <TableCell>Last Updated</TableCell>
                    <TableCell align="right">Actions</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {instances.map((instance) => (
                    <TableRow key={instance.id}>
                      <TableCell>{instance.id}</TableCell>
                      <TableCell>{getDefinitionName(instance.workflow_definition_id)}</TableCell>
                      <TableCell>
                        {getStateName(instance.workflow_definition_id, instance.current_state_id)}
                      </TableCell>
                      <TableCell>
                        <Chip
                          label={instance.status}
                          color={getStatusColor(instance.status) as any}
                          size="small"
                        />
                      </TableCell>
                      <TableCell>
                        {formatDistanceToNow(new Date(instance.created_at), { addSuffix: true })}
                      </TableCell>
                      <TableCell>
                        {formatDistanceToNow(new Date(instance.updated_at), { addSuffix: true })}
                      </TableCell>
                      <TableCell align="right">
                        <Tooltip title="View Details">
                          <IconButton onClick={() => handleView(instance.id)}>
                            <VisibilityIcon />
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
                No workflow instances found
              </Typography>
              <Typography variant="body1" color="textSecondary" paragraph>
                Start a new workflow instance to get started
              </Typography>
              <Button
                variant="contained"
                color="primary"
                startIcon={<AddIcon />}
                onClick={handleCreateNew}
              >
                Start New Workflow
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
      </Container>
    </main>
  );
}
