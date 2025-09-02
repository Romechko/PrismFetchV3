#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
PrismFetch V3 - Module de Logging
Système de logs avancé avec rotation et niveaux configurables
Version 3.0.0 FINAL - Créé par Metadata
"""

import logging
import logging.handlers
import os
import sys
from pathlib import Path
import time
from datetime import datetime

class ColoredFormatter(logging.Formatter):
    """Formatter coloré pour les logs console"""
    
    # Couleurs ANSI
    COLORS = {
        'DEBUG': '\033[36m',    # Cyan
        'INFO': '\033[32m',     # Vert
        'WARNING': '\033[33m',  # Jaune
        'ERROR': '\033[31m',    # Rouge
        'CRITICAL': '\033[35m', # Magenta
        'RESET': '\033[0m'      # Reset
    }
    
    def format(self, record):
        # Ajout de couleur si terminal supporté
        if hasattr(sys.stderr, 'isatty') and sys.stderr.isatty():
            log_color = self.COLORS.get(record.levelname, self.COLORS['RESET'])
            reset_color = self.COLORS['RESET']
            
            # Formatage avec couleur
            record.levelname = f"{log_color}{record.levelname}{reset_color}"
        
        return super().format(record)

class PrismFetchLogger:
    """Gestionnaire de logs centralisé pour PrismFetch V3"""
    
    def __init__(self):
        self.loggers = {}
        self.log_dir = Path("logs")
        self.log_dir.mkdir(exist_ok=True)
        
        # Configuration par défaut
        self.default_level = logging.INFO
        self.console_level = logging.INFO
        self.file_level = logging.DEBUG
        
        # Formats
        self.console_format = '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
        self.file_format = '%(asctime)s [%(levelname)s] [%(process)d] %(name)s.%(funcName)s:%(lineno)d - %(message)s'
        
        # Configuration initiale
        self._setup_root_logger()
    
    def _setup_root_logger(self):
        """Configuration du logger racine"""
        root_logger = logging.getLogger()
        root_logger.setLevel(self.default_level)
        
        # Éviter les handlers multiples
        if root_logger.handlers:
            root_logger.handlers.clear()
        
        # Handler console
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(self.console_level)
        console_formatter = ColoredFormatter(
            fmt='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
            datefmt='%H:%M:%S'
        )
        console_handler.setFormatter(console_formatter)
        root_logger.addHandler(console_handler)
        
        # Handler fichier avec rotation
        try:
            file_handler = logging.handlers.RotatingFileHandler(
                filename=self.log_dir / "prismfetch.log",
                maxBytes=10 * 1024 * 1024,  # 10 MB
                backupCount=5,
                encoding='utf-8'
            )
            file_handler.setLevel(self.file_level)
            file_formatter = logging.Formatter(
                fmt=self.file_format,
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            file_handler.setFormatter(file_formatter)
            root_logger.addHandler(file_handler)
        
        except Exception as e:
            print(f"⚠️ Impossible de créer le fichier de log: {e}")
    
    def get_logger(self, name):
        """Récupération d'un logger nommé"""
        if name in self.loggers:
            return self.loggers[name]
        
        logger = logging.getLogger(name)
        self.loggers[name] = logger
        
        return logger
    
    def set_level(self, level):
        """Modification du niveau global"""
        if isinstance(level, str):
            level = getattr(logging, level.upper(), logging.INFO)
        
        self.default_level = level
        
        # Mise à jour de tous les loggers
        root_logger = logging.getLogger()
        root_logger.setLevel(level)
        
        for logger in self.loggers.values():
            logger.setLevel(level)
    
    def set_console_level(self, level):
        """Modification du niveau console uniquement"""
        if isinstance(level, str):
            level = getattr(logging, level.upper(), logging.INFO)
        
        self.console_level = level
        
        # Mise à jour handler console
        root_logger = logging.getLogger()
        for handler in root_logger.handlers:
            if isinstance(handler, logging.StreamHandler) and not isinstance(handler, logging.FileHandler):
                handler.setLevel(level)
    
    def create_module_logger(self, module_name, log_file=None):
        """Création d'un logger spécifique pour un module"""
        logger = self.get_logger(module_name)
        
        # Logger de fichier spécifique si demandé
        if log_file:
            try:
                module_handler = logging.handlers.RotatingFileHandler(
                    filename=self.log_dir / log_file,
                    maxBytes=5 * 1024 * 1024,  # 5 MB
                    backupCount=3,
                    encoding='utf-8'
                )
                module_handler.setLevel(self.file_level)
                module_formatter = logging.Formatter(
                    fmt=self.file_format,
                    datefmt='%Y-%m-%d %H:%M:%S'
                )
                module_handler.setFormatter(module_formatter)
                logger.addHandler(module_handler)
            
            except Exception as e:
                logger.warning(f"Impossible de créer le fichier de log {log_file}: {e}")
        
        return logger
    
    def cleanup_old_logs(self, days=30):
        """Nettoyage des anciens logs"""
        try:
            current_time = time.time()
            cutoff_time = current_time - (days * 24 * 3600)
            
            deleted_count = 0
            for log_file in self.log_dir.glob("*.log*"):
                if log_file.stat().st_mtime < cutoff_time:
                    log_file.unlink()
                    deleted_count += 1
            
            if deleted_count > 0:
                logger = self.get_logger("cleanup")
                logger.info(f"🗑️ {deleted_count} anciens fichiers de logs supprimés")
        
        except Exception as e:
            logger = self.get_logger("cleanup")
            logger.error(f"Erreur nettoyage logs: {e}")
    
    def get_log_stats(self):
        """Statistiques des logs"""
        try:
            stats = {
                "log_directory": str(self.log_dir),
                "total_files": 0,
                "total_size": 0,
                "files": []
            }
            
            for log_file in self.log_dir.glob("*.log*"):
                size = log_file.stat().st_size
                stats["files"].append({
                    "name": log_file.name,
                    "size": size,
                    "size_mb": round(size / (1024 * 1024), 2),
                    "modified": datetime.fromtimestamp(log_file.stat().st_mtime).strftime('%Y-%m-%d %H:%M:%S')
                })
                stats["total_files"] += 1
                stats["total_size"] += size
            
            stats["total_size_mb"] = round(stats["total_size"] / (1024 * 1024), 2)
            
            return stats
        
        except Exception as e:
            return {"error": str(e)}

