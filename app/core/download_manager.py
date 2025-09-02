#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import subprocess
import time
import os
from pathlib import Path
from ..utils.logger import get_logger

class DownloadManager:
    """Gestionnaire avec gallery-dl pour Bunkr (cyberdrop-dl-patched défaillant)"""

    def __init__(self):
        try:
            self.logger = get_logger(__name__)
            self.active_downloads = {}
        except Exception as e:
            print(f"Erreur init DownloadManager: {e}")

    def is_tool_available(self, tool_name):
        """Vérifier disponibilité avec gestion Unicode"""
        try:
            result = subprocess.run([tool_name, "--version"], 
                                  capture_output=True, text=True, timeout=10,
                                  encoding='utf-8', errors='replace')
            return result.returncode == 0
        except Exception as e:
            try:
                self.logger.error(f"Erreur test {tool_name}: {e}")
            except:
                print(f"Erreur test {tool_name}: {e}")
            return False

    def get_available_tools(self):
        """Status de tous les outils"""
        tools = {
            "yt-dlp": self.is_tool_available("yt-dlp"),
            "gallery-dl": self.is_tool_available("gallery-dl"),
            "cyberdrop-dl-patched": False  # Désactivé car défaillant
        }
        try:
            self.logger.info(f"Outils disponibles: {tools}")
        except:
            print(f"Outils disponibles: {tools}")
        return tools

    def detect_best_tool(self, url):
        """Détection avec gallery-dl pour Bunkr"""
        url = url.lower()

        if any(site in url for site in ["youtube.com", "youtu.be", "vimeo.com", "dailymotion.com"]):
            return "yt-dlp"

        # TOUS les sites vers gallery-dl (y compris Bunkr)
        if any(site in url for site in ["instagram.com", "twitter.com", "x.com", 
                                       "reddit.com", "tiktok.com", "facebook.com",
                                       "cyberdrop", "bunkr.cr", "bunkr.is", "bunkr.la", 
                                       "bunkr.ru", "bunkr.su", "bunkrrr.org", "bunkr",
                                       "gofile.io", "anonfiles.com"]):
            return "gallery-dl"

        return "yt-dlp"

    def download(self, url, output_path=None, callback=None):
        """Téléchargement avec gallery-dl pour tout"""
        if output_path is None:
            output_path = Path("data/downloads")

        output_path = Path(output_path)
        output_path.mkdir(parents=True, exist_ok=True)

        tool = self.detect_best_tool(url)

        try:
            self.logger.info(f"=== TÉLÉCHARGEMENT SANS CYBERDROP ===")
            self.logger.info(f"URL: {url}")
            self.logger.info(f"Outil: {tool}")
            self.logger.info(f"Destination: {output_path}")
        except:
            print(f"URL: {url}, Outil: {tool}, Dest: {output_path}")

        if not self.is_tool_available(tool):
            error = f"Outil {tool} non disponible"
            try:
                self.logger.error(error)
            except:
                print(error)
            if callback:
                callback(False, error)
            return False, error

        try:
            original_dir = os.getcwd()
            files_before = {f.name for f in output_path.rglob("*") if f.is_file()}

            if tool == "yt-dlp":
                cmd = [
                    "yt-dlp",
                    "--output", str(output_path / "%(uploader)s - %(title)s.%(ext)s"),
                    "--format", "best[height<=720]",
                    "--no-playlist",
                    "--write-info-json",
                    url
                ]
            elif tool == "gallery-dl":
                cmd = [
                    "gallery-dl",
                    "--destination", str(output_path),
                    "--write-metadata",
                    url
                ]

            start_time = time.time()
            if callback:
                callback(True, f"Démarrage {tool}...", 20)

            print(f"\n🚀 LANCEMENT {tool}")
            print(f"Commande: {' '.join(cmd)}")

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300,
                cwd=original_dir,
                encoding='utf-8',
                errors='replace'
            )

            duration = time.time() - start_time
            files_after = {f.name for f in output_path.rglob("*") if f.is_file()}
            new_files = files_after - files_before

            print(f"📊 RÉSULTAT {tool}:")
            print(f"   Code retour: {result.returncode}")
            print(f"   Durée: {duration:.1f}s")
            print(f"   Nouveaux fichiers: {len(new_files)}")
            if result.stdout:
                print(f"   Stdout: {result.stdout[:200]}...")
            if result.stderr:
                print(f"   Stderr: {result.stderr[:200]}...")

            if result.returncode == 0 and new_files:
                success_msg = f"{tool}: {len(new_files)} fichier(s) téléchargé(s)"
                if len(new_files) <= 5:
                    success_msg += f": {', '.join(new_files)}"

                try:
                    self.logger.info(f"SUCCÈS: {success_msg}")
                except:
                    pass

                if callback:
                    callback(True, success_msg, 100)

                return True, success_msg
            else:
                error_msg = f"{tool} échec (code {result.returncode})"
                if result.stderr:
                    error_msg += f": {result.stderr.strip()[:200]}"

                try:
                    self.logger.error(f"ÉCHEC: {error_msg}")
                except:
                    pass

                if callback:
                    callback(False, error_msg)

                return False, error_msg

        except subprocess.TimeoutExpired:
            error = f"{tool} timeout (5 min)"
            try:
                self.logger.error(error)
            except:
                print(error)
            if callback:
                callback(False, error)
            return False, error

        except Exception as e:
            error = f"{tool} erreur: {str(e)}"
            try:
                self.logger.error(error)
            except:
                print(error)
            if callback:
                callback(False, error)
            return False, error
