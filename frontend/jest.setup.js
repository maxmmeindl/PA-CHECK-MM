// Learn more: https://github.com/testing-library/jest-dom
import '@testing-library/jest-dom';

// Mock next/navigation
jest.mock('next/navigation', () => ({
  useRouter: () => ({
    push: jest.fn(),
    replace: jest.fn(),
    prefetch: jest.fn(),
    back: jest.fn(),
  }),
  useSearchParams: () => ({
    get: jest.fn(() => null),
  }),
  usePathname: jest.fn(() => '/'),
}));

// Components are mocked in the __mocks__ directory

// Mock for ReactFlow
jest.mock('reactflow', () => ({
  __esModule: true,
  default: jest.fn(() => null),
  useNodesState: jest.fn(() => [[], jest.fn(), jest.fn()]),
  useEdgesState: jest.fn(() => [[], jest.fn(), jest.fn()]),
  Position: {
    Left: 'left',
    Right: 'right',
    Top: 'top',
    Bottom: 'bottom',
  },
  MarkerType: {
    Arrow: 'arrow',
    ArrowClosed: 'arrowclosed',
  },
  Controls: jest.fn(() => null),
  Background: jest.fn(() => null),
}));

// Mock for date-fns
jest.mock('date-fns', () => ({
  formatDistanceToNow: jest.fn(() => '2 days ago'),
  format: jest.fn(() => 'Jan 1, 2025 12:00:00'),
}));

// Mock for window.alert
global.alert = jest.fn();

// Suppress console errors during tests
console.error = jest.fn();
