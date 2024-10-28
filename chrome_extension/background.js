chrome.runtime.onConnect.addListener((port) => {
    console.log("Connection established to keep the service worker alive.");
    
    chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
        if (request.type === "getLastCallsign") {
            chrome.storage.local.get(['lastFetchedCallsign'], (result) => {
                sendResponse(result.lastFetchedCallsign || null);
            });
            return true; // Keeps the message channel open for async response
        } else if (request.type === "setLastCallsign") {
            chrome.storage.local.set({ lastFetchedCallsign: request.callsign });
            sendResponse();
        }
    });
});
