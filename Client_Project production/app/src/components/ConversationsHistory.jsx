import { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Button,
  TextField,
  IconButton,
  Stack,
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
    console.log(selectedConversation);
    setModalOpen(true);
    console.log(modalOpen);
  };

  // const handleCloseModal = () => {
  //   setSelectedConversation(null);
  //   setModalOpen(false);
  // };

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
      <Box
        sx={{
          display: 'flex',
          flexDirection: { xs: 'column', md: 'row' },
          minHeight: '100vh',
          width: '100%',
          backgroundColor: '#f0f4f8',
          overflow: 'hidden',
          position: 'relative',
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
            p: { xs: 2, sm: 3 },
            overflowY: 'auto',
            mt: { xs: isSidebarOpen ? 2 : 8, md: 2 },
            width: '100%',
            paddingBottom: { xs: 8, md: 4 },
            marginRight: { xs: 0, md: isSidebarOpen ? 15 : 2 }, // Removed margin-right for xs
            marginLeft: { xs: 0, md: isSidebarOpen ? 15 : 2 }, // Removed margin-left for xs
            transition: 'margin-right 0.3s ease',
          }}
        >
          {/* Header */}
          <Box
            sx={{
              p: { xs: 2, sm: 4 },
              backgroundColor: '#ffffff',
              borderRadius: 2,
              boxShadow: 3,
              mt: 2,
              mx: { xs: 0, sm: 2 }, // Removed margin for xs
            }}
          >
            <Typography
              variant="h4"
              sx={{
                fontWeight: 'bold',
                color: 'white',
                backgroundColor: '#4fa3f7',
                borderRadius: 3,
                px: 3,
                py: 2,
                mb: 3,
                textAlign: 'center',
                maxWidth: { xs: '100%', sm: 600 }, // Full width on xs
                mx: 'auto',
                fontSize: { xs: '1.5rem', md: '2rem' },
              }}
            >
              היסטוריית שיחות
            </Typography>
  
            {/* Filters */}
            <Stack
              direction={{ xs: 'column', sm: 'row' }}
              spacing={2}
              mb={3}
              alignItems="center"
              justifyContent="center"
            >
              <FormControl
                variant="outlined"
                size="small"
                sx={{ width: { xs: '100%', sm: 200 } }}
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
  
              <TextField
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="חפש לפי כינוי, שם הסייע/ת או מזהה שיחה"
                variant="outlined"
                size="small"
                sx={{ width: { xs: '100%', sm: 350 } }}
              />
            </Stack>
  
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
                    {['מזהה שיחה', 'שם הסייע/ת', 'כינוי', 'אחוז גלובלי'].map((header, idx) => (
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
                          {conversation.conversationId}
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
                          {conversation.consumerParticipants.consumerName}
                        </Typography>
                      </Box>
                      <Box sx={{ flex: 1, minWidth: { xs: 60, sm: 80 }, textAlign: 'center' }}>
                        <Typography 
                          variant="body2"
                          sx={{ fontSize: { xs: '0.75rem', sm: '0.8rem' } }}
                        >
                          {Number(conversation.FEGSR).toPrecision(4)}%
                        </Typography>
                      </Box>
                    </Stack>
                  </Box>
                ))}
              </Stack>
            </Box>
          </Box>
        </Box>
      </Box>
    </ThemeProvider>
  );
  
  
}

ConversationsHistory.propTypes = {
  handleLogout: PropTypes.func.isRequired, 
};

export default ConversationsHistory;