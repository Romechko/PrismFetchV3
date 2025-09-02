#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
PrismFetch V3 - CompatibilityLearner ULTRA STABLE
Version 3.0.0 FINAL - Créé par Metadata
Base de données SQLite avec sites pré-configurés
"""

import sqlite3
import json
import time
from pathlib import Path
from urllib.parse import urlparse

try:
    from utils.logger import get_logger
except ImportError:
    import logging
    def get_logger(name):
        logging.basicConfig(level=logging.INFO)
        return logging.getLogger(name)

class CompatibilityLearner:
    """Système d'apprentissage des compatibilités site→outil"""
    
    def __init__(self, db_path="data/compatibility.db"):
        """Initialisation avec base SQLite"""
        self.db_path = Path(db_path)
        self.logger = get_logger(__name__)
        
        # Sites pré-configurés avec confiance
        self.predefined_sites = {
            # Vidéo mainstream
            "youtube.com": {"tool": "yt-dlp", "confidence": 0.98, "category": "video"},
            "youtu.be": {"tool": "yt-dlp", "confidence": 0.98, "category": "video"},
            "dailymotion.com": {"tool": "yt-dlp", "confidence": 0.95, "category": "video"},
            "vimeo.com": {"tool": "yt-dlp", "confidence": 0.95, "category": "video"},
            
            # Musique
            "soundcloud.com": {"tool": "yt-dlp", "confidence": 0.94, "category": "audio"},
            "bandcamp.com": {"tool": "yt-dlp", "confidence": 0.92, "category": "audio"},
            "spotify.com": {"tool": "yt-dlp", "confidence": 0.85, "category": "audio"},
            
            # Contenu adulte
            "pornhub.com": {"tool": "yt-dlp", "confidence": 0.92, "category": "adult", "adult": True},
            "youporn.com": {"tool": "yt-dlp", "confidence": 0.92, "category": "adult", "adult": True},
            "xvideos.com": {"tool": "yt-dlp", "confidence": 0.90, "category": "adult", "adult": True},
            "xhamster.com": {"tool": "yt-dlp", "confidence": 0.88, "category": "adult", "adult": True},
            "redtube.com": {"tool": "yt-dlp", "confidence": 0.87, "category": "adult", "adult": True},
            
            # Galeries et manga
            "e-hentai.org": {"tool": "gallery-dl", "confidence": 0.95, "category": "gallery", "adult": True},
            "exhentai.org": {"tool": "gallery-dl", "confidence": 0.95, "category": "gallery", "adult": True},
            "nhentai.net": {"tool": "gallery-dl", "confidence": 0.94, "category": "gallery", "adult": True},
            "gelbooru.com": {"tool": "gallery-dl", "confidence": 0.93, "category": "gallery"},
            "danbooru.donmai.us": {"tool": "gallery-dl", "confidence": 0.93, "category": "gallery"},
            
            # Plateformes d'images
            "imgur.com": {"tool": "gallery-dl", "confidence": 0.90, "category": "images"},
            "flickr.com": {"tool": "gallery-dl", "confidence": 0.88, "category": "images"},
            "deviantart.com": {"tool": "gallery-dl", "confidence": 0.87, "category": "images"},
            
            # Social media
            "twitter.com": {"tool": "gallery-dl", "confidence": 0.85, "category": "social"},
            "x.com": {"tool": "gallery-dl", "confidence": 0.85, "category": "social"},
            "instagram.com": {"tool": "gallery-dl", "confidence": 0.83, "category": "social"},
            "reddit.com": {"tool": "gallery-dl", "confidence": 0.82, "category": "social"},
            
            # File sharing
            "bunkr.cr": {"tool": "gallery-dl", "confidence": 0.90, "category": "filehost"},
            "bunkr.is": {"tool": "gallery-dl", "confidence": 0.90, "category": "filehost"},
            "bunkr.si": {"tool": "gallery-dl", "confidence": 0.90, "category": "filehost"},
            "imgbox.com": {"tool": "gallery-dl", "confidence": 0.88, "category": "filehost"},
            
            # Autres
            "twitch.tv": {"tool": "yt-dlp", "confidence": 0.89, "category": "streaming"},
            "tiktok.com": {"tool": "yt-dlp", "confidence": 0.86, "category": "video"}
        }
        
        # Initialiser base de données
        self.init_database()
        self.load_predefined_compatibilities()
        
        print("📊 Base de données d'apprentissage initialisée")
        print(f"📚 {len(self.predefined_sites)} compatibilités prédéfinies chargées")
        print("🎓 Système d'apprentissage V3 initialisé")
        
        self.logger.info("🎓 CompatibilityLearner V3 initialisé")
    
    def init_database(self):
        """Initialisation base SQLite"""
        try:
            self.db_path.parent.mkdir(parents=True, exist_ok=True)
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Table principale des compatibilités
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS compatibility (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    domain TEXT UNIQUE NOT NULL,
                    tool TEXT NOT NULL,
                    confidence REAL NOT NULL DEFAULT 0.5,
                    category TEXT DEFAULT 'unknown',
                    success_count INTEGER DEFAULT 0,
                    failure_count INTEGER DEFAULT 0,
                    last_tested TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_adult BOOLEAN DEFAULT FALSE,
                    notes TEXT
                )
            """)
            
            # Index pour performances
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_domain ON compatibility(domain)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_tool ON compatibility(tool)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_confidence ON compatibility(confidence)")
            
            # Table historique des téléchargements
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS download_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    domain TEXT NOT NULL,
                    url_hash TEXT,
                    tool_used TEXT NOT NULL,
                    success BOOLEAN NOT NULL,
                    duration REAL,
                    file_size INTEGER,
                    error_message TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_history_domain ON download_history(domain)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_history_timestamp ON download_history(timestamp)")
            
            conn.commit()
            conn.close()
            
            self.logger.info("📊 Base de données d'apprentissage initialisée")
            
        except Exception as e:
            self.logger.error(f"❌ Erreur initialisation BD: {e}")
            raise
    
    def load_predefined_compatibilities(self):
        """Chargement des sites pré-configurés dans la BD"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            loaded_count = 0
            for domain, config in self.predefined_sites.items():
                cursor.execute("""
                    INSERT OR REPLACE INTO compatibility 
                    (domain, tool, confidence, category, success_count, is_adult, notes)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    domain,
                    config["tool"],
                    config["confidence"],
                    config.get("category", "unknown"),
                    10,  # Pré-supposer quelques succès
                    config.get("adult", False),
                    f"Site pré-configuré - {config.get('category', 'unknown')}"
                ))
                loaded_count += 1
            
            conn.commit()
            conn.close()
            
            self.logger.info(f"📚 {loaded_count} compatibilités prédéfinies chargées")
            
        except Exception as e:
            self.logger.error(f"❌ Erreur chargement sites: {e}")
    
    def get_best_tool(self, url):
        """Obtention du meilleur outil pour une URL"""
        try:
            domain = urlparse(url).netloc.lower()
            
            # Nettoyer le domaine
            if domain.startswith('www.'):
                domain = domain[4:]
            
            # Recherche exacte en BD
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT tool, confidence FROM compatibility 
                WHERE domain = ? 
                ORDER BY confidence DESC 
                LIMIT 1
            """, (domain,))
            
            result = cursor.fetchone()
            conn.close()
            
            if result:
                tool, confidence = result
                self.logger.debug(f"🎯 Outil trouvé pour {domain}: {tool} (confiance: {confidence:.2f})")
                return tool
            
            # Recherche par sous-domaine
            for site_domain, config in self.predefined_sites.items():
                if site_domain in domain or domain in site_domain:
                    self.logger.debug(f"🎯 Correspondance partielle {domain} → {config['tool']}")
                    return config["tool"]
            
            # Fallback par type d'URL
            return self._guess_tool_by_url_pattern(url)
            
        except Exception as e:
            self.logger.error(f"❌ Erreur sélection outil: {e}")
            return "yt-dlp"  # Fallback sûr
    
    def _guess_tool_by_url_pattern(self, url):
        """Devine l'outil selon des motifs d'URL"""
        url_lower = url.lower()
        
        # Motifs vidéo
        video_patterns = ["watch", "video", "v=", "/v/", "embed", "player"]
        if any(pattern in url_lower for pattern in video_patterns):
            return "yt-dlp"
        
        # Motifs galerie
        gallery_patterns = ["gallery", "album", "g/", "galleries", "collection"]
        if any(pattern in url_lower for pattern in gallery_patterns):
            return "gallery-dl"
        
        # Motifs image
        image_extensions = [".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp"]
        if any(ext in url_lower for ext in image_extensions):
            return "gallery-dl"
        
        # Défaut
        return "yt-dlp"
    
    def record_download_result(self, url, tool_used, success, duration=None, file_size=None, error_message=None):
        """Enregistrement du résultat d'un téléchargement"""
        try:
            domain = urlparse(url).netloc.lower()
            if domain.startswith('www.'):
                domain = domain[4:]
            
            # Hash URL pour éviter de stocker l'URL complète
            import hashlib
            url_hash = hashlib.md5(url.encode()).hexdigest()[:16]
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Enregistrer dans l'historique
            cursor.execute("""
                INSERT INTO download_history 
                (domain, url_hash, tool_used, success, duration, file_size, error_message)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (domain, url_hash, tool_used, success, duration, file_size, error_message))
            
            # Mettre à jour les statistiques de compatibilité
            if success:
                cursor.execute("""
                    UPDATE compatibility 
                    SET success_count = success_count + 1, 
                        last_tested = CURRENT_TIMESTAMP,
                        confidence = MIN(0.99, confidence + 0.01)
                    WHERE domain = ? AND tool = ?
                """, (domain, tool_used))
            else:
                cursor.execute("""
                    UPDATE compatibility 
                    SET failure_count = failure_count + 1, 
                        last_tested = CURRENT_TIMESTAMP,
                        confidence = MAX(0.01, confidence - 0.05)
                    WHERE domain = ? AND tool = ?
                """, (domain, tool_used))
            
            # Si aucune entrée mise à jour, créer une nouvelle
            if cursor.rowcount == 0:
                initial_confidence = 0.8 if success else 0.2
                cursor.execute("""
                    INSERT OR IGNORE INTO compatibility 
                    (domain, tool, confidence, success_count, failure_count)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    domain, tool_used, initial_confidence,
                    1 if success else 0,
                    0 if success else 1
                ))
            
            conn.commit()
            conn.close()
            
            self.logger.info(f"📈 Résultat enregistré: {domain} + {tool_used} = {'✅' if success else '❌'}")
            
        except Exception as e:
            self.logger.error(f"❌ Erreur enregistrement résultat: {e}")
    
    def get_site_statistics(self, domain=None):
        """Statistiques pour un domaine ou globales"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            if domain:
                # Stats spécifiques à un domaine
                cursor.execute("""
                    SELECT tool, confidence, success_count, failure_count, last_tested
                    FROM compatibility WHERE domain = ?
                    ORDER BY confidence DESC
                """, (domain,))
                
                results = cursor.fetchall()
                
            else:
                # Stats globales
                cursor.execute("""
                    SELECT 
                        COUNT(*) as total_sites,
                        AVG(confidence) as avg_confidence,
                        SUM(success_count) as total_successes,
                        SUM(failure_count) as total_failures
                    FROM compatibility
                """)
                
                results = cursor.fetchone()
            
            conn.close()
            return results
            
        except Exception as e:
            self.logger.error(f"❌ Erreur stats: {e}")
            return None
    
    def get_all_supported_sites(self):
        """Liste de tous les sites supportés avec confiance > 0.5"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT domain, tool, confidence, category 
                FROM compatibility 
                WHERE confidence > 0.5 
                ORDER BY confidence DESC
            """)
            
            results = cursor.fetchall()
            conn.close()
            
            return [
                {
                    "domain": row[0],
                    "tool": row[1], 
                    "confidence": row[2],
                    "category": row[3]
                }
                for row in results
            ]
            
        except Exception as e:
            self.logger.error(f"❌ Erreur liste sites: {e}")
            return []
    
    def cleanup_old_history(self, days_to_keep=30):
        """Nettoyage de l'historique ancien"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                DELETE FROM download_history 
                WHERE timestamp < datetime('now', '-{} days')
            """.format(days_to_keep))
            
            deleted = cursor.rowcount
            conn.commit()
            conn.close()
            
            if deleted > 0:
                self.logger.info(f"🧹 {deleted} entrées d'historique supprimées")
            
            return deleted
            
        except Exception as e:
            self.logger.error(f"❌ Erreur nettoyage: {e}")
            return 0
    
    def export_compatibility_data(self, export_path="data/compatibility_export.json"):
        """Export des données de compatibilité"""
        try:
            sites = self.get_all_supported_sites()
            
            export_data = {
                "export_date": time.strftime("%Y-%m-%d %H:%M:%S"),
                "version": "3.0.0",
                "total_sites": len(sites),
                "sites": sites
            }
            
            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"📤 Données exportées vers {export_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Erreur export: {e}")
            return False

# Test si exécuté directement
if __name__ == "__main__":
    print("🧪 Test CompatibilityLearner V3")
    
    cl = CompatibilityLearner("test_compatibility.db")
    
    # Test URLs
    test_urls = [
        "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        "https://www.youporn.com/watch/193607641/",
        "https://e-hentai.org/g/123456/abcdef/",
        "https://imgur.com/a/abc123"
    ]
    
    for url in test_urls:
        tool = cl.get_best_tool(url)
        print(f"🔧 {url[:50]}... → {tool}")
    
    # Test enregistrement résultat
    cl.record_download_result(
        "https://www.youtube.com/watch?v=test",
        "yt-dlp", 
        True, 
        duration=15.5,
        file_size=1024*1024*50
    )
    
    # Stats
    stats = cl.get_site_statistics()
    print(f"📊 Stats globales: {stats}")
    
    # Sites supportés
    sites = cl.get_all_supported_sites()
    print(f"🌐 {len(sites)} sites supportés")
    
    print("✅ Test terminé")