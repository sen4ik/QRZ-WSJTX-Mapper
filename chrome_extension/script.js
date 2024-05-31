chrome.tabs.query({ active: true, currentWindow: true }, async (tabs) => {
    const tabId = tabs[0].id;

    chrome.scripting.executeScript({
        target: { tabId: tabId },
        func: async () => {
            const callsignSpanClass = 'span.csigns.hamcall';
            const adiFileCallsignsList = await fetchAdiFileCallsigns();
            const callSignSpanElement = document.querySelector(callsignSpanClass);
            const callSignElementText = callSignSpanElement ? callSignSpanElement.textContent.trim() : null;

            if (callSignSpanElement && callSignElementText) {
                if (adiFileCallsignsList.includes(callSignElementText)) {
                    return `Callsign ${callSignElementText} found in the ADI file.`;
                } else {
                    return `Callsign ${callSignElementText} is NOT found in the ADI file.`;
                }
            } else {
                return '';
            }
        }
    }, (results) => {
        const message = results[0].result;
        document.getElementById('messageContainer').innerText = message;
    });
});