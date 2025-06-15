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
  const [loading, setLoading] = useState(false);

  

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
                         flexDirection: { xs: 'row-reverse', md: 'column' },
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
                   
        {/* Main Content - Reduced padding and margins */}
        <Box
          sx={{
            flexGrow: 1,
            p: { xs: 1, md: 2 }, // Reduced from 2,4
            backgroundColor: '#ffffff',
            borderRadius: 2,
            boxShadow: 3,
            mx: { xs: 'auto', md: 'auto' },
            mt: { xs: isSidebarOpen ? 4 : 2, md: 0 }, // Reduced
            marginRight: { xs: 'auto', md: isSidebarOpen ? 10 : 'auto' }, // Reduced from 12
            marginLeft: { xs: 'auto', md: 'auto' },
            width: { xs: '95%', md: '85%' }, // Increased width
            maxWidth: '1200px',
            minHeight: '85vh',
            transition: 'margin-right 0.3s ease',
            display: 'flex',
            flexDirection: 'column',
            overflow: 'hidden', // Prevent main content from scrolling
          }}
        >
          {/* Header with Title - More compact */}
          <Box
            sx={{
              display: 'flex',
              justifyContent: 'center',
              alignItems: 'center',
              p: { xs: 0.5, md: 1 }, // Reduced
              borderRadius: 1,
              mb: 1, // Reduced from 3
            }}
          >
            {/* Title - More compact */}
            <Typography
              variant="h4"
              sx={{
                textAlign: 'center',
                fontWeight: 'bold',
                color: 'white',
                padding: { xs: '8px 12px', md: '10px 20px' }, // Reduced
                backgroundColor: '#4fa3f7',
                width: '100%',
                borderRadius: '8px',
                margin: { xs: '5px auto', md: '10px auto' }, // Reduced
                boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
                direction: 'rtl',
                fontSize: { xs: '1.2rem', md: '1.5rem' }, // Reduced
              }}
            >
              שיחות פעילות
            </Typography>
          </Box>      

          {/* Search Input - More compact */}
          <Box sx={{
            display: 'flex',
            justifyContent: { xs: 'center', md: 'flex-end' },
            mb: 1, // Reduced from 3
          }}>
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
          </Box>

          {/* Header Row - More compact */}
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
              {['אחוז גלובלי','כינוי','שם הסייע/ת','מזהה שיחה'].map((header, idx) => (
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

          {/* Conversation List - More compact items */}
          <Box 
            sx={{ 
              overflowY: 'auto', 
              width: '100%', 
              flex: 1, 
              mb: 1, // Reduced
              maxHeight: { xs: '60vh', sm: '65vh', md: '70vh' }, // Increased for more content
              height: '100%', 
              display: 'block', 
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
                        {Number(conversation.FEGSR).toPrecision(3)}%
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
                        {conversation.latestAgentFullName}
                      </Typography>
                    </Box>
                    <Box sx={{ flex: 1, minWidth: { xs: 50, sm: 70 }, textAlign: 'center' }}> {/* Reduced */}
                      <Typography 
                        variant="body2"
                        sx={{ fontSize: { xs: '0.65rem', sm: '0.7rem' } }} // Reduced
                      >
                        {conversation.conversationId}
                      </Typography>
                    </Box>
                  </Stack>
                </Box>
              ))}
            </Stack>
          </Box>

          {/* Last Update Time - Smaller and more compact */}
          <Typography variant="body2" sx={{ 
            textAlign: 'center', 
            color: 'black', 
            mt: 0.5, // Reduced
            fontSize: '0.7rem' // Smaller
          }}>
            {formatTimeString(conversationsLastUpdateTime)}
          </Typography>
        </Box>
      </Box>

      {/* Modal for Conversation Details*/}
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
            <Button 
             variant="contained" 
             color="primary"
             sx={{ mt: 2 }}
             onClick={() => console.log('Button clicked')}
            >
             השג סיכום
            </Button>
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
    </>
  </ThemeProvider>
);
}

Conversations.propTypes = {
  handleLogout: PropTypes.func.isRequired, 
};

export default Conversations;
