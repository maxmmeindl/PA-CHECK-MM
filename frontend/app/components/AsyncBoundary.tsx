import React from 'react';
import { Alert, AlertTitle, Box, CircularProgress, Paper, Typography } from '@mui/material';

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
    return (
      <Box
        display="flex"
        flexDirection="column"
        alignItems="center"
        justifyContent="center"
        minHeight="200px"
        width="100%"
      >
        <CircularProgress size={40} />
        <Typography variant="body1" sx={{ mt: 2 }}>
          {loadingMessage}
        </Typography>
      </Box>
    );
  }

  if (isError) {
    return (
      <Paper sx={{ p: 3, mt: 2, mb: 2 }}>
        <Alert severity="error">
          <AlertTitle>Error</AlertTitle>
          {error?.message || 'An unexpected error occurred. Please try again.'}
        </Alert>
      </Paper>
    );
  }

  return <>{children}</>;
}
