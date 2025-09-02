@echo off
chcp 65001 >nul
title PrismFetch FINAL v2.1 - Interface Simple

pushd "%~dp0" 2>nul
cd .. 2>nul
set PYTHONPATH=%CD%

echo ================================================================
echo PrismFetch FINAL v2.1 - Interface Simple
echo Cree par : Metadata - TELECHARGEMENTS REELS
echo ================================================================
echo.

python main.py --simple

if errorlevel 1 pause
popd 2>nul
