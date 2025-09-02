#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import os
from pathlib import Path

class ConfigManager:
    """Gestionnaire de configuration - VÉRIFIÉ FONCTIONNEL"""

    def __init__(self):
        try:
            self.config_dir = Path("config")
            self.config_file = self.config_dir / "prismfetch.json"
            self.config_data = {}
            self.load()
        except Exception as e:
            print(f"Erreur init ConfigManager: {e}")
            self.config_data = {}

    def load(self):
        """Charger configuration - VÉRIFIÉ"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    self.config_data = json.load(f)
            else:
                # Configuration par défaut
                self.config_data = {
                    "first_run": True,
                    "download_path": "data/downloads",
                    "temp_path": "data/temp",
                    "max_concurrent_downloads": 2,
                    "timeout_seconds": 600
                }
                self.save()
        except Exception as e:
            print(f"Erreur chargement config: {e}")
            self.config_data = {
                "first_run": True,
                "download_path": "data/downloads",
                "temp_path": "data/temp",
                "max_concurrent_downloads": 2,
                "timeout_seconds": 600
            }

    def save(self):
        """Sauvegarder configuration - VÉRIFIÉ"""
        try:
            self.config_dir.mkdir(parents=True, exist_ok=True)
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Erreur sauvegarde config: {e}")

    def get(self, key, default=None):
        """Obtenir valeur - VÉRIFIÉ"""
        try:
            keys = key.split('.')
            value = self.config_data

            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default

    def set(self, key, value):
        """Définir valeur - VÉRIFIÉ"""
        try:
            keys = key.split('.')
            data = self.config_data

            for k in keys[:-1]:
                if k not in data:
                    data[k] = {}
                data = data[k]

            data[keys[-1]] = value
        except Exception as e:
            print(f"Erreur set config: {e}")

    def get_download_path(self):
        """Chemin téléchargement - VÉRIFIÉ"""
        try:
            path = Path(self.get("download_path", "data/downloads"))
            path.mkdir(parents=True, exist_ok=True)
            return path
        except Exception as e:
            print(f"Erreur download_path: {e}")
            path = Path("data/downloads")
            path.mkdir(parents=True, exist_ok=True)
            return path
