$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $PSScriptRoot
$Out = Join-Path $Root "bot.out.log"
$Err = Join-Path $Root "bot.err.log"
foreach ($Log in @($Out, $Err)) {
  if (Test-Path -LiteralPath $Log) {
    Remove-Item -LiteralPath $Log -Force
  }
}

Start-Process `
  -FilePath "powershell.exe" `
  -ArgumentList @("-NoProfile", "-ExecutionPolicy", "Bypass", "-File", (Join-Path $PSScriptRoot "run_bot.ps1")) `
  -WorkingDirectory $Root `
  -RedirectStandardOutput $Out `
  -RedirectStandardError $Err `
  -WindowStyle Hidden
