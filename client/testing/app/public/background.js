importScripts('https://cdn.socket.io/4.3.2/socket.io.min.js');

let lastAlertTime = 0;
const conversationHashSet = new Set();
const prevConversationsMap = new Map();
const alertCooldown = 5 * 60 * 1000; 
let socket = null;
let apiBaseURL = '/api';
let notificationTimeDuration = 2; 
let intervalId = null; 
let authToken = null; 

self.addEventListener('install', (event) => {
  console.log('Service Worker installed.');
  self.skipWaiting(); 
});

self.addEventListener('activate', (event) => {
  console.log('Service Worker activated.');
  event.waitUntil(
    (async () => {
      await self.clients.claim(); 
      setupSocketConnection();
    })()
  );
});

self.addEventListener('fetch', (event) => {
  event.respondWith(
    fetch(event.request).catch((error) => {
      console.error('Fetch failed:', error);
      return new Response(
        JSON.stringify({ error: 'Network request failed' }),
        { status: 500, headers: { 'Content-Type': 'application/json' } }
      );
    })
  );
});

self.addEventListener('message',async (event) => {
  const { type, data } = event.data;
  switch (type) {
    case 'SET_API_BASE_URL':
      apiBaseURL = data;
      console.log('Service Worker: API Base URL set to:', apiBaseURL);
      setupSocketConnection();
      break;
    case 'SET_NOTIFICATION_TIME':
      notificationTimeDuration = data;
      console.log(`Notification time updated to: ${notificationTimeDuration} minutes`);
      setupSocketConnection();
      break;
    case 'LOGIN':
      const { tokenData, API_BASE_URL,notificationTimeData } = data;
      authToken = tokenData;
      apiBaseURL = API_BASE_URL; 
      if (typeof notificationTimeData === 'number') {
        notificationTimeDuration = notificationTimeData;
        console.log(`Notification time set via LOGIN: ${notificationTimeDuration} minutes`);
      }
      console.log('User logged in. Starting fetch interval.');
      setupSocketConnection();
      break;

    case 'LOGOUT':
      authToken = null;
      console.log('User logged out. Stopping WebSocket connection.');
      if (socket) socket.disconnect();
      break;

    case 'GET_CONVERSATIONS':
      if(intervalId===null){
        setupSocketConnection();
    }
    break;

    case 'GET_TOKEN':
      setupSocketConnection();
      break;

      case 'WAKE_UP':
        console.log('Service Worker received WAKE_UP message.');
        if (!authToken) {
          requestAuthToken();    
        }
        if (!apiBaseURL) {
          requestApiBaseURL();    
        }
        if (!notificationTimeDuration) {
          requestNotificationTimeDuration();  
        }
        if (!intervalId) {
          console.log('Restarting fetch interval after WAKE_UP.');
          setupSocketConnection();
        }
        break;
      
    default:
      console.warn('Unhandled message type:', type);
  }
});

function setupSocketConnection() {
  try {
    const socketURL = `${self.location.origin}/test/`;
    console.log('Attempting to connect to:', socketURL);
    socket = io(socketURL, {
      transports: ['websocket'],
      auth: {
        token: authToken
      },
      withCredentials: true,
      reconnectionAttempts: 5,
      reconnectionDelay: 3000,
      path: '/test/socket.io'
    });

    socket.on('connect', () => {
      console.log('Connected to server');
      socket.emit('get_open_calls');
    });

    socket.on('open_calls_update', (data) => {
      console.log('Received open conversations:', data);
      processConversations(data);
    });

    socket.on('connect_error', (err) => {
      console.error('Socket connection error:', err);
      sendLogoutToClients();
    });

    socket.on('disconnect', () => {
      console.log('Socket disconnected');
    });
  } catch (error) {
    console.error('Error setting up socket connection:', error);
  }
}


function requestAuthToken() {
  console.log("Auth token is missing. Requesting from ServiceWorker clients...");
  self.clients.matchAll().then((clients) => {
    if (clients.length === 0) {
      console.log("No clients available to request the token.");
      return;
    }
    let tokenReceived = false;
    clients.forEach((client) => {
      const messageChannel = new MessageChannel();
      messageChannel.port1.onmessage = (event) => {
        const { type, token } = event.data;
        if (type === "TOKEN_RESPONSE" && token) {
          authToken = token;
          tokenReceived = true;
          console.log("Token received from client:", authToken);
        }
      };
      client.postMessage({ type: "GET_TOKEN" }, [messageChannel.port2]);
    });
    if (!tokenReceived) {
      console.log("Token request sent, but no response yet.");
    }
  });
}

