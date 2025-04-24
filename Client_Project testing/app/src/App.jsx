import { useState, useEffect, useRef } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Login from './components/Login.jsx';
import Conversations from './components/Conversations.jsx';
import ConversationsHistory from './components/ConversationsHistory.jsx';
import Settings from './components/Settings.jsx';
import CommonQuestions from './components/CommonQuestions.jsx';
import LogoutModal from "./components/LogoutModal.jsx";
import './index.css';
import { fetchLogin } from './http.js';
import TriggerModal from './components/TriggerModal';
import io from 'socket.io-client'; 

const basename = window.location.pathname.startsWith("/test") ? "/test/" : "/";
const isTestEnvironment = window.location.pathname.startsWith("/test");
const API_BASE_URL = isTestEnvironment ? '/test/api' : '/api';

function App() {
  const modalRef = useRef();
  const [setWindowSize] = useState({
    width: window.innerWidth,
    height: window.innerHeight,
  });
  const [errorMessage, setErrorMessage] = useState('');
  const [isLoading, setIsLoading] = useState(true);
  const [isLogged, setIsLogged] = useState(false);
  const [isModalOpen, setModalOpen] = useState(false);
  const [modalMessage, setModalMessage] = useState('');
  const [notificationTime, setNotificationTime] = useState(2);
  const [socket, setSocket] = useState(null); 
  const authToken = localStorage.getItem('token');
  let lastAlertTime = 0;

  useEffect(() => {
    const handleBeforeUnload = (e) => {
      handleLogout();
      e.preventDefault();
      e.returnValue = '';
    };
    window.addEventListener('unload', handleBeforeUnload);
    return () => {
      window.removeEventListener('unload', handleBeforeUnload);
    };
  }, []);

  const usePreventWindowAlert = () => {
    useEffect(() => {
      const originalAlert = window.alert;
      window.alert = (message) => {
        console.log('Alert prevented:', message);
      };
      return () => {
        window.alert = originalAlert;
      };
    }, []);
  };

  usePreventWindowAlert();
    
  useEffect(() => {
    if (isLogged && authToken) {
      const socketURL = `${window.location.origin}/test`;
      console.log('Attempting to connect to Socket.IO:', socketURL);
      const newSocket = io('https://saharassociation.cs.bgu.ac.il', {
        path: '/test/socket.io/',
        transports: ['websocket'],
        auth: { token: authToken }, 
      });
      
      setSocket(newSocket);

      newSocket.on('connect', () => {
        console.log('Socket.IO connected to server');
      });

      newSocket.on('open_calls_update', (data) => {
        const currentTime = Date.now();
        const notificationTimeData = Number(localStorage.getItem('notificationTime'));
        //console.log('Received open conversations:', data);
        localStorage.setItem('openConversations', JSON.stringify(data.data));
        localStorage.setItem('conversationsLastUpdateTime', new Date().toISOString());
        window.dispatchEvent(new Event('openConversationsUpdated'));
        const highRiskConversation = data.data && data.data.find(conv => conv.GSR > 0.8);
        if (highRiskConversation && currentTime- lastAlertTime > notificationTimeData * 60 * 1000) {
          lastAlertTime = currentTime;
          const alertMessage = 'אותרה שיחה ברמת אובדנות גבוהה';
          setModalMessage(alertMessage);
          setModalOpen(true);
        }
      });

      newSocket.on('connect_error', (err) => {
        console.error('Socket.IO connection error:', err);
        handleLogout();
      });

      newSocket.on('disconnect', () => {
        console.log('Socket.IO disconnected');
      });

      return () => {
        if (newSocket) {
          newSocket.disconnect();
        }
      };
    } else if (socket) {
      socket.disconnect();
      setSocket(null);
    }
  }, [isLogged, authToken]);

  useEffect(() => {
    const handleLogoutEvent = (event) => {
      if (event.detail.type === 'LOGOUT') {
        setIsLogged(false);
      }
    };
    document.addEventListener('backgroundMessage', handleLogoutEvent);
    return () => {
      document.removeEventListener('backgroundMessage', handleLogoutEvent);
    };
  }, []);

  useEffect(() => {
    const initializeApp = async () => {
      setIsLoading(true);
      try {
        const tokenData = localStorage.getItem('token');
        if (tokenData) {
          localStorage.setItem('isLogged', 'true');
          setIsLogged(true);
        }
      } catch (error) {
        console.error('Initialization error:', error);
        setErrorMessage('Failed to initialize application');
      } finally {
        setIsLoading(false);
      }
    };
    initializeApp();
    const handleResize = () => {
      setWindowSize({
        width: window.innerWidth,
        height: window.innerHeight,
      });
    };
    window.addEventListener("resize", handleResize);
    return () => window.removeEventListener("resize", handleResize);
  }, []);

  const handleLogin = async (accountNumber, userName, password, role, setLoadIcon) => {
    if (!accountNumber || !userName || !password || !role) {
      setErrorMessage('הפרטים שסיפקת אינם נכונים.');
      setLoadIcon(false);
      return;
    }
    try {
      await fetchLogin(accountNumber, userName, password);
      localStorage.setItem('username', userName);
      localStorage.setItem('notificationTime', '2');
      localStorage.setItem('token', localStorage.getItem('token')); 
      localStorage.setItem('isLogged', 'true');
      setIsLogged(true);
      setErrorMessage('');
      const notificationTimeData = Number(localStorage.getItem('notificationTime'));
      setNotificationTime(notificationTimeData);
      console.log(notificationTime);
      localStorage.setItem("apiBaseURL", API_BASE_URL);
    } catch (error) {
      console.error('Login failed:', error);
      setErrorMessage('הפרטים שסיפקת אינם נכונים.');
      localStorage.setItem('isLogged', 'false');
      setIsLogged(false);
    }
    setLoadIcon(false);
  };

  const handleLogout = () => {
    console.log("start logout process");
    setErrorMessage('');
    localStorage.removeItem('openConversations');
    localStorage.removeItem('token');
    localStorage.setItem('isLogged', 'false');
    setIsLogged(false);
    if (socket) {
      socket.disconnect();
      setSocket(null);
    }
  };

  const openLogoutModal = () => {
    if (modalRef.current) {
      modalRef.current.open();
    }
  };

  if (isLoading) {
    return <div>Loading...</div>;
  }

  return (
    <Router basename={basename}>
      <div className="min-h-screen bg-white">
        <div className="m-4">
          <LogoutModal ref={modalRef} handleLogout={handleLogout} />
          <TriggerModal
            isOpen={isModalOpen}
            message={modalMessage}
            onClose={() => setModalOpen(false)}
          />
          <Routes>
            <Route
              path="/login"
              element={!isLogged ?
                <Login handleLogin={handleLogin} errorMessage={errorMessage} /> :
                <Navigate to="/" />
              }
            />
            <Route
              path="/"
              element={isLogged ?
                <Conversations handleLogout={openLogoutModal} /> :
                <Navigate to="/login" />
              }
            />
            <Route
              path="/conversation-history"
              element={isLogged ?
                <ConversationsHistory handleLogout={openLogoutModal} /> :
                <Navigate to="/login" />
              }
            />
            <Route
              path="/common-questions"
              element={isLogged ?
                <CommonQuestions handleLogout={openLogoutModal} /> :
                <Navigate to="/login" />
              }
            />
            <Route
              path="/settings"
              element={isLogged ?
                <Settings handleLogout={openLogoutModal} /> :
                <Navigate to="/login" />
              }
            />
          </Routes>
        </div>
      </div>
    </Router>
  );
}

export default App;