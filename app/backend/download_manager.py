#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
PrismFetch V3 - Download Manager SANS CYBERDROP-DL
Version 3.0.0 FINAL - Créé par Metadata
Téléchargements RÉELS avec outils fiables uniquement
"""

import subprocess
import threading
import time
import os
import json
from pathlib import Path
from urllib.parse import urlparse

try:
    from utils.logger import get_logger
except ImportError:
    import logging
    def get_logger(name):
        return logging.getLogger(name)

class DownloadManager:
    """Gestionnaire de téléchargements SANS cyberdrop-dl"""
    
    def __init__(self, compatibility_learner=None, security_manager=None):
        """Initialisation avec outils fiables"""
        self.compatibility_learner = compatibility_learner
        self.security_manager = security_manager
        self.logger = get_logger(__name__)
        
        # Configuration
        self.output_dir = "data/downloads"
        self.max_concurrent = 4
        self.timeout = 300
        
        # État
        self.active_downloads = {}
        self.download_queue = []
        self.stats = {
            "total_downloads": 0,
            "successful_downloads": 0,
            "failed_downloads": 0
        }
        
        # Outils détectés (SANS cyberdrop-dl)
        self.tools = self._detect_tools()
        
        # Thread de traitement
        self.queue_thread = None
        self.queue_active = False
        self.queue_paused = False
        
        self.logger.info("🔧 DownloadManager V3 initialisé avec IA et sécurité")
        self.logger.info(f"📁 Dossier de sortie: {self.output_dir}")
        self.logger.info(f"⚡ Téléchargements simultanés: {self.max_concurrent}")
        self.logger.info(f"🛠️ Outils détectés: {list(self.tools.keys())}")
    
    def _detect_tools(self):
        """Détection outils fiables SANS cyberdrop-dl"""
        tools = {}
        
        # Liste réduite d'outils fiables
        tool_list = ["yt-dlp", "gallery-dl", "wget", "curl"]
        
        for tool in tool_list:
            path = self._find_tool(tool)
            if path:
                tools[tool] = path
                self.logger.info(f"✅ {tool} trouvé: {path}")
            else:
                self.logger.warning(f"❌ {tool} non trouvé")
        
        return tools
    
    def _find_tool(self, tool_name):
        """Recherche d'un outil"""
        try:
            # Test commande directe
            result = subprocess.run(
                [tool_name, "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                return tool_name
        except:
            pass
        
        # Recherche dans PATH
        try:
            if os.name == "nt":
                result = subprocess.run(["where", tool_name], capture_output=True, text=True)
            else:
                result = subprocess.run(["which", tool_name], capture_output=True, text=True)
            
            if result.returncode == 0:
                return result.stdout.strip().split('\n')[0]
        except:
            pass
        
        # Recherche dans dossier tools/
        tools_dir = Path("tools")
        if tools_dir.exists():
            for ext in [".exe", ".bat", ""]:
                tool_path = tools_dir / f"{tool_name}{ext}"
                if tool_path.exists():
                    return str(tool_path)
        
        return None
    
    def get_compatible_tool(self, url):
        """Sélection outil FIABLE pour une URL"""
        domain = urlparse(url).netloc.lower()
        
        # Règles de compatibilité FIABLES
        if any(site in domain for site in ["youtube.com", "youtu.be"]):
            return "yt-dlp" if "yt-dlp" in self.tools else None
        
        elif any(site in domain for site in ["e-hentai.org", "exhentai.org", "nhentai.net"]):
            return "gallery-dl" if "gallery-dl" in self.tools else "yt-dlp"
        
        elif any(site in domain for site in ["bunkr.cr", "bunkr.is", "cyberdrop"]):
            # Utiliser gallery-dl pour bunkr/cyberdrop (plus fiable que cyberdrop-dl)
            return "gallery-dl" if "gallery-dl" in self.tools else "yt-dlp"
        
        elif any(site in domain for site in ["pornhub.com", "xvideos.com", "youporn.com", "redtube.com"]):
            return "yt-dlp" if "yt-dlp" in self.tools else None
        
        elif any(site in domain for site in ["twitter.com", "x.com", "instagram.com"]):
            return "yt-dlp" if "yt-dlp" in self.tools else "gallery-dl"
        
        # Par défaut
        if "yt-dlp" in self.tools:
            return "yt-dlp"
        elif "gallery-dl" in self.tools:
            return "gallery-dl"
        else:
            return list(self.tools.keys())[0] if self.tools else None
    
    def test_site_support(self, url):
        """Test de support d'une URL"""
        tool = self.get_compatible_tool(url)
        
        if not tool:
            return False, "Aucun outil compatible trouvé"
        
        if tool not in self.tools:
            return False, f"Outil {tool} non disponible"
        
        return True, f"Supporté par {tool}"
    
    def download(self, url, output_dir=None, progress_callback=None, quality="best", force_tool=None):
        """Téléchargement RÉEL avec outils fiables"""
        if not url.strip():
            return False, "URL vide"
        
        # Sélection de l'outil
        tool = force_tool if force_tool and force_tool in self.tools else self.get_compatible_tool(url)
        
        if not tool or tool not in self.tools:
            error_msg = f"Outil non disponible: {tool}"
            self.logger.error(error_msg)
            if progress_callback:
                progress_callback(False, error_msg, 0)
            return False, error_msg
        
        # Dossier de sortie
        output_path = Path(output_dir or self.output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Sandbox si activé
        if self.security_manager and self.security_manager.is_sandbox_enabled():
            temp_output = Path(self.security_manager.get_sandbox_dir())
            temp_output.mkdir(parents=True, exist_ok=True)
            final_output = output_path
            output_path = temp_output
        else:
            final_output = None
        
        # Construction de la commande
        tool_path = self.tools[tool]
        command = self._build_command(tool, tool_path, url, output_path, quality)
        
        if not command:
            error_msg = f"Impossible de construire la commande pour {tool}"
            self.logger.error(error_msg)
            if progress_callback:
                progress_callback(False, error_msg, 0)
            return False, error_msg
        
        # Lancement du téléchargement
        self.logger.info(f"🚀 Lancement: {' '.join(command)}")
        if progress_callback:
            progress_callback(True, f"Démarrage avec {tool}...", 0)
        
        try:
            # Processus de téléchargement
            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                universal_newlines=True
            )
            
            # Lecture de la sortie en temps réel
            output_lines = []
            while True:
                line = process.stdout.readline()
                if line == '' and process.poll() is not None:
                    break
                
                if line:
                    line = line.strip()
                    output_lines.append(line)
                    self.logger.info(f"📥 {tool}: {line}")
                    
                    # Extraction du pourcentage si possible
                    progress = self._extract_progress(line, tool)
                    if progress is not None and progress_callback:
                        progress_callback(True, line, progress)
            
            # Vérification du résultat
            return_code = process.poll()
            
            if return_code == 0:
                # Succès - déplacement du sandbox si nécessaire
                if final_output and self.security_manager:
                    self.security_manager.process_sandbox_files(str(final_output))
                
                success_msg = f"✅ Téléchargement réussi avec {tool}"
                self.stats["successful_downloads"] += 1
                self.logger.info(success_msg)
                
                if progress_callback:
                    progress_callback(True, success_msg, 100)
                
                return True, success_msg
            else:
                # Échec
                error_msg = f"❌ Échec téléchargement (code {return_code})"
                self.stats["failed_downloads"] += 1
                self.logger.error(error_msg)
                
                if progress_callback:
                    progress_callback(False, error_msg, 0)
                
                return False, error_msg
                
        except subprocess.TimeoutExpired:
            error_msg = f"⏰ Timeout après {self.timeout}s"
            self.logger.error(error_msg)
            if progress_callback:
                progress_callback(False, error_msg, 0)
            return False, error_msg
            
        except Exception as e:
            error_msg = f"💥 Erreur: {e}"
            self.logger.error(error_msg)
            if progress_callback:
                progress_callback(False, error_msg, 0)
            return False, error_msg
        
        finally:
            self.stats["total_downloads"] += 1
    
    def _build_command(self, tool, tool_path, url, output_path, quality):
        """Construction de la commande selon l'outil FIABLE"""
        if tool == "yt-dlp":
            command = [
                tool_path,
                "--no-playlist",
                "--output", str(output_path / "%(uploader)s - %(title)s.%(ext)s"),
                "--format", self._convert_quality_ytdlp(quality),
                "--no-warnings",
                url
            ]
            
        elif tool == "gallery-dl":
            command = [
                tool_path,
                "--destination", str(output_path),
                "--no-skip",
                url
            ]
            
        elif tool == "wget":
            command = [
                tool_path,
                "--directory-prefix", str(output_path),
                "--timeout", str(self.timeout),
                url
            ]
            
        elif tool == "curl":
            # Créer nom de fichier depuis l'URL
            filename = url.split('/')[-1] or "download"
            command = [
                tool_path,
                "--output", str(output_path / filename),
                "--location",
                "--connect-timeout", str(self.timeout),
                url
            ]
            
        else:
            return None
        
        return command
    
    def _convert_quality_ytdlp(self, quality):
        """Conversion qualité pour yt-dlp"""
        quality_map = {
            "FLAC": "bestaudio[ext=flac]/bestaudio",
            "WAV": "bestaudio[ext=wav]/bestaudio", 
            "MP3 320kbps": "bestaudio[ext=mp3][abr>=320]/bestaudio",
            "MP3 256kbps": "bestaudio[ext=mp3][abr>=256]/bestaudio",
            "MP3 128kbps": "bestaudio[ext=mp3][abr>=128]/bestaudio",
            "4K": "bestvideo[height<=2160]+bestaudio/best",
            "1080p": "bestvideo[height<=1080]+bestaudio/best",
            "720p": "bestvideo[height<=720]+bestaudio/best",
            "480p": "bestvideo[height<=480]+bestaudio/best",
            "best": "best",
            "worst": "worst"
        }
        return quality_map.get(quality, "best")
    
    def _extract_progress(self, line, tool):
        """Extraction du pourcentage de progression"""
        import re
        
        if tool == "yt-dlp":
            # [download]  45.2% of 123.45MiB at  1.23MiB/s ETA 00:30
            match = re.search(r'\[download\]\s+(\d+\.?\d*)%', line)
            if match:
                return float(match.group(1))
        
        elif tool == "gallery-dl":
            # gallery-dl n'a pas de pourcentage standard
            if "Downloading" in line:
                return -1  # Mode indéterminé
        
        return None
    
    def add_to_queue(self, url, quality="best", force_tool=None):
        """Ajout à la queue de téléchargement"""
        item = {
            "url": url,
            "quality": quality,
            "force_tool": force_tool,
            "status": "En attente",
            "progress": 0,
            "tool": force_tool or self.get_compatible_tool(url)
        }
        self.download_queue.append(item)
        self.logger.info(f"➕ Ajouté à la queue: {url[:50]}...")
        return len(self.download_queue) - 1  # Index de l'item
    
    def start_queue_processing(self, progress_callback=None):
        """Démarrage du traitement de la queue"""
        if self.queue_active:
            return False, "Queue déjà active"
        
        if not self.download_queue:
            return False, "Queue vide"
        
        self.queue_active = True
        self.queue_paused = False
        
        def process_queue():
            self.logger.info("🚀 Démarrage traitement queue")
            
            while self.queue_active and self.download_queue:
                if self.queue_paused:
                    time.sleep(0.5)
                    continue
                
                # Prendre le premier item en attente
                item = None
                for i, queued_item in enumerate(self.download_queue):
                    if queued_item["status"] == "En attente":
                        item = queued_item
                        break
                
                if not item:
                    break
                
                # Marquer comme en cours
                item["status"] = "En cours"
                if progress_callback:
                    progress_callback("queue_update", item)
                
                # Télécharger
                def item_progress(success, message, progress):
                    item["progress"] = progress if progress >= 0 else 0
                    if progress_callback:
                        progress_callback("item_progress", item)
                
                success, message = self.download(
                    item["url"],
                    quality=item["quality"],
                    force_tool=item["force_tool"],
                    progress_callback=item_progress
                )
                
                # Mettre à jour le statut
                item["status"] = "Terminé" if success else "Erreur"
                item["progress"] = 100 if success else 0
                if progress_callback:
                    progress_callback("queue_update", item)
            
            self.queue_active = False
            self.logger.info("✅ Traitement queue terminé")
            
        self.queue_thread = threading.Thread(target=process_queue)
        self.queue_thread.daemon = True
        self.queue_thread.start()
        
        return True, "Queue démarrée"
    
    def pause_queue(self):
        """Pause de la queue"""
        self.queue_paused = True
        self.logger.info("⏸️ Queue en pause")
        return True, "Queue en pause"
    
    def resume_queue(self):
        """Reprise de la queue"""
        self.queue_paused = False
        self.logger.info("▶️ Queue reprise")
        return True, "Queue reprise"
    
    def stop_queue(self):
        """Arrêt de la queue"""
        self.queue_active = False
        self.queue_paused = False
        self.logger.info("⏹️ Queue arrêtée")
        return True, "Queue arrêtée"
    
    def clear_queue(self):
        """Vidage de la queue"""
        self.download_queue.clear()
        self.logger.info("🗑️ Queue vidée")
        return True, "Queue vidée"
    
    def get_download_stats(self):
        """Statistiques de téléchargement"""
        return {
            "total_downloads": self.stats["total_downloads"],
            "successful_downloads": self.stats["successful_downloads"],
            "failed_downloads": self.stats["failed_downloads"],
            "queue_size": len(self.download_queue),
            "active_downloads": len(self.active_downloads)
        }

# Test si exécuté directement
if __name__ == "__main__":
    print("🧪 Test DownloadManager SANS cyberdrop-dl")
    
    # Test basique
    dm = DownloadManager()
    
    # Test URL YouPorn
    test_url = "https://www.youporn.com/watch/193607641/"
    
    print(f"🔍 Test support: {test_url}")
    supported, message = dm.test_site_support(test_url)
    print(f"📊 Résultat: {supported} - {message}")
    
    if supported:
        print(f"🛠️ Outil recommandé: {dm.get_compatible_tool(test_url)}")
    
    print("✅ DownloadManager FIABLE testé")