$ErrorActionPreference = "Stop"

$TaskName = "MarketKlineRadar"
Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
Write-Host "Unregistered scheduled task: $TaskName"
