$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

python .\scanner.py --once --exchange bybit-linear --bootstrap-volume-alerts --chart-limit 180 --min-gain-pct 5 --min-gainer-volume-quote 25000000 --max-alerts 0
