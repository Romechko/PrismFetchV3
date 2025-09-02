@echo off
chcp 65001 >nul
title PrismFetch FINAL v2.1 - Interface Avancee

pushd "%~dp0" 2>nul
cd .. 2>nul
set PYTHONPATH=%CD%

echo ================================================================
echo PrismFetch FINAL v2.1 - Interface Avancee
echo Cree par : Metadata - TELECHARGEMENTS PAR LOTS REELS
echo ================================================================
echo.

python main.py --advanced

if errorlevel 1 pause
popd 2>nul
