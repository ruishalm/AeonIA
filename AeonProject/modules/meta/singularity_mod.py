import os
import ast
import re
import textwrap
from modules.base_module import AeonModule

class SingularityModule(AeonModule):
    def __init__(self, core_context):
        super().__init__(core_context)
        self.name = "Singularidade"
        self.triggers = ["iniciar singularidade", "criar nova habilidade", "aprender função"]
        self.dependencies = ["brain"]
        
        self.step = 0 
        self.temp_data = {"name": "", "triggers": "", "logic": ""}

    def process(self, command: str) -> str:
        mm = self.core_context.get("module_manager")
        brain = self.core_context.get("brain")
        ctx = self.core_context.get("context") # Acesso ao contexto

        # --- ESTADO 0: START ---
        if self.step == 0:
            if mm: mm.lock_focus(self)
            self.step = 1
            return "Singularidade ativa. Qual o nome técnico do novo módulo? (apenas letras)"

        # --- ESTADO 1: NOME ---
        if self.step == 1:
            clean_name = re.sub(r'[^a-zA-Z0-9_]', '', command.strip().lower())
            if not clean_name: return "Nome inválido. Tente novamente."
            self.temp_data["name"] = clean_name
            self.step = 2
            return f"Nome '{clean_name}' registrado. Quais os gatilhos? (separe por vírgula)"

        # --- ESTADO 2: TRIGGERS ---
        if self.step == 2:
            self.temp_data["triggers"] = str([t.strip() for t in command.split(',')])
            self.step = 3
            return "Ok. Descreva a LÓGICA. O que ele deve fazer?"

        # --- ESTADO 3: LÓGICA (COM CONTEXTO VISUAL) ---
        if self.step == 3:
            user_logic = command
            
            # MAGIA DO CONTEXTO: Verifica se a visão viu algo recentemente
            contexto_extra = ""
            if ctx:
                last_vision = ctx.get("vision_last_result")
                if last_vision:
                    contexto_extra = f"\n[CONTEXTO DE TELA]: O usuário viu recentemente: '{last_vision}'. USE ISSO SE FOR RELEVANTE PARA A LÓGICA."
                    print("[SINGULARIDADE] Contexto visual injetado no prompt.")

            self.temp_data["logic"] = user_logic + contexto_extra
            
            # Gera código
            prompt = self._build_prompt()
            try:
                # Chama o Brain
                resp = brain.pensar(prompt, "")
                
                # Extrai e Valida
                code = self._extract_code(resp)
                if not code: raise Exception("Cérebro não gerou código válido")
                
                syntax_err = self._validate_syntax(code)
                if syntax_err: raise Exception(f"Erro de sintaxe gerado: {syntax_err}")
                
                # Salva
                if self._save_module(code):
                    if mm: 
                        mm.scan_new_modules()
                        mm.release_focus()
                    self.step = 0
                    return f"Módulo '{self.temp_data['name']}' criado e assimilado com sucesso."
                
            except Exception as e:
                self._reset_state(mm)
                return f"Falha na Singularidade: {str(e)}"

        return ""

    def _reset_state(self, mm):
        self.step = 0
        self.temp_data = {}
        if mm: mm.release_focus()

    def _validate_syntax(self, code):
        try:
            ast.parse(code)
            return None
        except SyntaxError as e:
            return str(e)

    def _extract_code(self, text):
        match = re.search(r'```python(.*?)```', text, re.DOTALL)
        if match: return match.group(1).strip()
        match = re.search(r'```(.*?)```', text, re.DOTALL)
        if match: return match.group(1).strip()
        return None

    def _save_module(self, code):
        try:
            name = self.temp_data["name"]
            # Caminho robusto
            base = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", name))
            os.makedirs(base, exist_ok=True)
            
            with open(os.path.join(base, "__init__.py"), "w", encoding='utf-8') as f: f.write("")
            with open(os.path.join(base, f"{name}_mod.py"), "w", encoding='utf-8') as f: f.write(code)
            return True
        except: return False

    def _build_prompt(self):
        # CORREÇÃO: Adicionado coding utf-8 e reforço de sintaxe
        return textwrap.dedent(f"""
            ATUE COMO ENGENHEIRO PYTHON SÊNIOR.
            Tarefa: Criar módulo para sistema Aeon.
            
            DADOS:
            - Nome: {self.temp_data['name']}
            - Gatilhos: {self.temp_data['triggers']}
            - Lógica: {self.temp_data['logic']}
            
            TEMPLATE OBRIGATÓRIO (Use Exatamente este formato):
            ```python
            # -*- coding: utf-8 -*-
            from modules.base_module import AeonModule
            # outros imports padrão
            
            class {self.temp_data['name'].capitalize()}Module(AeonModule):
                def __init__(self, core_context):
                    super().__init__(core_context)
                    self.name = "{self.temp_data['name']}"
                    self.triggers = {self.temp_data['triggers']}
                
                def process(self, command):
                    # Implementação
                    return "resposta"
            ```
            Retorne APENAS o código dentro de markdown.
        """)