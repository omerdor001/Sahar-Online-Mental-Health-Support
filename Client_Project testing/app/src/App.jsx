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
  const [errorMessage, setErrorMessage] = useState('');
  const [isLoading, setIsLoading] = useState(true);
  const [isLogged, setIsLogged] = useState(undefined);
  const [isModalOpen, setModalOpen] = useState(false);
  const [modalMessage,setModalMessage] = useState('');
  const [notificationTime, setNotificationTime] = useState(localStorage.getItem("notificationTime")||999999999999);
  const [socket, setSocket] = useState(null); 
  const authToken = localStorage.getItem('token');
  const [ssoStatus, setSsoStatus] = useState('Checking SSO...');
  const [isLivePersonContext, setIsLivePersonContext] = useState(false);
  const [agentSDK, setAgentSDK] = useState(null);
  let lastAlertTime = localStorage.getItem("lastAlertTime")||0;
  let agentId;


  useEffect(() => {
    const handleBeforeUnload = (e) => {
      if(!localStorage.getItem('isLivePerson')){
        handleLogout();
      }

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
    const checkAgentSDK = setInterval(() => {
      if (window.lpTag && window.lpTag.agentSDK) {
        setAgentSDK(window.lpTag.agentSDK);
        clearInterval(checkAgentSDK);
        console.log('Agent SDK found and set.');
      } else {
        console.log('Waiting for Agent SDK...');
      }
    }, 100); 
    return () => clearInterval(checkAgentSDK);
  }, []);

  useEffect(() => {
    const initAgentSDK = async () => {
      if (!agentSDK) {
        return;
      }
      agentSDK.init({});
      console.log(isLivePersonContext);
      try {
        const agentInfo = await getVars('agentInfo', 5000);
        if (!agentInfo) {
          setSsoStatus('SSO Failed. Using standard login.');
          console.log(ssoStatus);
          setIsLogged(false);
        } else {
          agentId=agentInfo.agentId;
          setSsoStatus('Authentication successful. Fetching user info...');
          const serverResponse = await getTokenWithData();
          const responseData = await serverResponse.json();
          if (serverResponse.ok) {
            setSsoStatus('SSO successful! User authenticated.');
            localStorage.setItem('token', responseData.token);
            if(!localStorage.getItem('notificationTime')){
              localStorage.setItem('notificationTime', '9999999999999999999999');
            }
            if(!localStorage.getItem("lastAlertTime")){
              localStorage.setItem("lastAlertTime",0);
            }
            localStorage.setItem('isLogged', 'true');
            setIsLogged(true);
            setErrorMessage('');
            setNotificationTime(Number(localStorage.getItem('notificationTime')));
            localStorage.setItem('apiBaseURL', API_BASE_URL);
            setIsLivePersonContext(true);
            localStorage.setItem('isLivePerson',true);
          } else {
            const errorData = await serverResponse.json();
            console.log(errorData);
            setSsoStatus('SSO Failed. Using standard login.');
            setIsLogged(false);
            localStorage.setItem('isLivePerson',false);
          }
        }
      } catch (error) {
        console.log(error.message);
        setSsoStatus('SSO Failed. Using standard login.');
        setIsLogged(false);
      } finally {
        setIsLoading(false);
      }
    };
    initAgentSDK();
  }, [agentSDK]);

  async function getVars(info_type, timeout = 2000) {
    try {
      const timeoutPromise = new Promise((_, reject) =>
        setTimeout(() => reject(new Error("Request timed out")), timeout)
      );
      const fetchPromise = new Promise((resolve, reject) => {
        const callback = function (data) {
          console.log(`Data received by get:`, data);
          if (data) {
            console.log(`Successfully retrieved ${info_type}`, data);
            resolve(data);
          } else {
            reject(new Error(`No data received for ${info_type}`));
          }
        };
        window.lpTag.agentSDK.get(info_type, callback.bind(window.lpTag.agentSDK));
      });
      const result = await Promise.race([fetchPromise, timeoutPromise]);
      return result;
    } catch (e) {
      console.log(`Error: ${e.message}, could not retrieve ${info_type} within timeout ${timeout}`);
      return undefined;
    }
  }

  useEffect(() => {
  const handler = async () => {
    if(localStorage.getItem('isLivePerson')){
    try {
      let agentInfo = await getVars('agentInfo', 5000);
      if (!agentInfo) {
            setSsoStatus('SSO Failed. Using standard login.');
            console.log(ssoStatus);
            setIsLogged(false);
    } else {
      agentId.current = agentInfo.agentId; 
      const response = await getTokenWithData();
      const data = await response.json();
      if (response.ok) {
        localStorage.setItem('token', data.token);
        console.log("Token refreshed on 403");
      } else {
        console.error("Token refresh failed (403 handler)");
      }
    }
    } catch (err) {
      console.error("Error refreshing token after 403:", err);
      }
    }
  };
  window.addEventListener('triggerTokenRefresh', handler);
  return () => {
    window.removeEventListener('triggerTokenRefresh', handler);
  };
  }, []);

  useEffect(() => {
  const REFRESH_INTERVAL = 60 * 60 * 1000; 
  const GRACE_PERIOD = 5 * 60 * 1000; 
  const refreshTokenIfNeeded = async () => {
    if (!localStorage.getItem('isLivePerson')) return;
    const lastRefreshTime = parseInt(localStorage.getItem('lastTokenRefresh') || '0');
    const currentTime = Date.now();
    if (currentTime - lastRefreshTime >= REFRESH_INTERVAL - GRACE_PERIOD) {
      try {
        const serverResponse = await getTokenWithData();
        const responseData = await serverResponse.json();
        if (serverResponse.ok) {
          localStorage.setItem('token', responseData.token);
          localStorage.setItem('lastTokenRefresh', currentTime.toString());
          console.log("Token refreshed - timestamp updated");
        } else {
          console.error("Token refresh failed");
        }
      } catch (err) {
        console.error("Error during token refresh:", err);
      }
    }
  };
  refreshTokenIfNeeded();
  const intervalId = setInterval(refreshTokenIfNeeded, 15 * 60 * 1000); 
  return () => clearInterval(intervalId);
}, []);

  async function getTokenWithData(){
    const serverResponse = await fetch(`${API_BASE_URL}/validateToken`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({  agentId:agentId.current }),
    });
    return serverResponse;
  }

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
        const lastAlertTimeData = Number(localStorage.getItem('lastAlertTime'));
        localStorage.setItem('openConversations', JSON.stringify(data.data));
        localStorage.setItem('conversationsLastUpdateTime', new Date().toISOString());
        window.dispatchEvent(new Event('openConversationsUpdated'));
        const highRiskConversation = data.data && data.data.find(conv => conv.GSR > 0.8);
        console.log(currentTime- lastAlertTimeData > notificationTimeData * 60 * 1000);
        if (highRiskConversation && currentTime- lastAlertTimeData > notificationTimeData * 60 * 1000) {
          lastAlertTime = currentTime;
          localStorage.setItem("lastAlertTime",lastAlertTime);
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
  }, []);

  const handleLogin = async (accountNumber, userName, password, setLoadIcon) => {
    if (!accountNumber || !userName || !password ) {
      setErrorMessage('הפרטים שסיפקת אינם נכונים.');
      setLoadIcon(false);
      return;
    }
    try {
      await fetchLogin(accountNumber, userName, password);
      if(!localStorage.getItem('notificationTime')){
        localStorage.setItem('notificationTime', '9999999999999999999');
      }
      if(!localStorage.getItem("lastAlertTime")){
        localStorage.setItem("lastAlertTime",0);
      }
      console.log(notificationTime);
      localStorage.setItem('token', localStorage.getItem('token')); 
      localStorage.setItem('isLogged', 'true');
      setIsLogged(true);
      setErrorMessage('');
      const notificationTimeData = Number(localStorage.getItem('notificationTime'));
      setNotificationTime(notificationTimeData);
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
    if(isLivePersonContext){
      console.error("isLivePersonContext");
      return;
    }
    console.log("start logout process");
    setErrorMessage('');
    localStorage.removeItem('openConversations');
    localStorage.removeItem('token');
    localStorage.setItem('isLogged', 'false');
    setIsLogged(false);
    console.log(isLivePersonContext);
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
      <div className="page-wrapper">
        <div className="main-container custom-scrollbar">
          <LogoutModal ref={modalRef} handleLogout={handleLogout} />
          <TriggerModal
            isOpen={isModalOpen}
            message={modalMessage}
            onClose={() => setModalOpen(false)}
          />
          {isLogged === undefined ? null : ( <Routes>
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
          </Routes>)}
        </div>
      </div>
    </Router>
  );
}

export default App;