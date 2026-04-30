$ErrorActionPreference = "Stop"

$RunKey = "HKCU:\Software\Microsoft\Windows\CurrentVersion\Run"
Remove-ItemProperty -Path $RunKey -Name "MarketKlineRadarBot" -ErrorAction SilentlyContinue
Remove-ItemProperty -Path $RunKey -Name "MarketKlineRadarLoop" -ErrorAction SilentlyContinue
$Startup = [Environment]::GetFolderPath("Startup")
foreach ($LegacyName in @("MarketKlineRadarBot.bat", "MarketKlineRadarLoop.bat")) {
  $LegacyPath = Join-Path $Startup $LegacyName
  if (Test-Path -LiteralPath $LegacyPath) {
    Remove-Item -LiteralPath $LegacyPath -Force
  }
}
Write-Host "Removed login startup entries."
