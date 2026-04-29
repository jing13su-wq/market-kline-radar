$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

python -u .\telegram_bot.py --exchange bybit-linear --interval 15m --chart-limit 180
