chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === "openDiscordIframe") {
        let iframe = document.getElementById('discord_iframe');
        if (!iframe) {
            iframe = document.createElement('iframe');
            iframe.style.display = 'none';
            iframe.id = 'discord_iframe';
            iframe.src = 'https://discord.com/channels/@me';
            document.body.appendChild(iframe);
        }
    } else if (request.action === "removeDiscordIframe") {
        let iframe = document.getElementById('discord_iframe');
        if (iframe) {
            iframe.parentNode.removeChild(iframe);
        }
    }
});
