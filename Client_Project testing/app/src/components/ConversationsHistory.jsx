import { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Button,
  TextField,
  IconButton,
  Stack,
  Modal,
  CssBaseline,
  FormControl,
  InputLabel,
  Select,
  MenuItem
} from '@mui/material';
import MenuIcon from '@mui/icons-material/Menu';
import SettingsIcon from '@mui/icons-material/Settings';
import ExportIcon from '@mui/icons-material/ExitToApp';
import LogoutIcon from '@mui/icons-material/Logout';
import HomeIcon from '@mui/icons-material/Home';
import HelpOutlineIcon from '@mui/icons-material/HelpOutline';
import { useNavigate } from 'react-router-dom';
import { createTheme, ThemeProvider } from '@mui/material/styles';
import { fetchConversationsHistory } from '../http.js';
import PropTypes from 'prop-types';

const theme = createTheme({
  typography: {
    fontFamily: '"Segoe UI", "Helvetica Neue", Arial, sans-serif',
  },
});

function ConversationsHistory({ handleLogout }) {
  const navigate = useNavigate();
  const [searchQuery, setSearchQuery] = useState('');
  const [filteredConversations, setFilteredConversations] = useState([]);
  const [selectedConversation, setSelectedConversation] = useState(null);
  const [modalOpen, setModalOpen] = useState(false);
  const [isSidebarOpen, setSidebarOpen] = useState(false);
  const [historicalConversations,setHistoricalConversations] = useState([]);
  const [timeFilter, setTimeFilter] = useState('1hour');

  const getTimeFilterValue = () => {
    switch (timeFilter) {
      case '15min':
        return 15;
      case '30min':
        return 30;
      case '1hour':
        return 60; 
      case '2hours':
        return 2 * 60 ; 
      case '4hours':
        return 4 * 60; 
      default:
        return null; 
    }
  };

    useEffect(() => {
      const preventPrint = (e) => {
        e.preventDefault();
        return false;
      };
      const originalPrint = window.print;
      window.print = () => {
        console.log('Print prevented');
        return false;
      };
      window.addEventListener('beforeprint', preventPrint);
      return () => {
        window.removeEventListener('beforeprint', preventPrint);
        window.print = originalPrint;
      };
    }, []);

  function getBackgroundColor(FEGSR) {
    let hue = 120;
    let saturation = 50;
    let lightness = 70;
    if (FEGSR < 0.5) {
      hue = 120;
      lightness = 70 + FEGSR * 15;
    } else if (FEGSR >= 0.5 && FEGSR < 0.8) {
      hue = 60 + Math.pow(FEGSR - 0.5, 2) * 60;
      saturation = 50;
      lightness = 70 + (FEGSR - 0.5) * 10;
    } else {
      hue = 0;
      saturation = 50;
      lightness = 65 + (1 - FEGSR) * 15;
    }
    return `hsl(${hue}, ${saturation}%, ${lightness}%)`;
  }

  const handleSelectConversation = (conversation) => {
    setSelectedConversation(conversation);
    setModalOpen(true);
  };

  const handleCloseModal = () => {
    setSelectedConversation(null);
    setModalOpen(false);
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

  const goToHomePage = () => {
    navigate('/');
  };

  const toggleSidebar = () => {
    setSidebarOpen(!isSidebarOpen);
  };

  const handleTimeFilterChange = (event) => {
    const newTimeFilter = event.target.value;
    setTimeFilter(newTimeFilter);
  };

  const fetchConversationsWithTimeFilter = () => {
    const timeValue = getTimeFilterValue();
    console.log(`Fetching conversations with time value: ${timeValue} minutes`);
    fetchConversationsHistory(navigate, setHistoricalConversations, handleLogout, timeValue);
    console.log(historicalConversations);
  };

  useEffect(() => {
    fetchConversationsWithTimeFilter();
  }, [timeFilter]);

  useEffect(() => {
    const filtered = historicalConversations.filter(conversation =>
      conversation.consumerParticipants.consumerName.toLowerCase().includes(searchQuery.toLowerCase()) ||
      conversation.latestAgentFullName.toLowerCase().includes(searchQuery.toLowerCase()) ||
      conversation.conversationId.toLowerCase().includes(searchQuery.toLowerCase())
    );
    const updatedFiltered = filtered.map(conversation => ({
      ...conversation,
      FEGSR: conversation.GSR ? conversation.GSR * 100 : 0,
      FEIMSR: 0,
    }));
    setFilteredConversations(updatedFiltered);
  }, [searchQuery, historicalConversations]);

  let conversations = [...filteredConversations];
  
  conversations = conversations.sort((a, b) => {
    return b.GSR - a.GSR;
  });

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <>
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
              mt: 1,
              mb: 0,
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
            היסטוריית שיחות
          </Typography>
            </Box>

            {/* Filter Time Container */}
<Box 
  sx={{ 
    display: 'flex', 
    justifyContent: 'flex-end', 
    alignItems: 'center', 
    mb: 3, 
    flexDirection: { xs: 'column', sm: 'row' }, 
    width: '100%' 
  }}
>
  <FormControl 
    variant="outlined" 
    size="small" 
    sx={{ 
      minWidth: 200, 
      mb: { xs: 2, sm: 0 }, 
      ml: 'auto' 
    }}
  >
    <InputLabel id="time-filter-label">הצג שיחות שהתרחשו עד לפני</InputLabel>
    <Select
      labelId="time-filter-label"
      id="time-filter"
      value={timeFilter}
      onChange={handleTimeFilterChange}
      label="הצג שיחות שהתרחשו עד לפני"
    >
      <MenuItem value="15min">15 דקות אחרונות</MenuItem>
      <MenuItem value="30min">30 דקות אחרונות</MenuItem>
      <MenuItem value="1hour">שעה אחרונה</MenuItem>
      <MenuItem value="2hours">שעתיים אחרונות</MenuItem>
      <MenuItem value="4hours">4 שעות אחרונות</MenuItem>
    </Select>
  </FormControl>
</Box>

            {/* Search Input */}
            <Box sx={{ display: 'flex', justifyContent: 'flex-end', mb: 3 }}>
              <TextField
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="חפש לפי כינוי, שם הסייע/ת או מזהה שיחה"
                variant="outlined"
                size="small"
                sx={{ width: 350 }}
              />
            </Box>

            {/* Conversations List */}
            <Box sx={{ overflowY: 'auto', minWidth: '25vw' }}>
              <Stack spacing={1.5}>
                {/* Header Row */}
                <Box sx={{ p: 2, borderRadius: 2, backgroundColor: '#f1f8ff', width: '100%' }}>
                  <Stack direction="row" justifyContent="space-between" alignItems="center">
                    <Box sx={{ flex: 1, minWidth: 30, textAlign: 'center' }}>
                      <Typography variant="body1" sx={{ fontWeight: 'bold', m: 0 }}>אחוז גלובלי</Typography>
                    </Box>
                    <Box sx={{ flex: 1, minWidth: 30, textAlign: 'center' }}>
                      <Typography variant="body1" sx={{ fontWeight: 'bold', m: 0 }}>כינוי</Typography>
                    </Box>
                    <Box sx={{ flex: 1, minWidth: 30, textAlign: 'center' }}>
                      <Typography variant="body1" sx={{ fontWeight: 'bold', m: 0 }}>שם הסייעת</Typography>
                    </Box>
                    <Box sx={{ flex: 1, minWidth: 30, textAlign: 'center' }}>
                      <Typography variant="body1" sx={{ fontWeight: 'bold', m: 0 }}>מזהה שיחה</Typography>
                    </Box>
                  </Stack>
                </Box>

                {/* Conversations */}
                {conversations.map((conversation, index) => {
                  let backgroundColor = getBackgroundColor(conversation.GSR);

                  return (
                    <Box
                      key={index}
                      sx={{
                        p: 2,
                        borderRadius: 2,
                        background: backgroundColor,
                        boxShadow: 1,
                        '&:hover': {
                          boxShadow: 3,
                          cursor: 'pointer',
                        },
                        borderBottom: '1px solid #ddd',
                        width: '100%',
                      }}
                      onClick={() => handleSelectConversation(conversation)}
                    >
                      <Stack direction="row" justifyContent="space-between" alignItems="center">
                        <Box sx={{ flex: 1, minWidth: 30, textAlign: 'center' }}>
                        <Typography variant="body2" sx={{ m: 0 }}>
                            {Number(conversation.FEGSR).toPrecision(4)}%
                        </Typography>
                        </Box>
                        <Box sx={{ flex: 1, minWidth: 30, textAlign: 'center' }}>
                          <Typography variant="body2" sx={{ m: 0 }}>{conversation.consumerParticipants.consumerName}</Typography>
                        </Box>
                        <Box sx={{ flex: 1, minWidth: 30, textAlign: 'center' }}>
                          <Typography variant="body2" sx={{ m: 0 }}>{conversation.latestAgentFullName}</Typography>
                        </Box>
                        <Box sx={{ flex: 1, minWidth: 30, textAlign: 'center' }}>
                          <Typography variant="body2" sx={{ m: 0 }}>{conversation.conversationId}</Typography>
                        </Box>
                      </Stack>
                    </Box>
                  );
                })}
              </Stack>
            </Box>

            {/* Modal for Conversation Details */}
            <Modal open={modalOpen} onClose={handleCloseModal}>
              <Box
                sx={{
                  position: 'absolute',
                  top: '50%',
                  left: '50%',
                  transform: 'translate(-50%, -50%)',
                  width: 350,
                  maxHeight: '60vh',
                  bgcolor: 'background.paper',
                  border: '2px solid #1976d2',
                  boxShadow: 24,
                  p: 3,
                  borderRadius: 2,
                  overflow: 'auto',
                  display: 'flex',
                  flexDirection: 'column',
                  alignItems: 'flex-start',
                  textAlign: 'right',
                }}
              >
                {selectedConversation ? (
                  <>
                    <Typography
                      variant="h5"
                      sx={{
                        fontWeight: 'bold',
                        color: '#1976d2',
                        textAlign: 'center',
                        width: '100%',
                      }}
                    >
                      פרטי שיחה
                    </Typography>

                    <Box sx={{ mb: 2, width: '100%' }}>
                      <Typography variant="body2" sx={{ fontWeight: 'bold', color: '#333' }}>
                        מזהה שיחה
                      </Typography>
                      <Typography variant="body2" sx={{ color: '#555' }}>
                        {selectedConversation.conversationId}
                      </Typography>
                    </Box>

                    <Box sx={{ mb: 2, width: '100%' }}>
                      <Typography variant="body2" sx={{ fontWeight: 'bold', color: '#333' }}>
                        כינוי
                      </Typography>
                      <Typography variant="body2" sx={{ color: '#555' }}>
                        {selectedConversation.consumerParticipants.consumerName}
                      </Typography>
                    </Box>

                    <Box sx={{ mb: 2, width: '100%' }}>
                      <Typography variant="body2" sx={{ fontWeight: 'bold', color: '#333' }}>
                        שם הסייע/ת
                      </Typography>
                      <Typography variant="body2" sx={{ color: '#555' }}>
                        {selectedConversation.latestAgentFullName}
                      </Typography>
                    </Box>

                    <Box sx={{ mb: 2, width: '100%' }}>
                      <Typography variant="body2" sx={{ fontWeight: 'bold', color: '#333' }}>
                        קטגוריה
                      </Typography>
                      <Typography variant="body2" sx={{ color: '#555' }}>
                        {"אין קטגוריה זמינה לשיחה זו."}
                      </Typography>
                    </Box>

                    <Box sx={{ mb: 2, width: '100%' }}>
                      <Typography variant="body2" sx={{ fontWeight: 'bold', color: '#333' }}>
                        משפטי הסבר
                      </Typography>
                      <Typography variant="body2" sx={{ color: '#555', whiteSpace: 'pre-line' }}>
                        {"אין משפטים זמינים לשיחה זו."}
                      </Typography>
                    </Box>

                    <Button
                      onClick={handleCloseModal}
                      sx={{
                        alignSelf: 'flex-end',
                        mt: 3,
                        py: 1.5,
                        px: 4,
                        backgroundColor: '#1976d2',
                        color: 'white',
                        '&:hover': {
                          backgroundColor: '#1565c0',
                        },
                        borderRadius: 2,
                        fontWeight: 'bold',
                      }}
                    >
                      סגור
                    </Button>
                  </>
                ) : (
                  <Typography variant="body2" sx={{ textAlign: 'center', color: '#555' }}>
                    טוען שיחה...
                  </Typography>
                )}
              </Box>
            </Modal>
          </Box>
        </Box>
      </>
    </ThemeProvider>
  );
}

ConversationsHistory.propTypes = {
  handleLogout: PropTypes.func.isRequired, 
};

export default ConversationsHistory;