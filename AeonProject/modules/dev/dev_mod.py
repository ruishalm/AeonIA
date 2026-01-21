"""
DevFactory Module - Fábrica de Software Inteligente
"""

import os
import json
import subprocess
import threading
import re
from datetime import datetime
from modules.base_module import AeonModule

class DevFactory(AeonModule):
    """
    Módulo que gera projetos de software completos.
    """
    
    def __init__(self, core_context):
        super().__init__(core_context)
        self.name = "DevFactory"
        self.triggers = [
            "crie um site", "crie um script", "crie um projeto", 
            "gere um código", "construa um app", "crie uma calculadora",
            "faça um html", "crie uma api", "programar"
        ]
        self.dependencies = ["brain"]
        
        self.workspace_dir = os.path.join("AeonProject", "workspace")
        os.makedirs(self.workspace_dir, exist_ok=True)
        
        self.projects_log = os.path.join(self.workspace_dir, "projects.json")
        self._load_projects_log()

    @property
    def metadata(self) -> dict:
        return {
            "version": "1.1.0",
            "author": "Aeon DevFactory",
            "description": "Gera projetos de software completos usando IA"
        }

    def on_load(self) -> bool:
        if not os.path.exists(self.workspace_dir):
            try:
                os.makedirs(self.workspace_dir)
                return True
            except Exception as e:
                print(f"[DevFactory] Erro ao criar workspace: {e}")
                return False
        return True
    
    def on_unload(self) -> bool:
        self._save_projects_log()
        return True

    def _load_projects_log(self):
        if os.path.exists(self.projects_log):
            try:
                with open(self.projects_log, 'r', encoding='utf-8') as f:
                    self.projects = json.load(f)
            except:
                self.projects = []
        else:
            self.projects = []

    def _save_projects_log(self):
        try:
            with open(self.projects_log, 'w', encoding='utf-8') as f:
                json.dump(self.projects, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"[DevFactory] Erro ao salvar projects.json: {e}")

    def process(self, command: str) -> str:
        try:
            project_type, requirements = self._parse_command(command)
            
            if not project_type:
                return "Não entendi. Tente: 'Crie um site com animações' ou 'Gere um script Python'"
            
            threading.Thread(
                target=self._create_project,
                args=(project_type, requirements),
                daemon=True
            ).start()
            
            return f"Criando {project_type}... Aguarde."
        
        except Exception as e:
            return f"Erro ao criar projeto: {str(e)}"

    def _parse_command(self, command: str) -> tuple:
        cmd_lower = command.lower()
        
        if "site" in cmd_lower or "html" in cmd_lower or "web" in cmd_lower:
            project_type = "site"
        elif "script" in cmd_lower or "python" in cmd_lower or "py" in cmd_lower:
            project_type = "script"
        elif "calculadora" in cmd_lower or "calculator" in cmd_lower:
            project_type = "calculator"
        elif "api" in cmd_lower or "api" in cmd_lower:
            project_type = "api"
        elif "app" in cmd_lower or "aplicacao" in cmd_lower:
            project_type = "app"
        else:
            project_type = None
        
        requirements = command.replace(f"crie um {project_type}", "").strip() \
                              .replace(f"gere um {project_type}", "").strip() \
                              .replace(f"construa um {project_type}", "").strip()
        
        if not requirements:
            requirements = f"Um {project_type} funcional e bem estruturado"
        
        return project_type, requirements

    def _create_project(self, project_type: str, requirements: str):
        try:
            io_handler = self.core_context.get("io_handler")
            brain = self.core_context.get("brain")
            
            if not brain:
                if io_handler: io_handler.falar("Erro: Brain não disponível")
                return
            
            project_name = f"{project_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            project_dir = os.path.join(self.workspace_dir, project_name)
            os.makedirs(project_dir, exist_ok=True)
            
            if io_handler: io_handler.falar(f"Gerando código para {project_type}...")
            
            prompt = self._build_prompt(project_type, requirements)
            code_response = brain.pensar(prompt=prompt, historico_txt="", user_prefs={})
            
            files_dict = self._extract_json(code_response)
            
            if not files_dict:
                if io_handler: io_handler.falar("Erro ao gerar código. Resposta inválida.")
                return
            
            for filename, content in files_dict.items():
                filepath = os.path.join(project_dir, filename)
                os.makedirs(os.path.dirname(filepath), exist_ok=True)
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(content)
            
            self.projects.append({
                "name": project_name,
                "type": project_type,
                "created_at": datetime.now().isoformat(),
                "requirements": requirements,
                "path": project_dir,
                "files": list(files_dict.keys())
            })
            self._save_projects_log()
            
            if io_handler: io_handler.falar(f"Projeto criado em {project_dir}. Abrindo...")
            
            try:
                # Tenta abrir a pasta (funciona em Windows/Linux/Mac)
                if os.name == 'nt':
                    os.startfile(project_dir)
                else:
                    subprocess.Popen(["xdg-open", project_dir])
            except: pass
            
        except Exception as e:
            print(f"[DevFactory] Erro: {e}")
            io_handler = self.core_context.get("io_handler")
            if io_handler: io_handler.falar(f"Erro ao criar projeto: {str(e)}")

    def _build_prompt(self, project_type: str, requirements: str) -> str:
        # CORREÇÃO: Templates agora incluem cabeçalho UTF-8 para Python
        templates = {
            "site": f"""You are a Senior Web Developer. Create a website: {requirements}
OUTPUT ONLY JSON:
{{
  "index.html": "<!DOCTYPE html>...",
  "style.css": "body {{...}}",
  "script.js": "console.log('...')"
}}""",
            
            "script": f"""You are a Python Expert. Create a script: {requirements}
OUTPUT ONLY JSON:
{{
  "main.py": "# -*- coding: utf-8 -*-\\nimport os\\n\\n# Implementation..."
}}""",
            
            "calculator": f"""Create a JS Calculator.
OUTPUT ONLY JSON:
{{ "index.html": "...", "style.css": "...", "script.js": "..." }}""",
            
            "api": f"""Create a FASTAPI/Flask API: {requirements}
OUTPUT ONLY JSON:
{{
  "main.py": "# -*- coding: utf-8 -*-\\nfrom fastapi import FastAPI..."
}}""",
            
            "app": f"""Create an App logic: {requirements}
OUTPUT ONLY JSON:
{{
  "main.py": "# -*- coding: utf-8 -*-\\n..."
}}"""
        }
        return templates.get(project_type, templates["site"])

    def _extract_json(self, text: str) -> dict:
        try:
            json_match = re.search(r'\{.*\}', text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except: pass
        return None