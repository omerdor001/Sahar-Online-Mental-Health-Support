import { useState, useEffect } from 'react';
import { TextField, Button, Radio, FormControlLabel, CircularProgress, Typography, Box, IconButton } from '@mui/material';
import { AccountCircle, Lock, Person } from '@mui/icons-material';
import { createTheme, ThemeProvider } from '@mui/material/styles';
import { CssBaseline } from '@mui/material';
import PropTypes from 'prop-types';


const theme = createTheme({
  typography: {
    fontFamily: '"Segoe UI", "Helvetica Neue", Arial, sans-serif', 
  },
});

function Login({ handleLogin,errorMessage }) {
  const [accountNumber, setAccountNumber] = useState('');
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [role, setRole] = useState('');
  const [loadIcon, setLoadIcon] = useState(false);

  useEffect(() => {
    const handleBackgroundMessage = (event) => {
      if (event.detail.window === 'login') {
        console.log('Login window resized');
      }
    };
    document.addEventListener('resizePopup', handleBackgroundMessage);
    const event = new CustomEvent('resizePopup', {
      detail: { window: 'login' },
    });
    document.dispatchEvent(event);
    return () => {
      document.removeEventListener('resizePopup', handleBackgroundMessage);
    };
  }, []);

  const handleInputChange = (setter) => (event) => {
    setter(event.target.value);
  };

  const onSubmit = (event) => {
    event.preventDefault();
    setLoadIcon(true);
    handleLogin(accountNumber, username, password, role,setLoadIcon);
  };

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
    <div style={{
      display: 'flex', 
      justifyContent: 'center', 
      alignItems: 'center', 
      height: '100vh', 
      backgroundColor: '#F0F4F8', 
      fontFamily: "'Roboto', sans-serif"
    }}>
      <div style={{
        width: '380px', 
        padding: '30px', 
        backgroundColor: 'white', 
        borderRadius: '30px', 
        boxShadow: '0 10px 30px rgba(0, 0, 0, 0.1)',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center'
      }}>
        <Typography variant="h4" style={{
          fontWeight: '600', 
          marginBottom: '20px', 
          color: '#333', 
          textAlign: 'center',
          borderRadius: '30px'
        }}>
          התחברות
       </Typography>
        
        <form onSubmit={onSubmit} style={{ width: '100%' }}>
          <TextField
            label="מספר חשבון"
            variant="outlined"
            style={{
              marginBottom: '16px', 
              width: '100%', 
              borderRadius: '8px', 
              padding: '12px'
            }}
            dir="rtl"
            value={accountNumber}
            onChange={handleInputChange(setAccountNumber)}
            disabled={loadIcon}
            InputProps={{
              startAdornment: (
                <IconButton>
                  <AccountCircle style={{ color: '#1976d2' }} />
                </IconButton>
              ),
            }}
          />
          
          <TextField
            label="שם משתמש"
            variant="outlined"
            style={{
              marginBottom: '16px', 
              width: '100%', 
              borderRadius: '8px', 
              padding: '12px'
            }}
            dir="rtl"
            value={username}
            onChange={handleInputChange(setUsername)}
            disabled={loadIcon}
            InputProps={{
              startAdornment: (
                <IconButton>
                  <Person style={{ color: '#1976d2' }} />
                </IconButton>
              ),
            }}
          />
          
          <TextField
            label="סיסמא"
            variant="outlined"
            style={{
              marginBottom: '16px', 
              width: '100%', 
              borderRadius: '8px', 
              padding: '12px'
            }}
            dir="rtl"
            type="password"
            value={password}
            onChange={handleInputChange(setPassword)}
            disabled={loadIcon}
            InputProps={{
              startAdornment: (
                <IconButton>
                  <Lock style={{ color: '#1976d2' }} />
                </IconButton>
              ),
            }}
          />

          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '20px' }}>
            <FormControlLabel
              value="driver"
              control={<Radio />}
              label="כונן/ית"
              checked={role === 'driver'}
              onChange={(e) => setRole(e.target.value)}
            />
            <FormControlLabel
              value="assistant"
              control={<Radio />}
              label="סייע/ת"
              checked={role === 'assistant'}
              onChange={(e) => setRole(e.target.value)}
            />
          </div>

           {/* Display the error message */}
           {errorMessage && (
              <Typography style={{
                color: '#d32f2f', 
                marginBottom: '16px', 
                textAlign: 'center', 
                fontWeight: '500'
              }}>
                {errorMessage}
              </Typography>
            )}

          <Button
            type="submit"
            variant="contained"
            style={{
              width: '100%', 
              backgroundColor: '#1976d2', 
              color: 'white', 
              fontWeight: '600', 
              padding: '12px', 
              borderRadius: '8px',
              '&:hover': { backgroundColor: '#1565c0' }
            }}
            disabled={loadIcon}
          >
            התחברות
          </Button>

          {loadIcon && (
            <Box style={{ display: 'flex', justifyContent: 'center', marginTop: '20px' }}>
              <CircularProgress />
            </Box>
          )}
        </form>
      </div>
    </div>
    </ThemeProvider>
  );
}

Login.propTypes = {
  handleLogin: PropTypes.func.isRequired, 
  errorMessage: PropTypes.func.isRequired,
};

export default Login;
