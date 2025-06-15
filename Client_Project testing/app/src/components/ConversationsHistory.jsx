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
  MenuItem,
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
            mt: { xs: 0, md: 2 },
            width: '100%',
            paddingBottom: { xs: 8, md: 4 },
            marginRight: { xs: 0, md: isSidebarOpen ? 15 : 2 }, 
            marginLeft: { xs: 0, md: isSidebarOpen ? 15 : 2 }, 
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
              mt: { xs: isSidebarOpen ? 2 : 2, md: 2 },
              mx: { xs: 0, sm: 2 },
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
                maxWidth: { xs: '100%', sm: 600 }, 
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
  sx={{
    width: { xs: '100%', sm: 200 },
    '& .MuiOutlinedInput-root': {
      height: 30,
      fontSize: '0.75rem',
      padding: '0 8px',
    },
    '& .MuiSelect-select': {
      padding: '4px 8px',
    },
  }}
>
  <InputLabel id="time-filter-label" sx={{ fontSize: '0.75rem' }}>הצג שיחות שהתרחשו עד לפני</InputLabel>
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
                sx={{
    width: { xs: '100%', sm: 300 }, 
    '& .MuiOutlinedInput-root': {
      height: 30, 
      fontSize: '0.75rem',
      padding: '0 8px',
    },
    '& input': {
      padding: '4px 0', 
    },
  }}
              />
            </Stack>

          {/* Conversation List */}
<Box sx={{ p: 1, borderRadius: 2, backgroundColor: '#f1f8ff' }}> {/* Reduced padding */}
  <Stack 
    direction="row" 
    justifyContent="space-between" 
    alignItems="center" 
    flexWrap="wrap"
    sx={{
      '& > div': {
        px: { xs: 0.3, sm: 0.5 } // Reduced
      }
    }}
  >
    {['מזהה שיחה','שם הסייע/ת','כינוי','אחוז גלובלי'].map((header, idx) => (
      <Box key={idx} sx={{ flex: 1, minWidth: { xs: 50, sm: 70 }, textAlign: 'center' }}> {/* Reduced width */}
        <Typography 
          variant="body1" 
          sx={{ 
            fontWeight: 'bold',
            fontSize: { xs: '0.7rem', sm: '0.75rem', md: '0.85rem' } // Reduced
          }}
        >
          {header}
        </Typography>
      </Box>
    ))}
  </Stack>
</Box>

{/* Conversation List - Longer and scrollbar on the right */}
<Box 
  sx={{ 
    overflowY: 'auto', 
    width: '100%', 
    flex: 1, 
    mb: 1, // Reduced
    maxHeight: { xs: '70vh', sm: '75vh', md: '80vh' }, // Increased height
    height: '100%', 
    display: 'block',
    direction: 'ltr', // This forces scrollbar to the right side
    '& > *': {
      direction: 'rtl', // This maintains RTL text direction inside the container
    },
    '&::-webkit-scrollbar': { 
      width: '6px', // Reduced
    },
    '&::-webkit-scrollbar-thumb': {
      backgroundColor: 'rgba(0,0,0,0.2)',
      borderRadius: '4px',
    },
  }}
>
  <Stack spacing={0.75}> {/* Reduced from 1.5 */}
    {/* Conversations - More compact items */}
    {conversations.map((conversation, index) => (
      <Box
        key={index}
        sx={{
          p: { xs: 0.75, sm: 1 }, // Reduced from 1.5,2
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
              px: { xs: 0.3, sm: 0.5 } // Reduced
            }
          }}
        >
          <Box sx={{ flex: 1, minWidth: { xs: 50, sm: 70 }, textAlign: 'center' }}> {/* Reduced */}
            <Typography 
              variant="body2"
              sx={{ fontSize: { xs: '0.65rem', sm: '0.7rem' } }} // Reduced
            >
              {conversation.conversationId}
            </Typography>
          </Box>
          <Box sx={{ flex: 1, minWidth: { xs: 50, sm: 70 }, textAlign: 'center' }}> {/* Reduced */}
            <Typography 
              variant="body2"
              sx={{ fontSize: { xs: '0.65rem', sm: '0.7rem' } }} // Reduced
            >
               {conversation.latestAgentFullName}
            </Typography>
          </Box>
          <Box sx={{ flex: 1, minWidth: { xs: 50, sm: 70 }, textAlign: 'center' }}> {/* Reduced */}
            <Typography 
              variant="body2"
              sx={{ fontSize: { xs: '0.65rem', sm: '0.7rem' } }} // Reduced
            >
              {conversation.consumerParticipants.consumerName}
            </Typography>
          </Box>
          <Box sx={{ flex: 1, minWidth: { xs: 50, sm: 70 }, textAlign: 'center' }}> {/* Reduced */}
            <Typography 
              variant="body2"
              sx={{ fontSize: { xs: '0.65rem', sm: '0.7rem' } }} // Reduced
            >
              {Number(conversation.FEGSR).toPrecision(3)}%
            </Typography>
          </Box>
        </Stack>
      </Box>
    ))}
  </Stack>
