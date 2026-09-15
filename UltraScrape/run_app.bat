@echo off
title UltraScrape Studio
cd /d "%~dp0"
python main.py
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ================================================================
    echo [ERROR] La aplicacion se cerro con un error (codigo %ERRORLEVEL%).
    echo Si falta alguna libreria, ejecuta primero: install_dependencies.bat
    echo ================================================================
    pause
)
