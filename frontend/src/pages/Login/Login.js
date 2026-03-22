import React, { useState } from 'react';
import {
  Container,
  Paper,
  TextField,
  Button,
  Typography,
  Box,
  Alert,
  CircularProgress,
  Card,
  CardContent,
} from '@mui/material';
import { School, Login as LoginIcon } from '@mui/icons-material';
import { authService } from '../../services/authService';
import { toast } from 'react-toastify';
import './Login.css';

function Login({ onLogin }) {
  const [formData, setFormData] = useState({
    username: '',
    password: '',
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
    // Clear error when user starts typing
    if (error) {
      setError('');
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!formData.username || !formData.password) {
      setError('Please enter both username and password');
      return;
    }

    setLoading(true);
    setError('');

    try {
      const result = await authService.login(formData.username, formData.password);
      
      if (result.success) {
        toast.success('Login successful!');
        onLogin(result.user);
      } else {
        setError(result.error || 'Login failed');
      }
    } catch (error) {
      setError('Network error. Please check your connection and try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-container">
      <Container maxWidth="sm">
        <Box
          sx={{
            minHeight: '100vh',
            display: 'flex',
            flexDirection: 'column',
            justifyContent: 'center',
            alignItems: 'center',
          }}
        >
          {/* Header */}
          <Box sx={{ textAlign: 'center', mb: 4 }}>
            <School sx={{ fontSize: 60, color: 'primary.main', mb: 2 }} />
            <Typography variant="h4" component="h1" sx={{ fontWeight: 700, mb: 1 }}>
              Automated Attendance System
            </Typography>
            <Typography variant="subtitle1" color="textSecondary">
              Rural Schools Management Portal
            </Typography>
          </Box>

          {/* Login Form */}
          <Paper elevation={3} sx={{ width: '100%', maxWidth: 400 }}>
            <CardContent sx={{ p: 4 }}>
              <Box sx={{ textAlign: 'center', mb: 3 }}>
                <LoginIcon sx={{ fontSize: 40, color: 'primary.main', mb: 1 }} />
                <Typography variant="h5" component="h2" sx={{ fontWeight: 600 }}>
                  Sign In
                </Typography>
                <Typography variant="body2" color="textSecondary">
                  Enter your credentials to continue
                </Typography>
              </Box>

              {error && (
                <Alert severity="error" sx={{ mb: 2 }}>
                  {error}
                </Alert>
              )}

              <form onSubmit={handleSubmit}>
                <TextField
                  fullWidth
                  label="Username"
                  name="username"
                  value={formData.username}
                  onChange={handleChange}
                  margin="normal"
                  required
                  autoFocus
                  disabled={loading}
                  variant="outlined"
                />
                <TextField
                  fullWidth
                  label="Password"
                  name="password"
                  type="password"
                  value={formData.password}
                  onChange={handleChange}
                  margin="normal"
                  required
                  disabled={loading}
                  variant="outlined"
                />
                <Button
                  type="submit"
                  fullWidth
                  variant="contained"
                  size="large"
                  disabled={loading}
                  sx={{ 
                    mt: 3, 
                    mb: 2,
                    py: 1.5,
                    fontSize: '1rem',
                    fontWeight: 600,
                  }}
                >
                  {loading ? (
                    <>
                      <CircularProgress size={20} color="inherit" sx={{ mr: 1 }} />
                      Signing In...
                    </>
                  ) : (
                    'Sign In'
                  )}
                </Button>
              </form>
            </CardContent>
          </Paper>

          {/* Demo Credentials */}
          <Card sx={{ mt: 3, width: '100%', maxWidth: 400, bgcolor: 'grey.50' }}>
            <CardContent sx={{ p: 3 }}>
              <Typography variant="h6" sx={{ mb: 2, fontWeight: 600, color: 'primary.main' }}>
                Demo Credentials
              </Typography>
              <Box sx={{ mb: 2 }}>
                <Typography variant="subtitle2" sx={{ fontWeight: 600 }}>
                  Administrator:
                </Typography>
                <Typography variant="body2" color="textSecondary">
                  Username: <strong>admin</strong> | Password: <strong>admin123</strong>
                </Typography>
              </Box>
              <Box>
                <Typography variant="subtitle2" sx={{ fontWeight: 600 }}>
                  Teacher:
                </Typography>
                <Typography variant="body2" color="textSecondary">
                  Username: <strong>teacher1</strong> | Password: <strong>teacher123</strong>
                </Typography>
              </Box>
            </CardContent>
          </Card>

          {/* Footer */}
          <Box sx={{ mt: 4, textAlign: 'center' }}>
            <Typography variant="body2" color="textSecondary">
              © 2024 Automated Attendance System. All rights reserved.
            </Typography>
          </Box>
        </Box>
      </Container>
    </div>
  );
}

export default Login;