</Box>
         {/* Modal for Conversation Details - More compact */}
        <Modal open={modalOpen} onClose={handleCloseModal}>
          <Box
            sx={{
              position: 'fixed', 
              top: '50%',
              left: '50%',
              transform: 'translate(-50%, -50%)',
              width: { xs: '85%', sm: 320 },
              height: 'auto',
              minWidth: 280,
              minHeight: 200,
              maxWidth: '95vw',
              maxHeight: '90vh',
              bgcolor: 'background.paper',
              border: '2px solid #1976d2',
              boxShadow: 24,
              borderRadius: 2,
              overflow: 'hidden',
              display: 'flex',
              flexDirection: 'column',
              resize: 'both', 
              cursor: 'auto',
              zIndex: 1300, 
              '&::-webkit-resizer': {
                background: 'linear-gradient(-45deg, transparent 0%, transparent 35%, #1976d2 35%, #1976d2 45%, transparent 45%, transparent 65%, #1976d2 65%, #1976d2 75%, transparent 75%)',
                width: '16px',
                height: '16px',
              }
            }}
             ref={(el) => {
              if (el) {
                if (el._resizeObserver) {
                  el._resizeObserver.disconnect();
                }
                
                const resizeObserver = new ResizeObserver((entries) => {
                  const entry = entries[0];
                  if (entry) {
                    const { width } = entry.contentRect;
                    const scale = Math.max(0.7, Math.min(1.5, width / 320));
                    el.style.setProperty('--font-scale', scale);
                  }
                });
                resizeObserver.observe(el);
                
                el._resizeObserver = resizeObserver;
              } else {
                if (el && el._resizeObserver) {
                  el._resizeObserver.disconnect();
                  el._resizeObserver = null;
                }
              }
            }}
          >
            {/* Header with drag handle */}
            <Box
              sx={{
                p: 1,
                backgroundColor: '#1976d2',
                color: 'white',
                cursor: 'move',
                userSelect: 'none',
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                borderBottom: '1px solid #1565c0',
              }}
              onMouseDown={(e) => {
                e.preventDefault();
                e.stopPropagation();
              
                const modal = e.currentTarget.parentElement;
                if (!modal) return;
                
                // Get initial positions
                const startX = e.clientX;
                const startY = e.clientY;
                const rect = modal.getBoundingClientRect();
                
                // Store initial position
                const initialLeft = rect.left;
                const initialTop = rect.top;
                
                // Remove transform and set initial position
                modal.style.transform = 'none';
                modal.style.left = `${initialLeft}px`;
                modal.style.top = `${initialTop}px`;
                modal.style.position = 'fixed';
                
                // Add dragging visual feedback
                document.body.style.cursor = 'grabbing';
                document.body.style.userSelect = 'none';
                modal.style.pointerEvents = 'none'; // Prevent interference during drag
                e.currentTarget.style.pointerEvents = 'auto'; // Keep header clickable
                
                const handleMouseMove = (moveEvent) => {
                  moveEvent.preventDefault();
                  
                  const deltaX = moveEvent.clientX - startX;
                  const deltaY = moveEvent.clientY - startY;
                  
                  // Calculate new position
                  let newLeft = initialLeft + deltaX;
                  let newTop = initialTop + deltaY;
                  
                  // Get viewport dimensions
                  const viewportWidth = window.innerWidth;
                  const viewportHeight = window.innerHeight;
                  const modalWidth = modal.offsetWidth;
                  const modalHeight = modal.offsetHeight;
                  
                  // Constrain to viewport bounds with some padding
                  newLeft = Math.max(10, Math.min(viewportWidth - modalWidth - 10, newLeft));
                  newTop = Math.max(10, Math.min(viewportHeight - modalHeight - 10, newTop));
                  
                  modal.style.left = `${newLeft}px`;
                  modal.style.top = `${newTop}px`;
                };
                
                const handleMouseUp = () => {
                  // Reset cursors and user selection
                  modal.style.cursor = 'auto';
                  document.body.style.cursor = 'auto';
                  document.body.style.userSelect = 'auto';
                  
                  // Remove event listeners
                  document.removeEventListener('mousemove', handleMouseMove);
                  document.removeEventListener('mouseup', handleMouseUp);
                };
                
                // Add event listeners
                document.addEventListener('mousemove', handleMouseMove);
                document.addEventListener('mouseup', handleMouseUp);
              }}
            >
               <Typography
                variant="h6"
                sx={{
                  fontWeight: 'bold',
                  fontSize: `calc(1rem * var(--font-scale, 1))`,
                  '@media (min-width: 768px)': {
                    fontSize: `calc(1.1rem * var(--font-scale, 1))`,
                  }
                }}
              >
                פרטי שיחה
              </Typography>
              
              {/* Close button in header */}
              <IconButton
                onClick={handleCloseModal}
                sx={{
                  color: 'white',
                  p: 0.5,
                  width: `calc(32px * var(--font-scale, 1))`,
                  height: `calc(32px * var(--font-scale, 1))`,
                  fontSize: `calc(14px * var(--font-scale, 1))`,
                  '&:hover': {
                    backgroundColor: 'rgba(255,255,255,0.1)',
                  },
                }}
                size="small"
              >
                ✕
              </IconButton>
            </Box>
        
            {/* Scrollable content area */}
            <Box
              sx={{
                p: { xs: 1.5, md: 2 },
                overflow: 'auto',
                flex: 1,
                textAlign: 'right',
              }}
            >
               {selectedConversation ? (
                <>
                  <Box sx={{ mb: 1.5, width: '100%' }}>
                    <Typography 
                      variant="body2" 
                      sx={{ 
                        fontWeight: 'bold', 
                        color: '#333', 
                        fontSize: `calc(0.8rem * var(--font-scale, 1))` 
                      }}
                    >
                      מזהה שיחה
                    </Typography>
                    <Typography 
                      variant="body2" 
                      sx={{ 
                        color: '#555', 
                        fontSize: `calc(0.8rem * var(--font-scale, 1))`, 
                        wordBreak: 'break-all' 
                      }}
                    >
                      {selectedConversation.conversationId}
                    </Typography>
                  </Box>
        
                  <Box sx={{ mb: 1.5, width: '100%' }}>
                    <Typography 
                      variant="body2" 
                      sx={{ 
                        fontWeight: 'bold', 
                        color: '#333', 
                        fontSize: `calc(0.8rem * var(--font-scale, 1))` 
                      }}
                    >
                      כינוי
                    </Typography>
                    <Typography 
                      variant="body2" 
                      sx={{ 
                        color: '#555', 
                        fontSize: `calc(0.8rem * var(--font-scale, 1))` 
                      }}
                    >
                      {selectedConversation.consumerParticipants.consumerName}
                    </Typography>
                  </Box>
        
                  <Box sx={{ mb: 1.5, width: '100%' }}>
                    <Typography 
                      variant="body2" 
                      sx={{ 
                        fontWeight: 'bold', 
                        color: '#333', 
                        fontSize: `calc(0.8rem * var(--font-scale, 1))` 
                      }}
                    >
                      שם הסייע/ת
                    </Typography>
                    <Typography 
                      variant="body2" 
                      sx={{ 
                        color: '#555', 
                        fontSize: `calc(0.8rem * var(--font-scale, 1))` 
                      }}
                    >
                      {selectedConversation.latestAgentFullName}
                    </Typography>
                  </Box>
        
                  <Box sx={{ mb: 2, width: '100%' }}>
                    <Typography 
                      variant="body2" 
                      sx={{ 
                        fontWeight: 'bold', 
                        color: '#333', 
                        fontSize: `calc(0.8rem * var(--font-scale, 1))` 
                      }}
                    >
                      סיכום שיחה
                    </Typography>
                    <Typography 
                      variant="body2" 
                      sx={{ 
                        color: '#555', 
                        fontSize: `calc(0.8rem * var(--font-scale, 1))`,
                        lineHeight: 1.4,
                        whiteSpace: 'pre-wrap',
                      }}
                    >
                      כרגע אין סיכום לשיחה זו
                    </Typography>
                  </Box>
                </>
              ) : (
                <Typography 
                  variant="body2" 
                  sx={{ 
                    textAlign: 'center', 
                    color: '#555', 
                    fontSize: `calc(0.8rem * var(--font-scale, 1))` 
                  }}
                >
                  טוען שיחה...
                </Typography>
              )}
            </Box>
        
            {/* Footer with resize indicator */}
           <Box
              sx={{
                p: 1,
                borderTop: '1px solid #e0e0e0',
                backgroundColor: '#f5f5f5',
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                minHeight: '32px',
              }}
            >
              <Typography 
                variant="caption" 
                sx={{ 
                  color: '#666', 
                  fontSize: `calc(0.7rem * var(--font-scale, 1))` 
                }}
              >
                גרור לזוז • משוך פינה לשנות גודל
              </Typography>
              
              {/* Visual resize handle */}
               <Box
                sx={{
                  width: `calc(12px * var(--font-scale, 1))`,
                  height: `calc(12px * var(--font-scale, 1))`,
                  background: 'linear-gradient(-45deg, transparent 0%, transparent 35%, #999 35%, #999 45%, transparent 45%, transparent 65%, #999 65%, #999 75%, transparent 75%)',
                  cursor: 'nw-resize',
                }}
              />
            </Box>
          </Box>
        </Modal>
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