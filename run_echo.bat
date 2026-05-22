@echo off
cd /d "%~dp0"
if exist .venv\Scripts\activate.bat call .venv\Scripts\activate.bat
REM qt.conf in project root configures DPI awareness for Windows
python -m echo.main %*
