#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
PrismFetch V3 - Security Manager FONCTIONNEL
Version 3.0.0 FINAL - Créé par Metadata
Gestion TOR, Sandbox, Nettoyage RÉEL
"""

import os
import subprocess
import time
import shutil
import requests
from pathlib import Path

try:
    from utils.logger import get_logger
except ImportError:
    import logging
    def get_logger(name):
        return logging.getLogger(name)

class SecurityManager:
    """Gestionnaire de sécurité FONCTIONNEL"""
    
    def __init__(self, tor_enabled=False, sandbox_enabled=True, tor_port=9050, control_port=9051):
        """Initialisation FONCTIONNELLE"""
        self.tor_enabled = tor_enabled
        self.sandbox_enabled = sandbox_enabled
        self.tor_port = tor_port
        self.control_port = control_port
        
        # Dossiers
        self.sandbox_dir = Path("sandbox")
        self.quarantine_dir = Path("quarantine")
        self.logs_dir = Path("logs")
        
        # Création des dossiers
        for directory in [self.sandbox_dir, self.quarantine_dir, self.logs_dir]:
            directory.mkdir(parents=True, exist_ok=True)
        
        self.logger = get_logger(__name__)
        self.logger.info("🔒 Gestionnaire de sécurité V3 initialisé")
        
        # État TOR
        self._tor_process = None
        self._tor_running = False
    
    def check_url_safety(self, url: str) -> bool:
        """Vérification sécurité URL basique"""
        try:
            # Vérifications basiques
            if not url.startswith(('http://', 'https://')):
                return False
            
            # Liste noire basique
            blacklist = ['malware', 'virus', 'dangerous']
            url_lower = url.lower()
            
            for term in blacklist:
                if term in url_lower:
                    return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Erreur vérification URL: {e}")
            return False
    
    def is_sandbox_enabled(self) -> bool:
        """État sandbox"""
        return self.sandbox_enabled
    
    def get_sandbox_dir(self) -> str:
        """Dossier sandbox"""
        return str(self.sandbox_dir)
    
    def process_sandbox_files(self, dest_dir: str):
        """Traitement fichiers sandbox vers destination FONCTIONNEL"""
        try:
            dest_path = Path(dest_dir)
            dest_path.mkdir(parents=True, exist_ok=True)
            
            moved_files = 0
            for file_path in self.sandbox_dir.glob("*"):
                if file_path.is_file():
                    # Déplacer vers destination
                    dest_file = dest_path / file_path.name
                    shutil.move(str(file_path), str(dest_file))
                    moved_files += 1
                    self.logger.info(f"📦 Fichier déplacé: {file_path.name}")
            
            self.logger.info(f"📦 {moved_files} fichiers traités depuis sandbox")
            return moved_files
            
        except Exception as e:
            self.logger.error(f"Erreur traitement sandbox: {e}")
            return 0
    
    def clean_sandbox(self):
        """Nettoyage sandbox FONCTIONNEL"""
        try:
            cleaned_files = 0
            cleaned_size = 0
            
            for item in self.sandbox_dir.iterdir():
                try:
                    if item.is_file():
                        size = item.stat().st_size
                        item.unlink()
                        cleaned_files += 1
                        cleaned_size += size
                    elif item.is_dir():
                        shutil.rmtree(item)
                        cleaned_files += 1
                except PermissionError:
                    # Déplacer vers quarantine si impossible de supprimer
                    try:
                        quarantine_path = self.quarantine_dir / item.name
                        shutil.move(str(item), str(quarantine_path))
                        self.logger.warning(f"⚠️ Fichier en quarantaine: {item.name}")
                    except:
                        pass
                except Exception as e:
                    self.logger.warning(f"⚠️ Erreur suppression {item.name}: {e}")
            
            # Formatage taille
            if cleaned_size > 1024*1024:
                size_str = f"{cleaned_size/(1024*1024):.1f} MB"
            else:
                size_str = f"{cleaned_size/1024:.1f} KB"
            
            self.logger.info(f"🗑️ Sandbox nettoyé: {cleaned_files} éléments, {size_str}")
            return True, f"Sandbox nettoyé: {cleaned_files} éléments"
            
        except Exception as e:
            error_msg = f"Erreur nettoyage sandbox: {e}"
            self.logger.error(error_msg)
            return False, error_msg
    
    def enable_tor(self):
        """Activation TOR FONCTIONNELLE"""
        try:
            if self._tor_running:
                return True, "TOR déjà actif"
            
            # Recherche de TOR
            tor_path = self._find_tor_executable()
            if not tor_path:
                return False, "TOR non trouvé - installez Tor Browser"
            
            # Configuration TOR
            torrc_content = f"""
