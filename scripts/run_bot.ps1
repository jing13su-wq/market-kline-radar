$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

python .\telegram_bot.py --exchange bybit-linear --interval 15m --top-n 10 --chart-limit 180
