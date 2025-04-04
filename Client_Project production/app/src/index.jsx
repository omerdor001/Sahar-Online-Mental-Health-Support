import React from 'react';
import ReactDOM from 'react-dom';
import App from './App';

if ('serviceWorker' in navigator) {
  window.addEventListener('load', () => {
    navigator.serviceWorker.getRegistration().then((existingRegistration) => {
      if (!existingRegistration) {
        navigator.serviceWorker.register('/background.js')
          .then((registration) => {
            console.log('Service Worker registered with scope:', registration.scope);
          })
          .catch((error) => {
            console.error('Service Worker registration failed:', error);
          });
      } else {
        console.log('Service Worker already registered with scope:', existingRegistration.scope);
      }
    }).catch((error) => {
      console.error('Error checking Service Worker registration:', error);
    });
  });
} else {
  console.warn('Service Workers are not supported in this browser.');
}

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)




