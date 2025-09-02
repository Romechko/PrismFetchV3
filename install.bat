@echo off
title Installation PrismFetch V3 - Dépendances
color 0B

echo ================================================================
echo    INSTALLATION DÉPENDANCES PRISMFETCH V3
echo ================================================================
echo.

echo 🔧 Mise à jour pip...
python -m pip install --upgrade pip

echo.
echo 📦 Installation des dépendances V3...
python -m pip install -r requirements.txt

echo.
echo ✅ Installation des dépendances terminée!
echo    Vous pouvez maintenant:
echo    1. Copier les fichiers V3 manquants (voir INSTALLATION_GUIDE.md)
echo    2. Lancer PrismFetchV3.bat
echo.
pause
