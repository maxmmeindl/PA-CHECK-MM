import axios from 'axios';

// Types for our API
export interface WorkflowDefinition {
  id: string;
  name: string;
  description: string;
  version: string;
  states: WorkflowState[];
  transitions: WorkflowTransition[];
  created_at: string;
  updated_at: string;
}

export interface WorkflowState {
  id: string;
  name: string;
  description: string;
  is_initial: boolean;
  is_final: boolean;
}

export interface WorkflowTransition {
  id: string;
  name: string;
  description: string;
  from_state_id: string;
  to_state_id: string;
  conditions?: string[];
}

export interface WorkflowInstance {
  id: string;
  workflow_definition_id: string;
  current_state_id: string;
  data: Record<string, any>;
  status: 'active' | 'completed' | 'terminated';
  created_at: string;
  updated_at: string;
}

export interface WorkflowHistoryEntry {
  id: string;
  workflow_instance_id: string;
  from_state_id: string | null;
  to_state_id: string;
  transition_id: string | null;
  timestamp: string;
  data: Record<string, any>;
}

export interface CreateWorkflowDefinitionRequest {
  name: string;
  description: string;
  version: string;
  states: Omit<WorkflowState, 'id'>[];
  transitions: Omit<WorkflowTransition, 'id'>[];
}

export interface UpdateWorkflowDefinitionRequest {
  name?: string;
  description?: string;
  version?: string;
  states?: Omit<WorkflowState, 'id'>[];
  transitions?: Omit<WorkflowTransition, 'id'>[];
}

export interface CreateWorkflowInstanceRequest {
  workflow_definition_id: string;
  data?: Record<string, any>;
}

export interface TransitionWorkflowInstanceRequest {
  transition_id: string;
  data?: Record<string, any>;
}

// Create axios instance
const apiClient = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// API service
export const apiService = {
  // Workflow Definitions
  getWorkflowDefinitions: async (): Promise<WorkflowDefinition[]> => {
    const response = await apiClient.get('/workflow-definitions');
    return response.data;
  },

  getWorkflowDefinition: async (id: string): Promise<WorkflowDefinition> => {
    const response = await apiClient.get(`/workflow-definitions/${id}`);
    return response.data;
  },

  createWorkflowDefinition: async (data: CreateWorkflowDefinitionRequest): Promise<WorkflowDefinition> => {
    const response = await apiClient.post('/workflow-definitions', data);
    return response.data;
  },

  updateWorkflowDefinition: async (id: string, data: UpdateWorkflowDefinitionRequest): Promise<WorkflowDefinition> => {
    const response = await apiClient.put(`/workflow-definitions/${id}`, data);
    return response.data;
  },

  deleteWorkflowDefinition: async (id: string): Promise<void> => {
    await apiClient.delete(`/workflow-definitions/${id}`);
  },

  // Workflow Instances
  getWorkflowInstances: async (): Promise<WorkflowInstance[]> => {
    const response = await apiClient.get('/workflow-instances');
    return response.data;
  },

  getWorkflowInstance: async (id: string): Promise<WorkflowInstance> => {
    const response = await apiClient.get(`/workflow-instances/${id}`);
    return response.data;
  },

  createWorkflowInstance: async (data: CreateWorkflowInstanceRequest): Promise<WorkflowInstance> => {
    const response = await apiClient.post('/workflow-instances', data);
    return response.data;
  },

  transitionWorkflowInstance: async (id: string, data: TransitionWorkflowInstanceRequest): Promise<WorkflowInstance> => {
    const response = await apiClient.post(`/workflow-instances/${id}/transition`, data);
    return response.data;
  },

  getWorkflowInstanceHistory: async (id: string): Promise<WorkflowHistoryEntry[]> => {
    const response = await apiClient.get(`/workflow-instances/${id}/history`);
    return response.data;
  },
};
