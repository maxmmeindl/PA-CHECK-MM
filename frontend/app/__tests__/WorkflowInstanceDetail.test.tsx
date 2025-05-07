import React from 'react';
import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

// Mock the components and hooks
jest.mock('next/navigation', () => ({
  useRouter: jest.fn(() => ({
    push: jest.fn(),
  })),
  usePathname: jest.fn(() => '/workflow-instances'),
}));

jest.mock('../hooks/useWorkflow', () => ({
  useWorkflowInstance: jest.fn(),
  useWorkflowDefinition: jest.fn(),
  useWorkflowInstanceHistory: jest.fn(),
  useTransitionWorkflowInstance: jest.fn(),
}));

// Mock Navigation component
jest.mock('../components/Navigation', () => {
  return {
    __esModule: true,
    default: () => <div>Navigation</div>,
  };
});

// Mock AsyncBoundary component
jest.mock('../components/AsyncBoundary', () => {
  return {
    __esModule: true,
    default: ({ isLoading, isError, error, children }) => {
      if (isLoading) return <div>Loading...</div>;
      if (isError) return <div>Error<div>{error?.message}</div></div>;
      return <>{children}</>;
    },
  };
});

// Import hooks after mocking
import { useRouter } from 'next/navigation';
import {
  useWorkflowInstance,
  useWorkflowDefinition,
  useWorkflowInstanceHistory,
  useTransitionWorkflowInstance,
} from '../hooks/useWorkflow';

// Create a mock component for testing
const MockWorkflowInstanceDetailPage = ({ params }: { params: { id: string } }) => {
  const { id } = params;
  const router = useRouter();
  const { data: instance, isLoading: instanceLoading, isError: instanceError, error: instanceErrorData } = useWorkflowInstance(id);
  const { data: history, isLoading: historyLoading, isError: historyError, error: historyErrorData } = useWorkflowInstanceHistory(id);
  
  const { data: definition } = useWorkflowDefinition(
    instance?.workflow_definition_id || '',
    { enabled: !!instance?.workflow_definition_id }
  );

  const isLoading = instanceLoading || historyLoading;
  const isError = instanceError || historyError;
  const error = instanceErrorData || historyErrorData;

  if (isLoading) return <div>Loading...</div>;
  if (isError) return <div>Error: {error?.message}</div>;
  if (!instance || !definition) return <div>No data</div>;

  return (
    <div>
      <h1>{definition.name} (v{definition.version})</h1>
      <div>Instance ID: {instance.id}</div>
      <div>Status: {instance.status}</div>
      <div>Current State: {definition.states.find(s => s.id === instance.current_state_id)?.name}</div>
      {instance.status === 'active' && (
        <button>Transition Workflow</button>
      )}
    </div>
  );
};

// Create a wrapper for the component with QueryClientProvider
const createWrapper = () => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
      },
    },
  });
  
  return ({ children }: { children: React.ReactNode }) => (
    <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
  );
};

