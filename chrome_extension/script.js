chrome.tabs.query({ active: true, currentWindow: true }, async (tabs) => {

    const callsignSpanClass = 'span.csignm.hamcall';
    const result = chrome.scripting.executeScript({
        target: { tabId: tabs[0].id },
        func: (callsignSpanClass) => {
            fetchAdiFileCallsigns()
                .then(adiFileCallsignsList => {
                    const callSignSpanElement = document.querySelector(callsignSpanClass);
                    const callSignElementText = callSignSpanElement ? callSignSpanElement.textContent.trim() : null;

                    if (adiFileCallsignsList.includes(callSignElementText)) {
                        // const messageElement = document.createElement('div');
                        // messageElement.textContent = `Match found: ${callSignElementText}`;
                        // messageElement.style.color = 'green';
                        // document.body.appendChild(messageElement);
                        callSignSpanElement.style.border = '2px solid lime';
                        callSignSpanElement.style.padding = '5px';
                        callSignSpanElement.style.marginBottom = '10px';
                        callSignSpanElement.style.display = 'inline-block';
                    } else {
                        callSignSpanElement.style.border = 'none';
                        callSignSpanElement.style.padding = '0';
                        callSignSpanElement.style.marginBottom = '0';
                    }
                })
                .catch(error => {
                    console.error('Error fetching file content: ', error);
                });
        },
        args: [callsignSpanClass]
    });

});
