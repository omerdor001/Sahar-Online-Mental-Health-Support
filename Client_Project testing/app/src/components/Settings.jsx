import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Box,
  Typography,
  Button,
  Select,
  MenuItem,
  IconButton,
  FormControl,
  InputLabel,
  Switch,
  FormControlLabel,
} from '@mui/material';
import MenuIcon from '@mui/icons-material/Menu';
import SettingsIcon from '@mui/icons-material/Settings';
import ExportIcon from '@mui/icons-material/ExitToApp';
import LogoutIcon from '@mui/icons-material/Logout';
import HomeIcon from '@mui/icons-material/Home';
import HelpOutlineIcon from '@mui/icons-material/HelpOutline';
import { createTheme, ThemeProvider } from '@mui/material/styles';
import { CssBaseline } from '@mui/material';
import PropTypes from 'prop-types';

const theme = createTheme({
  typography: {
    fontFamily: '"Segoe UI", "Helvetica Neue", Arial, sans-serif',
  },
});

function Settings({ handleLogout }) {
  const [notificationTime, setNotificationTime] = useState('600');
  const [isChecked, setIsChecked] = useState(true);
  const [isSidebarOpen, setSidebarOpen] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    const monitorFocusData = localStorage.getItem('monitorFocus');
    if (monitorFocusData) {
      setIsChecked(JSON.parse(monitorFocusData));
    }

    const handleBackgroundMessage = () => {};
    document.addEventListener('resizePopup', handleBackgroundMessage);
    const event = new CustomEvent('resizePopup', {
      detail: { window: 'Settings' },
    });
    document.dispatchEvent(event);

    return () => {
      document.removeEventListener('resizePopup', handleBackgroundMessage);
    };
  }, []);

  const toggleSidebar = () => {
    setSidebarOpen(!isSidebarOpen);
  };

  const goToHomePage = () => {
    navigate('/');
  };

  const goToSettings = () => {
    navigate('/settings');
  };

  const goToConversationsHistory = () => {
    navigate('/conversation-history');
  };

  const goToCommonQuestions = () => {
    navigate('/common-questions');
  };

  const selectNotificationTime = (value) => {
    localStorage.setItem('notificationTime', JSON.stringify(value));
    document.dispatchEvent(new CustomEvent('NotificationTime_UPDATED'));
    setNotificationTime(value);
  };
  

  const handleToggle = (event) => {
    const newValue = event.target.checked;
    setIsChecked(newValue);
    localStorage.setItem('monitorFocus', JSON.stringify(newValue));
    document.dispatchEvent(new CustomEvent('MonitorFocus_UPDATED'));
  };

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Box sx={{ display: 'flex', flexDirection: 'row', height: '100vh', backgroundColor: '#f0f4f8' }}>

        {/* Sidebar Menu */}
        {isSidebarOpen && (
          <Box
            sx={{
              width: 120,
              position: 'fixed',
              top: 0,
              right: 0,
              height: '100vh',
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              pt: 4,
              boxShadow: 3,
              backgroundColor: '#4fa3f7',
              borderRadius: '15px 0 0 15px',
              zIndex: 1000,
              transition: 'transform 0.3s ease',
            }}
          >
            <Typography variant="h6" sx={{ mb: 4, fontWeight: 'bold', color: 'white' }}>
              תפריט
            </Typography>

            <Button
              onClick={goToHomePage}
              sx={{
                mb: 3,
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                gap: 1,
                textTransform: 'none',
                py: 2,
                px: 3,
                borderRadius: 2,
                backgroundColor: 'transparent',
                '&:hover': {
                  backgroundColor: '#0056b3',
                  boxShadow: 2,
                },
              }}
            >
              <HomeIcon sx={{ fontSize: 30, color: 'white' }} />
              <Typography variant="body2" sx={{ color: 'white' }}>
                דף בית
              </Typography>
            </Button>

            <Button
              onClick={goToSettings}
              sx={{
                mb: 3,
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                gap: 1,
                textTransform: 'none',
                py: 2,
                px: 3,
                borderRadius: 2,
                backgroundColor: 'transparent',
                '&:hover': {
                  backgroundColor: '#0056b3',
                  boxShadow: 2,
                },
              }}
            >
              <SettingsIcon sx={{ fontSize: 30, color: 'white' }} />
              <Typography variant="body2" sx={{ color: 'white' }}>
                הגדרות
              </Typography>
            </Button>

            <Button
              onClick={goToConversationsHistory}
              sx={{
                mb: 3,
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                gap: 1,
                textTransform: 'none',
                py: 2,
                px: 3,
                borderRadius: 2,
                backgroundColor: 'transparent',
                '&:hover': {
                  backgroundColor: '#0056b3',
                  boxShadow: 2,
                },
              }}
            >
              <ExportIcon sx={{ fontSize: 30, color: 'white' }} />
              <Typography variant="body2" sx={{ color: 'white' }}>
                היסטוריית שיחות
              </Typography>
            </Button>

            <Button
              onClick={goToCommonQuestions}
              sx={{
                mb: 3,
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                gap: 1,
                textTransform: 'none',
                py: 2,
                px: 3,
                borderRadius: 2,
                backgroundColor: 'transparent',
                '&:hover': {
                  backgroundColor: '#0056b3',
                  boxShadow: 2,
                },
              }}
            >
              <HelpOutlineIcon sx={{ fontSize: 30, color: 'white' }} />
              <Typography variant="body2" sx={{ color: 'white' }}>
                שאלות נפוצות
              </Typography>
            </Button>

            <Button
              onClick={() => {
                if (typeof handleLogout === 'function') {
                  handleLogout();
                }
              }}
              sx={{
                mb: 3,
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                gap: 1,
                textTransform: 'none',
                py: 2,
                px: 3,
                borderRadius: 2,
                backgroundColor: '#66aaff',
                '&:hover': {
                  backgroundColor: '#3381d6',
                  boxShadow: 2,
                },
              }}
            >
              <LogoutIcon sx={{ fontSize: 30, color: 'white' }} />
              <Typography variant="body2" sx={{ color: 'white' }}>
                התנתק
              </Typography>
            </Button>
          </Box>
        )}

        {/* Toggle Button */}
        <IconButton
          onClick={toggleSidebar}
          sx={{
            position: 'fixed',
            top: 16,
            right: isSidebarOpen ? 140 : 16,
            zIndex: 1100,
            backgroundColor: '#4fa3f7',
            color: 'white',
            '&:hover': {
              backgroundColor: '#3381d6',
            },
          }}
        >
          <MenuIcon />
        </IconButton>

        {/* Main Content */}
        <Box
          sx={{
            mr: 12,
            flexGrow: 1,
            p: 4,
            overflowY: 'auto',
            backgroundColor: '#ffffff',
            borderRadius: 2,
            boxShadow: 3,
            marginRight: isSidebarOpen ? 12 : 2
          }}
        >
          {/* Header */}
          <Box
            sx={{
              display: 'flex',
              justifyContent: 'center',
              alignItems: 'center',
              p: 2,
              borderRadius: 1,
              mb: 3,
            }}
          >
            <Typography
            variant="h4"
            sx={{
              textAlign: 'center',
              fontWeight: 'bold',
              color: 'white',
              mt: 6,
              mb: 3,
              direction: 'rtl',
              backgroundColor: '#4fa3f7',
              display: 'flex',
              justifyContent: 'center',
              alignItems: 'center',
              width: 'auto',
              ml: { xs: 0, md: -15 },
              flexGrow: 1,
              borderRadius: 3,
              p: 2,
            }}
          >
            הגדרות
          </Typography>
          </Box>

          {/* Settings Content */}
          <Box
            sx={{
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              gap: 4,
              maxWidth: 600,
              mx: 'auto',
              p: 4,
              backgroundColor: '#f8fafc',
              borderRadius: 3,
              boxShadow: 1,
            }}
          >
            {/* Notification Time Setting */}
            <FormControl fullWidth sx={{ maxWidth: 400 }} dir="rtl">
  <InputLabel
    id="notification-time-label"
    sx={{
      right: 14,
      left: 'auto',
      transformOrigin: 'right',
      '&.MuiInputLabel-shrink': {
        transform: 'translate(0, -9px) scale(0.75)',
      }
    }}
  >
    הגדרת תדירות התרעות
  </InputLabel>
  <Select
    labelId="notification-time-label"
    value={notificationTime}
    onChange={(e) => selectNotificationTime(e.target.value)}
    label="הגדרת תדירות התרעות"
    sx={{
      '& .MuiSelect-select': {
        textAlign: 'right',
        paddingRight: '14px',
      },
      '& .MuiOutlinedInput-notchedOutline': {
        textAlign: 'right',
      },
    }}
    MenuProps={{
      anchorOrigin: {
        vertical: 'bottom',
        horizontal: 'right'
      },
      transformOrigin: {
        vertical: 'top',
        horizontal: 'right'
      },
      PaperProps: {
        sx: {
          '& .MuiMenuItem-root': {
            textAlign: 'right',
            justifyContent: 'flex-end',
          }
        }
      }
    }}
  >
    <MenuItem value="1">דקה</MenuItem>
    <MenuItem value="3">3 דקות</MenuItem>
    <MenuItem value="5">5 דקות</MenuItem>
    <MenuItem value="10">10 דקות</MenuItem>
    <MenuItem value="15">15 דקות</MenuItem>
    <MenuItem value="30">30 דקות</MenuItem>
    <MenuItem value="45">45 דקות</MenuItem>
    <MenuItem value="60">60 דקות</MenuItem>
  </Select>
</FormControl>

            {/* Monitor Focus Toggle */}
            <FormControlLabel
              control={
                <Switch
                  checked={isChecked}
                  onChange={handleToggle}
                  color="primary"
                />
              }
              label="הצמד חלון למסך"
              labelPlacement="start"
              sx={{
                mr: 0,
                '& .MuiFormControlLabel-label': {
                  fontWeight: 500,
                },
              }}
            />
          </Box>
        </Box>
      </Box>
    </ThemeProvider>
  );
}

Settings.propTypes = {
  handleLogout: PropTypes.func.isRequired, 
};

export default Settings;


