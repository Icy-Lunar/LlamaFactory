@echo off
setlocal
cd /d "%~dp0"

powershell.exe -NoLogo -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\launch_windows.ps1" %*
set "RESULT=%ERRORLEVEL%"

if "%RESULT%"=="10" (
    echo.
    echo A system driver was installed. Restart Windows, then run start_windows.bat again.
) else if not "%RESULT%"=="0" (
    echo.
    echo Startup stopped with exit code %RESULT%.
)

exit /b %RESULT%
