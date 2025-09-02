@echo off
chcp 65001 >nul
title PrismFetch FINAL v2.1 - Installation

echo ================================================================
echo PrismFetch FINAL v2.1 - Installation COMPLETE
echo Cree par : Metadata - TELECHARGEMENTS REELS
echo ================================================================
echo.

REM Se placer a la racine
pushd "%~dp0" 2>nul
cd .. 2>nul

REM Verifier Python
echo [1/7] Verification de Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo [X] Python non detecte
    echo [!] Installez Python depuis python.org
    pause
    exit /b 1
) else (
    echo [OK] Python detecte
)

echo [2/7] Mise a jour de pip...
python -m pip install --upgrade pip --quiet >nul 2>&1

echo [3/7] Dependances essentielles...
python -m pip install --upgrade requests urllib3 colorama tqdm Pillow PyYAML --quiet >nul 2>&1

echo [4/7] Pydantic 2.x...
python -m pip uninstall -y pydantic pydantic-core >nul 2>&1
python -m pip install --upgrade "pydantic>=2.11.7" --quiet >nul 2>&1

echo [5/7] yt-dlp (YouTube, Vimeo)...
python -m pip install --upgrade yt-dlp --quiet >nul 2>&1

echo [6/7] gallery-dl (Instagram, TikTok)...
python -m pip install --upgrade gallery-dl --quiet >nul 2>&1

echo [7/7] cyberdrop-dl-patched (CyberDrop, Bunkr)...
python -m pip install --upgrade cyberdrop-dl-patched --quiet >nul 2>&1

echo.
echo Creation des repertoires...
if not exist "data\downloads" mkdir "data\downloads" >nul 2>&1
if not exist "data\temp" mkdir "data\temp" >nul 2>&1
if not exist "data\logs" mkdir "data\logs" >nul 2>&1
if not exist "config" mkdir "config" >nul 2>&1

echo.
echo Verification des outils...
yt-dlp --version >nul 2>&1 && echo [OK] yt-dlp || echo [!] yt-dlp manquant
gallery-dl --version >nul 2>&1 && echo [OK] gallery-dl || echo [!] gallery-dl manquant
cyberdrop-dl-patched --help >nul 2>&1 && echo [OK] cyberdrop-dl-patched || echo [!] cyberdrop-dl-patched manquant

echo.
echo ================================================================
echo INSTALLATION TERMINEE !
echo ================================================================
echo.
echo INTERFACES :
echo   Interface Simple  : scripts\run-simple.bat
echo   Interface Avancee : scripts\run-advanced.bat
echo   Choix auto        : scripts\run.bat
echo.
echo TELECHARGEMENTS REELS ACTIVES !
echo.

pause
popd 2>nul
