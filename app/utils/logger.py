#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
PrismFetch V3 - Logger système
Version 3.0.0 FINAL - Créé par Metadata
"""

import logging
import sys
from pathlib import Path
from datetime import datetime

def setup_logging():
    """Configuration du système de logging"""
    
    # Créer le dossier logs
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)
    
    # Configuration du logger principal
    logger = logging.getLogger("PrismFetch")
    logger.setLevel(logging.INFO)
    
    # Éviter les doublons de handlers
    if logger.handlers:
        return logger
    
    # Formatter avec couleurs pour console
    class ColoredFormatter(logging.Formatter):
        """Formatter avec codes couleur pour la console"""
        
        COLORS = {
            'DEBUG': '\033[94m',    # Bleu
            'INFO': '\033[92m',     # Vert  
            'WARNING': '\033[93m',  # Jaune
            'ERROR': '\033[91m',    # Rouge
            'CRITICAL': '\033[95m', # Magenta
            'ENDC': '\033[0m'       # Reset
        }
        
        def format(self, record):
            if record.levelname in self.COLORS:
                record.levelname = f"{self.COLORS[record.levelname]}{record.levelname}{self.COLORS['ENDC']}"
            return super().format(record)
    
    # Handler pour fichier
    file_handler = logging.FileHandler(
        logs_dir / "prismfetch.log", 
        encoding='utf-8'
    )
    file_handler.setLevel(logging.INFO)
    file_formatter = logging.Formatter(
        '%(asctime)s [%(levelname)s] [%(process)d] %(name)s.%(funcName)s:%(lineno)d - %(message)s'
    )
    file_handler.setFormatter(file_formatter)
    
    # Handler pour console
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_formatter = ColoredFormatter(
        '%(asctime)s [%(levelname)s] %(message)s',
        datefmt='%H:%M:%S'
    )
    console_handler.setFormatter(console_formatter)
    
    # Ajouter les handlers
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

def get_logger(name):
    """Obtenir un logger avec configuration"""
    setup_logging()
    return logging.getLogger(f"PrismFetch.{name}")

# Test si exécuté directement
if __name__ == "__main__":
    logger = get_logger(__name__)
    logger.info("🧪 Test du système de logging")
    logger.warning("⚠️ Test warning")
    logger.error("❌ Test error")
    print("✅ Logger testé")