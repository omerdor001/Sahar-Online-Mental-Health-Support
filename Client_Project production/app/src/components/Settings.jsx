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
      <Box
        sx={{
          display: 'flex',
          flexDirection: { xs: 'column', md: 'row' },
          height: '100vh',
          backgroundColor: '#f0f4f8',
          overflow: 'hidden',
          direction: 'rtl',
        }}
      >
        {/* Sidebar */}
        {isSidebarOpen && (
          <Box
            sx={{
              width: { xs: '100%', md: 120 },
              position: { xs: 'relative', md: 'fixed' },
              top: 0,
              right: 0,
              height: { xs: 'auto', md: '100vh' },
              display: 'flex',
              flexDirection: { xs: 'row-reverse', md: 'column' }, 
              alignItems: 'center',
              justifyContent: { xs: 'space-between', md: 'flex-start' },
              py: { xs: 1, md: 4 },
              backgroundColor: '#4fa3f7',
              boxShadow: 3,
              borderRadius: { xs: 0, md: '15px 0 0 15px' },
              zIndex: 1000,
            }}
          >
            {/* Home Button */}
            <Button
              onClick={goToHomePage}
              sx={{
                ...buttonStyles,
                flexDirection: { xs: 'row-reverse', md: 'column' }, 
              }}
            >
              <HomeIcon sx={iconStyles} />
              <Typography sx={textStyles}>דף בית</Typography>
            </Button>
  
            {/* Other buttons */}
            {[ 
              { icon: <SettingsIcon sx={iconStyles} />, text: 'הגדרות', onClick: goToSettings },
              { icon: <ExportIcon sx={iconStyles} />, text: 'היסטוריית שיחות', onClick: goToConversationsHistory },
              { icon: <HelpOutlineIcon sx={iconStyles} />, text: 'שאלות נפוצות', onClick: goToCommonQuestions },
            ].map((item, index) => (
              <Button
                key={index}
                onClick={item.onClick}
                sx={{
                  ...buttonStyles,
                  flexDirection: { xs: 'row-reverse', md: 'column' }, 
                }}
              >
                {item.icon}
                <Typography sx={textStyles}>{item.text}</Typography>
              </Button>
            ))}
  
            {/* Logout Button */}
            <Button
              onClick={() => typeof handleLogout === 'function' && handleLogout()}
              sx={{
                ...buttonStyles,
                flexDirection: { xs: 'row-reverse', md: 'column' },
                backgroundColor: '#66aaff',
                '&:hover': {
                  backgroundColor: '#3381d6',
                },
              }}
            >
              <LogoutIcon sx={iconStyles} />
              <Typography sx={textStyles}>התנתק</Typography>
            </Button>
          </Box>
        )}
  
        {/* Toggle Button */}
        <IconButton
                     onClick={toggleSidebar}
                     sx={{
                       position: 'fixed',
                       top: 16,
                       right: isSidebarOpen ? { xs: 16, md: 140 } : 16,
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
            flexGrow: 1,
            p: 2,
            overflowY: 'auto',
            backgroundColor: '#ffffff',
            borderRadius: 2,
            boxShadow: 3,
            mx: { xs: 2, md: 4 },
            mb: { xs: 2, md: 4 },
            marginRight: { xs: 0, md: isSidebarOpen ? 15 : 0 },
            transition: 'margin-right 0.3s ease',
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
                backgroundColor: '#4fa3f7',
                width: { xs: '100%', md: 'auto' },
                borderRadius: 3,
                p: 2,
                direction: 'rtl',
                fontSize: { xs: '1.5rem', md: '2rem' },
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
              p: 2,
              backgroundColor: '#f8fafc',
              borderRadius: 3,
              boxShadow: 1,
            }}
          >
            {/* Notification Time */}
            <FormControl fullWidth sx={{ maxWidth: 400 }} dir="rtl">
              <InputLabel id="notification-time-label" sx={inputLabelStyles}>
                הגדרת תדירות התרעות
              </InputLabel>
              <Select
                labelId="notification-time-label"
                value={notificationTime}
                onChange={(e) => selectNotificationTime(e.target.value)}
                label="הגדרת תדירות התרעות"
                sx={selectStyles}
                MenuProps={menuProps}
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
                '& .MuiFormControlLabel-label': { fontWeight: 500 },
              }}
            />
          </Box>
        </Box>
      </Box>
    </ThemeProvider>
  );
  
  } 
  
  const buttonStyles = {
    mb: { xs: 0, md: 3 },
    display: 'flex',
    alignItems: 'center',
    gap: { xs: 0.5, md: 1 },
    textTransform: 'none',
    py: { xs: 0.5, md: 1 },
    px: { xs: 1, md: 2 },
    borderRadius: 2,
    backgroundColor: 'transparent',
    '&:hover': {
      backgroundColor: '#0056b3',
      boxShadow: 2,
    },
  };
  
  const iconStyles = {
    fontSize: { xs: 24, md: 30 },
    color: 'white',
  };
  
  const textStyles = {
    color: 'white',
    fontSize: { xs: '0.7rem', md: '0.875rem' },
  };
  
  const inputLabelStyles = {
    right: 14,
    left: 'auto',
    transformOrigin: 'right',
    '&.MuiInputLabel-shrink': {
      transform: 'translate(0, -9px) scale(0.75)',
    },
  };
  
  const selectStyles = {
    '& .MuiSelect-select': {
      textAlign: 'right',
      paddingRight: '14px',
    },
  };
  
  const menuProps = {
    anchorOrigin: { vertical: 'bottom', horizontal: 'right' },
    transformOrigin: { vertical: 'top', horizontal: 'right' },
    PaperProps: {
      sx: {
        '& .MuiMenuItem-root': {
          textAlign: 'right',
          justifyContent: 'flex-end',
        },
      },
    },
  };

Settings.propTypes = {
  handleLogout: PropTypes.func.isRequired, 
};

export default Settings;


