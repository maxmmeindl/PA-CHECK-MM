import React from 'react';

interface AsyncBoundaryProps {
  isLoading: boolean;
  isError: boolean;
  error: Error | null;
  children: React.ReactNode;
  loadingMessage?: string;
}

export default function AsyncBoundary({
  isLoading,
  isError,
  error,
  children,
  loadingMessage = 'Loading...',
}: AsyncBoundaryProps) {
  if (isLoading) {
    return <div>{loadingMessage}</div>;
  }

  if (isError) {
    return (
      <div>
        <div>Error</div>
        <div>{error?.message || 'An unexpected error occurred. Please try again.'}</div>
      </div>
    );
  }

  return <>{children}</>;
}
