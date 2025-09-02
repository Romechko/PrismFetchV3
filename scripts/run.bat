@echo off
chcp 65001 >nul
title PrismFetch FINAL v2.1

pushd "%~dp0" 2>nul
cd .. 2>nul
set PYTHONPATH=%CD%

echo ================================================================
echo PrismFetch FINAL v2.1 - Telechargeur Multi-Plateformes
echo Cree par : Metadata - TELECHARGEMENTS REELS
echo ================================================================
echo.

python --version >nul 2>&1 || (
    echo [X] Python non detecte
    echo [!] Lancez scripts\install.bat
    pause
    exit /b 1
)

python -c "import tkinter" >nul 2>&1 || (
    echo [X] Tkinter non disponible
    pause
    exit /b 1
)

echo Lancement avec selection d'interface...
echo.
python main.py

if errorlevel 1 (
    echo.
    echo [X] Erreur lors du lancement
    pause
)

popd 2>nul
