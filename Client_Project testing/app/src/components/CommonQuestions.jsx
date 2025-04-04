import { useState } from 'react';
import {
  Box,
  Typography,
  Button,
  Stack,
  IconButton,
} from '@mui/material';
import MenuIcon from '@mui/icons-material/Menu';
import HomeIcon from '@mui/icons-material/Home';
import SettingsIcon from '@mui/icons-material/Settings';
import ExportIcon from '@mui/icons-material/ExitToApp';
import HelpOutlineIcon from '@mui/icons-material/HelpOutline';
import LogoutIcon from '@mui/icons-material/Logout';
import { useNavigate } from 'react-router-dom';
import { createTheme, ThemeProvider } from '@mui/material/styles';
import { CssBaseline } from '@mui/material';
import PropTypes from 'prop-types';

const theme = createTheme({
  typography: {
    fontFamily: '"Segoe UI", "Helvetica Neue", Arial, sans-serif', 
  },
});

function CommonQuestions({ handleLogout }) {
  const navigate = useNavigate();
  const [isSidebarOpen, setSidebarOpen] = useState(false);
  const faqs = [
    {
      question: 'לאחר ההתחברות, מהו משך הזמן עד שנדרשת התחברות חדשה?',
      answer: '24 שעות.',
    },
    {
      question: 'כל כמה זמן התוסף מעדכן את המידע על השיחות?',
      answer: 'כל 5 שניות.',
    },
    {
      question: 'מתי ולמה קופצת התראה?',
      answer: 'התראה תקפוץ על שיחה עם אחוז אובדנות גבוה מ- 80%. ניתן להגדיר בדף הגדרות -> הגדרת תדירות התרעות , אחרי כמה דקות תקפוץ התראה חוזרת על אותה השיחה.',
    },
    {
      question: 'כמה זמן שיחה נשארת בהיסטוריית שיחות?',
      answer: '28 ימים.',
    },
    {
      question: 'האם יש להשאיר את התוסף פתוח על מנת למשוך את השיחות?',
      answer: 'אין צורך. כל עוד הדפדפן (גוגל כרום) פתוח, התוסף מתעדכן ברקע ובמידה ותתגלה שיחה עם מעל 80 אחוז אובדנות, תופיע התראה על כך.',
    },
    {
      question: 'האם חייב חיבור אינטרנטי פעיל בכדי שהתוסף יעבוד?',
      answer: 'כן, ללא אינטרנט התוסף לא יוכל למשוך נתונים מהשרת.',
    },
    {
      question: 'האם לאחר ההתחברות לתוסף וסגירה של הדפדפן יש צורך להתחבר מחדש?',
      answer: 'אין צורך להתחבר מחדש. כמו כן, ברגע שהדפדפן נפתח התוסף מתחיל למשוך שיחות מהשרת כל 5 שניות.',
    },
    {
      question: 'מהם פרטי ההתחברות לתוסף?',
      answer: 'פרטי ההתחברות זהים לפרטי ההתחברות של LivePerson.',
    },
    {
      question: 'האם השיחות מסודרות בסדר ממוין?',
      answer: 'כן, שיחות של המתנדב המחובר יופיעו לפני שאר השיחות ושיחות אחרות, לפי ה GSR שלהן.',
    },
  ];

  const goToConversationsHistory = () => {
    navigate('/conversation-history');
  };

  const goToSettings = () => {
    navigate('/settings');
  };

  const goToCommonQuestions = () => {
    navigate('/common-questions');
  };

  const goToHomePage = () => {
    navigate('/');
  };

  const toggleSidebar = () => {
    setSidebarOpen(!isSidebarOpen);
  };

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Box
        sx={{
          display: 'flex',
          height: '100vh',
          direction: 'rtl',
          bgcolor: '#f0f8ff',
        }}
      >
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
    }}}
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
            right: isSidebarOpen ? 140 : 16, // Adjust position based on sidebar state
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

        {/* FAQ Section */}
        <Box
          sx={{
            flexGrow: 1,
            ml: 0,
            mr: isSidebarOpen ? '130px' : 0, // Adjust margin based on sidebar state
            p: 3,
            overflowY: 'auto',
            backgroundColor: '#f0f8ff',
            zIndex: 1,
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
            שאלות נפוצות
          </Typography>

          <Stack spacing={4}>
            {faqs.map((faq, index) => {
              let backgroundColor = index % 2 === 0 ? '#f1f8ff' : '#e3f2fd';
              return (
                <Box
                  key={index}
                  sx={{
                    p: 3,
                    borderRadius: 2,
                    backgroundColor,
                    boxShadow: 1,
                    '&:hover': {
                      boxShadow: 3,
                      cursor: 'pointer',
                    },
                    borderBottom: '1px solid #ddd',
                    mr: 5,
                  }}
                >
                  <Typography
                    variant="body1"
                    sx={{ fontWeight: 'bold', mb: 1, color: '#1976d2' }}
                  >
                    {faq.question}
                  </Typography>
                  <Typography variant="body2" sx={{ color: '#555' }}>
                    {faq.answer}
                  </Typography>
                </Box>
              );
            })}
          </Stack>
        </Box>
      </Box>
    </ThemeProvider>
  );
}

CommonQuestions.propTypes = {
  handleLogout: PropTypes.func.isRequired, 
};

export default CommonQuestions;
