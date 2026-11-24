$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath $PSScriptRoot
$env:PYTHONUTF8 = '1'

if ($env:PYTHON_BIN) {
    $bootstrapPython = $env:PYTHON_BIN
} elseif (Test-Path -LiteralPath "$PSScriptRoot/.venv/Scripts/python.exe") {
    $bootstrapPython = "$PSScriptRoot/.venv/Scripts/python.exe"
} else {
    $python = Get-Command python -ErrorAction SilentlyContinue
    if (-not $python) {
        & "$PSScriptRoot/scripts/launch_windows.ps1" @args
        exit $LASTEXITCODE
    }
    $bootstrapPython = $python.Source
}

& $bootstrapPython -X utf8 "$PSScriptRoot/scripts/bootstrap_webui.py" @args
exit $LASTEXITCODE
