@echo off
title PrismFetch V3 - Téléchargeur Intelligent Multi-Plateformes
color 0A

echo ================================================================
echo    PrismFetch V3 - Téléchargeur Intelligent Multi-Plateformes
echo    Version: 3.0.0 FINAL - Créé par: Metadata
echo    Basé sur: https://github.com/Romechko/PrismFetchV2
echo    
echo    🆕 NOUVELLES FONCTIONNALITÉS V3:
echo    • 🧠 IA d'apprentissage automatique des compatibilités
echo    • 🔒 Sécurité TOR/Bypass/Sandbox avancée  
echo    • 📝 Renommage intelligent contextuel
echo    • 🎨 Interface moderne avec 5 onglets
echo    • ⚡ Optimisations ultra-performantes
echo ================================================================
echo.

python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python non trouvé! 
    echo    Téléchargez Python 3.8+ depuis: https://python.org
    echo    Assurez-vous de cocher "Add to PATH"
    pause
    exit /b 1
)

if not exist "app\gui\main_window.py" (
    echo ⚠️ Fichiers V3 manquants détectés!
    echo    Consultez INSTALLATION_GUIDE.md pour les instructions
    echo    Copiez tous les fichiers [code_file:XX] dans les bons dossiers
    pause
    exit /b 1
)

echo 🚀 Lancement de PrismFetch V3...
echo    Interface moderne avec IA d'apprentissage
echo    Support TOR, bypass géo-restrictions, sandbox sécurisé
echo.
python main.py

if errorlevel 1 (
    echo.
    echo ❌ Erreur lors du lancement!
    echo.
    echo 🔧 Solutions possibles:
    echo    1. Lancez install.bat pour installer les dépendances
    echo    2. Vérifiez que tous les fichiers V3 sont copiés
    echo    3. Consultez INSTALLATION_GUIDE.md
    echo.
    pause
)
