param(
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$LaunchArguments
)

$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot
Set-Location -LiteralPath $projectRoot
$env:PYTHONUTF8 = '1'

function Test-CompatiblePython {
    param([string]$Executable)

    if (-not $Executable) {
        return $false
    }

    if (-not (Test-Path -LiteralPath $Executable -PathType Leaf)) {
        $command = Get-Command $Executable -ErrorAction SilentlyContinue
        if (-not $command) {
            return $false
        }
        $Executable = $command.Source
    }

    try {
        & $Executable -X utf8 -c "import sys, venv; raise SystemExit(0 if (3, 11) <= sys.version_info[:2] <= (3, 13) else 1)" 2>$null
        return $LASTEXITCODE -eq 0
    } catch {
        return $false
    }
}

function Find-CompatiblePython {
    $candidates = [System.Collections.Generic.List[string]]::new()
    if ($env:PYTHON_BIN) {
        $candidates.Add($env:PYTHON_BIN)
    }

    $localEnvironment = Join-Path $projectRoot '.venv\Scripts\python.exe'
    if (Test-Path -LiteralPath $localEnvironment) {
        $candidates.Add($localEnvironment)
    }

    $launcher = Get-Command py -ErrorAction SilentlyContinue
    if ($launcher) {
        foreach ($version in @('-3.12', '-3.13', '-3.11')) {
            try {
                $resolved = & $launcher.Source $version -c "import sys; print(sys.executable)" 2>$null
                if ($LASTEXITCODE -eq 0 -and $resolved) {
                    $candidates.Add($resolved.Trim())
                }
            } catch {
                continue
            }
        }
    }

    foreach ($commandName in @('python3.12', 'python3', 'python')) {
        $command = Get-Command $commandName -ErrorAction SilentlyContinue
        if ($command) {
            $candidates.Add($command.Source)
        }
    }

    $knownLocations = @(
        (Join-Path $env:LOCALAPPDATA 'Programs\Python\Python312\python.exe'),
        (Join-Path $env:ProgramFiles 'Python312\python.exe')
    )
    foreach ($candidate in $knownLocations) {
        if ($candidate) {
            $candidates.Add($candidate)
        }
    }

    foreach ($candidate in $candidates | Select-Object -Unique) {
        if (Test-CompatiblePython $candidate) {
            if (Test-Path -LiteralPath $candidate -PathType Leaf) {
                return (Resolve-Path -LiteralPath $candidate).Path
            }
            return (Get-Command $candidate -ErrorAction Stop).Source
        }
    }
    return $null
}

function Install-Python312 {
    $winget = Get-Command winget -ErrorAction SilentlyContinue
    if (-not $winget) {
        throw 'Python 3.11-3.13 with the venv module was not found, and winget is unavailable. Install Python 3.12 x64, then run this file again.'
    }

    Write-Host 'Python 3.12 was not found. Installing the official Python 3.12 package with winget...'
    & $winget.Source install --id Python.Python.3.12 --exact --silent --scope user --accept-package-agreements --accept-source-agreements
    if ($LASTEXITCODE -notin @(0, 3010)) {
        throw "winget could not install Python 3.12 (exit code $LASTEXITCODE)."
    }
}

$bootstrapPython = Find-CompatiblePython
if (-not $bootstrapPython) {
    Install-Python312
    $bootstrapPython = Find-CompatiblePython
}
if (-not $bootstrapPython) {
    throw 'Python 3.12 was installed but could not be located. Open a new terminal and run start_windows.bat again.'
}

$env:PYTHON_BIN = $bootstrapPython
Write-Host "Bootstrap Python: $bootstrapPython"

$identity = [Security.Principal.WindowsIdentity]::GetCurrent()
$principal = [Security.Principal.WindowsPrincipal]::new($identity)
$isAdmin = $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    $forwarded = @(
        '-NoLogo',
        '-NoProfile',
        '-ExecutionPolicy',
        'Bypass',
        '-File',
        ('"{0}"' -f $PSCommandPath)
    )
    foreach ($argument in $LaunchArguments) {
        $forwarded += ('"{0}"' -f $argument.Replace('"', '\"'))
    }
    Write-Host 'Requesting administrator privileges for optional system-driver installation...'
    $process = Start-Process -FilePath 'powershell.exe' -Verb RunAs -ArgumentList $forwarded -Wait -PassThru
    exit $process.ExitCode
}

if ($LaunchArguments.Count -eq 0) {
    & (Join-Path $projectRoot 'start_wizard.ps1')
} else {
    & (Join-Path $projectRoot 'start_multibackend.ps1') @LaunchArguments
}
exit $LASTEXITCODE
