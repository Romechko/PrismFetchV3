#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
PrismFetch V3 - Logger ULTRA STABLE
Version 3.0.0 FINAL - Créé par Metadata
Gestion des logs avec couleurs et rotation
"""

import logging
import sys
import os
from pathlib import Path
from datetime import datetime
from logging.handlers import RotatingFileHandler

def setup_logging():
    """Configuration complète du système de logging"""
    
    # Créer le dossier logs
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)
    
    # Logger principal
    logger = logging.getLogger("PrismFetch")
    logger.setLevel(logging.INFO)
    
    # Éviter la duplication des handlers
    if logger.handlers:
        return logger
    
    # Formatter avec couleurs pour console
    class ColoredFormatter(logging.Formatter):
        """Formatter avec codes couleur ANSI"""
        
        # Codes couleur ANSI
        COLORS = {
            'DEBUG': '\033[94m',     # Bleu
            'INFO': '\033[92m',      # Vert
            'WARNING': '\033[93m',   # Jaune
            'ERROR': '\033[91m',     # Rouge
            'CRITICAL': '\033[95m',  # Magenta
            'ENDC': '\033[0m'        # Reset
        }
        
        def format(self, record):
            """Format avec couleurs"""
            if record.levelname in self.COLORS and sys.stdout.isatty():
                # Terminal supporte les couleurs
                colored_level = f"{self.COLORS[record.levelname]}{record.levelname}{self.COLORS['ENDC']}"
                record.levelname = colored_level
            return super().format(record)
    
    # Handler pour fichier avec rotation
    try:
        file_handler = RotatingFileHandler(
            logs_dir / "prismfetch.log",
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.INFO)
        
        # Format détaillé pour fichier
        file_formatter = logging.Formatter(
            '%(asctime)s [%(levelname)s] [%(process)d] %(name)s.%(funcName)s:%(lineno)d - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
        
    except Exception as e:
        print(f"⚠️ Erreur création handler fichier: {e}")
    
    # Handler pour console
    try:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        
        # Format simplifié pour console
        console_formatter = ColoredFormatter(
            '%(asctime)s [%(levelname)s] %(message)s',
            datefmt='%H:%M:%S'
        )
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)
        
    except Exception as e:
        print(f"⚠️ Erreur création handler console: {e}")
    
    # Handler pour erreurs critiques
    try:
        error_handler = logging.FileHandler(
            logs_dir / "errors.log",
            encoding='utf-8'
        )
        error_handler.setLevel(logging.ERROR)
        
        error_formatter = logging.Formatter(
            '%(asctime)s [%(levelname)s] %(name)s:%(lineno)d - %(message)s\n%(pathname)s\n%(funcName)s\n---',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        error_handler.setFormatter(error_formatter)
        logger.addHandler(error_handler)
        
    except Exception as e:
        print(f"⚠️ Erreur création handler erreurs: {e}")
    
    # Configuration globale
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("requests").setLevel(logging.WARNING)
    
    return logger

def get_logger(name):
    """Obtenir un logger configuré"""
    setup_logging()
    return logging.getLogger(f"PrismFetch.{name}")

def log_system_info():
    """Log des informations système"""
    logger = get_logger("system")
    
    try:
        import platform
        import psutil
        
        logger.info(f"🖥️ Système: {platform.system()} {platform.release()}")
        logger.info(f"🐍 Python: {platform.python_version()}")
        logger.info(f"💾 RAM: {psutil.virtual_memory().total / (1024**3):.1f} GB")
        logger.info(f"💽 Disque libre: {psutil.disk_usage('/').free / (1024**3):.1f} GB" if os.name != 'nt' else f"💽 Disque libre: {psutil.disk_usage('C:').free / (1024**3):.1f} GB")
        
    except Exception as e:
        logger.warning(f"⚠️ Impossible d'obtenir info système: {e}")

def log_exception(exc_info=None):
    """Log une exception avec stack trace"""
    logger = get_logger("exception")
    
    if exc_info is None:
        import traceback
        exc_info = sys.exc_info()
    
    logger.error("💥 Exception capturée:", exc_info=exc_info)

# Configuration au premier import
_initialized = False

if not _initialized:
    # Créer logger de base
    setup_logging()
    
    # Log de démarrage
    logger = get_logger("init")
    logger.info("📚 Système de logging V3 initialisé")
    
    # Info système
    log_system_info()
    
    _initialized = True

# Test si exécuté directement
if __name__ == "__main__":
    print("🧪 Test du système de logging V3")
    
    logger = get_logger("test")
    
    logger.debug("🔍 Message debug")
    logger.info("ℹ️ Message info")
    logger.warning("⚠️ Message warning")
    logger.error("❌ Message erreur")
    
    try:
        raise ValueError("Test exception")
    except Exception:
        log_exception()
    
    print("✅ Test logging terminé - vérifiez logs/prismfetch.log")