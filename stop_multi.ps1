# Stop Multi-Device System
# Kills all backend servers and the load balancer, and closes their PowerShell windows

Write-Host ""
Write-Host "=" * 70 -ForegroundColor Red
Write-Host "🛑 Stopping Multi-Device System..." -ForegroundColor Red
Write-Host "=" * 70 -ForegroundColor Red
Write-Host ""

# Define all ports to kill
$ports = @(9888, 9889, 9890, 9891, 9892)
$killedPids = @()

foreach ($port in $ports) {
    try {
        $connections = Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue
        
        if ($connections) {
            $processIds = $connections | Select-Object -ExpandProperty OwningProcess -Unique
            
            foreach ($processId in $processIds) {
                $process = Get-Process -Id $processId -ErrorAction SilentlyContinue
                if ($process) {
                    $processName = $process.ProcessName
                    
                    # Get the parent process (PowerShell window)
                    $parentId = $null
                    try {
                        $wmi = Get-CimInstance Win32_Process -Filter "ProcessId = $processId" -ErrorAction SilentlyContinue
                        if ($wmi) {
                            $parentId = $wmi.ParentProcessId
                        }
                    } catch {}
                    
                    # Kill the main process
                    Stop-Process -Id $processId -Force
                    Write-Host "✅ Killed process '$processName' (PID: $processId) on port $port" -ForegroundColor Green
                    $killedPids += $processId
                    
                    # Kill the parent PowerShell window if it exists
                    if ($parentId) {
                        $parentProcess = Get-Process -Id $parentId -ErrorAction SilentlyContinue
                        if ($parentProcess -and $parentProcess.ProcessName -eq "powershell") {
                            Stop-Process -Id $parentId -Force -ErrorAction SilentlyContinue
                            Write-Host "   🪟 Closed PowerShell window (PID: $parentId)" -ForegroundColor Cyan
                        }
                    }
                }
            }
        } else {
            Write-Host "⚠️  No process found on port $port" -ForegroundColor Yellow
        }
    }
    catch {
        Write-Host "❌ Error checking port ${port}: $_" -ForegroundColor Red
    }
}

# Also kill any PowerShell windows with specific titles related to the servers
Write-Host ""
Write-Host "🔍 Checking for server PowerShell windows by title..." -ForegroundColor Yellow
$targetTitles = @(
    "Backend Server - Port 9889",
    "Backend Server - Port 9890", 
    "Backend Server - Port 9891",
    "Backend Server - Port 9892",
    "Load Balancer - Port 9888"
)

foreach ($title in $targetTitles) {
    try {
        $windows = Get-Process powershell -ErrorAction SilentlyContinue | Where-Object { $_.MainWindowTitle -eq $title }
        foreach ($window in $windows) {
            if ($window -and $killedPids -notcontains $window.Id) {
                Stop-Process -Id $window.Id -Force
                Write-Host "   🪟 Closed '$title' window (PID: $($window.Id))" -ForegroundColor Cyan
            }
        }
    } catch {}
}

Write-Host ""
Write-Host "=" * 70 -ForegroundColor Green
Write-Host "✅ Multi-Device System Stopped!" -ForegroundColor Green
Write-Host "=" * 70 -ForegroundColor Green
Write-Host ""
