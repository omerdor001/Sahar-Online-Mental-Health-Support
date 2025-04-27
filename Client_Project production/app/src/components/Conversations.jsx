import { useState, useEffect } from 'react';
import { 
  Box, 
  Typography, 
  Button, 
  TextField, 
  IconButton, 
  Stack,
  Modal
} from '@mui/material';
import MenuIcon from '@mui/icons-material/Menu';
import SettingsIcon from '@mui/icons-material/Settings';
import ExportIcon from '@mui/icons-material/ExitToApp';
import LogoutIcon from '@mui/icons-material/Logout';
import HomeIcon from '@mui/icons-material/Home';
import HelpOutlineIcon from '@mui/icons-material/HelpOutline';
import { useNavigate } from 'react-router-dom';
import { createTheme, ThemeProvider } from '@mui/material/styles';
import { CssBaseline } from '@mui/material';
import PropTypes from 'prop-types';

const theme = createTheme({
  typography: {
    fontFamily: '"Segoe UI", "Helvetica Neue", Arial, sans-serif', 
  },
});

function formatTimeString(dateString) {
  if (!dateString) return "ישנה תקלה עם הצגת התאריך";
  const date = new Date(dateString);
  if (isNaN(date.getTime())) return "ישנה תקלה זמנית עם הצגת התאריך"; 
  const day = date.getDate().toString().padStart(2, '0');
  const month = (date.getMonth() + 1).toString().padStart(2, '0');
  const year = date.getFullYear();
  const hours = date.getHours().toString().padStart(2, '0');
  const minutes = date.getMinutes().toString().padStart(2, '0');

  return `תאריך עדכון אחרון : ${day}/${month}/${year}, ${hours}:${minutes}`;
}

function Conversations({ handleLogout }) {
  const navigate = useNavigate();
  const [conversationsLastUpdateTime,setConversationsLastUpdateTime] = useState();
  const [searchQuery, setSearchQuery] = useState('');
  const [filteredConversations, setFilteredConversations] = useState([]);
  const [selectedConversation, setSelectedConversation] = useState(null); 
  const [modalOpen, setModalOpen] = useState(false); 
  const [isSidebarOpen, setSidebarOpen] = useState(false);
  const [openConversations, setOpenConversations] = useState([]);

  function getBackgroundColor(FEGSR) {
    let hue = 120;  
    let saturation = 50; 
    let lightness = 70;  
    if (FEGSR < 0.5) {
      hue = 120;  
      lightness = 70 + FEGSR * 15;  
    } else if (FEGSR >= 0.5 && FEGSR < 0.8) {
      hue = 60 + (Math.pow(FEGSR - 0.5, 2) * 60);  
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
  }

  const toggleSidebar = () => {
    setSidebarOpen(!isSidebarOpen);
  };

    useEffect(() => {
      const stored = localStorage.getItem('openConversations');
      if (stored) {
        try {
          const parsed = JSON.parse(stored);
          setOpenConversations(parsed);
        } catch (e) {
          console.error("Failed to parse openConversations:", e);
        }
      }
    }, []);
  
    useEffect(() => {
      const handleUpdate = (event) => {
        const updatedData = event.detail;
        if (updatedData) {
          console.log("Received openConversations from event.detail");
          setOpenConversations(updatedData);
        } else {
          try {
            const stored = localStorage.getItem('openConversations');
            if (stored) {
              setOpenConversations(JSON.parse(stored));
            }
          } catch (e) {
            console.error("Error parsing openConversations:", e);
          }
        }
      };
      window.addEventListener('openConversationsUpdated', handleUpdate);
      return () => window.removeEventListener('openConversationsUpdated', handleUpdate);
    }, []);
  
    useEffect(() => {
      let filtered = [];
      if (openConversations && Array.isArray(openConversations)) {
        filtered = openConversations.filter(conversation =>
          conversation.consumerParticipants?.consumerName?.toLowerCase().includes(searchQuery.toLowerCase()) ||
          conversation.latestAgentFullName?.toLowerCase().includes(searchQuery.toLowerCase()) ||
          conversation.conversationId?.toLowerCase().includes(searchQuery.toLowerCase())
        );
      }
      const updatedFiltered = filtered.map(conversation => ({
        ...conversation,
        FEGSR: conversation.GSR ? conversation.GSR * 100 : 0,
        FEIMSR: 0,
      }));
  
      setFilteredConversations(updatedFiltered);
      setConversationsLastUpdateTime(new Date().toISOString());
    }, [searchQuery, openConversations]); 

  let conversations = [...filteredConversations];
  conversations = conversations.sort((a, b) => {
    return b.GSR - a.GSR;
  });

  useEffect(() => {
    const resizePopupListener = () => {
      const event = new CustomEvent('resizePopup', {
        detail: { window: 'Conversations' },
      });
      document.dispatchEvent(event);
    };
    document.addEventListener('resizePopup', resizePopupListener);
    return () => {
      document.removeEventListener('resizePopup', resizePopupListener);
    };
  }, []);

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <>
        <Box sx={{
          display: 'flex',
          flexDirection: { xs: 'column', md: 'row' },
          height: { xs: 'auto', md: '100vh' },
          backgroundColor: '#f0f4f8',
          overflow: 'hidden',
        }}>
          
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
    p: { xs: 2, md: 4 },
    overflowY: 'auto',
    backgroundColor: '#ffffff',
    borderRadius: 2,
    boxShadow: 3,
    mx: { xs: 'auto', md: 'auto' }, 
    mt: { xs: isSidebarOpen ? 6 : 4, md: 0 },
    marginRight: { xs: 'auto', md: isSidebarOpen ? 12 : 'auto' },
    marginLeft: { xs: 'auto', md: 'auto' },
    width: { xs: '90%', md: '80%' },  
    maxWidth: '1200px',  
    minHeight: '85vh',  
    transition: 'margin-right 0.3s ease',
  }}
