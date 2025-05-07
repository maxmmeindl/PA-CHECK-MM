import { Box, Button, Container, Grid, Paper, Typography } from '@mui/material';
import Navigation from './components/Navigation';
import AccountTreeIcon from '@mui/icons-material/AccountTree';
import PlayArrowIcon from '@mui/icons-material/PlayArrow';
import Link from 'next/link';

export default function Home() {
  return (
    <main>
      <Navigation />
      <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
        <Paper
          sx={{
            p: 6,
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            textAlign: 'center',
            borderRadius: 2,
            boxShadow: 3,
            background: 'linear-gradient(to right bottom, #ffffff, #f5f5f5)',
          }}
        >
          <Typography
            variant="h2"
            component="h1"
            gutterBottom
            sx={{ fontWeight: 'bold', color: 'primary.main' }}
          >
            PA-CHECK-MM
          </Typography>
          <Typography variant="h5" color="text.secondary" paragraph>
            Enterprise Workflow Management Solution
          </Typography>
          <Box sx={{ mt: 4 }}>
            <Grid container spacing={4} justifyContent="center">
              <Grid item>
                <Button
                  component={Link}
                  href="/workflow-definitions"
                  variant="contained"
                  size="large"
                  startIcon={<AccountTreeIcon />}
                >
                  Manage Workflow Definitions
                </Button>
              </Grid>
              <Grid item>
                <Button
                  component={Link}
                  href="/workflow-instances"
                  variant="outlined"
                  size="large"
                  startIcon={<PlayArrowIcon />}
                >
                  View Workflow Instances
                </Button>
              </Grid>
            </Grid>
          </Box>
        </Paper>

        <Grid container spacing={4} sx={{ mt: 4 }}>
          <Grid item xs={12} md={4}>
            <Paper
              sx={{
                p: 3,
                display: 'flex',
                flexDirection: 'column',
                height: 240,
                borderRadius: 2,
              }}
            >
              <Typography variant="h6" gutterBottom>
                Define Workflows
              </Typography>
              <Typography variant="body1" paragraph sx={{ flex: 1 }}>
                Create and manage workflow definitions with states and transitions. Use our visual editor to design complex workflows.
              </Typography>
              <Button component={Link} href="/workflow-definitions" variant="text" color="primary">
                Get Started
              </Button>
            </Paper>
          </Grid>
          <Grid item xs={12} md={4}>
            <Paper
              sx={{
                p: 3,
                display: 'flex',
                flexDirection: 'column',
                height: 240,
                borderRadius: 2,
              }}
            >
              <Typography variant="h6" gutterBottom>
                Execute Workflows
              </Typography>
              <Typography variant="body1" paragraph sx={{ flex: 1 }}>
                Start workflow instances from your definitions and transition them through different states based on your business rules.
              </Typography>
              <Button component={Link} href="/workflow-instances" variant="text" color="primary">
                View Instances
              </Button>
            </Paper>
          </Grid>
          <Grid item xs={12} md={4}>
            <Paper
              sx={{
                p: 3,
                display: 'flex',
                flexDirection: 'column',
                height: 240,
                borderRadius: 2,
              }}
            >
              <Typography variant="h6" gutterBottom>
                Monitor Progress
              </Typography>
              <Typography variant="body1" paragraph sx={{ flex: 1 }}>
                Track the history and current state of all workflow instances. Get insights into your business processes.
              </Typography>
              <Button component={Link} href="/workflow-instances" variant="text" color="primary">
                View History
              </Button>
            </Paper>
          </Grid>
        </Grid>
      </Container>
    </main>
  );
}
