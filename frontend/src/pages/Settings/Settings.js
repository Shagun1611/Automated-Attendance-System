import React from 'react';
import { Container, Typography, Card, CardContent, Box } from '@mui/material';
import { Settings as SettingsIcon } from '@mui/icons-material';

function Settings() {
  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <div className="page-header">
        <Typography variant="h4" className="page-title">
          System Settings
        </Typography>
        <Typography variant="body1" className="page-subtitle">
          Configure system parameters and preferences
        </Typography>
      </div>

      <Card>
        <CardContent>
          <Box sx={{ textAlign: 'center', p: 4 }}>
            <SettingsIcon sx={{ fontSize: 80, color: 'secondary.main', mb: 2 }} />
            <Typography variant="h6" gutterBottom>
              System Configuration
            </Typography>
            <Typography variant="body1" color="textSecondary">
              This section will allow administrators to:
            </Typography>
            <Box sx={{ mt: 2, textAlign: 'left', maxWidth: 400, mx: 'auto' }}>
              <Typography variant="body2" sx={{ mb: 1 }}>
                • Configure face recognition parameters
              </Typography>
              <Typography variant="body2" sx={{ mb: 1 }}>
                • Manage user accounts and permissions
              </Typography>
              <Typography variant="body2" sx={{ mb: 1 }}>
                • Set up Power BI integration
              </Typography>
              <Typography variant="body2" sx={{ mb: 1 }}>
                • Configure notification settings
              </Typography>
              <Typography variant="body2">
                • System backup and maintenance
              </Typography>
            </Box>
          </Box>
        </CardContent>
      </Card>
    </Container>
  );
}

export default Settings;