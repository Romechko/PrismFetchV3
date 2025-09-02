#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
PrismFetch V3 - Détecteur d'Outils (PRÉVENTIF)
Module temporaire pour éviter les erreurs d'import
"""

import subprocess
import os
from pathlib import Path

class ToolDetector:
    """Détecteur d'outils de téléchargement (version préventive)"""
    
    def __init__(self):
        self.available_tools = {}
        self.detect_all_tools()
        print(f"🔧 {len(self.available_tools)} outils détectés")
    
    def detect_all_tools(self):
        """Détection de tous les outils disponibles"""
        tools_to_check = ["yt-dlp", "gallery-dl", "cyberdrop-dl", "wget", "curl"]
        
        for tool in tools_to_check:
            path = self.find_tool(tool)
            self.available_tools[tool] = path
    
    def find_tool(self, tool_name):
        """Recherche d'un outil"""
        try:
            # Vérification PATH
            result = subprocess.run(
                ["where" if os.name == "nt" else "which", tool_name],
                capture_output=True, text=True
            )
            if result.returncode == 0:
                return result.stdout.strip().split('\n')[0]
        except:
            pass
        
        # Vérification dossier tools/
        tools_dir = Path("tools")
        if tools_dir.exists():
            for ext in [".exe", ".bat", ""]:
                tool_path = tools_dir / f"{tool_name}{ext}"
                if tool_path.exists():
                    return str(tool_path)
        
        return None
    
    def is_tool_available(self, tool_name):
        """Vérification disponibilité outil"""
        return self.available_tools.get(tool_name) is not None
    
    def get_tool_path(self, tool_name):
        """Chemin d'un outil"""
        return self.available_tools.get(tool_name)
    
    def get_available_tools(self):
        """Liste des outils disponibles"""
        return {k: v for k, v in self.available_tools.items() if v is not None}

if __name__ == "__main__":
    detector = ToolDetector()
    print("✅ ToolDetector préventif OK")
