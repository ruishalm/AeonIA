import os
import ast
import re
import textwrap
from typing import List, Dict
from modules.base_module import AeonModule


class SingularityModule(AeonModule):
    """
    Módulo de Meta-Programação - Singularidade.
    Máquina de Estados que permite Aeon criar novos módulos para si mesmo em tempo de execução.
    
    Fluxo:
    Step 0: Inicialização (lock focus)
    Step 1: Coleta nome do módulo
    Step 2: Coleta triggers
    Step 3: Coleta lógica e gera código
    """
    
    def __init__(self, core_context):
        super().__init__(core_context)
        self.name = "Singularidade"
        self.triggers = ["iniciar singularidade", "criar nova habilidade", "aprender função"]
        
        # Máquina de estados
        self.step = 0 
        self.temp_data = {"name": "", "triggers": "", "logic": ""}
    
    @property
    def dependencies(self) -> List[str]:
        """Depende de brain para gerar código"""
        return ["brain"]
    
    @property
    def metadata(self) -> Dict[str, str]:
        return {
            "version": "1.0.0",
            "author": "Aeon Auto-Evolution",
            "description": "Meta-programação: Singularidade cria novos módulos em tempo de execução"
        }
    
    def on_load(self) -> bool:
        """Inicializa o módulo"""
        self.step = 0
        return True
    
    def on_unload(self) -> bool:
        """Limpa ao descarregar"""
        self.step = 0
        self.temp_data = {}
        return True
    
    def process(self, command: str) -> str:
        """
        Máquina de Estados que gerencia a criação do novo módulo.
        """
        # Acesso aos componentes do Core
        mm = self.core_context.get("module_manager")
        brain = self.core_context.get("brain")

        # --- ESTADO 0: INICIALIZAÇÃO ---
        if self.step == 0:
            if mm:
                mm.lock_focus(self)  # Trava o microfone na Singularidade
            self.step = 1
            return "Protocolo Singularidade iniciado. Eu vou aprender a me reprogramar. Primeiro: Qual o nome técnico da nova habilidade? (Ex: cotacao, piadas)"

        # --- ESTADO 1: NOME ---
        if self.step == 1:
            # Limpeza básica do nome (apenas letras e underscore)
            clean_name = re.sub(r'[^a-zA-Z0-9_]', '', command.strip().lower())
            if not clean_name:
                return "Nome inválido. Use apenas letras. Tente novamente."
            
            self.temp_data["name"] = clean_name
            self.step = 2
            return f"Módulo '{clean_name}' definido. Agora, quais são os GATILHOS de ativação? (Separe por vírgula)"

        # --- ESTADO 2: TRIGGERS ---
        if self.step == 2:
            triggers_list = [t.strip() for t in command.split(',')]
            self.temp_data["triggers"] = str(triggers_list)
            self.step = 3
            return "Entendido. Agora, descreva detalhadamente a LÓGICA. O que esse módulo deve fazer e como?"

        # --- ESTADO 3: LÓGICA & GERAÇÃO ---
        if self.step == 3:
            self.temp_data["logic"] = command
            
            # 1. Montar o Prompt de Engenharia
            prompt_system = self._build_prompt()
            
            # 2. Chamar o Cérebro
            try:
                resposta_brain = brain.pensar(prompt_system, "")
            except Exception as e:
                self._reset_state(mm)
                return f"Erro ao acessar o Cérebro: {e}. Singularidade abortada."

            # 3. Extrair e Validar Código
            code = self._extract_code(resposta_brain)
            if not code:
                self._reset_state(mm)
                return "Falha na geração: O Cérebro não retornou um código Python válido."

            validation_error = self._validate_syntax(code)
            if validation_error:
                self._reset_state(mm)
                return f"Protocolo de Segurança ativado. O código gerado contém erros de sintaxe: {validation_error}. Operação cancelada."

            # 4. Persistência (Salvar no Disco)
            if self._save_module(code):
                # 5. Hot Reload
                if mm:
                    new_modules = mm.scan_new_modules()
                    mm.release_focus()
                
                self.step = 0  # Reset para próxima vez
                return f"✓ Sucesso. O módulo '{self.temp_data['name']}' foi compilado, salvo e carregado. Já está ativo."
            else:
                self._reset_state(mm)
                return "Erro crítico ao salvar os arquivos no disco."

        return ""

    def _reset_state(self, mm):
        """Reseta a máquina de estados e libera o foco."""
        self.step = 0
        self.temp_data = {}
        if mm:
            mm.release_focus()

    def _validate_syntax(self, code_str):
        """Usa o AST (Abstract Syntax Tree) para verificar se o código é Python válido."""
        try:
            ast.parse(code_str)
            return None  # Sem erros
        except SyntaxError as e:
            return str(e)

    def _extract_code(self, text):
        """Extrai o código de dentro de blocos markdown ```python ... ```"""
        match = re.search(r'```python(.*?)```', text, re.DOTALL)
        if match:
            return match.group(1).strip()
        
        # Tenta achar sem 'python'
        match = re.search(r'```(.*?)```', text, re.DOTALL)
        if match:
            return match.group(1).strip()
        return None

    def _save_module(self, code):
        """Cria as pastas e salva o arquivo .py"""
        try:
            mod_name = self.temp_data["name"]
            # Caminho: AeonProject/modules/{mod_name}/
            base_path = os.path.join(os.path.dirname(__file__), "..", mod_name)
            base_path = os.path.abspath(base_path)

            if not os.path.exists(base_path):
                os.makedirs(base_path)

            # Criar __init__.py
            with open(os.path.join(base_path, "__init__.py"), "w", encoding='utf-8') as f:
                f.write("")

            # Criar {mod_name}_mod.py
            file_path = os.path.join(base_path, f"{mod_name}_mod.py")
            with open(file_path, "w", encoding='utf-8') as f:
                f.write(code)
            
            return True
        except Exception as e:
            print(f"[SINGULARITY] Erro ao salvar: {e}")
            return False

    def _build_prompt(self):
        """Cria o Prompt de Engenharia com o Template obrigatório."""
        return textwrap.dedent(f"""
            ATUE COMO UM ENGENHEIRO DE SOFTWARE PYTHON SÊNIOR.
            Sua tarefa é escrever um novo módulo para o sistema Aeon.
            
            ESPECIFICAÇÕES DO USUÁRIO:
            - Nome do Módulo: {self.temp_data['name']}
            - Gatilhos: {self.temp_data['triggers']}
            - Lógica Desejada: {self.temp_data['logic']}
            
            REGRAS OBRIGATÓRIAS (TEMPLATE):
            Você DEVE seguir exatamente esta estrutura de classe, herdando de AeonModule.
            Não invente imports complexos que não existem. Use bibliotecas padrão do Python (random, datetime, math, requests).
            Implemente os decorators @property para dependencies e metadata.
            Implemente os hooks on_load() e on_unload().
            
            TEMPLATE DO CÓDIGO:
            ```python
            from modules.base_module import AeonModule
            from typing import List, Dict
            import random  # ou o que precisar
            
            class {self.temp_data['name'].capitalize()}Module(AeonModule):
                def __init__(self, core_context):
                    super().__init__(core_context)
                    self.name = "{self.temp_data['name']}"
                    self.triggers = {self.temp_data['triggers']}
                    
                @property
                def dependencies(self) -> List[str]:
                    return []
                
                @property
                def metadata(self) -> Dict[str, str]:
                    return {{"version": "1.0.0", "author": "Aeon Singularidade"}}
                
                def on_load(self) -> bool:
                    return True
                
                def on_unload(self) -> bool:
                    return True
                
                def process(self, command: str) -> str:
                    # Implemente a lógica aqui baseada no pedido: {self.temp_data['logic']}
                    # Retorne uma STRING com a resposta do Aeon.
                    return "Resposta do módulo"
            ```
            
            SAÍDA:
            Retorne APENAS o código Python dentro de blocos markdown ```python ... ```.
            Não escreva explicações antes ou depois.
        """)

