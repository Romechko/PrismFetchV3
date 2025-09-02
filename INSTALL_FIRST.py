#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
PrismFetch V3 - Installation automatisée (PRÉVENTIF)
Version basique pour éviter les erreurs
"""

import subprocess
import sys

def install_dependencies():
    """Installation basique des dépendances"""
    print("🔧 Installation dépendances PrismFetch V3...")
    
    dependencies = [
        "requests", "psutil", "ttkbootstrap", "pillow",
        "yt-dlp", "gallery-dl", "cryptography"
    ]
    
    for dep in dependencies:
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", dep], check=True)
            print(f"✅ {dep} installé")
        except Exception as e:
            print(f"⚠️ Erreur {dep}: {e}")
    
    print("✅ Installation terminée")

if __name__ == "__main__":
    install_dependencies()
