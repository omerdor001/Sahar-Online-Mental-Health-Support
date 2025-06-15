import { useState } from 'react';
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
  const [isSidebarOpen, setSidebarOpen] = useState(false);
  const navigate = useNavigate();

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
    if(value == 0){
      localStorage.setItem('notificationTime', JSON.stringify(9999999999999));
      localStorage.setItem("lastAlertTime",0);
    }
    else{
      localStorage.setItem('notificationTime', value);
    }
    document.dispatchEvent(new CustomEvent('NotificationTime_UPDATED'));
    setNotificationTime(value);
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
        {/* Sidebar Menu */}
        {isSidebarOpen && (
                     <Box
                       sx={{
                         width: { xs: '100%', md: 120 },
                         position: { xs: 'relative', md: 'fixed' },
                         top: 0,
                         right: 0,
                         height: { xs: 'auto', md: '100vh' },
                         overflowY: 'auto',
                         display: 'flex',
                         flexDirection: { xs: 'row', md: 'column' },
                         alignItems: 'center',
                         justifyContent: { xs: 'space-around', md: 'flex-start' },
                         pt: { xs: 2, md: 4 },
                         pb: { xs: 2, md: 0 },
                         boxShadow: 3,
                         backgroundColor: '#4fa3f7',
                         borderRadius: { xs: 0, md: '15px 0 0 15px' },
                         zIndex: 1000,
                         transition: 'transform 0.3s ease',
                       }}
                     >
                       {/* Sidebar buttons */}
                       {[ 
                         { icon: <HomeIcon sx={{ fontSize: { xs: 24, md: 30 }, color: 'white' }} />, text: 'דף בית', onClick: goToHomePage },
                         { icon: <SettingsIcon sx={{ fontSize: { xs: 24, md: 30 }, color: 'white' }} />, text: 'הגדרות', onClick: goToSettings },
                         { icon: <ExportIcon sx={{ fontSize: { xs: 24, md: 30 }, color: 'white' }} />, text: 'היסטוריית שיחות', onClick: goToConversationsHistory },
                         { icon: <HelpOutlineIcon sx={{ fontSize: { xs: 24, md: 30 }, color: 'white' }} />, text: 'שאלות נפוצות', onClick: goToCommonQuestions },
                       ].map((item, index) => (
                         <Button
                           key={index}
                           onClick={item.onClick}
                           sx={{
                             mb: { xs: 0, md: 3 },
                             display: 'flex',
                             flexDirection: 'column',
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
                           }}
                         >
                           {item.icon}
                           <Typography variant="body2" sx={{ 
                             color: 'white',
                             fontSize: { xs: '0.7rem', md: '0.875rem' }
                           }}>
                             {item.text}
                           </Typography>
                         </Button>
                       ))}
             
                       {/* Logout button */}
                       <Button
                         onClick={() => typeof handleLogout === 'function' && handleLogout()}
                         sx={{
                           mb: { xs: 0, md: 3 },
                           display: 'flex',
                           flexDirection: 'column',
                           alignItems: 'center',
                           gap: { xs: 0.5, md: 1 },
                           textTransform: 'none',
                           py: { xs: 0.5, md: 1 },
                           px: { xs: 1, md: 2 },
                           borderRadius: 2,
                           backgroundColor: '#66aaff',
                           '&:hover': {
                             backgroundColor: '#3381d6',
                             boxShadow: 2,
                           },
                         }}
                       >
                         <LogoutIcon sx={{ fontSize: { xs: 24, md: 30 }, color: 'white' }} />
                         <Typography variant="body2" sx={{ 
                           color: 'white',
                           fontSize: { xs: '0.7rem', md: '0.875rem' }
                         }}>
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
            mt: { xs: 2, md: 4 },
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
              mb: 1,
            }}
          >
           <Typography
  variant="h4"
  sx={{
    width: '100%',             
    textAlign: 'center',
    fontWeight: 'bold',
    color: 'white',
    mt: { xs: 0, md: 2 }, 
    mb: 2,
    direction: 'rtl',
    bgcolor: '#4fa3f7',        
    borderRadius: '12px',       
    p: 2,                        
    fontSize: { xs: '1.3rem', sm: '1.5rem', md: '1.75rem' },
    mx: { xs: 2, sm: 4, md: 8 }, 
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
              maxWidth: 600,
              mx: 'auto',
              p: 2,
              pt: 1,
              backgroundColor: '#f8fafc',
              borderRadius: 3,
              boxShadow: 1,
            }}
          >
            {/* Notification Time */}
            <FormControl fullWidth sx={{ maxWidth: 400, mt: 1 }} dir="rtl">
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
                <MenuItem value="1">דקה אחת</MenuItem>
<MenuItem value="3">שלוש דקות</MenuItem>
<MenuItem value="5">חמש דקות</MenuItem>
<MenuItem value="10">עשר דקות</MenuItem>
<MenuItem value="0">ביטול</MenuItem>
              </Select>
            </FormControl>
          </Box>
        </Box>
      </Box>
    </ThemeProvider>
  );
  } 

  
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


