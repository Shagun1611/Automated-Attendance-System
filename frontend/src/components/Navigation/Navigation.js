import React from 'react';
import {
  Drawer,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  AppBar,
  Toolbar,
  Typography,
  IconButton,
  Avatar,
  Menu,
  MenuItem,
  Divider,
  Box,
} from '@mui/material';
import {
  Dashboard,
  People,
  CheckCircle,
  Assessment,
  Settings,
  AccountCircle,
  Logout,
  School,
} from '@mui/icons-material';
import { useNavigate, useLocation } from 'react-router-dom';
import './Navigation.css';

const drawerWidth = 280;

const navigationItems = [
  { text: 'Dashboard', icon: Dashboard, path: '/dashboard', roles: ['admin', 'teacher', 'principal'] },
  { text: 'Students', icon: People, path: '/students', roles: ['admin', 'teacher', 'principal'] },
  { text: 'Attendance', icon: CheckCircle, path: '/attendance', roles: ['admin', 'teacher', 'principal'] },
  { text: 'Reports', icon: Assessment, path: '/reports', roles: ['admin', 'teacher', 'principal'] },
  { text: 'Settings', icon: Settings, path: '/settings', roles: ['admin'] },
  { text: 'Add Teacher', icon: People, path: '/admin/add-teacher', roles: ['admin'] },
];

function Navigation({ currentUser, onLogout }) {
  const navigate = useNavigate();
  const location = useLocation();
  const [anchorEl, setAnchorEl] = React.useState(null);

  const handleUserMenuOpen = (event) => {
    setAnchorEl(event.currentTarget);
  };

  const handleUserMenuClose = () => {
    setAnchorEl(null);
  };

  const handleLogout = () => {
    handleUserMenuClose();
    onLogout();
  };

  const filteredNavigationItems = navigationItems.filter(item => 
    item.roles.includes(currentUser?.role)
  );

  return (
    <>
      {/* App Bar */}
      <AppBar position="fixed" sx={{ zIndex: (theme) => theme.zIndex.drawer + 1 }}>
        <Toolbar>
          <School sx={{ mr: 2 }} />
          <Typography variant="h6" noWrap component="div" sx={{ flexGrow: 1 }}>
            Automated Attendance System
          </Typography>
          <Box sx={{ display: 'flex', alignItems: 'center' }}>
            <Typography variant="body2" sx={{ mr: 2, display: { xs: 'none', sm: 'block' } }}>
              Welcome, {currentUser?.full_name}
            </Typography>
            <IconButton
              size="large"
              edge="end"
              aria-label="account of current user"
              aria-controls="user-menu"
              aria-haspopup="true"
              onClick={handleUserMenuOpen}
              color="inherit"
            >
              <Avatar sx={{ width: 32, height: 32, bgcolor: 'secondary.main' }}>
                {currentUser?.full_name?.charAt(0) || 'U'}
              </Avatar>
            </IconButton>
          </Box>
        </Toolbar>
      </AppBar>

      {/* User Menu */}
      <Menu
        id="user-menu"
        anchorEl={anchorEl}
        open={Boolean(anchorEl)}
        onClose={handleUserMenuClose}
        anchorOrigin={{
          vertical: 'bottom',
          horizontal: 'right',
        }}
        transformOrigin={{
          vertical: 'top',
          horizontal: 'right',
        }}
      >
        <MenuItem onClick={handleUserMenuClose}>
          <ListItemIcon>
            <AccountCircle fontSize="small" />
          </ListItemIcon>
          Profile
        </MenuItem>
        <Divider />
        <MenuItem onClick={handleLogout}>
          <ListItemIcon>
            <Logout fontSize="small" />
          </ListItemIcon>
          Logout
        </MenuItem>
      </Menu>

      {/* Sidebar Drawer */}
      <Drawer
        variant="permanent"
        sx={{
          width: drawerWidth,
          flexShrink: 0,
          '& .MuiDrawer-paper': {
            width: drawerWidth,
            boxSizing: 'border-box',
          },
        }}
      >
        <Toolbar /> {/* This creates space for the AppBar */}
        <Box sx={{ overflow: 'auto', height: '100%' }}>
          <List>
            {filteredNavigationItems.map((item) => {
              const Icon = item.icon;
              const isActive = location.pathname === item.path;
              
              return (
                <ListItem key={item.text} disablePadding>
                  <ListItemButton
                    onClick={() => navigate(item.path)}
                    className={isActive ? 'active-nav-item' : ''}
                    sx={{
                      minHeight: 48,
                      px: 2.5,
                      backgroundColor: isActive ? 'action.selected' : 'transparent',
                      '&:hover': {
                        backgroundColor: 'action.hover',
                      },
                    }}
                  >
                    <ListItemIcon
                      sx={{
                        minWidth: 0,
                        mr: 3,
                        justifyContent: 'center',
                        color: isActive ? 'primary.main' : 'inherit',
                      }}
                    >
                      <Icon />
                    </ListItemIcon>
                    <ListItemText 
                      primary={item.text}
                      sx={{
                        '& .MuiListItemText-primary': {
                          fontWeight: isActive ? 600 : 400,
                          color: isActive ? 'primary.main' : 'inherit',
                        },
                      }}
                    />
                  </ListItemButton>
                </ListItem>
              );
            })}
          </List>
          
          {/* User Info at Bottom */}
          <Box
            sx={{
              position: 'absolute',
              bottom: 0,
              left: 0,
              right: 0,
              p: 2,
              backgroundColor: 'grey.100',
              borderTop: 1,
              borderColor: 'divider',
            }}
          >
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
              <Avatar sx={{ width: 40, height: 40, mr: 2, bgcolor: 'primary.main' }}>
                {currentUser?.full_name?.charAt(0) || 'U'}
              </Avatar>
              <Box>
                <Typography variant="subtitle2" sx={{ fontWeight: 600 }}>
                  {currentUser?.full_name}
                </Typography>
                <Typography variant="caption" color="textSecondary">
                  {currentUser?.role?.charAt(0).toUpperCase() + currentUser?.role?.slice(1)}
                </Typography>
              </Box>
            </Box>
          </Box>
        </Box>
      </Drawer>
    </>
  );
}

export default Navigation;