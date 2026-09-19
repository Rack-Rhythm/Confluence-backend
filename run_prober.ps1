<#
.SYNOPSIS
    Starts the Confluence Backend Keep-Alive Auto-Prober.
.DESCRIPTION
    Sends lightweight keep-alive probes to Render backend every 12 minutes
    so that Render free tier never sleeps / spins down.
#>
$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition

$VenvPython = Join-Path $ScriptDir "..\venv\Scripts\python.exe"
if (Test-Path $VenvPython) {
    $PythonExe = $VenvPython
} else {
    $PythonExe = "python"
}

Write-Host ">>> Launching Confluence Auto-Prober..." -ForegroundColor Cyan
& $PythonExe (Join-Path $ScriptDir "auto_prober.py") $args
