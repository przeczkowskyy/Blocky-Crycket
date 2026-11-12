@echo off
rem BLOCKY and CRYCKET - panel zespolu. Zamkniecie tego okna zatrzymuje panel.
cd /d "%~dp0.."
where python >nul 2>nul
if %errorlevel%==0 (
  python panel\serwer.py %*
) else (
  py -3 panel\serwer.py %*
)
if errorlevel 1 pause
