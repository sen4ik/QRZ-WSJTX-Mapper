// Open a connection to keep the service worker alive
const port = chrome.runtime.connect();

async function checkAndReloadCallsign() {
    const newCallsign = await fetchCurrentCallsign();
    if (!newCallsign) return;

    // Request the last callsign from the background script
    const lastFetchedCallsign = await new Promise((resolve) => {
        chrome.runtime.sendMessage({ type: "getLastCallsign" }, (response) => {
            resolve(response);
        });
    });

    // If the new callsign is different, update storage
    if (newCallsign !== lastFetchedCallsign) {
        chrome.runtime.sendMessage({ type: "setLastCallsign", callsign: newCallsign });
        const qrzUrl = `https://www.qrz.com/db/${newCallsign}`;
        window.location.href = qrzUrl;
    }
}

setInterval(checkAndReloadCallsign, 1000);

async function highlightCallSign() {
    const callsignSpanClass = 'span.hamcall';

    const adiFileCallsignsList = await fetchAdiFileCallsigns();
    const callSignSpanElement = document.querySelector(callsignSpanClass);
    const callSignElementText = callSignSpanElement ? callSignSpanElement.textContent.trim() : null;

    if (callSignSpanElement && callSignElementText) {
        if (adiFileCallsignsList.includes(callSignElementText)) {
            callSignSpanElement.style.border = '2px solid lime';
            callSignSpanElement.style.padding = '5px';
            callSignSpanElement.style.marginBottom = '10px';
            callSignSpanElement.style.display = 'inline-block';
        } else {
            callSignSpanElement.style.border = 'none';
            callSignSpanElement.style.padding = '0';
            callSignSpanElement.style.marginBottom = '0';
        }
    }
}

highlightCallSign();