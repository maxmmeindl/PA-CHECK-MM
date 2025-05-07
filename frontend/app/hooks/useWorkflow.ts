import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { 
  apiService, 
  WorkflowDefinition, 
  WorkflowInstance, 
  WorkflowHistoryEntry,
  CreateWorkflowDefinitionRequest,
  UpdateWorkflowDefinitionRequest,
  CreateWorkflowInstanceRequest,
  TransitionWorkflowInstanceRequest
} from '../api/apiService';

// Query keys
export const queryKeys = {
  workflowDefinitions: 'workflowDefinitions',
  workflowDefinition: (id: string) => ['workflowDefinition', id],
  workflowInstances: 'workflowInstances',
  workflowInstance: (id: string) => ['workflowInstance', id],
  workflowInstanceHistory: (id: string) => ['workflowInstanceHistory', id],
};

// Workflow Definition Hooks
export const useWorkflowDefinitions = () => {
  return useQuery({
    queryKey: [queryKeys.workflowDefinitions],
    queryFn: () => apiService.getWorkflowDefinitions(),
  });
};

export const useWorkflowDefinition = (id: string) => {
  return useQuery({
    queryKey: queryKeys.workflowDefinition(id),
    queryFn: () => apiService.getWorkflowDefinition(id),
    enabled: !!id,
  });
};

export const useCreateWorkflowDefinition = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (data: CreateWorkflowDefinitionRequest) => 
      apiService.createWorkflowDefinition(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [queryKeys.workflowDefinitions] });
    },
  });
};

export const useUpdateWorkflowDefinition = (id: string) => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (data: UpdateWorkflowDefinitionRequest) => 
      apiService.updateWorkflowDefinition(id, data),
    onSuccess: (updatedDefinition) => {
      queryClient.invalidateQueries({ queryKey: [queryKeys.workflowDefinitions] });
      queryClient.invalidateQueries({ queryKey: queryKeys.workflowDefinition(id) });
      queryClient.setQueryData(queryKeys.workflowDefinition(id), updatedDefinition);
    },
  });
};

export const useDeleteWorkflowDefinition = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (id: string) => apiService.deleteWorkflowDefinition(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [queryKeys.workflowDefinitions] });
    },
  });
};

// Workflow Instance Hooks
export const useWorkflowInstances = () => {
  return useQuery({
    queryKey: [queryKeys.workflowInstances],
    queryFn: () => apiService.getWorkflowInstances(),
  });
};

export const useWorkflowInstance = (id: string) => {
  return useQuery({
    queryKey: queryKeys.workflowInstance(id),
    queryFn: () => apiService.getWorkflowInstance(id),
    enabled: !!id,
  });
};

export const useWorkflowInstanceHistory = (id: string) => {
  return useQuery({
    queryKey: queryKeys.workflowInstanceHistory(id),
    queryFn: () => apiService.getWorkflowInstanceHistory(id),
    enabled: !!id,
  });
};

export const useCreateWorkflowInstance = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (data: CreateWorkflowInstanceRequest) => 
      apiService.createWorkflowInstance(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [queryKeys.workflowInstances] });
    },
  });
};

export const useTransitionWorkflowInstance = (id: string) => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (data: TransitionWorkflowInstanceRequest) => 
      apiService.transitionWorkflowInstance(id, data),
    onSuccess: (updatedInstance) => {
      queryClient.invalidateQueries({ queryKey: [queryKeys.workflowInstances] });
      queryClient.invalidateQueries({ queryKey: queryKeys.workflowInstance(id) });
      queryClient.invalidateQueries({ queryKey: queryKeys.workflowInstanceHistory(id) });
      queryClient.setQueryData(queryKeys.workflowInstance(id), updatedInstance);
    },
  });
};
