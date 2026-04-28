$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

python .\scanner.py --loop --interval-minutes 5 --exchange bybit-linear --chart-limit 180
