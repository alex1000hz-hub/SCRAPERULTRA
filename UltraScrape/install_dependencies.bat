@echo off
title UltraScrape - Instalador de Dependencias
color 0b
echo ================================================================
echo           ⚡ ULTRASCRAPE - INSTALADOR DE DEPENDENCIAS
echo ================================================================
echo.
echo [1/2] Instalando paquetes de Python (PySide6, requests, lxml, openpyxl, etc.)...
python -m pip install --upgrade pip
python -m pip install -r "%~dp0requirements.txt"
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] Hubo un problema al instalar las dependencias con pip.
    pause
    exit /b %ERRORLEVEL%
)

echo.
echo [2/2] Instalando binarios del navegador Playwright...
python -m playwright install
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [AVISO] No se completó la descarga de Playwright, pero el modo estático funcionará.
)

echo.
echo ================================================================
echo   Instalacion completada con exito.
echo   Ya puedes iniciar UltraScrape haciendo doble clic en 'run_app.bat'
echo ================================================================
echo.
pause
