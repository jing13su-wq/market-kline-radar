$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

python .\scanner.py --once --exchange bybit-linear --bootstrap-volume-alerts --chart-limit 180
