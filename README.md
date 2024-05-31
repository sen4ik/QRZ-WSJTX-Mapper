You need Node.js installed on your machine. I am using version 20.13.
First, run the server that will read local WSJTX ADI file so that the Chrome extension can read it.
To run on Windows using PowerShell, do
```
$env:ADI_FILE_PATH = "C:\Users\kn6rdd\AppData\Local\WSJT-X\wsjtx_log.adi"
node server.js
```
where you should replace `"C:\Users\kn6rdd\AppData\Local\WSJT-X\wsjtx_log.adi"` with path to ADI file on your machine.
<br/>
Alternatively, you can edit `server/server.js` file and tweak the path there.

When the server started and there are no errors in the PowerShell, to see if it works you will need to navigate to http://localhost:3088/file in your browser and that should
load your ADI file content.

Now we need to load up the extension into Chrome.
- Navigate to `chrome://extensions/` in the Chrome browser.
- Enable Developer mode.
- Load unpacked extension and select the `chrome_extension` directory.

That is pretty much it.
Now if you navigate to QRZ page for someone that is in your ADI file, there will be green border around their callsign on the QRZ webpage.