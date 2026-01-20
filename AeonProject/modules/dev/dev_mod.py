"""
DevFactory Module - Fábrica de Software Inteligente

Cria projetos de software automaticamente usando o Brain (LLM).
Suporta: Sites, Scripts Python, Calculadoras, etc.

Triggers: ["crie um site", "crie um script", "crie um projeto", "gere um código"]
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
    
    Workflow:
    1. Usuário: "Crie um site de portfólio"
    2. DevFactory extrai tipo + requisitos
    3. Brain gera código (JSON)
    4. DevFactory cria arquivos em /workspace
    5. Abre no VS Code automaticamente
    """
    
    def __init__(self, core_context):
        super().__init__(core_context)
        self._name = "DevFactory"
        self._triggers = [
            "crie um site", "crie um script", "crie um projeto", 
            "gere um código", "construa um app", "crie uma calculadora",
            "faça um html", "crie uma api", "programar"
        ]
        self._dependencies = ["brain"]
        
        # Criar diretório workspace se não existir
        self.workspace_dir = os.path.join("AeonProject", "workspace")
        os.makedirs(self.workspace_dir, exist_ok=True)
        
        # Histórico de projetos criados
        self.projects_log = os.path.join(self.workspace_dir, "projects.json")
        self._load_projects_log()

    @property
    def name(self) -> str:
        return self._name

    @property
    def triggers(self) -> list:
        return self._triggers

    @property
    def dependencies(self) -> list:
        return self._dependencies

    @property
    def metadata(self) -> dict:
        return {
            "version": "1.0.0",
            "author": "Aeon DevFactory",
            "description": "Gera projetos de software completos usando IA"
        }

    def on_load(self) -> bool:
        """Hook: Validar que workspace está pronto."""
        if not os.path.exists(self.workspace_dir):
            try:
                os.makedirs(self.workspace_dir)
                return True
            except Exception as e:
                print(f"[DevFactory] Erro ao criar workspace: {e}")
                return False
        return True
    
    def on_unload(self) -> bool:
        """Hook: Limpar ao descarregar o módulo."""
        self._save_projects_log()
        return True

    def _load_projects_log(self):
        """Carrega histórico de projetos criados."""
        if os.path.exists(self.projects_log):
            try:
                with open(self.projects_log, 'r', encoding='utf-8') as f:
                    self.projects = json.load(f)
            except:
                self.projects = []
        else:
            self.projects = []

    def _save_projects_log(self):
        """Salva histórico de projetos criados."""
        try:
            with open(self.projects_log, 'w', encoding='utf-8') as f:
                json.dump(self.projects, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"[DevFactory] Erro ao salvar projects.json: {e}")

    def process(self, command: str) -> str:
        """Processa comando de criação de projeto."""
        try:
            # Extrair tipo de projeto e requisitos
            project_type, requirements = self._parse_command(command)
            
            if not project_type:
                return "Não entendi. Tente: 'Crie um site com animações' ou 'Gere um script Python'"
            
            # Executar em thread para não bloquear
            threading.Thread(
                target=self._create_project,
                args=(project_type, requirements),
                daemon=True
            ).start()
            
            return f"Criando {project_type}... Aguarde (pode levar até 1 minuto)."
        
        except Exception as e:
            return f"Erro ao criar projeto: {str(e)}"

    def _parse_command(self, command: str) -> tuple:
        """Extrai tipo de projeto e requisitos do comando."""
        cmd_lower = command.lower()
        
        # Detectar tipo
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
        
        # Extrair requisitos (tudo após o tipo)
        requirements = command.replace(f"crie um {project_type}", "").strip() \
                              .replace(f"gere um {project_type}", "").strip() \
                              .replace(f"construa um {project_type}", "").strip()
        
        if not requirements:
            requirements = f"Um {project_type} funcional e bem estruturado"
        
        return project_type, requirements

    def _create_project(self, project_type: str, requirements: str):
        """Cria o projeto (executa em thread)."""
        try:
            io_handler = self.core_context.get("io_handler")
            brain = self.core_context.get("brain")
            
            if not brain:
                if io_handler:
                    io_handler.falar("Erro: Brain não disponível")
                return
            
            # Criar pasta do projeto
            project_name = f"{project_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            project_dir = os.path.join(self.workspace_dir, project_name)
            os.makedirs(project_dir, exist_ok=True)
            
            if io_handler:
                io_handler.falar(f"Gerando código para {project_type}...")
            
            # Gerar código via Brain (forçar resposta JSON)
            prompt = self._build_prompt(project_type, requirements)
            code_response = brain.pensar(prompt=prompt, historico_txt="", user_prefs={})
            
            # Extrair JSON
            files_dict = self._extract_json(code_response)
            
            if not files_dict:
                if io_handler:
                    io_handler.falar("Erro ao gerar código. Resposta inválida.")
                return
            
            # Criar arquivos
            for filename, content in files_dict.items():
                filepath = os.path.join(project_dir, filename)
                
                # Criar subdiretórios se necessário
                os.makedirs(os.path.dirname(filepath), exist_ok=True)
                
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(content)
            
            # Registrar no histórico
            self.projects.append({
                "name": project_name,
                "type": project_type,
                "created_at": datetime.now().isoformat(),
                "requirements": requirements,
                "path": project_dir,
                "files": list(files_dict.keys())
            })
            self._save_projects_log()
            
            if io_handler:
                io_handler.falar(f"Projeto criado em {project_dir}. Abrindo no VS Code...")
            
            # Abrir no VS Code
            try:
                subprocess.Popen(["code", project_dir])
            except Exception as e:
                print(f"[DevFactory] Não consegui abrir VS Code: {e}")
            
            if io_handler:
                io_handler.falar(f"Pronto! Projeto '{project_name}' criado e aberto.")
        
        except Exception as e:
            print(f"[DevFactory] Erro ao criar projeto: {e}")
            io_handler = self.core_context.get("io_handler")
            if io_handler:
                io_handler.falar(f"Erro ao criar projeto: {str(e)}")

    def _build_prompt(self, project_type: str, requirements: str) -> str:
        """Constrói prompt para o Brain gerar código."""
        templates = {
            "site": f"""You are a Senior Web Developer. Create a complete website with the following requirements:
{requirements}

OUTPUT ONLY VALID JSON (no other text):
{{
  "index.html": "...full HTML...",
  "style.css": "...full CSS...",
  "script.js": "...full JavaScript..."
}}

Make it professional, modern, and fully functional.""",
            
            "script": f"""You are a Senior Python Developer. Create a complete Python script with the following requirements:
{requirements}

OUTPUT ONLY VALID JSON (no other text):
{{
  "main.py": "...full Python code..."
}}

Include proper error handling and comments.""",
            
            "calculator": """You are a Senior Web Developer. Create a modern HTML5 calculator.

OUTPUT ONLY VALID JSON (no other text):
{{
  "index.html": "...full HTML...",
  "style.css": "...full CSS...",
  "script.js": "...full JavaScript..."
}}

Make it functional, with buttons for all basic operations (+ - * / =).""",
            
            "api": f"""You are a Senior Backend Developer. Create a REST API with the following requirements:
{requirements}

OUTPUT ONLY VALID JSON (no other text):
{{
  "main.py": "...Flask/FastAPI code..."
}}

Use Flask or FastAPI with proper error handling.""",
            
            "app": f"""You are a Senior Software Engineer. Create an application with the following requirements:
{requirements}

OUTPUT ONLY VALID JSON (no other text):
{{
  "main.py": "...full code...",
  "README.md": "...usage instructions..."
}}"""
        }
        
        return templates.get(project_type, templates["site"])

    def _extract_json(self, text: str) -> dict:
        """Extrai JSON de uma resposta de texto."""
        try:
            # Procurar por { ... } no texto
            json_match = re.search(r'\{.*\}', text, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                return json.loads(json_str)
        except Exception as e:
            print(f"[DevFactory] Erro ao extrair JSON: {e}")
        
        return None
