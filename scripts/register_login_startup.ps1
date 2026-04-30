$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $PSScriptRoot
$RunKey = "HKCU:\Software\Microsoft\Windows\CurrentVersion\Run"
$BotStarter = Join-Path $PSScriptRoot "start_bot_background.ps1"
$LoopStarter = Join-Path $PSScriptRoot "start_loop_background.ps1"
$Startup = [Environment]::GetFolderPath("Startup")
foreach ($LegacyName in @("MarketKlineRadarBot.bat", "MarketKlineRadarLoop.bat")) {
  $LegacyPath = Join-Path $Startup $LegacyName
  if (Test-Path -LiteralPath $LegacyPath) {
    Remove-Item -LiteralPath $LegacyPath -Force
  }
}

Set-ItemProperty `
  -Path $RunKey `
  -Name "MarketKlineRadarBot" `
  -Value "powershell.exe -NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File `"$BotStarter`""

Set-ItemProperty `
  -Path $RunKey `
  -Name "MarketKlineRadarLoop" `
  -Value "powershell.exe -NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File `"$LoopStarter`""

Write-Host "Registered login startup entries:"
Get-ItemProperty -Path $RunKey -Name MarketKlineRadarBot,MarketKlineRadarLoop |
  Select-Object MarketKlineRadarBot, MarketKlineRadarLoop
