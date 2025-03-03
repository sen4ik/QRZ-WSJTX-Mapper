$wsjtxPath = "C:\Program Files\wsjtx\bin\wsjtx.exe"
$gridTrackerPath = "C:\Program Files (x86)\GridTracker\GridTracker.exe"

Start-Process -FilePath $wsjtxPath -ArgumentList "-stylesheet :/qdarkstyle/style.qss"
Start-Sleep -Seconds 5

Start-Process -FilePath $gridTrackerPath
Start-Sleep -Seconds 5

$scriptPath = "$HOME\Desktop\QRZ-WSJTX-Mapper\py\wsjt-x_get_dx_call.py"

# Open a new PowerShell window, set size and run the Python script
Start-Process powershell -ArgumentList '-NoExit -Command "mode con: cols=80 lines=4; cd \"$HOME\Desktop\QRZ-WSJTX-Mapper\py\"; python.exe wsjt-x_get_dx_call.py; pause"' -WindowStyle Normal
