#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import shutil
import sys

# Chemin racine du projet (lancez ce script depuis PrismFetchV3/)
ROOT = os.path.abspath(os.path.dirname(__file__))

# Structure attendue : mapping dossier -> liste de fichiers
EXPECTED = {
    "app": ["__init__.py"],
    os.path.join("app", "core"): ["__init__.py", "config_manager.py", "download_manager.py", "orchestrator.py"],
    os.path.join("app", "gui"): ["__init__.py", "simple_interface.py", "advanced_interface.py"],
    os.path.join("app", "utils"): ["__init__.py", "logger.py", "system_utils.py"],
    "config": ["prismfetch.yaml"],
    "data": [],  # dossiers data/downloads et data/logs créés à l'exécution
    os.path.join("data", "downloads"): [],
    os.path.join("data", "logs"): [],
    "scripts": ["install.bat", "run.bat"],
    "": ["main.py", "requirements.txt"],
}

# Dossier de référence où se trouvent les fichiers sources si absents
# ADAPTEZ ce chemin vers l’emplacement de vos fichiers fournis (code_file…)
REFERENCE = os.path.join(ROOT, "reference_files")

missing_files = []

def ensure_dir(path):
    if not os.path.isdir(path):
        print(f"  Création du dossier manquant : {path}")
        os.makedirs(path, exist_ok=True)

def copy_from_reference(dest_rel_path):
    src = os.path.join(REFERENCE, dest_rel_path)
    dst = os.path.join(ROOT, dest_rel_path)
    if os.path.isfile(src):
        print(f"    Copie de {dest_rel_path} depuis reference_files/")
        shutil.copy2(src, dst)
        return True
    return False

def main():
    print(f"Analyse de la structure dans {ROOT}\n")
    for rel_dir, files in EXPECTED.items():
        dir_path = os.path.join(ROOT, rel_dir)
        ensure_dir(dir_path)
        for fname in files:
            fpath = os.path.join(dir_path, fname)
            if not os.path.isfile(fpath):
                print(f"Fichier manquant : {os.path.join(rel_dir, fname)}")
                if copy_from_reference(os.path.join(rel_dir, fname)):
                    continue
                missing_files.append(os.path.join(rel_dir, fname))
    if missing_files:
        print("\nLes fichiers suivants sont toujours manquants :")
        for f in missing_files:
            print("  -", f)
        print("\nPlacez-les dans le dossier reference_files/ ou corrigez manuellement.")
        sys.exit(1)
    print("\nTous les fichiers et dossiers sont en place. Vous pouvez relancer PrismFetch V3.")
    sys.exit(0)

if __name__ == "__main__":
    main()
