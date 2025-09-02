#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
PrismFetch V3 - Installation Dépendances AUTOMATIQUE
Script pour installer automatiquement toutes les dépendances requises
"""

import subprocess
import sys
import os
from pathlib import Path

def install_package(package):
    """Installation d'un package Python"""
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])
        print(f"✅ {package} installé avec succès")
        return True
    except subprocess.CalledProcessError:
        print(f"❌ Erreur installation {package}")
        return False

def main():
    print("🚀 Installation des dépendances PrismFetch V3")
    print("=" * 50)

    # Liste des dépendances requises
    dependencies = [
        "ttkbootstrap",
        "psutil", 
        "requests",
        "tkinterdnd2",
        "urllib3",
        "pathlib2"
    ]

    installed = 0
    failed = 0

    for package in dependencies:
        print(f"📦 Installation de {package}...")
        if install_package(package):
            installed += 1
        else:
            failed += 1

    print("=" * 50)
    print(f"📊 Résultat: {installed} installés, {failed} échecs")

    if failed == 0:
        print("✅ Toutes les dépendances sont installées!")
        print("🚀 Vous pouvez maintenant lancer PrismFetch V3")
    else:
        print("⚠️ Certaines dépendances ont échoué")
        print("💡 Essayez de les installer manuellement:")
        for package in dependencies:
            print(f"   pip install {package}")

    input("\nAppuyez sur Entrée pour continuer...")

if __name__ == "__main__":
    main()
