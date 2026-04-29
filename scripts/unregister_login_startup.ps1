$ErrorActionPreference = "Stop"

$RunKey = "HKCU:\Software\Microsoft\Windows\CurrentVersion\Run"
Remove-ItemProperty -Path $RunKey -Name "MarketKlineRadarBot" -ErrorAction SilentlyContinue
Remove-ItemProperty -Path $RunKey -Name "MarketKlineRadarLoop" -ErrorAction SilentlyContinue
Write-Host "Removed login startup entries."
