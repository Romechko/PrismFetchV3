#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import time
import os
from pathlib import Path

from ..core.config_manager import ConfigManager
from ..core.download_manager import DownloadManager
from ..utils.logger import get_logger

class AdvancedInterface:
    """Interface Avancée COMPLÈTE et FONCTIONNELLE"""

    def __init__(self):
        self.logger = get_logger(__name__)
        self.config = ConfigManager()
        self.download_manager = DownloadManager()
        self.root = None
        self.url_list = []
        self.downloads_active = False

    def run(self):
        self.root = tk.Tk()
        self.setup_window()
        self.create_ui()
        self.show_legal_warning()
        self.root.mainloop()

    def setup_window(self):
        self.root.title("PrismFetch FINAL v2.1 - Interface Avancée")
        self.root.geometry("1000x650")
        self.root.configure(bg="#0d1117")
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Dark.TFrame", background="#0d1117")
        style.configure("Dark.TLabel", background="#0d1117", foreground="#f0f6fc", font=("Segoe UI", 10))
        style.configure("Title.TLabel", background="#0d1117", foreground="#58a6ff", font=("Segoe UI", 18, "bold"))
        style.configure("Dark.TNotebook", background="#0d1117")
        style.configure("Dark.TNotebook.Tab", background="#21262d", foreground="#f0f6fc", padding=[15, 8])

        x = (self.root.winfo_screenwidth() // 2) - 500
        y = (self.root.winfo_screenheight() // 2) - 325
        self.root.geometry(f"1000x650+{x}+{y}")

    def create_ui(self):
        main_container = ttk.Frame(self.root, style="Dark.TFrame")
        main_container.pack(fill="both", expand=True, padx=15, pady=15)

        header_frame = ttk.Frame(main_container, style="Dark.TFrame")
        header_frame.pack(fill="x", pady=(0, 15))

        logo_canvas = tk.Canvas(header_frame, width=80, height=60, bg="#0d1117", highlightthickness=0)
        logo_canvas.pack(side="left")
        logo_canvas.create_oval(5, 5, 55, 55, fill="#58a6ff", outline="#1f6feb", width=2)
        logo_canvas.create_text(30, 30, text="PF", font=("Arial", 14, "bold"), fill="#ffffff")

        title_frame = ttk.Frame(header_frame, style="Dark.TFrame")
        title_frame.pack(side="left", padx=(15, 0))
        ttk.Label(title_frame, text="PrismFetch FINAL", style="Title.TLabel").pack(anchor="w")
        ttk.Label(title_frame, text="Interface Avancée • TÉLÉCHARGEMENTS PAR LOTS • v2.1",
                  background="#0d1117", foreground="#8b949e", font=("Segoe UI", 9)).pack(anchor="w")
        ttk.Label(title_frame, text="Créé par: Metadata",
                  background="#0d1117", foreground="#3fb950", font=("Segoe UI", 10, "bold")).pack(anchor="w")

        self.notebook = ttk.Notebook(main_container, style="Dark.TNotebook")
        self.notebook.pack(fill="both", expand=True, pady=(10, 0))

        self.create_download_tab()
        self.create_settings_tab()
        self.create_status_bar(main_container)

    def create_download_tab(self):
        download_tab = ttk.Frame(self.notebook, style="Dark.TFrame")
        self.notebook.add(download_tab, text="Téléchargement")

        url_section = tk.LabelFrame(download_tab, text="  Ajouter URL  ",
                                   font=("Segoe UI", 11, "bold"),
                                   fg="#58a6ff", bg="#161b22", bd=2)
        url_section.pack(fill="x", padx=15, pady=10)

        self.url_var = tk.StringVar()
        url_entry = tk.Entry(url_section, textvariable=self.url_var, font=("Consolas", 11),
                             bg="#21262d", fg="#f0f6fc", bd=8, insertbackground="#58a6ff")
        url_entry.pack(fill="x", padx=15, pady=10, ipady=6)

        placeholder = "URL à ajouter (YouTube, Instagram, TikTok, CyberDrop, Bunkr, etc.)"
        self.url_var.set(placeholder)
        url_entry.configure(fg="#8b949e")

        def on_focus_in(event):
            if self.url_var.get() == placeholder:
                self.url_var.set("")
                url_entry.configure(fg="#f0f6fc")

        def on_focus_out(event):
            if not self.url_var.get():
                self.url_var.set(placeholder)
                url_entry.configure(fg="#8b949e")

        url_entry.bind("<FocusIn>", on_focus_in)
        url_entry.bind("<FocusOut>", on_focus_out)
        url_entry.bind("<Return>", lambda e: self.add_url())

        url_buttons = ttk.Frame(url_section, style="Dark.TFrame")
        url_buttons.pack(fill="x", padx=15, pady=(0, 10))

        self.create_button(url_buttons, "Ajouter", "#3fb950", self.add_url).pack(side="left", padx=5)
        self.create_button(url_buttons, "Fichier .txt", "#58a6ff", self.load_file).pack(side="left", padx=5)
        self.create_button(url_buttons, "Analyser", "#f78166", self.analyze_current).pack(side="left", padx=5)

        list_section = tk.LabelFrame(download_tab, text="  URLs à télécharger  ",
                                    font=("Segoe UI", 11, "bold"),
                                    fg="#58a6ff", bg="#161b22", bd=2)
        list_section.pack(fill="both", expand=True, padx=15, pady=10)

        list_container = ttk.Frame(list_section, style="Dark.TFrame")
        list_container.pack(fill="both", expand=True, padx=15, pady=10)

        self.url_listbox = tk.Listbox(list_container, font=("Consolas", 9),
                                     bg="#21262d", fg="#f0f6fc",
                                     selectbackground="#58a6ff", relief="flat")

        list_scrollbar = ttk.Scrollbar(list_container, orient="vertical", command=self.url_listbox.yview)
        self.url_listbox.configure(yscrollcommand=list_scrollbar.set)

        self.url_listbox.pack(side="left", fill="both", expand=True)
        list_scrollbar.pack(side="right", fill="y")

        default_url = "https://bunkr.cr/a/6YAJm5p5"
        self.url_list = [default_url]
        plugin = self.download_manager.detect_best_tool(default_url)
        self.url_listbox.insert(tk.END, f"{default_url} [{plugin}]")

        list_buttons = ttk.Frame(list_section, style="Dark.TFrame")
        list_buttons.pack(fill="x", padx=15, pady=(0, 10))

        self.create_button(list_buttons, "Supprimer", "#f85149", self.remove_url).pack(side="left", padx=5)
        self.create_button(list_buttons, "Vider", "#ff6b35", self.clear_urls).pack(side="left", padx=5)
        self.create_button(list_buttons, "Sauvegarder", "#a5a5a5", self.save_list).pack(side="left", padx=5)

        download_section = ttk.Frame(download_tab, style="Dark.TFrame")
        download_section.pack(fill="x", padx=20, pady=15)

        self.main_btn = self.create_button(download_section, "DÉMARRER TÉLÉCHARGEMENTS RÉELS",
                                           "#238636", self.start_batch_download, 35, 3)
        self.main_btn.pack(fill="x")

        self.create_log(download_tab)

    def create_settings_tab(self):
        settings_tab = ttk.Frame(self.notebook, style="Dark.TFrame")
        self.notebook.add(settings_tab, text="Paramètres")

        ttk.Label(settings_tab, text="Configuration", style="Title.TLabel").pack(pady=20)

        folder_section = tk.LabelFrame(settings_tab, text="  Dossier de téléchargement  ",
                                      font=("Segoe UI", 11, "bold"),
                                      fg="#58a6ff", bg="#161b22", bd=2)
        folder_section.pack(fill="x", padx=20, pady=10)

        folder_frame = ttk.Frame(folder_section, style="Dark.TFrame")
        folder_frame.pack(fill="x", padx=15, pady=15)

        self.folder_var = tk.StringVar(value=str(self.config.get_download_path()))
        folder_entry = tk.Entry(folder_frame, textvariable=self.folder_var,
                               font=("Consolas", 10),
                               bg="#21262d", fg="#f0f6fc", bd=5)
        folder_entry.pack(fill="x", side="left", padx=(0, 10))
        self.create_button(folder_frame, "Parcourir", "#a5a5a5", self.choose_folder).pack(side="right")

        stats_section = tk.LabelFrame(settings_tab, text="  Statistiques  ",
                                     font=("Segoe UI", 11, "bold"),
                                     fg="#58a6ff", bg="#161b22", bd=2)
        stats_section.pack(fill="x", padx=20, pady=10)

        self.stats_frame = ttk.Frame(stats_section, style="Dark.TFrame")
        self.stats_frame.pack(fill="x", padx=15, pady=15)

        self.update_stats()

    def create_log(self, parent):
        log_section = tk.LabelFrame(parent, text="  Journal en temps réel  ",
                                   font=("Segoe UI", 11, "bold"),
                                   fg="#58a6ff", bg="#161b22", bd=2)
        log_section.pack(fill="both", expand=True, padx=15, pady=10)

        log_container = ttk.Frame(log_section, style="Dark.TFrame")
        log_container.pack(fill="both", expand=True, padx=15, pady=10)

        self.log_text = tk.Text(log_container,
                                height=8,
                                font=("Consolas", 9),
                                bg="#0d1117", fg="#f0f6fc",
                                relief="flat", wrap="word")

        log_scroll = ttk.Scrollbar(log_container, orient="vertical", command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=log_scroll.set)

        self.log_text.pack(side="left", fill="both", expand=True)
        log_scroll.pack(side="right", fill="y")

        self.log("PrismFetch FINAL v2.1 - Interface Avancée")
        self.log("Téléchargements par lots RÉELS activés")
        self.log("Prêt pour téléchargements massifs")

    def create_status_bar(self, parent):
        self.status_frame = ttk.Frame(parent, style="Dark.TFrame")
        self.status_frame.pack(fill="x", pady=(10, 0))

        self.status_label = ttk.Label(self.status_frame, text="Prêt", style="Dark.TLabel")
        self.status_label.pack(side="left")

        self.progress_bar = ttk.Progressbar(self.status_frame, mode="determinate")
        self.progress_bar.pack(side="right", fill="x", expand=True, padx=10)

    def create_button(self, parent, text, color, command, width=None, height=None):
        btn = tk.Button(parent, text=text, font=("Segoe UI", 10, "bold"),
                        bg=color, fg="white", relief="flat", bd=0,
                        cursor="hand2", command=command)
        if width:
            btn.configure(width=width)
        if height:
            btn.configure(height=height)
        return btn

    def add_url(self):
        url = self.url_var.get().strip()
        placeholder = "URL à ajouter (YouTube, Instagram, TikTok, CyberDrop, Bunkr, etc.)"
        if not url or url == placeholder:
            messagebox.showwarning("URL manquante", "Entrez une URL valide!")
            return
        if not url.startswith(("http://", "https://")):
            messagebox.showerror("URL invalide", "L'URL doit commencer par http:// ou https://")
            return
        if url in self.url_list:
            messagebox.showwarning("Déjà présente", "Cette URL est déjà dans la liste!")
            return
        self.url_list.append(url)
        plugin = self.download_manager.detect_best_tool(url)
        self.url_listbox.insert(tk.END, f"{url} [{plugin}]")
        self.url_var.set(placeholder)
        self.log(f"URL ajoutée: {url} (Plugin: {plugin})")
        self.update_stats()

    def load_file(self):
        filename = filedialog.askopenfilename(title="Charger fichier d'URLs",
                                              filetypes=[("Fichiers texte", "*.txt"), ("Tous", "*.*")])
        if filename:
            try:
                loaded = 0
                with open(filename, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#') and line not in self.url_list:
                            if line.startswith(('http://', 'https://')):
                                self.url_list.append(line)
                                plugin = self.download_manager.detect_best_tool(line)
                                self.url_listbox.insert(tk.END, f"{line} [{plugin}]")
                                loaded += 1
                self.log(f"{loaded} URL(s) chargée(s) depuis {Path(filename).name}")
                self.update_stats()
            except Exception as e:
                messagebox.showerror("Erreur", f"Impossible de charger:\n{e}")

    def analyze_current(self):
        url = self.url_var.get().strip()
        placeholder = "URL à ajouter (YouTube, Instagram, TikTok, CyberDrop, Bunkr, etc.)"
        if not url or url == placeholder:
            messagebox.showwarning("URL manquante", "Entrez une URL à analyser!")
            return
        self.analyze_url(url)

    def analyze_url(self, url):
        plugin = self.download_manager.detect_best_tool(url)
        available = self.download_manager.is_tool_available(plugin)
        url_lower = url.lower()
        platforms = {
            ("youtube.com", "youtu.be"): "YouTube",
            ("instagram.com",): "Instagram",
            ("tiktok.com",): "TikTok",
            ("twitter.com", "x.com"): "Twitter/X",
            ("bunkr.cr", "cyberdrop"): "CyberDrop/Bunkr",
            ("reddit.com",): "Reddit"
        }
        platform = "Inconnue"
        for sites, name in platforms.items():
            if any(site in url_lower for site in sites):
                platform = name
                break
        status = "DISPONIBLE" if available else "MANQUANT"
        analysis = (f"ANALYSE DÉTAILLÉE\n\nURL: {url}\nPlateforme: {platform}\n"
                    f"Outil requis: {plugin}\nStatus: {status}\n\n"
                    f"{'Téléchargement possible' if available else 'Installez ' + plugin + ' via install.bat'}")
        self.log(f"Analyse: {platform} -> {plugin} ({status})")
        messagebox.showinfo("Analyse", analysis)

    def remove_url(self):
        selection = self.url_listbox.curselection()
        if not selection:
            messagebox.showwarning("Aucune sélection", "Sélectionnez une URL!")
            return
        index = selection[0]
        removed = self.url_list.pop(index)
        self.url_listbox.delete(index)
        self.log(f"URL supprimée: {removed}")
        self.update_stats()

    def clear_urls(self):
        if not self.url_list:
            messagebox.showinfo("Liste vide", "La liste est déjà vide!")
            return
        if messagebox.askyesno("Confirmation", f"Supprimer toutes les {len(self.url_list)} URLs?"):
            count = len(self.url_list)
            self.url_list.clear()
            self.url_listbox.delete(0, tk.END)
            self.log(f"{count} URL(s) supprimée(s)")
            self.update_stats()

    def save_list(self):
        if not self.url_list:
            messagebox.showwarning("Liste vide", "Aucune URL à sauvegarder!")
            return
        filename = filedialog.asksaveasfilename(title="Sauvegarder liste",
                                                defaultextension=".txt",
                                                filetypes=[("Fichiers texte", "*.txt")])
        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(f"# Liste PrismFetch FINAL - {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write(f"# {len(self.url_list)} URLs\n\n")
                    for url in self.url_list:
                        f.write(f"{url}\n")
                self.log(f"Liste sauvegardée: {Path(filename).name}")
            except Exception as e:
                messagebox.showerror("Erreur", f"Impossible de sauvegarder:\n{e}")

    def start_batch_download(self):
        if not self.url_list:
            messagebox.showwarning("Liste vide", "Aucune URL à télécharger!")
            return
        if self.downloads_active:
            messagebox.showwarning("En cours", "Des téléchargements sont en cours!")
            return
        tools = self.download_manager.get_available_tools()
        if not any(tools.values()):
            messagebox.showerror("Outils manquants", "Aucun outil disponible!\n\nLancez scripts/install.bat")
            return
        if not messagebox.askyesno("Téléchargements RÉELS",
                                   f"Démarrer téléchargements par lots?\n\n"
                                   f"URLs: {len(self.url_list)}\n"
                                   f"Destination: {self.folder_var.get()}\n\n"
                                   f"Les téléchargements seront RÉELS!"):
            return
        self.downloads_active = True
        self.main_btn.configure(state="disabled", text="TÉLÉCHARGEMENTS EN COURS...")
        self.progress_bar.configure(maximum=len(self.url_list), value=0)
        self.log(f"DÉMARRAGE téléchargements par lots RÉELS")
        self.log(f"{len(self.url_list)} URLs à traiter")
        threading.Thread(target=self.batch_worker, daemon=True).start()

    def batch_worker(self):
        try:
            download_path = Path(self.folder_var.get())
            download_path.mkdir(parents=True, exist_ok=True)
            success_count = 0
            error_count = 0
            for i, url in enumerate(self.url_list, 1):
                if not self.downloads_active:
                    break
                self.root.after(0, lambda: self.status_label.configure(text=f"[{i}/{len(self.url_list)}] Téléchargement..."))
                self.root.after(0, lambda: self.log(f"[{i}/{len(self.url_list)}] {url}"))
                try:
                    success, message = self.download_manager.download(url, download_path)
                    if success:
                        success_count += 1
                        self.root.after(0, lambda msg=message: self.log(f"SUCCÈS: {msg}"))
                    else:
                        error_count += 1
                        self.root.after(0, lambda msg=message: self.log(f"ÉCHEC: {msg}"))
                    self.root.after(0, lambda val=i: self.progress_bar.configure(value=val))
                    time.sleep(1)
                except Exception as e:
                    error_count += 1
                    self.root.after(0, lambda msg=str(e): self.log(f"ERREUR: {msg}"))
            self.root.after(0, self.batch_finished, success_count, error_count)
        except Exception as e:
            self.root.after(0, lambda: self.log(f"ERREUR CRITIQUE: {e}"))
            self.root.after(0, self.batch_finished, 0, len(self.url_list))

    def batch_finished(self, success, errors):
        self.downloads_active = False
        self.main_btn.configure(state="normal", text="DÉMARRER TÉLÉCHARGEMENTS RÉELS")
        self.status_label.configure(text="Terminé")
        self.log("=" * 40)
        self.log("TÉLÉCHARGEMENTS TERMINÉS")
        self.log(f"Succès: {success}")
        self.log(f"Échecs: {errors}")
        self.log(f"Total: {success + errors}")
        if success > 0:
            if messagebox.askyesno("Terminé!",
                                   f"Téléchargements terminés!\n\nSuccès: {success}\nÉchecs: {errors}\n\nOuvrir dossier?"):
                self.open_folder()
        else:
            messagebox.showerror("Échec", "Tous les téléchargements ont échoué!")

    def choose_folder(self):
        folder = filedialog.askdirectory(title="Choisir dossier de téléchargement")
        if folder:
            self.folder_var.set(folder)
            self.config.set("download_path", folder)
            self.config.save()
            self.log(f"Dossier changé: {folder}")

    def open_folder(self):
        try:
            folder = self.folder_var.get()
            if os.name == 'nt':
                os.startfile(folder)
            else:
                os.system(f'xdg-open "{folder}"')
            self.log(f"Dossier ouvert: {folder}")
        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible d'ouvrir: {e}")

    def update_stats(self):
        for w in self.stats_frame.winfo_children():
            w.destroy()
        if not self.url_list:
            ttk.Label(self.stats_frame, text="Aucune URL", style="Dark.TLabel").pack()
            return
        plugin_count = {}
        for url in self.url_list:
            plugin = self.download_manager.detect_best_tool(url)
            plugin_count[plugin] = plugin_count.get(plugin, 0) + 1
        ttk.Label(self.stats_frame, text=f"{len(self.url_list)} URL(s) total",
                  style="Dark.TLabel", font=("Segoe UI", 11, "bold")).pack(anchor="w")
        for plugin, count in plugin_count.items():
            ttk.Label(self.stats_frame, text=f"  • {plugin}: {count} URL(s)",
                      background="#0d1117", foreground="#8b949e").pack(anchor="w")

    def log(self, message):
        timestamp = time.strftime("%H:%M:%S")
        formatted = f"[{timestamp}] {message}\n"
        self.log_text.insert(tk.END, formatted)
        self.log_text.see(tk.END)
        try:
            self.logger.info(message)
        except:
            pass

    def show_legal_warning(self):
        if self.config.get("first_run", True):
            legal_text = (
                "AVERTISSEMENT LÉGAL IMPORTANT\n\n"
                "PrismFetch FINAL effectue de VRAIS téléchargements par lots.\n\n"
                "Vous êtes seul responsable du respect:\n"
                "• Des conditions d'utilisation des plateformes\n"
                "• Des lois sur les droits d'auteur\n"
                "• Des réglementations locales\n\n"
                "RISQUES ACCRUS:\n"
                "• Téléchargements par lots = risque multiplié\n"
                "• Certaines plateformes interdisent explicitement\n"
                "• Contenu protégé = poursuites possibles\n\n"
                "En continuant, vous acceptez l'entière responsabilité.\n\n"
                "Continuer?"
            )
            if messagebox.askyesno("Avertissement Légal", legal_text):
                self.config.set("first_run", False)
                self.config.save()
                self.log("Avertissement légal accepté")
            else:
                self.log("Avertissement refusé - Fermeture")
                self.root.quit()