describe('WorkflowInstanceDetailPage', () => {
  const mockRouter = {
    push: jest.fn(),
  };
  
  const mockTransitionMutation = {
    mutateAsync: jest.fn(),
    isPending: false,
  };
  
  const mockInstance = {
    id: 'inst-1',
    workflow_definition_id: 'def-1',
    current_state_id: 'state-1',
    data: { key: 'value' },
    status: 'active',
    created_at: '2025-01-01T00:00:00Z',
    updated_at: '2025-01-02T00:00:00Z',
  };
  
  const mockDefinition = {
    id: 'def-1',
    name: 'Approval Workflow',
    description: 'A simple approval workflow',
    version: '1.0.0',
    states: [
      { id: 'state-1', name: 'Draft', is_initial: true, is_final: false, description: 'Initial draft state' },
      { id: 'state-2', name: 'Approved', is_initial: false, is_final: true, description: 'Final approved state' },
    ],
    transitions: [
      { 
        id: 'trans-1', 
        name: 'Approve', 
        from_state_id: 'state-1', 
        to_state_id: 'state-2',
        description: 'Approve the document'
      },
    ],
    created_at: '2025-01-01T00:00:00Z',
    updated_at: '2025-01-01T00:00:00Z',
  };
  
  const mockHistory = [
    {
      id: 'hist-1',
      workflow_instance_id: 'inst-1',
      from_state_id: null,
      to_state_id: 'state-1',
      transition_id: null,
      timestamp: '2025-01-01T00:00:00Z',
      data: { action: 'create' },
    },
  ];
  
  beforeEach(() => {
    jest.clearAllMocks();
    (useRouter as jest.Mock).mockReturnValue(mockRouter);
    (useTransitionWorkflowInstance as jest.Mock).mockReturnValue(mockTransitionMutation);
    (useWorkflowInstance as jest.Mock).mockReturnValue({
      data: mockInstance,
      isLoading: false,
      isError: false,
      error: null,
    });
    (useWorkflowDefinition as jest.Mock).mockReturnValue({
      data: mockDefinition,
      isLoading: false,
      isError: false,
      error: null,
    });
    (useWorkflowInstanceHistory as jest.Mock).mockReturnValue({
      data: mockHistory,
      isLoading: false,
      isError: false,
      error: null,
    });
  });
  
  test('renders loading state correctly', () => {
    (useWorkflowInstance as jest.Mock).mockReturnValue({
      data: undefined,
      isLoading: true,
      isError: false,
      error: null,
    });
    
    render(<WorkflowInstanceDetailPage params={{ id: 'inst-1' }} />, { wrapper: createWrapper() });
    
    expect(screen.getByText('Loading...')).toBeInTheDocument();
  });
  
  test('renders error state correctly', () => {
    (useWorkflowInstance as jest.Mock).mockReturnValue({
      data: undefined,
      isLoading: false,
      isError: true,
      error: new Error('Failed to fetch workflow instance'),
    });
    
    render(<WorkflowInstanceDetailPage params={{ id: 'inst-1' }} />, { wrapper: createWrapper() });
    
    expect(screen.getByText('Error')).toBeInTheDocument();
    expect(screen.getByText('Failed to fetch workflow instance')).toBeInTheDocument();
  });
  
  test('renders workflow instance details correctly', () => {
    render(<WorkflowInstanceDetailPage params={{ id: 'inst-1' }} />, { wrapper: createWrapper() });
    
    // Check if basic information is displayed
    expect(screen.getByText('Approval Workflow (v1.0.0)')).toBeInTheDocument();
    expect(screen.getByText('Instance ID: inst-1')).toBeInTheDocument();
    expect(screen.getByText('Status: active')).toBeInTheDocument();
    expect(screen.getByText('Current State: Draft')).toBeInTheDocument();
    
    // Check if current data is displayed
    expect(screen.getByText(/"key": "value"/)).toBeInTheDocument();
    
    // Check if available transitions are displayed
    expect(screen.getByText('Available Transitions')).toBeInTheDocument();
    expect(screen.getByText('Approve')).toBeInTheDocument();
    expect(screen.getByText('Approved')).toBeInTheDocument();
    
    // Check if history is displayed
    expect(screen.getByText('Workflow History')).toBeInTheDocument();
    expect(screen.getByText('Initial')).toBeInTheDocument();
    expect(screen.getByText('Draft')).toBeInTheDocument();
    expect(screen.getByText('Initialization')).toBeInTheDocument();
  });
  
  test('opens transition dialog when transition button is clicked', async () => {
    render(<WorkflowInstanceDetailPage params={{ id: 'inst-1' }} />, { wrapper: createWrapper() });
    
    const transitionButton = screen.getByText('Transition Workflow');
    fireEvent.click(transitionButton);
    
    // Check if the transition dialog is shown
    await waitFor(() => {
      expect(screen.getByText('Transition Workflow')).toBeInTheDocument();
      expect(screen.getByText('Select Transition')).toBeInTheDocument();
      expect(screen.getByText('Transition Data (JSON)')).toBeInTheDocument();
    });
  });
  
  test('submits transition when form is submitted', async () => {
    mockTransitionMutation.mutateAsync.mockResolvedValue({
      ...mockInstance,
      current_state_id: 'state-2',
    });
    
    render(<WorkflowInstanceDetailPage params={{ id: 'inst-1' }} />, { wrapper: createWrapper() });
    
    // Open the transition dialog
    const transitionButton = screen.getByText('Transition Workflow');
    fireEvent.click(transitionButton);
    
    // Wait for the dialog to appear
    await waitFor(() => {
      expect(screen.getByText('Transition Workflow')).toBeInTheDocument();
    });
    
    // Select a transition
    const selectElement = screen.getByLabelText('Select Transition');
    fireEvent.mouseDown(selectElement);
    
    // Wait for the dropdown to appear and select the option
    await waitFor(() => {
      const option = screen.getByText('Approve (to Approved)');
      fireEvent.click(option);
    });
    
    // Enter JSON data
    const dataField = screen.getByPlaceholderText('Enter JSON data');
    fireEvent.change(dataField, { target: { value: '{"comment": "Looks good"}' } });
    
    // Submit the form
    const submitButton = screen.getByText('Execute Transition');
    fireEvent.click(submitButton);
    
    // Check if the mutation was called with the correct parameters
    await waitFor(() => {
      expect(mockTransitionMutation.mutateAsync).toHaveBeenCalledWith({
        transition_id: 'trans-1',
        data: { comment: 'Looks good' },
      });
    });
    
    // Check if success message is shown
    await waitFor(() => {
      expect(screen.getByText('Workflow transitioned successfully')).toBeInTheDocument();
    });
  });
  
  test('handles completed workflow state correctly', () => {
    (useWorkflowInstance as jest.Mock).mockReturnValue({
      data: { ...mockInstance, status: 'completed', current_state_id: 'state-2' },
      isLoading: false,
      isError: false,
      error: null,
    });
    
    render(<WorkflowInstanceDetailPage params={{ id: 'inst-1' }} />, { wrapper: createWrapper() });
    
    // Check if status is displayed correctly
    expect(screen.getByText('Status: completed')).toBeInTheDocument();
    
    // Check if transition button is not present
    expect(screen.queryByText('Transition Workflow')).not.toBeInTheDocument();
    
    // Check if the available transitions section shows the completed message
    expect(screen.getByText('Workflow is completed')).toBeInTheDocument();
  });
});
