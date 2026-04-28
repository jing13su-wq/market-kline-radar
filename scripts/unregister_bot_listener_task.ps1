$ErrorActionPreference = "Stop"

$TaskName = "MarketKlineRadarBot"
Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
Write-Host "Unregistered scheduled task: $TaskName"
