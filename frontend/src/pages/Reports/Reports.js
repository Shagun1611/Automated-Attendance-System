import React from 'react';
import { Container, Typography, Card, CardContent, Box } from '@mui/material';
import { Assessment } from '@mui/icons-material';

function Reports() {
  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <div className="page-header">
        <Typography variant="h4" className="page-title">
          Reports & Analytics
        </Typography>
        <Typography variant="body1" className="page-subtitle">
          Comprehensive attendance reports and Power BI integration
        </Typography>
      </div>

      <Card>
        <CardContent>
          <Box sx={{ textAlign: 'center', p: 4 }}>
            <Assessment sx={{ fontSize: 80, color: 'warning.main', mb: 2 }} />
            <Typography variant="h6" gutterBottom>
              Advanced Analytics Dashboard
            </Typography>
            <Typography variant="body1" color="textSecondary">
              This section will include:
            </Typography>
            <Box sx={{ mt: 2, textAlign: 'left', maxWidth: 400, mx: 'auto' }}>
              <Typography variant="body2" sx={{ mb: 1 }}>
                • Daily, weekly, and monthly attendance reports
              </Typography>
              <Typography variant="body2" sx={{ mb: 1 }}>
                • Student-wise attendance analytics
              </Typography>
              <Typography variant="body2" sx={{ mb: 1 }}>
                • Class and section performance metrics
              </Typography>
              <Typography variant="body2" sx={{ mb: 1 }}>
                • Export reports to Excel/PDF formats
              </Typography>
              <Typography variant="body2">
                • Power BI dashboard integration
              </Typography>
            </Box>
          </Box>
        </CardContent>
      </Card>
    </Container>
  );
}

export default Reports;