let lastAlertTime = 0;
const conversationHashSet = new Set();
const prevConversationsMap = new Map();
const alertCooldown = 5 * 60 * 1000; 
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
      setupInterval();
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
      setupInterval(); 
      break;
    case 'SET_NOTIFICATION_TIME':
      setupInterval();
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
      setupInterval();
      break;

    case 'LOGOUT':
      authToken = null;
      console.log('User logged out. Stopping fetch interval.');
      stopInterval();
      break;

    case 'GET_CONVERSATIONS':
      if(intervalId===null){
        setupInterval();
    }
    break;

    case 'GET_TOKEN':
      setupInterval();
      break;

    case 'WAKE_UP':
      console.log('Service Worker received WAKE_UP message.');
      if (!intervalId) {
        console.log('Restarting fetch interval after WAKE_UP.');
        setupInterval(); 
      }
      break;
      
    default:
      console.warn('Unhandled message type:', type);
  }
});

function setupInterval() {
  console.log("Try to set up interval");
  stopInterval();
  if (!authToken) {
    requestAuthToken();
    return;
  }
  if (!apiBaseURL) {
    requestApiBaseURL();
    return;
  }
  if (!notificationTimeDuration) {
    requestNotificationTimeDuration();
    return;
  }
  startInterval();
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
          startInterval();
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
          startInterval();
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
          startInterval();
        }
      };
      client.postMessage({ type: "GET_NOTIFICATION_TIME" }, [messageChannel.port2]);
    });

    if (!notificationTimeReceived) {
      console.log("Notification time request sent, but no response yet.");
    }
  });
}


function startInterval() {
  getOpenConversations();
  try {
    intervalId = setInterval(() => {
      stopInterval();
  if (!authToken) {
    requestAuthToken();
  }
  if (!apiBaseURL) {
    requestApiBaseURL();
  }
  if (!notificationTimeDuration) {
    requestNotificationTimeDuration();
  }
      console.log("Interval triggered at:", Date.now());
      const currentTime = new Date();
      const currentSecond = currentTime.getSeconds();
      console.log(currentSecond)
      if ([0, 15, 30, 45].includes(currentSecond)) {
        if (!authToken) {
          console.log("Auth token missing during interval. Skipping fetch.");
          return;
        }
        getOpenConversations();
      }
    }, 1000); 
    console.log("Interval setup complete. ID:", intervalId);
  } catch (error) {
    console.error("Error setting up interval:", error);
  }
}

function stopInterval() {
  console.log("Try to stop interval");
  if (intervalId) {
    console.log('Stopping interval:', intervalId);
    clearInterval(intervalId);
    intervalId = null;
  }
}


async function getOpenConversations() {
  if (!authToken) {
    console.warn('No auth token available. Skipping fetch.');
    return;
  }
  if (!apiBaseURL) {
    console.warn('No url available. Skipping fetch.');
    return;
  }
  try {
    const response = await fetch(`${apiBaseURL}/get_open_calls`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `${authToken}`,
      },
      credentials: 'include',
      cache: 'no-store',
    });

    if (response.ok) {
      console.log("open call happened");
      const data = await response.json();
      processConversations(data);
    } else {
      console.log(apiBaseURL);
      console.log(response.status);
      console.warn('Error fetching conversations:', response.statusText);
      if (response.status === 401 || response.status === 403 || response.status === 502) {
        console.log('Token expired or invalid. Logging out...');
        sendLogoutToClients(); 
        stopInterval(); 
        authToken = null; 
      }
    }
  } catch (error) {
    console.error('Error fetching conversations:', error);
  }
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
  console.log("Processing new conversations:", newConversations);
  if (newConversations.length === 0) {
    sendConversationsToClients(newConversations);
    return;
  }
  const currentTime = Date.now();
  const validConversations = [];
  for (const conversation of newConversations) {
    const { conversationId, GSR, status, duration } = conversation;
    if (!conversationId || GSR === undefined || duration === undefined) {
      console.warn('Invalid conversation data:', conversation);
      continue;
    }
    if (status === "CLOSE") {
      continue; 
    }
    const previousConversation = prevConversationsMap.get(conversationId);
    if (!previousConversation || previousConversation.duration !== duration) {
      validConversations.push(conversation);
      prevConversationsMap.set(conversationId, conversation);
    }
  }
  if (validConversations.length > 0) {
    conversationHashSet.clear();
    validConversations.forEach((conversation) => conversationHashSet.add(conversation));
  }
  console.log("Before Analyze");
  await analyzeGSRValues(validConversations, currentTime);
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


function fillPrevMap(){
  conversationHashSet.forEach((conversation) => {
    const { conversationId } = conversation;
    if (conversationId) {
      prevConversationsMap.set(conversationId, conversation);
    } else {
      console.warn("Conversation missing an ID:", conversation);
    }
  });
}


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