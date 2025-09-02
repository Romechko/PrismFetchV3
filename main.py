#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
PrismFetch V3 - Point d'entrée principal
Téléchargeur Intelligent Multi-Plateformes avec IA
Version 3.0.0 FINAL - Créé par Metadata
Basé sur: https://github.com/Romechko/PrismFetchV2
"""

import sys
import os
import tkinter as tk
from pathlib import Path

# Ajout du dossier app au path Python
sys.path.insert(0, str(Path(__file__).parent / "app"))

def main():
    """Point d'entrée principal de PrismFetch V3"""
    
    try:
        print("🚀 Lancement de PrismFetch V3...")
        print("💎 Version 3.0.0 FINAL - Créé par Metadata")
        print("🧠 IA + TOR + Renommage + Interface moderne")
        print("-" * 50)
        
        # Vérification dépendances V3
        try:
            import ttkbootstrap
            import requests
            import psutil
        except ImportError as e:
            print(f"❌ Dépendance V3 manquante: {e}")
            print("💡 Exécutez: pip install -r requirements.txt")
            print("🔧 Ou lancez: install.bat")
            input("Appuyez sur Entrée pour continuer...")
            sys.exit(1)
        
        # Import des modules V3
        try:
            from gui.main_window import PrismFetchMainWindow
            from backend.download_manager import DownloadManager
            from backend.security_manager import SecurityManager
            from backend.compatibility_learner import CompatibilityLearner
            from utils.logger import get_logger
        except ImportError as e:
            print(f"❌ Module V3 manquant: {e}")
            print("⚠️ Vérifiez que tous les fichiers V3 sont copiés")
            print("📋 Consultez INSTALLATION_GUIDE.md")
            input("Appuyez sur Entrée pour continuer...")
            sys.exit(1)
        
        # Initialisation logger V3
        logger = get_logger("main")
        logger.info("🚀 Démarrage PrismFetch V3")
        
        # Initialisation des managers V3
        compatibility_learner = CompatibilityLearner()
        security_manager = SecurityManager()
        download_manager = DownloadManager(compatibility_learner, security_manager)
        
        # Lancement interface V3
        root = tk.Tk()
        app = PrismFetchMainWindow(root, download_manager, security_manager)
        
        logger.info("✅ Interface V3 initialisée")
        
        # Boucle principale
        try:
            root.mainloop()
        except KeyboardInterrupt:
            logger.info("👋 Arrêt demandé par utilisateur")
        except Exception as e:
            logger.error(f"💥 Erreur interface: {e}")
            raise
        
        logger.info("👋 Arrêt de PrismFetch V3")
        
    except Exception as e:
        print(f"💥 Erreur critique: {e}")
        print("📋 Consultez les logs dans logs/prismfetch.log")
        input("Appuyez sur Entrée pour fermer...")
        sys.exit(1)

if __name__ == "__main__":
    main()
