#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
PrismFetch V3 - Sécurité TOR/Bypass (PRÉVENTIF)
Module temporaire pour éviter les erreurs d'import
"""

import tkinter as tk
import ttkbootstrap as ttkb

class Securitytab(ttkb.Frame):
    """Onglet Sécurité TOR/Bypass (version préventive)"""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.create_widgets()
    
    def create_widgets(self):
        """Création des widgets"""
        label = ttkb.Label(
            self,
            text="🚧 Sécurité TOR/Bypass\n\n⚠️ Module préventif\nÀ implémenter dans la version finale",
            justify="center",
            font=("Arial", 12)
        )
        label.pack(expand=True)
