$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath $PSScriptRoot
$env:PYTHONUTF8 = '1'

if ($args.Count -eq 0) {
    & "$PSScriptRoot/start_wizard.ps1"
    exit $LASTEXITCODE
}

if ($env:PYTHON_BIN) {
    $bootstrapPython = $env:PYTHON_BIN
} else {
    $bootstrapPython = $null
    $launcher = Get-Command py -ErrorAction SilentlyContinue
    if ($launcher) {
        try {
            $bootstrapPython = & $launcher.Source -3.12 -c "import sys; print(sys.executable)" 2>$null
        } catch {
            $bootstrapPython = $null
        }
    }
    if (-not $bootstrapPython) {
        $python = Get-Command python -ErrorAction SilentlyContinue
        if (-not $python) {
            throw 'Python 3.12 x64 was not found.'
        }
        $bootstrapPython = $python.Source
    }
}

& $bootstrapPython -X utf8 "$PSScriptRoot/scripts/bootstrap_multibackend.py" @args
exit $LASTEXITCODE
