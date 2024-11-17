async function fetchCurrentCallsign() {
    try {
        const response = await fetch('http://localhost:3088/dx_input');
        if (!response.ok) throw new Error('Network response was not ok ' + response.statusText);
        const currentCallsign = await response.text();
        return currentCallsign.trim();
    } catch (error) {
        console.error('Error fetching callsign:', error);
    }
    return null;
}

async function fetchAdiFileCallsigns() {
    try {
        const response = await fetch('http://localhost:3088/file');
        if (!response.ok) {
            throw new Error('Network response was not ok ' + response.statusText);
        }
        const content = await response.text();

        // document.getElementById('fileContent').textContent = content;
        // console.log(content);

        return content;
    } catch (error) {
        console.error('There has been a problem with your fetch operation:', error);
        return [];
    }
}