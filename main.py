#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
PrismFetch V3 - Point d'entrée principal
Version 3.0.0 FINAL - Créé par Metadata
Migration complète depuis V2
"""

import sys
import os
import traceback
from pathlib import Path

# Ajouter le dossier app au PATH
sys.path.insert(0, str(Path(__file__).parent / "app"))

def check_v3_files():
    """Vérification des fichiers V3"""
    required_files = [
        "app/backend/download_manager.py",
        "app/backend/security_manager.py", 
        "app/backend/compatibility_learner.py",
        "app/gui/main_window.py",
        "config/settings.json"
    ]
    
    missing = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing.append(file_path)
    
    if missing:
        print("❌ Fichiers V3 manquants détectés!")
        print("   Consultez INSTALLATION_GUIDE.md pour les instructions")
        print("   Copiez tous les fichiers [code_file:XX] dans les bons dossiers")
        input("Appuyez sur une touche pour continuer...")
        return False
    
    return True

def create_directories():
    """Création des dossiers nécessaires"""
    directories = [
        "config", "data/downloads", "logs", 
        "sandbox", "quarantine", "tools"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)

def main():
    """Point d'entrée principal"""
    
    print("================================================================")
    print("   PrismFetch V3 - Téléchargeur Intelligent Multi-Plateformes")
    print("   Version: 3.0.0 FINAL - Créé par: Metadata") 
    print("   Basé sur: https://github.com/Romechko/PrismFetchV2")
    print("================================================================")
    print("   🚀 NOUVELLES FONCTIONNALITÉS V3:")
    print("   • 🧠 IA d'apprentissage automatique des compatibilités")
    print("   • 🔒 Sécurité TOR/Bypass/Sandbox avancée")
    print("   • 📝 Renommage intelligent contextuel") 
    print("   • 🎨 Interface moderne avec 5 onglets")
    print("   • ⚡ Optimisations ultra-performantes")
    print("================================================================")
    
    # Créer les dossiers
    create_directories()
    
    # Vérifier les fichiers V3
    if not check_v3_files():
        return
    
    try:
        print("🚀 Démarrage PrismFetch V3")
        
        # Import des modules V3
        from backend.download_manager import DownloadManager
        from backend.security_manager import SecurityManager  
        from backend.compatibility_learner import CompatibilityLearner
        from gui.main_window import PrismFetchMainWindow
        from utils.logger import get_logger
        
        import tkinter as tk
        import ttkbootstrap as ttkb
        
        # Configuration du logger
        logger = get_logger(__name__)
        logger.info("🚀 Démarrage PrismFetch V3")
        
        # Initialisation des managers V3
        compatibility_learner = CompatibilityLearner()
        security_manager = SecurityManager()
        download_manager = DownloadManager(compatibility_learner, security_manager)
        
        # Interface V3
        root = ttkb.Window(themename="darkly")
        app = PrismFetchMainWindow(root, download_manager, security_manager)
        
        logger.info("✅ Interface V3 initialisée")
        print("✅ Interface V3 initialisée")
        
        # Lancement
        root.mainloop()
        
        logger.info("👋 Arrêt de PrismFetch V3")
        print("👋 Arrêt de PrismFetch V3")
        
    except ImportError as e:
        print(f"❌ Module V3 manquant: {e}")
        print("⚠️ Vérifiez que tous les fichiers V3 sont copiés")
        print("📋 Consultez INSTALLATION_GUIDE.md")
        input("Appuyez sur Entrée pour continuer...")
        
    except Exception as e:
        print(f"💥 Erreur critique: {e}")
        print("📋 Consultez les logs dans logs/prismfetch.log")
        traceback.print_exc()
        input("Appuyez sur Entrée pour fermer...")

if __name__ == "__main__":
    main()