# Instance globale
_logger_manager = PrismFetchLogger()

def get_logger(name):
    """Fonction utilitaire pour récupérer un logger"""
    return _logger_manager.get_logger(name)

def set_log_level(level):
    """Fonction utilitaire pour changer le niveau de log"""
    _logger_manager.set_level(level)

def set_console_log_level(level):
    """Fonction utilitaire pour changer le niveau console"""
    _logger_manager.set_console_level(level)

def create_module_logger(module_name, log_file=None):
    """Fonction utilitaire pour créer un logger de module"""
    return _logger_manager.create_module_logger(module_name, log_file)

def cleanup_old_logs(days=30):
    """Fonction utilitaire pour nettoyer les anciens logs"""
    _logger_manager.cleanup_old_logs(days)

def get_log_statistics():
    """Fonction utilitaire pour les statistiques"""
    return _logger_manager.get_log_stats()

class LogContext:
    """Gestionnaire de contexte pour logging temporaire"""
    
    def __init__(self, logger_name, level=None, extra_info=None):
        self.logger = get_logger(logger_name)
        self.original_level = self.logger.level
        self.new_level = level
        self.extra_info = extra_info or {}
    
    def __enter__(self):
        if self.new_level:
            self.logger.setLevel(self.new_level)
        
        # Log d'entrée de contexte
        context_info = " | ".join([f"{k}={v}" for k, v in self.extra_info.items()])
        if context_info:
            self.logger.debug(f"🔽 Début contexte: {context_info}")
        
        return self.logger
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        # Log de sortie de contexte
        if exc_type:
            self.logger.error(f"🔺 Fin contexte avec erreur: {exc_type.__name__}: {exc_val}")
        else:
            context_info = " | ".join([f"{k}={v}" for k, v in self.extra_info.items()])
            if context_info:
                self.logger.debug(f"🔺 Fin contexte: {context_info}")
        
        # Restauration du niveau original
        if self.new_level:
            self.logger.setLevel(self.original_level)
        
        # Ne pas supprimer l'exception
        return False