SocksPort {self.tor_port}
ControlPort {self.control_port}
DataDirectory sandbox/tor_data
"""
            
            torrc_path = self.sandbox_dir / "torrc"
            with open(torrc_path, 'w') as f:
                f.write(torrc_content)
            
            # Démarrage TOR
            self.logger.info(f"🧅 Démarrage TOR sur port {self.tor_port}")
            
            self._tor_process = subprocess.Popen([
                tor_path,
                "-f", str(torrc_path)
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            
            # Attendre que TOR démarre (max 30s)
            for i in range(30):
                if self._test_tor_connection():
                    self._tor_running = True
                    self.tor_enabled = True
                    self.logger.info("✅ TOR démarré avec succès")
                    return True, "TOR activé avec succès"
                time.sleep(1)
            
            # Échec démarrage
            if self._tor_process:
                self._tor_process.terminate()
                self._tor_process = None
            
            return False, "Timeout démarrage TOR"
            
        except Exception as e:
            error_msg = f"Erreur activation TOR: {e}"
            self.logger.error(error_msg)
            return False, error_msg
    
    def disable_tor(self):
        """Désactivation TOR FONCTIONNELLE"""
        try:
            if not self._tor_running:
                return True, "TOR déjà désactivé"
            
            # Arrêter le processus TOR
            if self._tor_process:
                self._tor_process.terminate()
                
                # Attendre arrêt propre
                try:
                    self._tor_process.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    self._tor_process.kill()
                
                self._tor_process = None
            
            self._tor_running = False
            self.tor_enabled = False
            
            # Nettoyage fichiers TOR
            tor_data_dir = self.sandbox_dir / "tor_data"
            if tor_data_dir.exists():
                shutil.rmtree(tor_data_dir, ignore_errors=True)
            
            torrc_path = self.sandbox_dir / "torrc"
            if torrc_path.exists():
                torrc_path.unlink()
            
            self.logger.info("🧅 TOR désactivé")
            return True, "TOR désactivé avec succès"
            
        except Exception as e:
            error_msg = f"Erreur désactivation TOR: {e}"
            self.logger.error(error_msg)
            return False, error_msg
    
    def _find_tor_executable(self):
        """Recherche exécutable TOR"""
        # Chemins courants TOR
        if os.name == 'nt':  # Windows
            possible_paths = [
                "C:\\Users\\{}\\Desktop\\Tor Browser\\Browser\\TorBrowser\\Tor\\tor.exe".format(os.getenv('USERNAME')),
                "C:\\Program Files\\Tor Browser\\Browser\\TorBrowser\\Tor\\tor.exe",
                "C:\\Program Files (x86)\\Tor Browser\\Browser\\TorBrowser\\Tor\\tor.exe",
                "tor.exe"
            ]
        else:  # Linux/Mac
            possible_paths = [
                "/usr/bin/tor",
                "/usr/local/bin/tor",
                "tor"
            ]
        
        for path in possible_paths:
            try:
                if Path(path).exists():
                    return path
                # Test commande
                result = subprocess.run([path, "--version"], 
                                      capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    return path
            except:
                continue
        
        return None
    
    def _test_tor_connection(self):
        """Test connexion TOR"""
        try:
            proxies = {
                'http': f'socks5://127.0.0.1:{self.tor_port}',
                'https': f'socks5://127.0.0.1:{self.tor_port}'
            }
            
            response = requests.get('http://httpbin.org/ip', 
                                  proxies=proxies, timeout=10)
            return response.status_code == 200
            
        except:
            return False
    
    def new_identity(self):
        """Nouvelle identité TOR FONCTIONNELLE"""
        try:
            if not self._tor_running:
                return False, "TOR non actif"
            
            # Commande de nouvelle identité via port de contrôle
            try:
                import socket
                s = socket.socket()
                s.connect(('127.0.0.1', self.control_port))
                s.send(b'AUTHENTICATE\r\n')
                s.recv(1024)
                s.send(b'SIGNAL NEWNYM\r\n')
                response = s.recv(1024)
                s.close()
                
                if b'250 OK' in response:
                    self.logger.info("🔄 Nouvelle identité TOR obtenue")
                    return True, "Nouvelle identité obtenue"
                else:
                    return False, "Erreur commande TOR"
                    
            except Exception as e:
                # Fallback: redémarrer TOR
                self.disable_tor()
                time.sleep(2)
                return self.enable_tor()
            
        except Exception as e:
            error_msg = f"Erreur nouvelle identité: {e}"
            self.logger.error(error_msg)
            return False, error_msg
    
    def test_connectivity(self, country="US", timeout=10):
        """Test connectivité FONCTIONNEL"""
        try:
            # Test connexion normale
            start_time = time.time()
            
            try:
                response = requests.get('https://httpbin.org/ip', timeout=timeout)
                normal_ip = response.json().get('origin', 'unknown')
                normal_time = time.time() - start_time
            except Exception as e:
                return False, f"Connexion normale échoué: {e}"
            
            # Test connexion TOR si activé
            if self._tor_running:
                try:
                    proxies = {
                        'http': f'socks5://127.0.0.1:{self.tor_port}',
                        'https': f'socks5://127.0.0.1:{self.tor_port}'
                    }
                    
                    tor_start = time.time()
                    response = requests.get('https://httpbin.org/ip', 
                                          proxies=proxies, timeout=timeout)
                    tor_ip = response.json().get('origin', 'unknown')
                    tor_time = time.time() - tor_start
                    
                    # Vérifier que les IPs sont différentes
                    if normal_ip != tor_ip:
                        result = f"✅ Connexions OK\n🌐 Normal: {normal_ip} ({normal_time:.1f}s)\n🧅 TOR: {tor_ip} ({tor_time:.1f}s)"
                        return True, result
                    else:
                        return False, "TOR ne change pas l'IP"
                        
                except Exception as e:
                    return False, f"Connexion TOR échouée: {e}"
            else:
                result = f"✅ Connexion normale OK\n🌐 IP: {normal_ip} ({normal_time:.1f}s)"
                return True, result
            
        except Exception as e:
            error_msg = f"Erreur test connectivité: {e}"
            self.logger.error(error_msg)
            return False, error_msg
    
    def scan_file_security(self, file_path):
        """Scan sécurité fichier basique"""
        try:
            path = Path(file_path)
            if not path.exists():
                return False, "Fichier inexistant"
            
            # Vérifications basiques
            size = path.stat().st_size
            
            # Fichier trop volumineux
            if size > 1024 * 1024 * 1024:  # 1GB
                return False, "Fichier trop volumineux"
            
            # Extensions dangereuses
            dangerous_exts = ['.exe', '.scr', '.bat', '.cmd', '.com', '.vbs', '.js']
            if path.suffix.lower() in dangerous_exts:
                return False, f"Extension dangereuse: {path.suffix}"
            
            return True, "Fichier sécurisé"
            
        except Exception as e:
            return False, f"Erreur scan: {e}"
    
    def get_security_logs(self):
        """Récupération logs sécurité"""
        try:
            log_file = self.logs_dir / "security.log"
            if log_file.exists():
                with open(log_file, 'r', encoding='utf-8') as f:
                    return f.read()
            return "Aucun log de sécurité"
        except:
            return "Erreur lecture logs"
    
    def log_security_event(self, event, level="INFO"):
        """Log événement sécurité"""
        try:
            log_file = self.logs_dir / "security.log"
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
            log_entry = f"[{timestamp}] {level}: {event}\n"
            
            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(log_entry)
                
        except Exception as e:
            self.logger.error(f"Erreur log sécurité: {e}")

# Test si exécuté directement
if __name__ == "__main__":
    print("🧪 Test SecurityManager FONCTIONNEL")
    
    sm = SecurityManager()
    
    # Test nettoyage sandbox
    print("🗑️ Test nettoyage sandbox...")
    success, message = sm.clean_sandbox()
    print(f"Résultat: {success} - {message}")
    
    # Test connectivité
    print("🧪 Test connectivité...")
    success, message = sm.test_connectivity()
    print(f"Résultat: {success} - {message}")
    
    print("✅ SecurityManager testé")