>
            {/* Header with Logout Button */}
            <Box
              sx={{
                display: 'flex',
                justifyContent: 'center',
                alignItems: 'center',
                p: { xs: 1, md: 2 },
                borderRadius: 1,
                mb: 3,
              }}
            >
  
              {/* Title */}
              <Typography
                variant="h4"
                sx={{
                  textAlign: 'center',
                  fontWeight: 'bold',
                  color: 'white',
                  padding: { xs: '12px 16px', md: '16px 32px' },
                  backgroundColor: '#4fa3f7',
                  width: '100%',
                  borderRadius: '8px',
                  margin: { xs: '10px auto', md: '20px auto' },
                  boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
                  direction: 'rtl',
                  fontSize: { xs: '1.5rem', md: '2rem' },
                }}
              >
                שיחות פעילות
              </Typography>
            </Box>      
  
            {/* Search Input */}
            <Box sx={{
              display: 'flex',
              justifyContent: { xs: 'center', md: 'flex-end' },
              mb: 3,
            }}>
              <TextField
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="חפש לפי כינוי, שם הסייע/ת או מזהה שיחה"
                variant="outlined"
                size="small"
                sx={{
                  width: { xs: '100%', sm: 350 },
                }}
              />
            </Box>
  
            {/* Conversation List */}
            <Box sx={{ overflowY: 'auto', width: '100%' }}>
              <Stack spacing={1.5}>
                {/* Header Row */}
                <Box sx={{ p: 2, borderRadius: 2, backgroundColor: '#f1f8ff' }}>
                  <Stack 
                    direction="row" 
                    justifyContent="space-between" 
                    alignItems="center" 
                    flexWrap="wrap"
                    sx={{
                      '& > div': {
                        px: { xs: 0.5, sm: 1 }
                      }
                    }}
                  >
                    {['אחוז גלובלי','כינוי','שם הסייע/ת','מזהה שיחה'].map((header, idx) => (
                      <Box key={idx} sx={{ flex: 1, minWidth: { xs: 60, sm: 80 }, textAlign: 'center' }}>
                        <Typography 
                          variant="body1" 
                          sx={{ 
                            fontWeight: 'bold',
                            fontSize: { xs: '0.8rem', sm: '0.875rem', md: '1rem' } 
                          }}
                        >
                          {header}
                        </Typography>
                      </Box>
                    ))}
                  </Stack>
                </Box>
  
                {/* Conversations */}
                {conversations.map((conversation, index) => (
                  <Box
                    key={index}
                    sx={{
                      p: { xs: 1.5, sm: 2 },
                      borderRadius: 2,
                      background: getBackgroundColor(conversation.GSR),
                      boxShadow: 1,
                      '&:hover': { boxShadow: 3, cursor: 'pointer' },
                    }}
                    onClick={() => handleSelectConversation(conversation)}
                  >
                    <Stack 
                      direction="row" 
                      justifyContent="space-between" 
                      alignItems="center" 
                      flexWrap="wrap"
                      sx={{
                        '& > div': {
                          px: { xs: 0.5, sm: 1 }
                        }
                      }}
                    >
                      <Box sx={{ flex: 1, minWidth: { xs: 60, sm: 80 }, textAlign: 'center' }}>
                        <Typography 
                          variant="body2"
                          sx={{ fontSize: { xs: '0.75rem', sm: '0.8rem' } }}
                        >
                          {Number(conversation.FEGSR).toPrecision(4)}%
                        </Typography>
                      </Box>
                      <Box sx={{ flex: 1, minWidth: { xs: 60, sm: 80 }, textAlign: 'center' }}>
                        <Typography 
                          variant="body2"
                          sx={{ fontSize: { xs: '0.75rem', sm: '0.8rem' } }}
                        >
                          {conversation.consumerParticipants.consumerName}
                        </Typography>
                      </Box>
                      <Box sx={{ flex: 1, minWidth: { xs: 60, sm: 80 }, textAlign: 'center' }}>
                        <Typography 
                          variant="body2"
                          sx={{ fontSize: { xs: '0.75rem', sm: '0.8rem' } }}
                        >
                          {conversation.latestAgentFullName}
                        </Typography>
                      </Box>
                      <Box sx={{ flex: 1, minWidth: { xs: 60, sm: 80 }, textAlign: 'center' }}>
                        <Typography 
                          variant="body2"
                          sx={{ fontSize: { xs: '0.75rem', sm: '0.8rem' } }}
                        >
                          {conversation.conversationId}
                        </Typography>
                      </Box>
                    </Stack>
                  </Box>
                ))}
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
                  width: { xs: '90%', sm: 350 },
                  maxWidth: '90vw',
                  maxHeight: '80vh',
                  bgcolor: 'background.paper',
                  border: '2px solid #1976d2',
                  boxShadow: 24,
                  p: { xs: 2, md: 3 },
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
                        fontSize: { xs: '1.25rem', md: '1.5rem' },
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
                        {".כרגע אין קטגוריה זמינה לשיחה זו"}
                      </Typography>
                    </Box>
  
                    <Box sx={{ mb: 2, width: '100%' }}>
                      <Typography variant="body2" sx={{ fontWeight: 'bold', color: '#333' }}>
                        משפטי הסבר
                      </Typography>
                      <Typography variant="body2" sx={{ color: '#555', whiteSpace: 'pre-line' }}>
                        {".כרגע אין משפטים זמינים לשיחה זו"}
                      </Typography>
                    </Box>
  
                    <Button
                      onClick={handleCloseModal}
                      sx={{
                        alignSelf: 'flex-end',
                        mt: 3,
                        py: { xs: 1, md: 1.5 },
                        px: { xs: 3, md: 4 },
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
            
            {/* Last Update Time */}
            <Typography variant="body2" sx={{ textAlign: 'center', color: 'black', mt: 4 }}>
              {formatTimeString(conversationsLastUpdateTime)}
            </Typography>
          </Box>
        </Box>
      </>
    </ThemeProvider>
  );
}

Conversations.propTypes = {
  handleLogout: PropTypes.func.isRequired, 
};

export default Conversations;
