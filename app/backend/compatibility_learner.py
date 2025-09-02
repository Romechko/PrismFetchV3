#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
PrismFetch V3 - IA d'Apprentissage des Compatibilités
Version 3.0.0 FINAL - Créé par Metadata
"""

import sqlite3
import json
from pathlib import Path
from urllib.parse import urlparse

class CompatibilityLearner:
    """IA d'apprentissage des compatibilités site→outil"""

    def __init__(self):
        self.db_path = Path("data/compatibility.db")
        self.predefined_sites = {
            "youtube.com": {"tool": "yt-dlp", "confidence": 0.98},
            "e-hentai.org": {"tool": "gallery-dl", "confidence": 0.95, "adult": True},
            "bunkr.cr": {"tool": "gallery-dl", "confidence": 0.90},
            "pornhub.com": {"tool": "yt-dlp", "confidence": 0.92, "adult": True},
            "soundcloud.com": {"tool": "yt-dlp", "confidence": 0.94}
        }
        self.setup_database()
        print("📊 Base de données d'apprentissage initialisée")
        print(f"📚 {len(self.predefined_sites)} compatibilités prédéfinies chargées")
        print("🎓 Système d'apprentissage V3 initialisé")

    def setup_database(self):
        """Configuration de la base SQLite"""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS compatibility (
                domain TEXT PRIMARY KEY,
                tool TEXT,
                confidence REAL
            )
        """)
        for domain, info in self.predefined_sites.items():
            cursor.execute("""
                INSERT OR IGNORE INTO compatibility (domain, tool, confidence)
                VALUES (?, ?, ?)
            """, (domain, info["tool"], info["confidence"]))
        conn.commit()
        conn.close()

    def get_best_tool(self, url):
        """Obtention du meilleur outil pour une URL"""
        try:
            domain = urlparse(url).netloc.lower()
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT tool FROM compatibility WHERE domain = ?", (domain,))
            row = cursor.fetchone()
            conn.close()
            if row:
                return row[0]
            for site, config in self.predefined_sites.items():
                if site in domain:
                    return config["tool"]
            return "yt-dlp"
        except:
            return "yt-dlp"

    def record_download_result(self, url, tool, success):
        """Enregistrement du résultat dans la base"""
        try:
            domain = urlparse(url).netloc.lower()
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO compatibility (domain, tool, confidence)
                VALUES (?, ?, ?)
            """, (domain, tool, 1.0 if success else 0.0))
            conn.commit()
            conn.close()
        except:
            pass

    def get_all_supported_sites(self):
        """Liste des sites supportés"""
        return list(self.predefined_sites.keys())
