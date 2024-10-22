const express = require('express');
const fs = require('fs');
const path = require('path');
const cors = require('cors');
const app = express();
const PORT = 3088;

// Use CORS middleware
app.use(cors());

// Path to ADI file
const filePath = process.env.ADI_FILE_PATH || path.join('C:', 'Users', 'kn6rdd', 'AppData', 'Local', 'WSJT-X', 'wsjtx_log.adi');

const dxInputLogPath = path.join(__dirname, '..', 'py', 'dx_input_log.txt');

app.get('/file', (req, res) => {
    fs.readFile(filePath, 'utf8', (err, data) => {
        if (err) {
            console.error('Error reading file:', err);
            return res.status(500).send('Error reading file');
        }
		console.log("Sending data");
        res.send(data);
    });
});

app.get('/dx_input', (req, res) => {
    fs.readFile(dxInputLogPath, 'utf8', (err, data) => {
        if (err) {
            console.error('Error reading dx_input_log.txt:', err);
            return res.status(500).send('Error reading dx_input_log.txt');
        }
        console.log("Sending DX input data");
        res.send(data);
    });
});

app.listen(PORT, () => {
    console.log(`Server running at http://localhost:${PORT}`);
});
