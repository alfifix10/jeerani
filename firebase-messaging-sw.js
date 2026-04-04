// Service Worker for Push Notifications
// Jeerani — دردش مع جيرانك

importScripts('https://www.gstatic.com/firebasejs/10.14.0/firebase-app-compat.js');
importScripts('https://www.gstatic.com/firebasejs/10.14.0/firebase-messaging-compat.js');

firebase.initializeApp({
    apiKey: "AIzaSyBxr265lCyx0GJw02oE9GQev8kBQRgiTZw",
    authDomain: "jiranak-e9ee2.firebaseapp.com",
    projectId: "jiranak-e9ee2",
    messagingSenderId: "196785031299",
    appId: "1:196785031299:web:08147b2c4fc0023d2b73b6"
});

const messaging = firebase.messaging();

// إشعارات الخلفية
messaging.onBackgroundMessage(function(payload) {
    const title = payload.data.title || 'Jeerani';
    const options = {
        body: payload.data.body || 'رسالة جديدة',
        icon: 'data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><text y=".9em" font-size="90">💬</text></svg>',
        badge: 'data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><text y=".9em" font-size="90">💬</text></svg>',
        dir: 'rtl',
        tag: 'jeerani-msg',
        renotify: true,
        data: payload.data
    };
    self.registration.showNotification(title, options);
});

// لما يضغط على الإشعار
self.addEventListener('notificationclick', function(event) {
    event.notification.close();
    event.waitUntil(
        clients.matchAll({ type: 'window', includeUncontrolled: true }).then(function(clientList) {
            for (let client of clientList) {
                if (client.url.includes('jeerani') && 'focus' in client) {
                    return client.focus();
                }
            }
            return clients.openWindow('/');
        })
    );
});
