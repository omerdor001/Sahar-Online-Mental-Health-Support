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

const basename = window.location.pathname.startsWith("/test") ? "/test" : "/";
const isTestEnvironment = window.location.pathname.startsWith("/test");
const API_BASE_URL = isTestEnvironment ? '/test/api' : '/api';


const handleClose = () => {
  localStorage.removeItem('openConversations');
  localStorage.removeItem('username');
  localStorage.removeItem('token'); 
  localStorage.setItem('isLogged', 'false');
  window.close();
};

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
    const tokenData=localStorage.getItem('token');
    const storedNotificationTime = localStorage.getItem('notificationTime');
    if (storedNotificationTime) {
      setNotificationTime(parseInt(storedNotificationTime, 2));
    }
    if ('serviceWorker' in navigator) {
      navigator.serviceWorker.getRegistration().then((existingRegistration) => {
        if (!existingRegistration) {
      navigator.serviceWorker
        .register(`${basename}/background.js`)
        .then((registration) => {
          console.log('Service Worker registered in app:', registration);
          if (navigator.serviceWorker.controller) {
            navigator.serviceWorker.controller.postMessage({
              type: 'SET_NOTIFICATION_TIME',
              data: notificationTime,
            });
            if (isLogged) {
              navigator.serviceWorker.controller.postMessage({
                type: 'GET_CONVERSATIONS',
              });
            }
          }
        })
        .catch((error) => {
          console.error('Service Worker registration failed in app:', error);
        });
      } else {
        console.log('Service Worker already registered:', existingRegistration);
      }
    });
      const handleServiceWorkerMessage = (event) => {
        const { type, message,conversations:newConversations, date:update_date } = event.data;
        switch (type) {
          case 'ALERT': {
            if (event.stopPropagation) {
              event.stopPropagation();
            }
            setModalMessage(message);
            setModalOpen(true);
            break;
          }
          case 'OPEN_CONVERSATIONS': {
            localStorage.setItem(
              'openConversations',
              JSON.stringify(newConversations)
            );
            if(update_date){
              console.log(update_date);
              localStorage.setItem('conversationsLastUpdateTime', update_date);
            }
            console.log(update_date);
            console.log("Updating conversations in App");
            break;
          }
          case 'GET_TOKEN': {
            event.ports[0].postMessage({
                type: 'TOKEN_RESPONSE',
                token: tokenData || null, 
             });
            break;
          }
          default: {
            console.warn('Unhandled message type:', type);
          }
          
        }
      };
      navigator.serviceWorker.addEventListener('message', handleServiceWorkerMessage);
    const wakeUpInterval = setInterval(() => {
      navigator.serviceWorker.ready.then((registration) => {
        if (registration.active) {
          console.log('Sending WAKE_UP to Service Worker.');
          registration.active.postMessage({ type: 'WAKE_UP' });
        } else {
          console.warn('No active Service Worker found for WAKE_UP.');
        }
      });
    }, 15000); 
    return () => {
      navigator.serviceWorker.removeEventListener('message', handleServiceWorkerMessage);
      clearInterval(wakeUpInterval); 
    };
  }
  }, [notificationTime, isLogged]);

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
      localStorage.setItem('isLogged', 'true');
      setIsLogged(true);
      setErrorMessage('');
      const tokenData = localStorage.getItem('token');
      navigator.serviceWorker.controller?.postMessage({
        type: 'LOGIN',
        data: tokenData
      });
      navigator.serviceWorker.controller?.postMessage({
        type: 'SET_API_BASE_URL',
        data: API_BASE_URL, 
      });
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
    if (navigator.serviceWorker.controller) {
      navigator.serviceWorker.controller.postMessage({ type: 'LOGOUT' });
    }
    navigator.serviceWorker.getRegistration().then((registration) => {
      if (registration) {
        registration.unregister().then((success) => {
          if (success) {
            console.log('Service Worker unregistered successfully.');
          } else {
            console.warn('Failed to unregister Service Worker.');
          }
        });
      } else {
        console.log('No Service Worker registered.');
      }
    });
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
        <button 
          onClick={handleClose} 
          className="absolute top-1 right-1 h-5 w-5 leading-5 rounded-full text-lg font-mono text-black hover:text-gray-500 hover:bg-gray-200"
        >
          &times;
        </button>
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
              element={ !isLogged ? 
                <Login handleLogin={handleLogin} errorMessage={errorMessage} />:
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
