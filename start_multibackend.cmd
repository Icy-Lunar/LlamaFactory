@echo off
setlocal
cd /d "%~dp0"

fltmc >nul 2>&1
if errorlevel 1 (
    echo Requesting administrator privileges for optional system-driver installation...
    powershell.exe -NoProfile -ExecutionPolicy Bypass -Command "Start-Process -FilePath '%~f0' -Verb RunAs"
    exit /b
)

powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0start_wizard.ps1"
set "RESULT=%ERRORLEVEL%"

if "%RESULT%"=="10" (
    echo.
    echo A system driver was installed. Reboot Windows, then double-click this file again.
) else if not "%RESULT%"=="0" (
    echo.
    echo Startup stopped with exit code %RESULT%. Review the message above.
)

pause
exit /b %RESULT%
