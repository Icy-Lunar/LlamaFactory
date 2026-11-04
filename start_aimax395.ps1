$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath $PSScriptRoot

if (-not $env:PYTHON_BIN) {
    $pythonPath = $null
    $pythonLauncher = Get-Command py -ErrorAction SilentlyContinue
    if ($pythonLauncher) {
        try {
            $pythonPath = & $pythonLauncher.Source -3.12 -c "import sys; print(sys.executable)" 2>$null
        } catch {
            $pythonPath = $null
        }
    }

    if ($pythonPath) {
        $env:PYTHON_BIN = $pythonPath.Trim()
    } elseif (Get-Command python -ErrorAction SilentlyContinue) {
        $env:PYTHON_BIN = (Get-Command python).Source
    } else {
        throw 'Python 3.12 x64 was not found. Install it before running this script.'
    }
}

if (-not $env:VENV_DIR) {
    $env:VENV_DIR = Join-Path $PSScriptRoot '.venv-aimax395-windows'
}
if (-not $env:LLAMAFACTORY_LIGER_PROBE_TIMEOUT) {
    $env:LLAMAFACTORY_LIGER_PROBE_TIMEOUT = '600'
}
if (-not $env:LLAMAFACTORY_DEFAULT_COMPUTE_TYPE) {
    $env:LLAMAFACTORY_DEFAULT_COMPUTE_TYPE = 'fp16'
}

& "$PSScriptRoot/start_webui.ps1" --backend rocm --rocm-profile aimax395 @args
exit $LASTEXITCODE
