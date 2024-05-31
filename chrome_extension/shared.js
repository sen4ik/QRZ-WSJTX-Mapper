async function fetchAdiFileCallsigns() {
    try {
        const response = await fetch('http://localhost:3088/file');
        if (!response.ok) {
            throw new Error('Network response was not ok ' + response.statusText);
        }
        const content = await response.text();
        const strippedData = await stripCallData(content);

        // document.getElementById('fileContent').textContent = strippedData.join('\n');
        // console.log(strippedData);

        return strippedData;
    } catch (error) {
        console.error('There has been a problem with your fetch operation:', error);
        return [];
    }
}

async function stripCallData(data) {
    const lines = data.split('\n');
    const callSigns = [];

    const callRegex = /<call:\d+>(.*?) <gridsquare/;

    lines.forEach(line => {
        const match = line.match(callRegex);
        if (match && match[1]) {
            callSigns.push(match[1].trim());
        }
    });

    return callSigns;
}