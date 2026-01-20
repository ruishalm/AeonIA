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
    
    Suporta:
    - Carregamento dinâmico ("Plug & Play")
    - Verificação de dependências
    - Hooks de ciclo de vida
    - Metadados de módulos
    - Sistema de FOCO para módulos com fluxo contínuo (ex: Ditado)
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

    def load_modules(self):
        """
        Escaneia /modules, importa dinamicamente cada módulo,
        instancia e registra (com validação de dependências).
        """
        modules_dir = os.path.join("AeonProject", "modules")
        log_display(f"Carregando módulos de: {modules_dir}")

        # PASSO 1: Descobrir e instanciar todos os módulos
        for item in os.listdir(modules_dir):
            module_path = os.path.join(modules_dir, item)
            if os.path.isdir(module_path) and item != "__pycache__":
                try:
                    # Encontrar arquivo *_mod.py
                    mod_file = next(
                        (f for f in os.listdir(module_path) if f.endswith("_mod.py")),
                        None
                    )
                    if not mod_file:
                        continue

                    module_name = f"modules.{item}.{mod_file.replace('.py', '')}"
                    log_display(f"Importando '{module_name}'...")
                    module_import = importlib.import_module(module_name)

                    # Encontrar classe AeonModule
                    for name, obj in inspect.getmembers(module_import):
                        if inspect.isclass(obj) and issubclass(obj, AeonModule) and obj is not AeonModule:
                            log_display(f"  ✓ Classe encontrada: {name}")
                            
                            try:
                                # Instanciar módulo
                                module_instance = obj(self.core_context)
                                self.modules.append(module_instance)
                                self.module_map[module_instance.name.lower()] = module_instance
                                
                                log_display(f"  ✓ Módulo '{module_instance.name}' instanciado")
                                break
                            except Exception as e:
                                log_display(f"  ✗ Erro ao instanciar {name}: {e}")
                                self.failed_modules.append({"name": name, "error": str(e)})

                except StopIteration:
                    log_display(f"  ⊘ Pasta '{item}' não contém arquivo _mod.py")
                except Exception as e:
                    log_display(f"  ✗ Erro ao carregar '{item}': {e}")
                    self.failed_modules.append({"name": item, "error": str(e)})

        # PASSO 2: Chamar hook on_load() e validar dependências
        log_display("\nValidando e inicializando módulos...")
        for module in self.modules:
            # Verificar dependências
            if not module.check_dependencies():
                log_display(f"  ✗ '{module.name}' tem dependências não satisfeitas")
                log_display(f"     Dependências: {module.dependencies}")
                self.failed_modules.append({"name": module.name, "error": "Unmet dependencies"})
                continue

            # Chamar hook on_load
            try:
                success = module.on_load()
                if not success:
                    log_display(f"  ✗ '{module.name}' falhou em on_load()")
                    self.failed_modules.append({"name": module.name, "error": "on_load() failed"})
                    continue
            except Exception as e:
                log_display(f"  ✗ '{module.name}' erro em on_load(): {e}")
                self.failed_modules.append({"name": module.name, "error": f"on_load() error: {e}"})
                continue

            # Registrar triggers
            for trigger in module.triggers:
                if trigger in self.trigger_map:
                    log_display(f"  ⚠ Trigger '{trigger}' duplicado (sobrescrevendo)")
                self.trigger_map[trigger] = module
            
            log_display(f"  ✓ '{module.name}' carregado com {len(module.triggers)} triggers")

        # Resumo
        log_display(f"\n{'='*60}")
        log_display(f"Módulos carregados: {len(self.modules) - len(self.failed_modules)}/{len(self.modules)}")
        if self.failed_modules:
            log_display(f"Módulos com falha: {len(self.failed_modules)}")
            for failed in self.failed_modules:
                log_display(f"  - {failed['name']}: {failed['error']}")
        log_display(f"{'='*60}\n")

    def route_command(self, command: str) -> str:
        """
        Recebe um comando e roteia para o módulo apropriado.
        
        LÓGICA DE FOCO:
        - Se focused_module != None: envia DIRETAMENTE para ele, ignora outros triggers
        - Se focused_module == None (Modo Livre): varre trigger_map normalmente
        
        Fallback: envia para o Brain (LLM).
        """
        command_lower = command.lower()
        
        # ===== MODO FOCO: Microfone travado em um módulo =====
        if self.focused_module is not None:
            log_display(f"🔒 MODO FOCO: Enviando para '{self.focused_module.name}'")
            response = self.focused_module.process(command)
            return response if response else ""
        
        # ===== MODO LIVRE: Roteamento automático por triggers =====
        # Procurar por módulo que tenha trigger
        for trigger, module in self.trigger_map.items():
            if trigger in command_lower:
                # Validar dependências novamente (pode ter mudado)
                if not module.check_dependencies():
                    return f"O módulo '{module.name}' tem dependências não satisfeitas."
                
                log_display(f"Roteando para: '{module.name}' (trigger: '{trigger}')")
                response = module.process(command)
                
                if response:
                    return response

        # Fallback: usar Brain como padrão
        log_display("Nenhum módulo especializado acionado. Roteando para o Cérebro...")
        brain = self.core_context.get("brain")
        if brain:
            return brain.pensar(prompt=command, historico_txt="", user_prefs={})
        else:
            return "Cérebro não encontrado."

    # ========== SISTEMA DE FOCO ==========
    
    def lock_focus(self, module_instance, timeout_seconds=None):
        """
        Trava o foco em um módulo específico.
        
        Args:
            module_instance: Instância do módulo que quer o foco
            timeout_seconds: Se fornecido, foco é liberado automaticamente após X segundos
        
        Exemplo:
            module_manager.lock_focus(typewriter_module, timeout_seconds=300)  # 5 min
        """
        with self.focus_lock:
            self.focused_module = module_instance
            log_display(f"🔒 FOCO TRAVADO: {module_instance.name}")
            
            # Se timeout definido, cria thread para auto-release
            if timeout_seconds:
                self._set_focus_timeout(timeout_seconds)
    
    def release_focus(self):
        """
        Libera o foco. Volta ao Modo Livre.
        """
        with self.focus_lock:
            if self.focused_module:
                old_module = self.focused_module.name
                self.focused_module = None
                log_display(f"🔓 FOCO LIBERADO: {old_module} → Modo Livre")
            
            # Cancelar timeout se existir
            if self.focus_timeout:
                self.focus_timeout.cancel()
                self.focus_timeout = None
    
    def is_focused(self) -> bool:
        """Retorna True se há algum módulo com foco travado."""
        return self.focused_module is not None
    
    def get_focused_module(self):
        """Retorna o módulo que tem foco, ou None."""
        return self.focused_module
    
    def _set_focus_timeout(self, seconds):
        """Define timeout para auto-release do foco."""
        # Cancelar timeout anterior se houver
        if self.focus_timeout:
            self.focus_timeout.cancel()
        
        # Criar novo timeout
        self.focus_timeout = threading.Timer(
            seconds,
            self._timeout_handler
        )
        self.focus_timeout.daemon = True
        self.focus_timeout.start()
        log_display(f"⏱ Timeout de foco definido para {seconds}s")
    
    def _timeout_handler(self):
        """Handler chamado quando o timeout de foco expira."""
        log_display("⏱ Timeout de foco expirou!")
        self.release_focus()

    def get_loaded_modules(self):
        """Retorna lista de módulos carregados com sucesso."""
        return self.modules

    def get_module_info(self, module_name: str = None):
        """
        Retorna informações sobre um módulo específico ou todos.
        Útil para debug/admin.
        """
        if module_name:
            module = self.module_map.get(module_name.lower())
            if module:
                return module.get_info()
            return None
        
        return {
            "total": len(self.modules),
            "failed": len(self.failed_modules),
            "modules": [m.get_info() for m in self.modules],
            "failed_modules": self.failed_modules
        }

    def list_modules(self, verbose=False):
        """Lista todos os módulos carregados."""
        log_display(f"\n{'='*60}")
        log_display(f"MÓDULOS CARREGADOS ({len(self.modules)})")
        log_display(f"{'='*60}")
        
        for i, module in enumerate(self.modules, 1):
            info = module.get_info()
            log_display(f"\n{i}. {info['name']}")
            log_display(f"   Triggers: {', '.join(info['triggers'])}")
            
            if verbose:
                log_display(f"   Versão: {info['metadata'].get('version', '?')}")
                log_display(f"   Autor: {info['metadata'].get('author', '?')}")
                log_display(f"   Descrição: {info['metadata'].get('description', '?')}")
                log_display(f"   Dependências: {info['dependencies'] or 'Nenhuma'}")
                log_display(f"   Status: {'✓ OK' if info['dependencies_ok'] else '✗ FALHA'}")
        
        log_display(f"\n{'='*60}\n")
