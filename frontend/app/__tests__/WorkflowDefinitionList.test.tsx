import React from 'react';
import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

// Mock the components and hooks
jest.mock('next/navigation', () => ({
  useRouter: jest.fn(() => ({
    push: jest.fn(),
  })),
  usePathname: jest.fn(() => '/workflow-definitions'),
}));

jest.mock('../hooks/useWorkflow', () => ({
  useWorkflowDefinitions: jest.fn(),
  useDeleteWorkflowDefinition: jest.fn(),
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
import { useWorkflowDefinitions, useDeleteWorkflowDefinition } from '../hooks/useWorkflow';

// Import the component after mocking dependencies
import WorkflowDefinitionsPage from '../workflow-definitions/page';

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

describe('WorkflowDefinitionsPage', () => {
  const mockRouter = {
    push: jest.fn(),
  };
  
  const mockDeleteMutation = {
    mutateAsync: jest.fn(),
    isPending: false,
  };
  
  beforeEach(() => {
    jest.clearAllMocks();
    (useRouter as jest.Mock).mockReturnValue(mockRouter);
    (useDeleteWorkflowDefinition as jest.Mock).mockReturnValue(mockDeleteMutation);
  });
  
  test('renders loading state correctly', () => {
    (useWorkflowDefinitions as jest.Mock).mockReturnValue({
      data: undefined,
      isLoading: true,
      isError: false,
      error: null,
      refetch: jest.fn(),
    });
    
    render(<WorkflowDefinitionsPage />, { wrapper: createWrapper() });
    
    expect(screen.getByText('Loading...')).toBeInTheDocument();
  });
  
  test('renders error state correctly', () => {
    (useWorkflowDefinitions as jest.Mock).mockReturnValue({
      data: undefined,
      isLoading: false,
      isError: true,
      error: new Error('Failed to fetch workflow definitions'),
      refetch: jest.fn(),
    });
    
    render(<WorkflowDefinitionsPage />, { wrapper: createWrapper() });
    
    expect(screen.getByText('Error')).toBeInTheDocument();
    expect(screen.getByText('Failed to fetch workflow definitions')).toBeInTheDocument();
  });
  
  test('renders empty state correctly', () => {
    (useWorkflowDefinitions as jest.Mock).mockReturnValue({
      data: [],
      isLoading: false,
      isError: false,
      error: null,
      refetch: jest.fn(),
    });
    
    render(<WorkflowDefinitionsPage />, { wrapper: createWrapper() });
    
    expect(screen.getByText('No workflow definitions found')).toBeInTheDocument();
    expect(screen.getByText('Create your first workflow definition to get started')).toBeInTheDocument();
  });
  
  test('renders workflow definitions list correctly', () => {
    const mockDefinitions = [
      {
        id: '1',
        name: 'Approval Workflow',
        description: 'A simple approval workflow',
        version: '1.0.0',
        states: [{ id: 's1', name: 'Draft' }, { id: 's2', name: 'Approved' }],
        transitions: [{ id: 't1', name: 'Approve', from_state_id: 's1', to_state_id: 's2' }],
        created_at: '2025-01-01T00:00:00Z',
        updated_at: '2025-01-02T00:00:00Z',
      },
      {
        id: '2',
        name: 'Order Process',
        description: 'Order processing workflow',
        version: '2.1.0',
        states: [{ id: 's1', name: 'New' }, { id: 's2', name: 'Processing' }, { id: 's3', name: 'Shipped' }],
        transitions: [
          { id: 't1', name: 'Process', from_state_id: 's1', to_state_id: 's2' },
          { id: 't2', name: 'Ship', from_state_id: 's2', to_state_id: 's3' },
        ],
        created_at: '2025-02-01T00:00:00Z',
        updated_at: '2025-02-02T00:00:00Z',
      },
    ];
    
    (useWorkflowDefinitions as jest.Mock).mockReturnValue({
      data: mockDefinitions,
      isLoading: false,
      isError: false,
      error: null,
      refetch: jest.fn(),
    });
    
    render(<WorkflowDefinitionsPage />, { wrapper: createWrapper() });
    
    expect(screen.getByText('Approval Workflow')).toBeInTheDocument();
    expect(screen.getByText('Order Process')).toBeInTheDocument();
    expect(screen.getByText('1.0.0')).toBeInTheDocument();
    expect(screen.getByText('2.1.0')).toBeInTheDocument();
    expect(screen.getByText('2')).toBeInTheDocument(); // Number of states for first workflow
    expect(screen.getByText('3')).toBeInTheDocument(); // Number of states for second workflow
  });
  
  test('navigates to create new definition page when button is clicked', () => {
    (useWorkflowDefinitions as jest.Mock).mockReturnValue({
      data: [],
      isLoading: false,
      isError: false,
      error: null,
      refetch: jest.fn(),
    });
    
    render(<WorkflowDefinitionsPage />, { wrapper: createWrapper() });
    
    const createButton = screen.getByText('Create New Definition');
    fireEvent.click(createButton);
    
    expect(mockRouter.push).toHaveBeenCalledWith('/workflow-definitions/new');
  });
  
  test('shows delete confirmation dialog when delete button is clicked', async () => {
    const mockDefinitions = [
      {
        id: '1',
        name: 'Approval Workflow',
        description: 'A simple approval workflow',
        version: '1.0.0',
        states: [{ id: 's1', name: 'Draft' }, { id: 's2', name: 'Approved' }],
        transitions: [{ id: 't1', name: 'Approve', from_state_id: 's1', to_state_id: 's2' }],
        created_at: '2025-01-01T00:00:00Z',
        updated_at: '2025-01-02T00:00:00Z',
      },
    ];
    
    (useWorkflowDefinitions as jest.Mock).mockReturnValue({
      data: mockDefinitions,
      isLoading: false,
      isError: false,
      error: null,
      refetch: jest.fn(),
    });
    
    render(<WorkflowDefinitionsPage />, { wrapper: createWrapper() });
    
    // Find and click the delete button (using the aria-label of the IconButton)
    const deleteButtons = screen.getAllByRole('button');
    const deleteButton = deleteButtons.find(button => 
      button.getAttribute('aria-label') === 'Delete' || 
      button.textContent === 'delete'
    );
    
    if (deleteButton) {
      fireEvent.click(deleteButton);
    }
    
    // Check if the confirmation dialog is shown
    await waitFor(() => {
      expect(screen.getByText('Delete Workflow Definition')).toBeInTheDocument();
      expect(screen.getByText('Are you sure you want to delete this workflow definition? This action cannot be undone.')).toBeInTheDocument();
    });
  });
});
