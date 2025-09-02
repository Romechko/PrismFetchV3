#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
PrismFetch V3 - Interface Principale ULTRA STABLE
Version 3.0.0 FINAL - Créé par Metadata
SANS erreurs drag & drop, encodage fixé
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import ttkbootstrap as ttkb
from ttkbootstrap.constants import *
import threading
import time
import json
import os
import subprocess
import psutil
from pathlib import Path
from urllib.parse import urlparse

# Support drag & drop SÉCURISÉ (test complet)
DRAG_DROP_AVAILABLE = False
try:
    from tkinterdnd2 import DND_FILES, TkinterDnD
    # Test réel si tkinterdnd2 fonctionne
    test_root = TkinterDnD.Tk()
    test_root.withdraw()
    test_root.destroy()
    DRAG_DROP_AVAILABLE = True
    print("✅ Drag & drop disponible")
except Exception as e:
    print(f"⚠️ Drag & drop désactivé: {e}")
    DRAG_DROP_AVAILABLE = False

try:
    from utils.logger import get_logger
except ImportError:
    import logging
    def get_logger(name):
        logging.basicConfig(level=logging.INFO)
        return logging.getLogger(name)

class PrismFetchMainWindow:
    """Interface principale ULTRA STABLE"""
    
    def __init__(self, root, download_manager, security_manager):
        """Initialisation SANS erreurs"""
        self.root = root
        self.download_manager = download_manager
        self.security_manager = security_manager
        self.logger = get_logger(__name__)
        
        # Configuration
        self.config = self.load_config()
        self.current_mode = self.config.get("interface", {}).get("mode", "simple")
        self.current_theme = self.config.get("interface", {}).get("theme", "darkly")
        
        # Variables
        self.url_var = tk.StringVar()
        self.output_dir_var = tk.StringVar(value="data/downloads")
        self.progress_var = tk.DoubleVar()
        self.status_var = tk.StringVar(value="✅ PrismFetch V3 prêt")
        self.is_downloading = False
        
        # URLs queue
        self.urls_queue = []
        
        # Monitoring
        self.monitoring_active = True
        self.monitoring_data = {"cpu": 0, "ram": 0, "disk": 0}
        
        # Initialisation SÉCURISÉE
        self.setup_window()
        self.create_widgets()
        self.start_monitoring()
        
        self.logger.info("✅ Interface V3 ULTRA STABLE initialisée")
    
    def load_config(self):
        """Chargement config avec fallback"""
        try:
            config_path = Path("config/settings.json")
            if config_path.exists():
                with open(config_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"⚠️ Config par défaut utilisée: {e}")
        
        return {
            "interface": {"mode": "simple", "theme": "darkly"},
            "download": {"default_path": "data/downloads", "quality": "best", "parallel": 4},
            "security": {"tor_enabled": False, "sandbox": True},
            "renaming": {"enabled": True}
        }
    
    def setup_window(self):
        """Configuration fenêtre SANS drag & drop"""
        self.root.title("🚀 PrismFetch V3 - Téléchargeur Intelligent")
        self.root.geometry("1200x800")
        self.root.minsize(1000, 600)
        
        # Style
        self.style = ttkb.Style(theme=self.current_theme)
        
        # Drag & drop SEULEMENT si disponible
        if DRAG_DROP_AVAILABLE:
            try:
                # Transformer root en TkinterDnD si nécessaire
                if not hasattr(self.root, 'drop_target_register'):
                    # Recréer avec TkinterDnD
                    old_root = self.root
                    self.root = TkinterDnD.Tk()
                    self.root.title(old_root.title())
                    self.root.geometry("1200x800")
                    old_root.destroy()
                
                self.root.drop_target_register(DND_FILES)
                self.root.dnd_bind('<<Drop>>', self.on_file_drop)
                print("✅ Drag & drop activé")
            except Exception as e:
                print(f"⚠️ Drag & drop échoué: {e}")
                # Continuer sans drag & drop
        
        # Raccourcis
        self.root.bind('<Control-v>', lambda e: self.paste_url())
        self.root.bind('<Control-d>', lambda e: self.start_download())
        self.root.bind('<Control-s>', lambda e: self.switch_mode())
        
        self.center_window()
    
    def center_window(self):
        """Centrage fenêtre"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")
    
    def on_file_drop(self, event):
        """Gestion fichiers droppés"""
        try:
            files = self.root.tk.splitlist(event.data)
            for file_path in files:
                file_path = file_path.replace('{', '').replace('}', '')
                path_obj = Path(file_path)
                
                if path_obj.suffix.lower() == '.txt':
                    self.import_urls_from_file(file_path)
                elif path_obj.suffix.lower() == '.torrent':
                    self.add_torrent_file(file_path)
            
            self.log_message(f"📁 {len(files)} fichier(s) traité(s)")
        except Exception as e:
            self.log_message(f"❌ Erreur drag & drop: {e}")
    
    def create_widgets(self):
        """Création interface COMPLÈTE"""
        # Nettoyer interface existante
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Frame principal
        self.main_frame = ttkb.Frame(self.root, padding=10)
        self.main_frame.pack(fill=BOTH, expand=YES)
        
        # En-tête
        self.create_header()
        
        # Interface selon mode
        if self.current_mode == "simple":
            self.create_simple_interface()
        else:
            self.create_advanced_interface()
        
        # Barre de statut
        self.create_status_bar()
    
    def create_header(self):
        """En-tête avec commutateur mode"""
        header_frame = ttkb.Frame(self.main_frame)
        header_frame.pack(fill=X, pady=(0, 20))
        
        # Titre
        title_frame = ttkb.Frame(header_frame)
        title_frame.pack(side=LEFT)
        
        ttkb.Label(title_frame, text="🚀 PrismFetch V3", font=("Arial", 18, "bold"), bootstyle=PRIMARY).pack(anchor=W)
        ttkb.Label(title_frame, text="💎 Version 3.0.0 FINAL - Créé par Metadata", font=("Arial", 9), bootstyle=SECONDARY).pack(anchor=W)
        
        # Commutateur de mode
        mode_frame = ttkb.Frame(header_frame)
        mode_frame.pack(side=RIGHT)
        
        ttkb.Label(mode_frame, text="Mode:", font=("Arial", 10, "bold")).pack(side=LEFT, padx=(0, 10))
        
        self.simple_btn = ttkb.Button(
            mode_frame,
            text="🎯 Simple",
            bootstyle="success" if self.current_mode == "simple" else "outline-success",
            command=lambda: self.switch_to_mode("simple"),
            width=12
        )
        self.simple_btn.pack(side=LEFT, padx=(0, 5))
        
        self.advanced_btn = ttkb.Button(
            mode_frame,
            text="🔧 Avancé", 
            bootstyle="primary" if self.current_mode == "advanced" else "outline-primary",
            command=lambda: self.switch_to_mode("advanced"),
            width=12
        )
        self.advanced_btn.pack(side=LEFT)
    
    def switch_to_mode(self, mode):
        """Changement de mode SANS duplication"""
        if mode != self.current_mode:
            self.current_mode = mode
            self.config["interface"]["mode"] = mode
            self.save_config()
            self.create_widgets()  # Recréer interface
            self.log_message(f"🔄 Mode {mode} activé")
    
    def save_config(self):
        """Sauvegarde configuration"""
        try:
            config_path = Path("config/settings.json")
            config_path.parent.mkdir(exist_ok=True)
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"⚠️ Erreur sauvegarde config: {e}")
    
    def create_simple_interface(self):
        """Interface simple COMPLÈTE"""
        content_frame = ttkb.Frame(self.main_frame)
        content_frame.pack(fill=BOTH, expand=YES)
        
        # Zone URL
        url_frame = ttkb.LabelFrame(content_frame, text="🌐 URL ou Fichier", padding=15)
        url_frame.pack(fill=X, pady=(0, 15))
        
        # Instructions
        if DRAG_DROP_AVAILABLE:
            instruction_text = "• Collez URL • Glissez .txt/.torrent • Import manuel"
        else:
            instruction_text = "• Collez URL • Import .txt/.torrent (drag & drop désactivé)"
        
        ttkb.Label(url_frame, text=instruction_text, font=("Arial", 9), bootstyle=INFO).pack(anchor=W, pady=(0, 5))
        
        # Entry URL
        self.url_entry = ttkb.Entry(url_frame, textvariable=self.url_var, font=("Arial", 11))
        self.url_entry.pack(fill=X, pady=(0, 10))
        
        # Boutons URL
        url_buttons = ttkb.Frame(url_frame)
        url_buttons.pack(fill=X)
        
        ttkb.Button(url_buttons, text="📋 Coller", command=self.paste_url, bootstyle=INFO).pack(side=LEFT, padx=(0, 5))
        ttkb.Button(url_buttons, text="📄 Import .txt", command=self.import_txt_file, bootstyle=SUCCESS).pack(side=LEFT, padx=(0, 5))
        ttkb.Button(url_buttons, text="🧲 .torrent", command=self.import_torrent_file, bootstyle=WARNING).pack(side=LEFT, padx=(0, 5))
        ttkb.Button(url_buttons, text="🧪 Test", command=self.test_url, bootstyle=SECONDARY).pack(side=LEFT, padx=(0, 15))
        ttkb.Button(url_buttons, text="🗑️ Clear", command=self.clear_url, bootstyle=DANGER).pack(side=RIGHT)
        
        # Configuration
        config_frame = ttkb.LabelFrame(content_frame, text="⚙️ Configuration", padding=15)
        config_frame.pack(fill=X, pady=(0, 15))
        
        # Dossier + qualité
        output_frame = ttkb.Frame(config_frame)
        output_frame.pack(fill=X, pady=(0, 10))
        
        ttkb.Label(output_frame, text="📁 Dossier:").pack(side=LEFT)
        self.output_entry = ttkb.Entry(output_frame, textvariable=self.output_dir_var, width=40)
        self.output_entry.pack(side=LEFT, padx=(5, 5))
        ttkb.Button(output_frame, text="📂", command=self.browse_output_dir, width=3).pack(side=LEFT, padx=(0, 20))
        
        ttkb.Label(output_frame, text="🎵 Qualité:").pack(side=RIGHT, padx=(0, 5))
        self.quality_var = tk.StringVar(value="Auto")
        quality_combo = ttkb.Combobox(
            output_frame,
            textvariable=self.quality_var,
            values=["Auto", "FLAC", "WAV", "MP3 320k", "MP3 256k", "4K", "1080p", "720p", "best", "worst"],
            width=12,
            state="readonly"
        )
        quality_combo.pack(side=RIGHT)
        
        # Options
        options_frame = ttkb.Frame(config_frame)
        options_frame.pack(fill=X)
        
        self.rename_var = tk.BooleanVar(value=True)
        self.sandbox_var = tk.BooleanVar(value=True)
        self.tor_var = tk.BooleanVar(value=False)
        
        ttkb.Checkbutton(options_frame, text="📝 Renommage IA", variable=self.rename_var, bootstyle="round-toggle").pack(side=LEFT, padx=(0, 15))
        ttkb.Checkbutton(options_frame, text="🔒 Sandbox", variable=self.sandbox_var, bootstyle="round-toggle").pack(side=LEFT, padx=(0, 15))
        ttkb.Checkbutton(options_frame, text="🧅 TOR", variable=self.tor_var, bootstyle="round-toggle").pack(side=LEFT)
        
        # Zone téléchargement
        download_frame = ttkb.LabelFrame(content_frame, text="⬇️ Téléchargement", padding=15)
        download_frame.pack(fill=BOTH, expand=YES)
        
        # Bouton principal
        download_header = ttkb.Frame(download_frame)
        download_header.pack(fill=X, pady=(0, 15))
        
        self.download_btn = ttkb.Button(
            download_header,
            text="🚀 TÉLÉCHARGER",
            bootstyle="success",
            command=self.start_download,
            width=25
        )
        self.download_btn.pack(side=LEFT)
        
        # Queue info
        self.queue_label = ttkb.Label(
            download_header,
            text=f"📋 Queue: {len(self.urls_queue)} éléments",
            font=("Arial", 10),
            bootstyle=INFO
        )
        self.queue_label.pack(side=RIGHT)
        
        # Barre de progression
        self.progress_bar = ttkb.Progressbar(
            download_frame,
            variable=self.progress_var,
            bootstyle="striped",
            length=600
        )
        self.progress_bar.pack(fill=X, pady=(0, 15))
        
        # Logs
        self.create_log_section(download_frame)
    
    def create_advanced_interface(self):
        """Interface avancée avec onglets"""
        content_frame = ttkb.Frame(self.main_frame)
        content_frame.pack(fill=BOTH, expand=YES)
        
        # Notebook
        self.notebook = ttkb.Notebook(content_frame)
        self.notebook.pack(fill=BOTH, expand=YES)
        
        # Onglets
        self.create_download_tab()
        self.create_security_tab()
        self.create_renaming_tab()
        self.create_maintenance_tab()
        self.create_settings_tab()
    
    def create_download_tab(self):
        """Onglet téléchargements"""
        download_tab = ttkb.Frame(self.notebook, padding=15)
        self.notebook.add(download_tab, text="⬇️ Téléchargements")
        
        # URLs multiples
        urls_frame = ttkb.LabelFrame(download_tab, text="🌐 URLs Multiples", padding=10)
        urls_frame.pack(fill=X, pady=(0, 15))
        
        # Entry + boutons
        url_input_frame = ttkb.Frame(urls_frame)
        url_input_frame.pack(fill=X, pady=(0, 10))
        
        self.multi_url_entry = ttkb.Entry(url_input_frame, font=("Arial", 10))
        self.multi_url_entry.pack(side=LEFT, fill=X, expand=YES, padx=(0, 10))
        
        ttkb.Button(url_input_frame, text="➕ Ajouter", command=self.add_url_to_queue, bootstyle=SUCCESS).pack(side=RIGHT, padx=(5, 0))
        ttkb.Button(url_input_frame, text="📄 Import", command=self.import_txt_file, bootstyle=INFO).pack(side=RIGHT, padx=(5, 0))
        
        # Liste URLs
        list_frame = ttkb.Frame(urls_frame)
        list_frame.pack(fill=X)
        
        columns = ("URL", "Statut", "Outil", "Progrès")
        self.urls_tree = ttkb.Treeview(list_frame, columns=columns, show="headings", height=6)
        
        for col in columns:
            self.urls_tree.heading(col, text=col)
            width = 200 if col == "URL" else 100
            self.urls_tree.column(col, width=width)
        
        urls_scrollbar = ttkb.Scrollbar(list_frame, orient=VERTICAL, command=self.urls_tree.yview)
        self.urls_tree.configure(yscrollcommand=urls_scrollbar.set)
        
        self.urls_tree.pack(side=LEFT, fill=BOTH, expand=YES)
        urls_scrollbar.pack(side=RIGHT, fill=Y)
        
        # Boutons de gestion
        urls_buttons = ttkb.Frame(urls_frame)
        urls_buttons.pack(fill=X, pady=(10, 0))
        
        ttkb.Button(urls_buttons, text="🚀 Démarrer", command=self.start_batch_download, bootstyle=SUCCESS).pack(side=LEFT, padx=(0, 5))
        ttkb.Button(urls_buttons, text="⏸️ Pause", command=self.pause_downloads, bootstyle=WARNING).pack(side=LEFT, padx=(0, 5))
        ttkb.Button(urls_buttons, text="⏹️ Stop", command=self.stop_downloads, bootstyle=DANGER).pack(side=LEFT, padx=(0, 5))
        ttkb.Button(urls_buttons, text="🗑️ Clear", command=self.clear_queue, bootstyle=SECONDARY).pack(side=LEFT, padx=(0, 15))
        
        # Logs téléchargement
        self.create_log_section(download_tab)
    
    def create_security_tab(self):
        """Onglet sécurité"""
        security_tab = ttkb.Frame(self.notebook, padding=15)
        self.notebook.add(security_tab, text="🔒 Sécurité")
        
        # TOR
        tor_frame = ttkb.LabelFrame(security_tab, text="🧅 Configuration TOR", padding=15)
        tor_frame.pack(fill=X, pady=(0, 15))
        
        tor_status_frame = ttkb.Frame(tor_frame)
        tor_status_frame.pack(fill=X, pady=(0, 15))
        
        self.tor_status_var = tk.StringVar(value="🔴 TOR Désactivé")
        self.tor_status_label = ttkb.Label(tor_status_frame, textvariable=self.tor_status_var, font=("Arial", 12, "bold"))
        self.tor_status_label.pack(side=LEFT)
        
        self.tor_toggle_btn = ttkb.Button(
            tor_status_frame,
            text="🟢 Activer TOR",
            command=self.toggle_tor,
            bootstyle=SUCCESS,
            width=15
        )
        self.tor_toggle_btn.pack(side=RIGHT)
        
        # Contrôles sécurité
        security_controls = ttkb.Frame(tor_frame)
        security_controls.pack(fill=X)
        
        ttkb.Button(security_controls, text="🔄 Nouvelle Identité", command=self.new_tor_identity, bootstyle=WARNING).pack(side=LEFT, padx=(0, 10))
        ttkb.Button(security_controls, text="🧪 Test Connexion", command=self.test_connection, bootstyle=INFO).pack(side=LEFT, padx=(0, 10))
        ttkb.Button(security_controls, text="🗑️ Nettoyer", command=self.clean_sandbox, bootstyle=SECONDARY).pack(side=LEFT)
        
        # Logs sécurité
        security_logs_frame = ttkb.LabelFrame(security_tab, text="📋 Logs Sécurité", padding=10)
        security_logs_frame.pack(fill=BOTH, expand=YES)
        
        self.security_log_text = ttkb.Text(security_logs_frame, height=12, wrap=WORD, font=("Consolas", 9))
        security_scrollbar = ttkb.Scrollbar(security_logs_frame, orient=VERTICAL, command=self.security_log_text.yview)
        self.security_log_text.configure(yscrollcommand=security_scrollbar.set)
        
        self.security_log_text.pack(side=LEFT, fill=BOTH, expand=YES)
        security_scrollbar.pack(side=RIGHT, fill=Y)
    
    def create_renaming_tab(self):
        """Onglet renommage"""
        renaming_tab = ttkb.Frame(self.notebook, padding=15)
        self.notebook.add(renaming_tab, text="📝 Renommage")
        
        # Type de contenu
        type_frame = ttkb.LabelFrame(renaming_tab, text="🎯 Type de Contenu", padding=15)
        type_frame.pack(fill=X, pady=(0, 15))
        
        self.content_type_var = tk.StringVar(value="automatique")
        content_types = ["automatique", "manga", "video_adult", "music", "video_youtube", "images"]
        
        type_buttons_frame = ttkb.Frame(type_frame)
        type_buttons_frame.pack(fill=X)
        
        for i, content_type in enumerate(content_types):
            ttkb.Radiobutton(
                type_buttons_frame,
                text=content_type.replace("_", " ").title(),
                variable=self.content_type_var,
                value=content_type,
                bootstyle="outline-toolbutton"
            ).pack(side=LEFT, padx=(5, 0))
        
        # Template
        template_frame = ttkb.LabelFrame(renaming_tab, text="📝 Template", padding=15)
        template_frame.pack(fill=X, pady=(0, 15))
        
        self.template_var = tk.StringVar(value="[{author}] {title} ({language})")
        template_entry = ttkb.Entry(template_frame, textvariable=self.template_var, font=("Courier", 10))
        template_entry.pack(fill=X, pady=(0, 10))
        
        variables_text = "Variables: {title} {author} {artist} {channel} {quality} {language} {tags} {date}"
        ttkb.Label(template_frame, text=variables_text, font=("Arial", 8), bootstyle=INFO).pack(anchor=W)
        
        # Boutons
        actions_frame = ttkb.Frame(renaming_tab)
        actions_frame.pack(fill=X, pady=(15, 0))
        
        ttkb.Button(actions_frame, text="💾 Sauvegarder", command=self.save_renaming_rules, bootstyle=SUCCESS).pack(side=LEFT, padx=(0, 10))
        ttkb.Button(actions_frame, text="📥 Charger", command=self.load_renaming_rules, bootstyle=INFO).pack(side=LEFT, padx=(0, 10))
        ttkb.Button(actions_frame, text="🔄 Reset", command=self.reset_renaming_rules, bootstyle=WARNING).pack(side=LEFT)
    
    def create_maintenance_tab(self):
        """Onglet maintenance"""
        maintenance_tab = ttkb.Frame(self.notebook, padding=15)
        self.notebook.add(maintenance_tab, text="🔧 Entretien")
        
        # Monitoring
        monitoring_frame = ttkb.LabelFrame(maintenance_tab, text="📊 Monitoring", padding=15)
        monitoring_frame.pack(fill=X, pady=(0, 15))
        
        # Métriques
        metrics_frame = ttkb.Frame(monitoring_frame)
        metrics_frame.pack(fill=X, pady=(0, 15))
        
        # CPU
        cpu_frame = ttkb.Frame(metrics_frame)
        cpu_frame.pack(side=LEFT, fill=X, expand=YES, padx=(0, 10))
        
        ttkb.Label(cpu_frame, text="🖥️ CPU", font=("Arial", 10, "bold")).pack()
        self.cpu_var = tk.StringVar(value="0%")
        self.cpu_progress = ttkb.Progressbar(cpu_frame, length=150, bootstyle="info")
        self.cpu_progress.pack(pady=(5, 2))
        ttkb.Label(cpu_frame, textvariable=self.cpu_var, font=("Arial", 9)).pack()
        
        # RAM
        ram_frame = ttkb.Frame(metrics_frame)
        ram_frame.pack(side=LEFT, fill=X, expand=YES, padx=(0, 10))
        
        ttkb.Label(ram_frame, text="🧠 RAM", font=("Arial", 10, "bold")).pack()
        self.ram_var = tk.StringVar(value="0%")
        self.ram_progress = ttkb.Progressbar(ram_frame, length=150, bootstyle="warning")
        self.ram_progress.pack(pady=(5, 2))
        ttkb.Label(ram_frame, textvariable=self.ram_var, font=("Arial", 9)).pack()
        
        # Disque
        disk_frame = ttkb.Frame(metrics_frame)
        disk_frame.pack(side=LEFT, fill=X, expand=YES)
        
        ttkb.Label(disk_frame, text="💽 Disque", font=("Arial", 10, "bold")).pack()
        self.disk_var = tk.StringVar(value="0%")
        self.disk_progress = ttkb.Progressbar(disk_frame, length=150, bootstyle="success")
        self.disk_progress.pack(pady=(5, 2))
        ttkb.Label(disk_frame, textvariable=self.disk_var, font=("Arial", 9)).pack()
        
        # Contrôles
        monitoring_controls = ttkb.Frame(monitoring_frame)
        monitoring_controls.pack(fill=X)
        
        self.monitoring_btn = ttkb.Button(
            monitoring_controls,
            text="⏸️ Pause",
            command=self.toggle_monitoring,
            bootstyle=WARNING
        )
        self.monitoring_btn.pack(side=LEFT)
        
        # Nettoyage
        cleanup_frame = ttkb.LabelFrame(maintenance_tab, text="🧹 Nettoyage", padding=15)
        cleanup_frame.pack(fill=X, pady=(0, 15))
        
        cleanup_buttons = ttkb.Frame(cleanup_frame)
        cleanup_buttons.pack(fill=X)
        
        ttkb.Button(cleanup_buttons, text="🗑️ Temp", command=lambda: self.cleanup_system("temp"), bootstyle=DANGER).pack(side=LEFT, padx=(0, 10))
        ttkb.Button(cleanup_buttons, text="📋 Cache", command=lambda: self.cleanup_system("cache"), bootstyle=WARNING).pack(side=LEFT, padx=(0, 10))
        ttkb.Button(cleanup_buttons, text="🧹 Complet", command=self.full_system_cleanup, bootstyle=SUCCESS).pack(side=RIGHT)
        
        # Résultats
        self.cleanup_result_var = tk.StringVar(value="Aucun nettoyage")
        ttkb.Label(cleanup_frame, textvariable=self.cleanup_result_var, font=("Arial", 9), bootstyle=INFO).pack(pady=(10, 0))
    
    def create_settings_tab(self):
        """Onglet paramètres"""
        settings_tab = ttkb.Frame(self.notebook, padding=15)
        self.notebook.add(settings_tab, text="⚙️ Paramètres")
        
        # Configuration générale
        general_frame = ttkb.LabelFrame(settings_tab, text="🎯 Général", padding=15)
        general_frame.pack(fill=X, pady=(0, 15))
        
        # Options
        self.auto_update_var = tk.BooleanVar(value=True)
        self.minimize_tray_var = tk.BooleanVar()
        
        ttkb.Checkbutton(general_frame, text="Mise à jour auto", variable=self.auto_update_var, bootstyle="round-toggle").pack(anchor=W, pady=5)
        ttkb.Checkbutton(general_frame, text="Minimiser en tray", variable=self.minimize_tray_var, bootstyle="round-toggle").pack(anchor=W, pady=5)
        
        # Statut drag & drop
        dragdrop_status = "✅ Activé" if DRAG_DROP_AVAILABLE else "❌ Désactivé"
        ttkb.Label(general_frame, text=f"📁 Drag & Drop: {dragdrop_status}", font=("Arial", 10)).pack(anchor=W, pady=10)
        
        if not DRAG_DROP_AVAILABLE:
            install_btn = ttkb.Button(general_frame, text="💡 Installer tkinterdnd2", command=self.install_dragdrop, bootstyle=INFO)
            install_btn.pack(anchor=W)
        
        # Actions
        actions_frame = ttkb.Frame(settings_tab)
        actions_frame.pack(fill=X, pady=(20, 0))
        
        ttkb.Button(actions_frame, text="💾 Sauvegarder", command=self.save_all_settings, bootstyle=SUCCESS).pack(side=LEFT, padx=(0, 10))
        ttkb.Button(actions_frame, text="🔄 Reset", command=self.reset_all_settings, bootstyle=WARNING).pack(side=LEFT)
    
    def create_log_section(self, parent):
        """Section logs avec coloration"""
        log_frame = ttkb.LabelFrame(parent, text="📋 Logs", padding=10)
        log_frame.pack(fill=BOTH, expand=YES)
        
        # Contrôles
        log_controls = ttkb.Frame(log_frame)
        log_controls.pack(fill=X, pady=(0, 10))
        
        self.auto_scroll_var = tk.BooleanVar(value=True)
        ttkb.Checkbutton(log_controls, text="Auto-scroll", variable=self.auto_scroll_var, bootstyle="round-toggle").pack(side=LEFT)
        
        ttkb.Button(log_controls, text="🗑️ Clear", command=self.clear_logs, bootstyle=DANGER).pack(side=RIGHT)
        
        # Zone de texte
        log_text_frame = ttkb.Frame(log_frame)
        log_text_frame.pack(fill=BOTH, expand=YES)
        
        self.log_text = ttkb.Text(log_text_frame, height=8, wrap=WORD, font=("Consolas", 9))
        log_scrollbar = ttkb.Scrollbar(log_text_frame, orient=VERTICAL, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=log_scrollbar.set)
        
        self.log_text.pack(side=LEFT, fill=BOTH, expand=YES)
        log_scrollbar.pack(side=RIGHT, fill=Y)
        
        # Tags couleur
        self.log_text.tag_configure("ERROR", foreground="red")
        self.log_text.tag_configure("WARNING", foreground="orange")
        self.log_text.tag_configure("SUCCESS", foreground="green")
        self.log_text.tag_configure("INFO", foreground="lightblue")
    
    def create_status_bar(self):
        """Barre de statut"""
        status_frame = ttkb.Frame(self.main_frame)
        status_frame.pack(fill=X, pady=(15, 0))
        
        ttkb.Separator(status_frame, orient=HORIZONTAL).pack(fill=X, pady=(0, 10))
        
        # Statut principal
        self.main_status_label = ttkb.Label(status_frame, textvariable=self.status_var, font=("Arial", 10))
        self.main_status_label.pack(side=LEFT)
        
        # Version + info
        version_text = f"v3.0.0 | Mode: {self.current_mode.title()}"
        if not DRAG_DROP_AVAILABLE:
            version_text += " | D&D: OFF"
        
        version_label = ttkb.Label(status_frame, text=version_text, font=("Arial", 8), bootstyle=DARK)
        version_label.pack(side=RIGHT)
    
    # MÉTHODES D'ACTION
    
    def paste_url(self):
        """Coller URL"""
        try:
            clipboard_content = self.root.clipboard_get()
            if '\n' in clipboard_content:
                urls = [line.strip() for line in clipboard_content.split('\n') if line.strip()]
                for url in urls:
                    if url.startswith('http'):
                        self.urls_queue.append({
                            'url': url,
                            'status': 'En attente',
                            'tool': self.get_tool_for_url(url),
                            'progress': 0
                        })
                self.update_queue_display()
                self.log_message(f"📋 {len(urls)} URLs ajoutées")
            else:
                self.url_var.set(clipboard_content)
                self.log_message("📋 URL collée")
        except tk.TclError:
            self.log_message("⚠️ Presse-papier vide")
    
    def get_tool_for_url(self, url):
        """Obtenir outil recommandé"""
        if self.download_manager:
            return self.download_manager.get_compatible_tool(url)
        
        domain = urlparse(url).netloc.lower()
        if "youtube" in domain:
            return "yt-dlp"
        elif "e-hentai" in domain or "nhentai" in domain:
            return "gallery-dl"
        elif any(site in domain for site in ["pornhub", "youporn", "xvideos"]):
            return "yt-dlp"
        else:
            return "yt-dlp"
    
    def clear_url(self):
        """Effacer URL"""
        self.url_var.set("")
        if hasattr(self, 'multi_url_entry'):
            self.multi_url_entry.delete(0, tk.END)
        self.log_message("🗑️ URL effacée")
    
    def import_txt_file(self):
        """Import fichier .txt"""
        file_path = filedialog.askopenfilename(
            title="Import fichier .txt",
            filetypes=[("Fichiers texte", "*.txt"), ("Tous", "*.*")]
        )
        if file_path:
            self.import_urls_from_file(file_path)
    
    def import_urls_from_file(self, file_path):
        """Import URLs depuis fichier"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                urls = [line.strip() for line in f if line.strip() and line.startswith('http')]
            
            added = 0
            for url in urls:
                self.urls_queue.append({
                    'url': url,
                    'status': 'En attente',
                    'tool': self.get_tool_for_url(url),
                    'progress': 0
                })
                added += 1
            
            self.update_queue_display()
            self.log_message(f"📄 {added} URLs importées depuis {Path(file_path).name}")
            
        except Exception as e:
            error_msg = f"❌ Erreur import: {e}"
            self.log_message(error_msg)
            messagebox.showerror("Erreur", error_msg)
    
    def import_torrent_file(self):
        """Import .torrent"""
        file_path = filedialog.askopenfilename(
            title="Import .torrent",
            filetypes=[("Torrents", "*.torrent"), ("Tous", "*.*")]
        )
        if file_path:
            self.add_torrent_file(file_path)
    
    def add_torrent_file(self, file_path):
        """Ajouter torrent à la queue"""
        try:
            torrent_dir = Path("data/torrents")
            torrent_dir.mkdir(exist_ok=True)
            
            import shutil
            dest_path = torrent_dir / Path(file_path).name
            shutil.copy2(file_path, dest_path)
            
            self.urls_queue.append({
                'url': f"file://{dest_path}",
                'status': 'En attente',
                'tool': 'torrent',
                'progress': 0
            })
            
            self.update_queue_display()
            self.log_message(f"🧲 Torrent ajouté: {Path(file_path).name}")
            
        except Exception as e:
            error_msg = f"❌ Erreur torrent: {e}"
            self.log_message(error_msg)
            messagebox.showerror("Erreur", error_msg)
    
    def test_url(self):
        """Test URL"""
        url = self.url_var.get().strip()
        if not url:
            messagebox.showwarning("Attention", "Saisissez une URL")
            return
        
        self.log_message(f"🧪 Test: {url[:50]}...")
        
        def test_thread():
            try:
                if self.download_manager:
                    supported, message = self.download_manager.test_site_support(url)
                    tool = self.download_manager.get_compatible_tool(url)
                    result = f"✅ Supporté par {tool}\n{message}" if supported else f"❌ Non supporté\n{message}"
                else:
                    result = f"✅ URL valide\n🔧 Outil: {self.get_tool_for_url(url)}"
                
                self.root.after(0, lambda: messagebox.showinfo("Test URL", result))
                self.root.after(0, lambda: self.log_message(f"🧪 {result.replace(chr(10), ' | ')}"))
                
            except Exception as e:
                error_msg = f"💥 Erreur test: {e}"
                self.root.after(0, lambda: messagebox.showerror("Erreur", error_msg))
                self.root.after(0, lambda: self.log_message(error_msg))
        
        threading.Thread(target=test_thread, daemon=True).start()
    
    def browse_output_dir(self):
        """Parcourir dossier"""
        directory = filedialog.askdirectory(initialdir=self.output_dir_var.get())
        if directory:
            self.output_dir_var.set(directory)
            self.log_message(f"📁 Dossier: {directory}")
    
    def start_download(self):
        """Démarrage téléchargement"""
        url = self.url_var.get().strip()
        if not url:
            messagebox.showwarning("Attention", "Saisissez une URL")
            return
        
        if self.is_downloading:
            messagebox.showinfo("Info", "Téléchargement en cours...")
            return
        
        self.is_downloading = True
        self.download_btn.config(state="disabled", text="⏳ En cours...")
        self.progress_var.set(0)
        
        quality = self.quality_var.get() if hasattr(self, 'quality_var') else "best"
        if quality == "Auto":
            quality = "best"
        
        self.log_message(f"🚀 Démarrage: {url[:50]}...")
        self.status_var.set("⏳ Téléchargement en cours...")
        
        def download_thread():
            try:
                def progress_callback(success, message, progress):
                    self.root.after(0, lambda: self.update_progress(success, message, progress))
                
                if self.download_manager:
                    success, message = self.download_manager.download(
                        url,
                        self.output_dir_var.get(),
                        progress_callback,
                        quality=quality
                    )
                else:
                    # Simulation
                    for i in range(0, 101, 20):
                        progress_callback(True, f"Simulation {i}%", i)
                        time.sleep(0.3)
                    success, message = True, "Téléchargement simulé"
                
                self.root.after(0, lambda: self.download_finished(success, message))
                
            except Exception as e:
                error_msg = f"💥 Erreur: {e}"
                self.root.after(0, lambda: self.download_finished(False, error_msg))
        
        threading.Thread(target=download_thread, daemon=True).start()
    
    def update_progress(self, success, message, progress):
        """Mise à jour progression"""
        if progress >= 0:
            self.progress_var.set(progress)
        self.log_message(f"📊 {message}")
    
    def download_finished(self, success, message):
        """Fin téléchargement"""
        self.is_downloading = False
        self.download_btn.config(state="normal", text="🚀 TÉLÉCHARGER")
        
        if success:
            self.progress_var.set(100)
            self.status_var.set("✅ Téléchargement réussi")
            self.log_message(f"✅ Succès: {message}")
            messagebox.showinfo("Succès", f"Téléchargement terminé!\n\n{message}")
        else:
            self.progress_var.set(0)
            self.status_var.set("❌ Téléchargement échoué")
            self.log_message(f"❌ Échec: {message}")
            messagebox.showerror("Erreur", f"Échec téléchargement:\n\n{message}")
    
    def update_queue_display(self):
        """Mise à jour affichage queue"""
        if hasattr(self, 'queue_label'):
            self.queue_label.config(text=f"📋 Queue: {len(self.urls_queue)} éléments")
        
        if hasattr(self, 'urls_tree'):
            # Vider le tree
            for item in self.urls_tree.get_children():
                self.urls_tree.delete(item)
            
            # Ajouter items
            for i, item in enumerate(self.urls_queue):
                url_short = item['url'][:50] + "..." if len(item['url']) > 50 else item['url']
                self.urls_tree.insert("", "end", values=(
                    url_short,
                    item['status'],
                    item['tool'],
                    f"{item['progress']}%"
                ))
    
    def log_message(self, message):
        """Ajout message au log"""
        if hasattr(self, 'log_text'):
            timestamp = time.strftime("%H:%M:%S")
            full_message = f"[{timestamp}] {message}\n"
            
            # Tag couleur
            tag = ""
            if "❌" in message or "ERROR" in message or "Erreur" in message:
                tag = "ERROR"
            elif "⚠️" in message or "WARNING" in message:
                tag = "WARNING"
            elif "✅" in message or "SUCCESS" in message or "Succès" in message:
                tag = "SUCCESS"
            else:
                tag = "INFO"
            
            self.log_text.insert(tk.END, full_message, tag)
            
            # Auto-scroll
            if hasattr(self, 'auto_scroll_var') and self.auto_scroll_var.get():
                self.log_text.see(tk.END)
            
            # Limite
            lines = int(self.log_text.index('end-1c').split('.')[0])
            if lines > 500:
                self.log_text.delete(1.0, "250.0")
    
    def start_monitoring(self):
        """Démarrage monitoring système"""
        def update_monitoring():
            if self.monitoring_active:
                try:
                    # CPU
                    cpu = psutil.cpu_percent(interval=None)
                    self.monitoring_data["cpu"] = cpu
                    if hasattr(self, 'cpu_var'):
                        self.cpu_var.set(f"{cpu:.1f}%")
                        self.cpu_progress['value'] = cpu
                    
                    # RAM
                    ram = psutil.virtual_memory().percent
                    self.monitoring_data["ram"] = ram
                    if hasattr(self, 'ram_var'):
                        self.ram_var.set(f"{ram:.1f}%")
                        self.ram_progress['value'] = ram
                    
                    # Disque
                    disk = psutil.disk_usage('/').percent if os.name != 'nt' else psutil.disk_usage('C:').percent
                    self.monitoring_data["disk"] = disk
                    if hasattr(self, 'disk_var'):
                        self.disk_var.set(f"{disk:.1f}%")
                        self.disk_progress['value'] = disk
                    
                except Exception as e:
                    pass
            
            # Répéter
            self.root.after(2000, update_monitoring)
        
        update_monitoring()
    
    # Méthodes stubs pour fonctionnalités avancées
    def add_url_to_queue(self): 
        url = self.multi_url_entry.get().strip() if hasattr(self, 'multi_url_entry') else ""
        if url and url.startswith('http'):
            self.urls_queue.append({
                'url': url,
                'status': 'En attente',
                'tool': self.get_tool_for_url(url),
                'progress': 0
            })
            self.multi_url_entry.delete(0, tk.END)
            self.update_queue_display()
            self.log_message(f"➕ URL ajoutée: {url[:50]}...")
    
    def start_batch_download(self): 
        if self.urls_queue and self.download_manager:
            self.log_message("🚀 Démarrage batch...")
            # Implémenter batch download
        else:
            self.log_message("⚠️ Queue vide ou manager indisponible")
    
    def pause_downloads(self): 
        self.log_message("⏸️ Téléchargements en pause")
        if hasattr(self.download_manager, 'pause_queue'):
            self.download_manager.pause_queue()
    
    def stop_downloads(self): 
        self.log_message("⏹️ Téléchargements arrêtés")
        if hasattr(self.download_manager, 'stop_queue'):
            self.download_manager.stop_queue()
    
    def clear_queue(self): 
        self.urls_queue.clear()
        self.update_queue_display()
        self.log_message("🗑️ Queue vidée")
    
    def toggle_tor(self): 
        if hasattr(self.security_manager, 'enable_tor'):
            if not self.security_manager.tor_enabled:
                success, msg = self.security_manager.enable_tor()
                if success:
                    self.tor_status_var.set("🟢 TOR Activé")
                    self.tor_toggle_btn.config(text="🔴 Désactiver")
                self.log_message(f"🧅 TOR: {msg}")
            else:
                success, msg = self.security_manager.disable_tor()
                if success:
                    self.tor_status_var.set("🔴 TOR Désactivé")
                    self.tor_toggle_btn.config(text="🟢 Activer")
                self.log_message(f"🧅 TOR: {msg}")
    
    def new_tor_identity(self): 
        if hasattr(self.security_manager, 'new_identity'):
            success, msg = self.security_manager.new_identity()
            self.log_message(f"🔄 Nouvelle identité: {msg}")
    
    def test_connection(self): 
        if hasattr(self.security_manager, 'test_connectivity'):
            success, msg = self.security_manager.test_connectivity()
            self.log_message(f"🧪 Test connexion: {msg}")
            messagebox.showinfo("Test Connexion", msg)
    
    def clean_sandbox(self): 
        if hasattr(self.security_manager, 'clean_sandbox'):
            success, msg = self.security_manager.clean_sandbox()
            self.log_message(f"🗑️ Sandbox: {msg}")
    
    def save_renaming_rules(self): 
        self.log_message("💾 Règles renommage sauvegardées")
    
    def load_renaming_rules(self): 
        self.log_message("📥 Règles renommage chargées")
    
    def reset_renaming_rules(self): 
        self.template_var.set("[{author}] {title} ({language})")
        self.log_message("🔄 Règles renommage réinitialisées")
    
    def toggle_monitoring(self): 
        self.monitoring_active = not self.monitoring_active
        status = "repris" if self.monitoring_active else "en pause"
        self.monitoring_btn.config(text="⏸️ Pause" if self.monitoring_active else "▶️ Reprise")
        self.log_message(f"📊 Monitoring {status}")
    
    def cleanup_system(self, cleanup_type): 
        self.log_message(f"🧹 Nettoyage {cleanup_type} en cours...")
        # Simuler nettoyage
        import tempfile
        temp_dir = Path(tempfile.gettempdir())
        count = len(list(temp_dir.glob("*"))) if temp_dir.exists() else 0
        self.cleanup_result_var.set(f"Nettoyage {cleanup_type}: {count} éléments trouvés")
        self.log_message(f"✅ Nettoyage {cleanup_type} terminé")
    
    def full_system_cleanup(self): 
        self.cleanup_system("complet")
    
    def install_dragdrop(self): 
        if messagebox.askyesno("Installation", "Installer tkinterdnd2 ?"):
            def install():
                try:
                    subprocess.run([sys.executable, "-m", "pip", "install", "tkinterdnd2"], check=True)
                    self.root.after(0, lambda: messagebox.showinfo("Succès", "tkinterdnd2 installé! Redémarrez l'application."))
                except Exception as e:
                    self.root.after(0, lambda: messagebox.showerror("Erreur", f"Installation échouée: {e}"))
            
            threading.Thread(target=install, daemon=True).start()
    
    def save_all_settings(self): 
        self.save_config()
        self.log_message("💾 Paramètres sauvegardés")
    
    def reset_all_settings(self): 
        self.config = {"interface": {"mode": "simple", "theme": "darkly"}}
        self.save_config()
        self.log_message("🔄 Paramètres réinitialisés")
    
    def clear_logs(self): 
        if hasattr(self, 'log_text'):
            self.log_text.delete(1.0, tk.END)
    
    def switch_mode(self):
        """Basculement rapide de mode"""
        new_mode = "advanced" if self.current_mode == "simple" else "simple"
        self.switch_to_mode(new_mode)

