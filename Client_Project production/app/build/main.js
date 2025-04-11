const basename = window.location.pathname.startsWith("/test") ? "/test" : "/";

if ('serviceWorker' in navigator) {
  navigator.serviceWorker.getRegistration().then((existingRegistration) => {
    if (!existingRegistration) {
      navigator.serviceWorker.register(`${basename}background.js`)
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
} else {
  console.warn('Service Workers are not supported in this browser.');
}

// navigator.serviceWorker.addEventListener('message', (event) => {
//   const data = event.data;

//   if (data.type === 'ALERT') {
//     alert(data.message); 
//   }

//   if (data.type === 'SAVE_CONVERSATIONS') {
//     localStorage.setItem('openConversations', JSON.stringify(data.conversations));
//   }

//   if (data.type === 'GET_CONVERSATIONS') {
//     const storedConversations = JSON.parse(localStorage.getItem('openConversations')) || [];
//     event.ports[0].postMessage(storedConversations);
//   }

// });

// function requestToken() {
//   if (navigator.serviceWorker.controller) {
//     const messageChannel = new MessageChannel();
//     messageChannel.port1.onmessage = (event) => {
//       const token = event.data.token;
//       if (token) {
//         console.log('Received token:', token);
//       }
//     };
//     navigator.serviceWorker.controller.postMessage({ type: 'GET_TOKEN' }, [messageChannel.port2]);
//   }
// }

// setInterval(requestToken, 60 * 1000); 

// function getStoredConversations() {
//   const conversations = JSON.parse(localStorage.getItem('openConversations')) || [];
//   console.log(conversations);
// }
