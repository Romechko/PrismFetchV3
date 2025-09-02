#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
PrismFetch V3 - Point d'entrée ULTRA STABLE
Version 3.0.0 FINAL - Créé par Metadata
Gestion complète des erreurs et encodage
"""

import sys
import os
import traceback
from pathlib import Path

# Forcer encodage UTF-8
if os.name == 'nt':
    import locale
    locale.setlocale(locale.LC_ALL, 'C.UTF-8')

# Ajouter app au PATH
sys.path.insert(0, str(Path(__file__).parent / "app"))

def check_v3_files():
    """Vérification fichiers V3 requis"""
    required_files = [
        "app/backend/download_manager.py",
        "app/backend/security_manager.py", 
        "app/backend/compatibility_learner.py",
        "app/gui/main_window.py",
        "app/utils/logger.py"
    ]
    
    missing = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing.append(file_path)
    
    if missing:
        print("❌ Fichiers V3 manquants détectés!")
        print("   Fichiers requis manquants:")
        for file in missing:
            print(f"   - {file}")
        print("\n   Consultez INSTALLATION_GUIDE.md")
        print("   Copiez les fichiers [code_file:XX] dans les bons dossiers")
        input("\nAppuyez sur Entrée pour continuer...")
        return False
    
    return True

def create_directories():
    """Création des dossiers nécessaires"""
    directories = [
        "config", "data/downloads", "data/torrents", "logs", 
        "sandbox", "quarantine", "tools"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)

def create_default_config():
    """Création config par défaut"""
    config_path = Path("config/settings.json")
    if not config_path.exists():
        config = {
            "version": "3.0.0",
            "app_name": "PrismFetch V3",
            "interface": {
                "theme": "darkly",
                "mode": "simple",
                "language": "fr"
            },
            "download": {
                "default_path": "data/downloads",
                "max_concurrent": 4,
                "timeout": 300,
                "quality": "best"
            },
            "security": {
                "tor_enabled": False,
                "sandbox_enabled": True,
                "tor_port": 9050,
                "control_port": 9051
            },
            "renaming": {
                "enabled": True,
                "template": "[{author}] {title} ({language})",
                "auto_detect": True
            }
        }
        
        try:
            import json
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            print("✅ Configuration par défaut créée")
        except Exception as e:
            print(f"⚠️ Erreur création config: {e}")

def main():
    """Point d'entrée principal ULTRA STABLE"""
    
    # Bannière avec encodage sécurisé
    print("=" * 64)
    print("   PrismFetch V3 - Téléchargeur Intelligent Multi-Plateformes")
    print("   Version: 3.0.0 FINAL - Créé par: Metadata") 
    print("   Basé sur: https://github.com/Romechko/PrismFetchV2")
    print("=" * 64)
    print("   🚀 NOUVELLES FONCTIONNALITÉS V3:")
    print("   • 🧠 IA d'apprentissage automatique des compatibilités")
    print("   • 🔒 Sécurité TOR/Bypass/Sandbox avancée")
    print("   • 📝 Renommage intelligent contextuel") 
    print("   • 🎨 Interface moderne avec 5 onglets")
    print("   • ⚡ Optimisations ultra-performantes")
    print("=" * 64)
    
    # Créer structure
    create_directories()
    create_default_config()
    
    # Vérifier fichiers V3
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
        
        # Support drag & drop avancé
        try:
            from tkinterdnd2 import TkinterDnD
            use_dnd = True
        except ImportError:
            use_dnd = False
        
        # Configuration du logger
        logger = get_logger(__name__)
        logger.info("🚀 Démarrage PrismFetch V3")
        
        # Initialisation des managers V3
        try:
            compatibility_learner = CompatibilityLearner()
            security_manager = SecurityManager()
            download_manager = DownloadManager(compatibility_learner, security_manager)
            
            logger.info("✅ Managers V3 initialisés")
        except Exception as e:
            logger.error(f"❌ Erreur initialisation managers: {e}")
            raise
        
        # Interface V3 avec gestion drag & drop
        try:
            if use_dnd:
                root = TkinterDnD.Tk()
                logger.info("✅ Interface avec drag & drop")
            else:
                root = ttkb.Window(themename="darkly")
                logger.info("✅ Interface standard (sans drag & drop)")
            
            app = PrismFetchMainWindow(root, download_manager, security_manager)
            
            logger.info("✅ Interface V3 initialisée")
            print("✅ Interface V3 initialisée")
            
        except Exception as e:
            logger.error(f"❌ Erreur création interface: {e}")
            raise
        
        # Gestion propre de la fermeture
        def on_closing():
            try:
                logger.info("👋 Fermeture PrismFetch V3")
                
                # Arrêter téléchargements
                if hasattr(download_manager, 'stop_queue'):
                    download_manager.stop_queue()
                
                # Désactiver TOR
                if hasattr(security_manager, 'disable_tor'):
                    security_manager.disable_tor()
                
                root.destroy()
                
            except Exception as e:
                logger.error(f"❌ Erreur fermeture: {e}")
                root.destroy()
        
        root.protocol("WM_DELETE_WINDOW", on_closing)
        
        # Lancement
        try:
            root.mainloop()
            logger.info("👋 Arrêt propre de PrismFetch V3")
            print("👋 Arrêt propre de PrismFetch V3")
            
        except KeyboardInterrupt:
            logger.info("⏹️ Interruption utilisateur")
            print("\n⏹️ Interruption utilisateur")
            
        except Exception as e:
            logger.error(f"❌ Erreur runtime: {e}")
            raise
        
    except ImportError as e:
        print(f"❌ Module V3 manquant: {e}")
        print("⚠️ Vérifiez que tous les fichiers V3 sont copiés correctement")
        print("📋 Consultez INSTALLATION_GUIDE.md pour les instructions")
        print("\n💡 Fichiers requis:")
        print("   - app/gui/main_window.py")
        print("   - app/backend/download_manager.py") 
        print("   - app/backend/security_manager.py")
        print("   - app/backend/compatibility_learner.py")
        print("   - app/utils/logger.py")
        input("\nAppuyez sur Entrée pour continuer...")
        
    except Exception as e:
        print(f"💥 Erreur critique: {e}")
        print("📋 Consultez les logs dans logs/prismfetch.log")
        
        # Trace complète en mode debug
        if "--debug" in sys.argv:
            traceback.print_exc()
        else:
            print("\n💡 Lancez avec --debug pour plus de détails")
        
        input("\nAppuyez sur Entrée pour fermer...")

if __name__ == "__main__":
    main()