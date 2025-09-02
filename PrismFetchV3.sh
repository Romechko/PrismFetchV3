#!/bin/bash

# PrismFetch V3 - Script de lancement Linux/macOS
# Version 3.0.0 FINAL - Créé par Metadata

echo "================================================================"
echo "   PrismFetch V3 - Téléchargeur Intelligent Multi-Plateformes"
echo "   Version: 3.0.0 FINAL - Créé par: Metadata"  
echo "   Basé sur: https://github.com/Romechko/PrismFetchV2"
echo ""
echo "   🆕 NOUVELLES FONCTIONNALITÉS V3:"
echo "   • 🧠 IA d'apprentissage automatique"
echo "   • 🔒 Sécurité TOR/Bypass/Sandbox"
echo "   • 📝 Renommage intelligent contextuel"
echo "   • 🎨 Interface moderne avec 5 onglets"
echo "================================================================"

if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 non trouvé!"
    echo "   Installez Python 3.8+ avec votre gestionnaire de paquets"
    echo "   Ubuntu/Debian: sudo apt install python3 python3-pip python3-tk"
    echo "   macOS: brew install python3"
    exit 1
fi

if [ ! -f "app/gui/main_window.py" ]; then
    echo "⚠️ Fichiers V3 manquants détectés!"
    echo "   Consultez INSTALLATION_GUIDE.md pour les instructions"
    echo "   Copiez tous les fichiers [code_file:XX] dans les bons dossiers"
    read -p "Appuyez sur Entrée pour continuer..."
    exit 1
fi

echo "🚀 Lancement de PrismFetch V3..."
python3 main.py
