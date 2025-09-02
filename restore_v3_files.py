#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import requests

# 1) Configuration
ROOT = os.path.abspath(os.path.dirname(__file__))
GITHUB_BASE = "https://raw.githubusercontent.com/Romechko/PrismFetchV2/main"

# Structure attendue : { chemin_relatif: url_suffix }
FILES = {
    "app/core/orchestrator.py":      "app/core/orchestrator.py",
    "app/utils/system_utils.py":     "app/utils/system_utils.py",
    "config/prismfetch.yaml":        "config/prismfetch.yaml",
    # ajoutez ici tous les autres fichiers V3 (simple_interface.py, advanced_interface.py, etc.)
}

def download_file(relpath, url_suffix):
    dest = os.path.join(ROOT, relpath)
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    url = f"{GITHUB_BASE}/{url_suffix}"
    print(f"Téléchargement de {relpath} depuis GitHub…")
    resp = requests.get(url)
    if resp.status_code == 200:
        with open(dest, "wb") as f:
            f.write(resp.content)
        print(f"  → OK")
        return True
    else:
        print(f"  × Échec {resp.status_code}")
        return False

def main():
    missing = []
    for relpath, suffix in FILES.items():
        path = os.path.join(ROOT, relpath)
        if not os.path.isfile(path):
            if not download_file(relpath, suffix):
                missing.append(relpath)
    if missing:
        print("\nCertains fichiers n'ont pas pu être récupérés :")
        for p in missing:
            print("  -", p)
        sys.exit(1)
    print("\nTous les fichiers manquants ont été restaurés. Vous pouvez relancer PrismFetch V3.")
    sys.exit(0)

if __name__ == "__main__":
    try:
        import requests
    except ImportError:
        print("Le module requests est requis. Installez-le avec : pip install requests")
        sys.exit(1)
    main()