def log_execution_time(logger_name="performance"):
    """Décorateur pour mesurer le temps d'exécution"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            logger = get_logger(logger_name)
            start_time = time.time()
            
            try:
                result = func(*args, **kwargs)
                execution_time = time.time() - start_time
                
                logger.debug(f"⏱️ {func.__name__} exécuté en {execution_time:.3f}s")
                return result
            
            except Exception as e:
                execution_time = time.time() - start_time
                logger.error(f"💥 {func.__name__} échoué après {execution_time:.3f}s: {e}")
                raise
        
        return wrapper
    return decorator

def log_function_calls(logger_name="calls"):
    """Décorateur pour logger les appels de fonction"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            logger = get_logger(logger_name)
            
            # Préparation des arguments pour log (tronqués si trop longs)
            args_str = ", ".join([str(arg)[:50] + "..." if len(str(arg)) > 50 else str(arg) for arg in args[:3]])
            kwargs_str = ", ".join([f"{k}={str(v)[:30]}{'...' if len(str(v)) > 30 else ''}" for k, v in list(kwargs.items())[:3]])
            
            logger.debug(f"📞 {func.__name__}({args_str}{', ' + kwargs_str if kwargs_str else ''})")
            
            try:
                result = func(*args, **kwargs)
                logger.debug(f"✅ {func.__name__} terminé avec succès")
                return result
            
            except Exception as e:
                logger.error(f"❌ {func.__name__} échoué: {e}")
                raise
        
        return wrapper
    return decorator

# Configuration des niveaux de log spécialisés
class LogLevels:
    """Niveaux de log spécialisés pour PrismFetch"""
    
    TRACE = 5      # Très détaillé
    DEBUG = 10     # Debug normal
    VERBOSE = 15   # Verbeux
    INFO = 20      # Information
    SUCCESS = 25   # Succès d'opération
    WARNING = 30   # Avertissement
    ERROR = 40     # Erreur
    CRITICAL = 50  # Critique

# Ajout des niveaux personnalisés
logging.addLevelName(LogLevels.TRACE, "TRACE")
logging.addLevelName(LogLevels.VERBOSE, "VERBOSE")
logging.addLevelName(LogLevels.SUCCESS, "SUCCESS")

def trace(self, message, *args, **kwargs):
    """Méthode trace pour logger"""
    if self.isEnabledFor(LogLevels.TRACE):
        self._log(LogLevels.TRACE, message, args, **kwargs)

def verbose(self, message, *args, **kwargs):
    """Méthode verbose pour logger"""
    if self.isEnabledFor(LogLevels.VERBOSE):
        self._log(LogLevels.VERBOSE, message, args, **kwargs)

def success(self, message, *args, **kwargs):
    """Méthode success pour logger"""
    if self.isEnabledFor(LogLevels.SUCCESS):
        self._log(LogLevels.SUCCESS, message, args, **kwargs)

# Ajout des méthodes aux loggers
logging.Logger.trace = trace
logging.Logger.verbose = verbose
logging.Logger.success = success

if __name__ == "__main__":
    # Test du système de logging
    print("🔍 Test du système de logging PrismFetch V3")
    print("=" * 50)
    
    # Création de loggers de test
    main_logger = get_logger("main")
    download_logger = create_module_logger("download", "download.log")
    security_logger = get_logger("security")
    
    # Test des niveaux
    main_logger.debug("🐛 Message de debug")
    main_logger.info("ℹ️ Message d'information")
    main_logger.success("✅ Opération réussie")
    main_logger.warning("⚠️ Avertissement")
    main_logger.error("❌ Erreur")
    
    # Test contexte
    with LogContext("test_context", extra_info={"operation": "download", "url": "test.com"}):
        main_logger.info("Opération dans contexte")
    
    # Statistiques
    stats = get_log_statistics()
    print(f"\n📊 Statistiques des logs:")
    print(f"   📁 Dossier: {stats['log_directory']}")
    print(f"   📄 Fichiers: {stats['total_files']}")
    print(f"   💾 Taille totale: {stats['total_size_mb']} MB")
    
    print(f"\n✅ Test du système de logging terminé")
    print(f"   Consultez les logs dans le dossier: {Path('logs').absolute()}")