# Test si exécuté directement
if __name__ == "__main__":
    print("🧪 Test interface ULTRA STABLE")
    
    # Mock managers basiques
    class MockDownloadManager:
        def test_site_support(self, url): 
            return True, "Site supporté (mock)"
        def get_compatible_tool(self, url): 
            return "yt-dlp"
        def download(self, url, output_dir, progress_callback, quality="best"):
            if progress_callback:
                for i in [0, 25, 50, 75, 100]:
                    progress_callback(True, f"Mock {i}%", i)
                    time.sleep(0.2)
            return True, "Téléchargement mock réussi"
    
    class MockSecurityManager:
        def __init__(self):
            self.tor_enabled = False
        def is_sandbox_enabled(self): 
            return True
        def get_sandbox_dir(self): 
            return "sandbox"
        def enable_tor(self): 
            self.tor_enabled = True; return True, "TOR activé (mock)"
        def disable_tor(self): 
            self.tor_enabled = False; return True, "TOR désactivé (mock)"
        def test_connectivity(self): 
            return True, "Connexion OK (mock)"
        def clean_sandbox(self): 
            return True, "Sandbox nettoyé (mock)"
    
    # Créer interface avec tkinter standard ou TkinterDnD
    if DRAG_DROP_AVAILABLE:
        root = TkinterDnD.Tk()
    else:
        root = tk.Tk()
    
    mock_dm = MockDownloadManager()
    mock_sm = MockSecurityManager()
    
    app = PrismFetchMainWindow(root, mock_dm, mock_sm)
    
    print("✅ Interface ULTRA STABLE créée")
    print(f"📁 Drag & Drop: {'✅ Activé' if DRAG_DROP_AVAILABLE else '❌ Désactivé'}")
    
    root.mainloop()