$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

python .\scanner.py --once --exchange bybit-linear --test-symbol SOLUSDT --chart-limit 180
