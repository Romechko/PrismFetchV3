#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
PrismFetch V3 - Gestionnaire de Téléchargements avec IA
Version 3.0.0 FINAL - Créé par Metadata
Compatible avec l'initialisation V3 : DownloadManager(compatibility_learner, security_manager)
"""

import os
import sys
import subprocess
import threading
import time
import json
from pathlib import Path
from urllib.parse import urlparse
import requests

try:
    from utils.logger import get_logger
except ImportError:
    import logging
    def get_logger(name):
        return logging.getLogger(name)

class DownloadManager:
    """Gestionnaire de téléchargements intelligent avec IA V3"""
    
    def __init__(self, compatibility_learner=None, security_manager=None):
        """Initialisation compatible V3 avec IA et sécurité"""
        self.compatibility_learner = compatibility_learner
        self.security_manager = security_manager
        self.logger = get_logger(__name__)
        
        # Configuration par défaut
        self.config = {
            "default_output_dir": "data/downloads",
            "max_concurrent_downloads": 4,
            "timeout": 300,
            "user_agent": "PrismFetch V3/3.0.0",
            "quality_priority": ["flac", "wav", "mp3_320", "aac", "mp3"]
        }
        
        # État des téléchargements
        self.active_downloads = {}
        self.download_queue = []
        self.stats = {
            "total_downloads": 0,
            "successful_downloads": 0,
            "failed_downloads": 0,
            "bytes_downloaded": 0
        }
        
        # Cache des outils
        self.tools_cache = {}
        self.tools_paths = {
            "yt-dlp": self._find_tool("yt-dlp"),
            "gallery-dl": self._find_tool("gallery-dl"),
            "cyberdrop-dl": self._find_tool("cyberdrop-dl"),
            "wget": self._find_tool("wget"),
            "curl": self._find_tool("curl")
        }
        
        self.logger.info("🔧 DownloadManager V3 initialisé avec IA et sécurité")
        self.logger.info(f"📁 Dossier de sortie: {self.config['default_output_dir']}")
        self.logger.info(f"⚡ Téléchargements simultanés: {self.config['max_concurrent_downloads']}")
    
    def _find_tool(self, tool_name):
        """Recherche d'un outil dans le système ou dossier tools/"""
        try:
            # Vérification dans le PATH
            result = subprocess.run(
                ["where" if os.name == "nt" else "which", tool_name],
                capture_output=True, text=True
            )
            if result.returncode == 0:
                return result.stdout.strip().split('\n')[0]
            
        except Exception:
            pass
        
        # Vérification dans le dossier tools/
        tools_dir = Path("tools")
        if tools_dir.exists():
            for ext in [".exe", ".bat", ""]:
                tool_path = tools_dir / f"{tool_name}{ext}"
                if tool_path.exists():
                    return str(tool_path)
        
        return None
    
    def get_compatible_tool(self, url):
        """Obtention de l'outil compatible via IA d'apprentissage"""
        try:
            if self.compatibility_learner:
                # Utilisation de l'IA d'apprentissage
                recommended_tool = self.compatibility_learner.get_best_tool(url)
                self.logger.info(f"🧠 IA recommande: {recommended_tool} pour {self._get_domain(url)}")
                return recommended_tool
            else:
                # Fallback sur détection basique
                return self._detect_tool_basic(url)
                
        except Exception as e:
            self.logger.warning(f"⚠️ Erreur IA, fallback basique: {e}")
            return self._detect_tool_basic(url)
    
    def _detect_tool_basic(self, url):
        """Détection basique d'outil sans IA"""
        domain = self._get_domain(url).lower()
        
        # Règles de détection basiques
        if any(video_site in domain for video_site in ["youtube", "vimeo", "dailymotion", "tiktok"]):
            return "yt-dlp"
        elif any(gallery_site in domain for gallery_site in ["e-hentai", "imgur", "instagram"]):
            return "gallery-dl" 
        elif any(cyber_site in domain for cyber_site in ["cyberdrop", "bunkr"]):
            return "cyberdrop-dl"
        else:
            return "yt-dlp"  # Outil par défaut
    
    def _get_domain(self, url):
        """Extraction du domaine d'une URL"""
        try:
            return urlparse(url).netloc
        except:
            return "unknown"
    
    def download(self, url, output_dir=None, callback=None, force_tool=None, quality_settings=None):
        """Téléchargement principal avec IA et sécurité V3"""
        try:
            self.logger.info(f"🚀 Début téléchargement: {url[:50]}...")
            
            # Configuration du téléchargement
            if output_dir is None:
                output_dir = self.config["default_output_dir"]
            
            # Création du dossier de sortie
            Path(output_dir).mkdir(parents=True, exist_ok=True)
            
            # Sélection de l'outil
            if force_tool:
                tool = force_tool
                self.logger.info(f"🔧 Outil forcé: {tool}")
            else:
                tool = self.get_compatible_tool(url)
                self.logger.info(f"🎯 Outil sélectionné: {tool}")
            
            # Vérification sécurité
            if self.security_manager:
                is_safe = self.security_manager.check_url_safety(url)
                if not is_safe:
                    self.logger.warning(f"⚠️ URL potentiellement dangereuse: {url}")
                    if callback:
                        callback(False, "URL bloquée par sécurité", 0)
                    return False, "URL bloquée par sécurité"
            
            # Exécution du téléchargement
            success, message = self._execute_download(url, output_dir, tool, callback, quality_settings)
            
            # Apprentissage de l'IA
            if self.compatibility_learner:
                self.compatibility_learner.record_download_result(url, tool, success)
            
            # Mise à jour des statistiques
            self.stats["total_downloads"] += 1
            if success:
                self.stats["successful_downloads"] += 1
            else:
                self.stats["failed_downloads"] += 1
            
            self.logger.info(f"✅ Téléchargement terminé: {message}")
            return success, message
            
        except Exception as e:
            error_msg = f"Erreur téléchargement: {e}"
            self.logger.error(f"💥 {error_msg}")
            if callback:
                callback(False, error_msg, 0)
            return False, error_msg
    
    def _execute_download(self, url, output_dir, tool, callback=None, quality_settings=None):
        """Exécution effective du téléchargement"""
        try:
            tool_path = self.tools_paths.get(tool)
            if not tool_path:
                return False, f"Outil {tool} non trouvé"
            
            # Construction de la commande selon l'outil
            if tool == "yt-dlp":
                cmd = self._build_ytdlp_command(url, output_dir, quality_settings)
            elif tool == "gallery-dl":
                cmd = self._build_gallerydl_command(url, output_dir)
            elif tool == "cyberdrop-dl":
                cmd = self._build_cyberdrop_command(url, output_dir)
            else:
                return False, f"Outil {tool} non supporté"
            
            self.logger.debug(f"🔧 Commande: {' '.join(cmd)}")
            
            # Exécution avec callback de progression
            if callback:
                callback(True, "Téléchargement en cours...", -1)
            
            # Sandbox si activé
            if self.security_manager and self.security_manager.is_sandbox_enabled():
                sandbox_dir = self.security_manager.get_sandbox_dir()
                Path(sandbox_dir).mkdir(parents=True, exist_ok=True)
                # Redirection temporaire vers sandbox
                original_output = output_dir
                output_dir = sandbox_dir
                cmd = self._update_command_output(cmd, output_dir)
            
            # Exécution de la commande
            process = subprocess.Popen(
                cmd, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE,
                text=True,
                cwd=Path.cwd()
            )
            
            stdout, stderr = process.communicate(timeout=self.config["timeout"])
            
            if process.returncode == 0:
                # Succès du téléchargement
                if callback:
                    callback(True, "Téléchargement terminé avec succès", 100)
                
                # Déplacement du sandbox vers destination finale si nécessaire
                if self.security_manager and self.security_manager.is_sandbox_enabled():
                    self.security_manager.process_sandbox_files(original_output)
                
                return True, "Téléchargement réussi"
            else:
                error_msg = stderr.strip() if stderr else "Erreur inconnue"
                if callback:
                    callback(False, f"Échec: {error_msg}", 0)
                return False, error_msg
            
        except subprocess.TimeoutExpired:
            error_msg = "Timeout de téléchargement"
            if callback:
                callback(False, error_msg, 0)
            return False, error_msg
        except Exception as e:
            error_msg = f"Erreur exécution: {e}"
            if callback:
                callback(False, error_msg, 0)
            return False, error_msg
    
    def _build_ytdlp_command(self, url, output_dir, quality_settings=None):
        """Construction commande yt-dlp"""
        cmd = [self.tools_paths["yt-dlp"]]
        
        # Format de sortie
        output_template = str(Path(output_dir) / "%(uploader)s - %(title)s.%(ext)s")
        cmd.extend(["-o", output_template])
        
        # Qualité
        if quality_settings and quality_settings.get("format"):
            format_selector = quality_settings["format"]
            if format_selector == "best":
                cmd.extend(["-f", "best"])
            elif format_selector in ["4K", "1080p", "720p", "480p"]:
                height = format_selector.replace("p", "").replace("K", "160")  # 4K = 2160p
                cmd.extend(["-f", f"best[height<={height}]"])
        
        # Options supplémentaires
        cmd.extend([
            "--no-playlist",
            "--ignore-errors",
            "--user-agent", self.config["user_agent"]
        ])
        
        cmd.append(url)
        return cmd
    
    def _build_gallerydl_command(self, url, output_dir):
        """Construction commande gallery-dl"""
        cmd = [self.tools_paths["gallery-dl"]]
        cmd.extend(["-d", str(output_dir)])
        cmd.extend(["--user-agent", self.config["user_agent"]])
        cmd.append(url)
        return cmd
    
    def _build_cyberdrop_command(self, url, output_dir):
        """Construction commande cyberdrop-dl"""
        cmd = [self.tools_paths["cyberdrop-dl"]]
        cmd.extend(["--output-folder", str(output_dir)])
        cmd.append(url)
        return cmd
    
    def _update_command_output(self, cmd, new_output_dir):
        """Mise à jour du dossier de sortie dans une commande"""
        # Implémentation basique - à améliorer selon les outils
        for i, arg in enumerate(cmd):
            if arg in ["-d", "--output-folder", "-o"] and i + 1 < len(cmd):
                cmd[i + 1] = str(new_output_dir)
                break
        return cmd
    
    def test_site_support(self, url, tool=None):
        """Test de support d'un site"""
        try:
            if tool is None:
                tool = self.get_compatible_tool(url)
            
            tool_path = self.tools_paths.get(tool)
            if not tool_path:
                return False, f"Outil {tool} non disponible"
            
            # Test basique avec timeout court
            if tool == "yt-dlp":
                cmd = [tool_path, "--dump-json", "--no-download", url]
            elif tool == "gallery-dl":
                cmd = [tool_path, "--dump-json", url]
            else:
                return True, f"Test non implémenté pour {tool}"
            
            try:
                result = subprocess.run(
                    cmd, capture_output=True, text=True, timeout=30
                )
                return result.returncode == 0, "Site supporté" if result.returncode == 0 else "Site non supporté"
            except subprocess.TimeoutExpired:
                return False, "Timeout du test"
            
        except Exception as e:
            return False, f"Erreur test: {e}"
    
    def stop_all_downloads(self):
        """Arrêt de tous les téléchargements actifs"""
        self.logger.info("⏹️ Arrêt de tous les téléchargements")
        # Implémentation de l'arrêt des téléchargements
        # (nécessiterait gestion des processus actifs)
        self.active_downloads.clear()
        self.download_queue.clear()
    
    def get_download_stats(self):
        """Récupération des statistiques de téléchargement"""
        return self.stats.copy()
    
    def get_supported_sites(self):
        """Liste des sites supportés"""
        supported_sites = []
        
        if self.compatibility_learner:
            supported_sites = self.compatibility_learner.get_all_supported_sites()
        else:
            # Sites basiques si pas d'IA
            supported_sites = [
                "youtube.com", "vimeo.com", "dailymotion.com",
                "e-hentai.org", "imgur.com", "instagram.com",
                "cyberdrop.me", "bunkr.cr", "soundcloud.com"
            ]
        
        return supported_sites
    
    def add_to_queue(self, url, output_dir=None, options=None):
        """Ajout d'un téléchargement à la queue"""
        download_item = {
            "url": url,
            "output_dir": output_dir or self.config["default_output_dir"],
            "options": options or {},
            "status": "pending",
            "added_time": time.time()
        }
        
        self.download_queue.append(download_item)
        self.logger.info(f"➕ Ajouté à la queue: {url[:50]}...")
        return len(self.download_queue)
    
    def process_queue(self, callback=None):
        """Traitement de la queue de téléchargements"""
        self.logger.info(f"🔄 Traitement queue: {len(self.download_queue)} éléments")
        
        while self.download_queue and len(self.active_downloads) < self.config["max_concurrent_downloads"]:
            item = self.download_queue.pop(0)
            
            # Lancement du téléchargement en thread
            def download_thread(download_item):
                try:
                    success, message = self.download(
                        download_item["url"],
                        download_item["output_dir"],
                        callback
                    )
                    download_item["status"] = "completed" if success else "failed"
                    download_item["result"] = message
                    
                except Exception as e:
                    download_item["status"] = "error"
                    download_item["result"] = str(e)
                
                # Suppression des actifs
                if download_item["url"] in self.active_downloads:
                    del self.active_downloads[download_item["url"]]
            
            # Ajout aux téléchargements actifs
            self.active_downloads[item["url"]] = item
            
            # Lancement du thread
            thread = threading.Thread(target=download_thread, args=(item,))
            thread.daemon = True
            thread.start()
    
    def get_queue_status(self):
        """Status de la queue"""
        return {
            "pending": len(self.download_queue),
            "active": len(self.active_downloads),
            "completed": self.stats["successful_downloads"],
            "failed": self.stats["failed_downloads"]
        }

if __name__ == "__main__":
    # Test du DownloadManager
    print("🔧 Test DownloadManager V3")
    
    # Test d'initialisation
    manager = DownloadManager()
    print(f"✅ DownloadManager initialisé")
    
    # Test de détection d'outil
    test_urls = [
        "https://www.youtube.com/watch?v=test",
        "https://e-hentai.org/test",
        "https://bunkr.cr/test"
    ]
    
    for url in test_urls:
        tool = manager.get_compatible_tool(url)
        print(f"🎯 {url} → {tool}")
    
    # Test des outils disponibles
    print(f"\n🔧 Outils disponibles:")
    for tool, path in manager.tools_paths.items():
        status = "✅" if path else "❌"
        print(f"   {status} {tool}: {path or 'Non trouvé'}")
    
    print(f"\n✅ Test DownloadManager terminé")