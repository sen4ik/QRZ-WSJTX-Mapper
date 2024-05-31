async function highlightCallSign() {
    const callsignSpanClass = 'span.csigns.hamcall';

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