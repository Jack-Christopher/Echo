@echo off
setlocal EnableDelayedExpansion
cd /d "%~dp0"

REM Wait for desktop / OneDrive (Task Scheduler has no -Delay on older Windows)
timeout /t 20 /nobreak >nul 2>&1

set "ECHO_LOG_DIR=%LOCALAPPDATA%\Echo\logs"
if not exist "%ECHO_LOG_DIR%" mkdir "%ECHO_LOG_DIR%"
set "ECHO_STARTUP_LOG=%ECHO_LOG_DIR%\startup-last.log"

> "%ECHO_STARTUP_LOG%" echo [%date% %time%] Starting Echo
>> "%ECHO_STARTUP_LOG%" echo Working directory: %CD%

set "PY="
if exist ".venv\Scripts\pythonw.exe" set "PY=.venv\Scripts\pythonw.exe"
if not defined PY if exist ".venv\Scripts\python.exe" set "PY=.venv\Scripts\python.exe"
if not defined PY (
    where pythonw >nul 2>&1 && set "PY=pythonw"
)
if not defined PY set "PY=python"

>> "%ECHO_STARTUP_LOG%" echo Python: %PY%

set PYTHONIOENCODING=utf-8
REM Detach so this console closes; log remains in startup-last.log
start "" /B "%PY%" -m echo.main >> "%ECHO_STARTUP_LOG%" 2>&1
endlocal & exit /b 0
