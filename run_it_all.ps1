$wsjtxPath = "C:\Program Files\wsjtx2.7.0\bin\wsjtx.exe"
$gridTrackerPath = "C:\Users\kn6rdd\AppData\Local\Programs\GridTracker2\GridTracker2.exe"

Start-Process -FilePath $wsjtxPath -ArgumentList "-stylesheet :/qdarkstyle/style.qss"
Start-Sleep -Seconds 5

Start-Process -FilePath $gridTrackerPath
Start-Sleep -Seconds 5

$scriptPath = "$HOME\Desktop\QRZ-WSJTX-Mapper\py\wsjt-x_get_dx_call.py"

# Open a new PowerShell window, set size and run the Python script
Start-Process powershell -ArgumentList '-NoExit -Command "mode con: cols=80 lines=4; cd \"$HOME\Desktop\QRZ-WSJTX-Mapper\py\"; python.exe wsjt-x_get_dx_call.py; pause"' -WindowStyle Normal
