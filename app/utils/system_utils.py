#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import subprocess
import sys

def check_dependencies() -> list:
    """
    Vérifie la présence des modules Python requis.
    Retourne la liste des packages manquants.
    """
    missing = []
    try:
        import tkinter, requests, pathlib
    except ImportError as e:
        name = e.name if hasattr(e, 'name') else str(e).split()[-1]
        missing.append(name)
    return missing

def install_dependencies(packages: list):
    """
    Installe les packages manquants via pip.
    """
    if not packages:
        return
    cmd = [sys.executable, "-m", "pip", "install", "--upgrade"] + packages
    subprocess.run(cmd, check=True)
