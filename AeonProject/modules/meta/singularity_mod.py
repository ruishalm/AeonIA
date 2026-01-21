import os
import ast
import re
import textwrap
from modules.base_module import AeonModule

class SingularityModule(AeonModule):
    def __init__(self, core_context):
        super().__init__(core_context)
        self.name = "Singularidade"
        self.triggers = ["iniciar singularidade", "criar nova habilidade"]
        self.dependencies = ["brain"]
        self.step = 0 
        self.temp_data = {}

    def process(self, command: str) -> str:
        mm = self.core_context.get("module_manager")
        brain = self.core_context.get("brain")
        ctx = self.core_context.get("context")

        if self.step == 0:
            if mm: mm.lock_focus(self)
            self.step = 1
            return "Singularidade ativa. Nome do módulo? (sem espaços)"

        if self.step == 1:
            self.temp_data["name"] = re.sub(r'[^a-zA-Z0-9_]', '', command.strip().lower())
            self.step = 2
            return f"Nome '{self.temp_data['name']}' ok. Gatilhos? (separados por vírgula)"

        if self.step == 2:
            self.temp_data["triggers"] = str([t.strip() for t in command.split(',')])
            self.step = 3
            return "Descreva a LÓGICA."

        if self.step == 3:
            contexto_extra = ""
            if ctx and ctx.get("vision_last_result"):
                contexto_extra = f"\n[CONTEXTO VISUAL]: {ctx.get('vision_last_result')}"

            self.temp_data["logic"] = command + contexto_extra
            
            prompt = self._build_prompt()
            try:
                resp = brain.pensar(prompt, "")
                code = self._extract_code(resp)
                
                if self._save_module(code):
                    if mm: 
                        mm.scan_new_modules()
                        mm.release_focus()
                    self.step = 0
                    return f"Módulo '{self.temp_data['name']}' criado."
            except Exception as e:
                if mm: mm.release_focus()
                self.step = 0
                return f"Erro: {e}"
        return ""

    def _extract_code(self, text):
        match = re.search(r'```python(.*?)```', text, re.DOTALL)
        return match.group(1).strip() if match else None

    def _save_module(self, code):
        try:
            name = self.temp_data["name"]
            base = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", name))
            os.makedirs(base, exist_ok=True)
            with open(os.path.join(base, "__init__.py"), "w", encoding='utf-8') as f: f.write("")
            with open(os.path.join(base, f"{name}_mod.py"), "w", encoding='utf-8') as f: f.write(code)
            return True
        except: return False

    def _build_prompt(self):
        # TEMPLATE V80 com UTF-8
        return textwrap.dedent(f"""
            ATUE COMO ENGENHEIRO PYTHON.
            Tarefa: Criar módulo Aeon.
            Nome: {self.temp_data['name']}
            Gatilhos: {self.temp_data['triggers']}
            Lógica: {self.temp_data['logic']}
            
            TEMPLATE OBRIGATÓRIO:
            ```python
            # -*- coding: utf-8 -*-
            from modules.base_module import AeonModule
            
            class {self.temp_data['name'].capitalize()}Module(AeonModule):
                def __init__(self, core_context):
                    super().__init__(core_context)
                    self.name = "{self.temp_data['name']}"
                    self.triggers = {self.temp_data['triggers']}
                
                def process(self, command):
                    # Implementação aqui
                    return "resposta"
            ```
            Retorne APENAS o código.
        """)