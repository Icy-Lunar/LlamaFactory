param(
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$WizardArguments
)

$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath $PSScriptRoot
$env:PYTHONUTF8 = '1'

$identity = [Security.Principal.WindowsIdentity]::GetCurrent()
$principal = [Security.Principal.WindowsPrincipal]::new($identity)
$isAdmin = $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    $forwarded = @('-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', $PSCommandPath) + $WizardArguments
    $process = Start-Process -FilePath 'powershell.exe' -Verb RunAs -ArgumentList $forwarded -Wait -PassThru
    exit $process.ExitCode
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

& $bootstrapPython -X utf8 "$PSScriptRoot/scripts/terminal_wizard.py" @WizardArguments
$result = $LASTEXITCODE
exit $result
