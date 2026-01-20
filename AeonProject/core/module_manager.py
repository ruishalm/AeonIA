import os
import importlib
import inspect
import threading
import time
from modules.base_module import AeonModule

def log_display(msg):
    print(f"[MOD_MANAGER] {msg}")

class ModuleManager:
    """
    Carrega, gerencia e roteia comandos para todos os módulos do Aeon.
    """
    
    def __init__(self, core_context):
        self.core_context = core_context
        self.modules = []                    # Lista de todas as instâncias
        self.trigger_map = {}               # Mapeia trigger → módulo
        self.module_map = {}                # Mapeia nome → módulo (para busca rápida)
        self.failed_modules = []            # Módulos que falharam no carregamento
        
        # Sistema de FOCO (Módulo com microfone travado)
        self.focused_module = None           # Módulo com foco (None = modo livre)
        self.focus_timeout = None            # Thread de timeout do foco
        self.focus_lock = threading.Lock()   # Lock para thread-safety
        
        # Memória de Conversa (Corrige Efeito Dory)
        self.chat_history = []               
        self.max_history = 10                

    def load_modules(self):
        """Escaneia /modules e carrega tudo."""
        # Usa caminho relativo que funciona de qualquer lugar
        modules_dir = os.path.join(os.path.dirname(__file__), "..", "modules")
        modules_dir = os.path.abspath(modules_dir)
        log_display(f"Carregando módulos de: {modules_dir}")

        # Varre diretórios
        for item in os.listdir(modules_dir):
            module_path = os.path.join(modules_dir, item)
            if os.path.isdir(module_path) and item != "__pycache__":
                try:
                    # Encontrar arquivo *_mod.py
                    mod_file = next((f for f in os.listdir(module_path) if f.endswith("_mod.py")), None)
                    if not mod_file: continue

                    module_name = f"modules.{item}.{mod_file.replace('.py', '')}"
                    self._import_and_register(module_name)

                except Exception as e:
                    log_display(f"  ✗ Erro ao carregar '{item}': {e}")
                    self.failed_modules.append({"name": item, "error": str(e)})
        
        # Log final
        log_display(f"Módulos carregados: {len(self.modules)}")

    def _import_and_register(self, module_name):
        """Helper para importar e registrar um único módulo."""
        try:
            module_import = importlib.import_module(module_name)
            for name, obj in inspect.getmembers(module_import):
                if inspect.isclass(obj) and issubclass(obj, AeonModule) and obj is not AeonModule:
                    # Instanciar
                    module_instance = obj(self.core_context)
                    
                    # Verificar dependências
                    if not module_instance.check_dependencies():
                        log_display(f"  ⚠ Dependências falharam para {module_instance.name}")
                        return

                    # Chamar on_load
                    if module_instance.on_load():
                        self.modules.append(module_instance)
                        self.module_map[module_instance.name.lower()] = module_instance
                        
                        # Registrar triggers
                        for trigger in module_instance.triggers:
                            self.trigger_map[trigger.lower()] = module_instance
                        
                        log_display(f"  ✓ {module_instance.name} carregado.")
                    break
        except Exception as e:
            log_display(f"Erro importando {module_name}: {e}")

    def scan_new_modules(self):
        """Re-escaneia módulos (usado pela Singularidade)."""
        log_display("Re-escaneando novos módulos...")
        # Simplesmente roda o load_modules de novo (versão simplificada para evitar duplicatas complexas)
        # O ideal seria verificar um por um, mas para o MVP, vamos recarregar.
        self.trigger_map = {} # Limpa triggers antigos para evitar lixo
        self.modules = []
        self.load_modules()
        return ["Reloaded"]

    def _format_history(self):
        """Formata histórico para o LLM."""
        history_text = ""
        for msg in self.chat_history:
            role = "Usuário" if msg['role'] == 'user' else "Aeon"
            history_text += f"{role}: {msg['content']}\n"
        return history_text

    def route_command(self, command: str) -> str:
        """Roteia comando com PRIORIDADE DE TAMANHO."""
        command_lower = command.lower()
        response = ""

        # 1. MODO FOCO
        if self.focused_module is not None:
            log_display(f"🔒 FOCO: {self.focused_module.name}")
            return self.focused_module.process(command) or ""
        
        # 2. MODO LIVRE (Agora ordenado!)
        triggered = False
        
        # ORDENAÇÃO CRÍTICA: Triggers maiores primeiro
        # Ex: "criar site" (10 chars) vem antes de "criar" (5 chars)
        sorted_triggers = sorted(self.trigger_map.items(), key=lambda x: len(x[0]), reverse=True)

        for trigger, module in sorted_triggers:
            if trigger in command_lower:
                if not module.check_dependencies():
                    return f"Erro: Dependência de {module.name} falhou."
                
                log_display(f"Trigger '{trigger}' acionou '{module.name}'")
                response = module.process(command)
                triggered = True
                break # Para no primeiro trigger (o mais específico)

        # 3. FALLBACK (Brain)
        if not triggered:
            brain = self.core_context.get("brain")
            if brain:
                hist = self._format_history()
                response = brain.pensar(prompt=command, historico_txt=hist, user_prefs={})
            else:
                response = "Cérebro indisponível."

        # 4. MEMÓRIA
        if response:
            self.chat_history.append({"role": "user", "content": command})
            self.chat_history.append({"role": "assistant", "content": response})
            if len(self.chat_history) > self.max_history * 2:
                self.chat_history.pop(0); self.chat_history.pop(0)

        return response if response else ""

    # Métodos de Foco (Iguais ao anterior)
    def lock_focus(self, module, timeout=None):
        with self.focus_lock:
            self.focused_module = module
    
    def release_focus(self):
        with self.focus_lock:
            self.focused_module = None

    def get_loaded_modules(self):
        return self.modules