function requestApiBaseURL() {
  console.log("API Base URL is missing. Requesting from ServiceWorker clients...");
  self.clients.matchAll().then((clients) => {
    if (clients.length === 0) {
      console.log("No clients available to request the API Base URL.");
      return;
    }
    let urlReceived = false;
    clients.forEach((client) => {
      const messageChannel = new MessageChannel();
      messageChannel.port1.onmessage = (event) => {
        const { type, receivedUrl } = event.data;
        if (type === "API_BASE_URL_RESPONSE" && receivedUrl) {
          apiBaseURL = receivedUrl;
          urlReceived = true;
          console.log("API Base URL received from client:", apiBaseURL);
        }
      };
      client.postMessage({ type: "SET_API_BASE_URL" }, [messageChannel.port2]);
    });
    if (!urlReceived) {
      console.log("API Base URL request sent, but no response yet.");
    }
  });
}

function requestNotificationTimeDuration() {
  console.log("Notification time is missing. Requesting from ServiceWorker clients...");
  self.clients.matchAll().then((clients) => {
    if (clients.length === 0) {
      console.log("No clients available to request the Notification time.");
      return;
    }
    let notificationTimeReceived = false;
    clients.forEach((client) => {
      const messageChannel = new MessageChannel();
      messageChannel.port1.onmessage = (event) => {
        const { type, receivedTime } = event.data;
        if (type === "NOTIFICATION_TIME_RESPONSE" && typeof receivedTime === "number") {
          notificationTimeReceived = true;
          console.log("Notification time received from client:", receivedTime);
          notificationTimeDuration = receivedTime;
        }
      };
      client.postMessage({ type: "GET_NOTIFICATION_TIME" }, [messageChannel.port2]);
    });

    if (!notificationTimeReceived) {
      console.log("Notification time request sent, but no response yet.");
    }
  });
}

function sendLogoutToClients() {
  console.log('Sending logout message to clients');
  self.clients.matchAll().then((clients) => {
    clients.forEach((client) => {
      client.postMessage({
        type: 'LOGOUT_INVALID_TOKEN', 
      });
    });
  });
}


async function processConversations(newData) {
  const newConversations = newData.data || [];
  if(newConversations.length===0){
    conversationHashSet.clear();
    sendConversationsToClients();
    return;
  }
  console.log("Processing new conversations:", newConversations);
  const currentTime = Date.now();
  // const validConversations = [];
  // for (const conversation of newConversations) {
  //   const { conversationId, GSR, status, duration } = conversation;
  //   if (!conversationId || GSR === undefined || duration === undefined) {
  //     console.warn('Invalid conversation data:', conversation);
  //     continue;
  //   }
  //   if (status === "CLOSE") {
  //     continue; 
  //   }
  //   const previousConversation = prevConversationsMap.get(conversationId);
  //   if (!previousConversation || previousConversation.duration !== duration) {
  //     validConversations.push(conversation);
  //     prevConversationsMap.set(conversationId, conversation);
  //   }
  // }
  // if (validConversations.length > 0) {
  //   conversationHashSet.clear();
  //   validConversations.forEach((conversation) => conversationHashSet.add(conversation));
  // }
  // await analyzeGSRValues(validConversations, currentTime);
  conversationHashSet.clear(); 
  newConversations.forEach((conversation) => {
    conversationHashSet.add(conversation); 
  });
  await analyzeGSRValues(conversationHashSet, currentTime);
  sendConversationsToClients();
}

async function analyzeGSRValues(conversations, currentTime) {
  for (const { GSR } of conversations) {
    if (GSR > 0.8 && currentTime - lastAlertTime > notificationTimeDuration * 60 * 1000) {
      lastAlertTime = currentTime;
      sendAlertToClients('אותרה שיחה ברמת אובדנות גבוהה');
    }
  }
}


// function fillPrevMap(){
//   conversationHashSet.forEach((conversation) => {
//     const { conversationId } = conversation;
//     if (conversationId) {
//       prevConversationsMap.set(conversationId, conversation);
//     } else {
//       console.warn("Conversation missing an ID:", conversation);
//     }
//   });
// }


function sendConversationsToClients() {
  const now=new Date();
  const conversationsArray = Array.from(conversationHashSet); 
  console.log("Just before sending");
  console.log(conversationsArray);
  self.clients.matchAll().then((clients) => {
    clients.forEach((client) => {
      client.postMessage({
        type: 'OPEN_CONVERSATIONS',
        conversations: conversationsArray,
        date: now.toISOString(),
      });
    });
  });
}

function sendAlertToClients(message) {
  console.log('Sending alert to clients:', message);
  self.clients.matchAll().then((clients) => {
    clients.forEach((client) => {
      client.postMessage({
        type: 'ALERT',
        message: message,
      });
    });
  });
}