#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import threading
from ..utils.logger import get_logger
from .download_manager import DownloadManager
from .config_manager import ConfigManager

class Orchestrator:
    """Lance et coordonne les téléchargements."""

    def __init__(self, config: dict = None):
        self.logger = get_logger(__name__)
        self.config = config or ConfigManager.load()
        self.download_manager = DownloadManager()

    def run(self, url: str = None, file_path: str = None):
        """Télécharge une URL ou toutes les URLs listées dans un fichier."""
        targets = []
        if url:
            targets.append(url)
        if file_path:
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        targets.append(line)
        if not targets:
            self.logger.error("Aucune URL fournie à orchestrator.run()")
            return

        threads = []
        for u in targets:
            t = threading.Thread(target=self._download_thread, args=(u,))
            t.start()
            threads.append(t)
        for t in threads:
            t.join()
        self.logger.info("Tous les téléchargements orchestrés sont terminés.")

    def _download_thread(self, url: str):
        self.logger.info(f"Orchestrator lance le téléchargement: {url}")
        success, msg = self.download_manager.download(url, self.config.get('download_path'))
        if success:
            self.logger.info(f"Téléchargé: {msg}")
        else:
            self.logger.error(f"Échec téléchargement: {msg}")
