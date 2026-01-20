from abc import ABC, abstractmethod
from typing import List, Dict, Any

class AeonModule(ABC):
    """
    A classe base abstrata para todos os módulos do Aeon.
    
    Suporta:
    - Carregamento dinâmico ("Plug & Play")
    - Verificação de dependências
    - Metadados de módulo
    - Hooks de ciclo de vida
    """
    
    def __init__(self, core_context: Dict[str, Any]):
        """
        Inicializa o módulo.

        Args:
            core_context: Dicionário com acesso aos componentes centrais 
                         (Brain, IOHandler, ConfigManager, etc).
        """
        self.core_context = core_context
        self._name = None
        self._triggers = []
        self._dependencies = []
        self._loaded = False

    @property
    def name(self) -> str:
        """Nome único do módulo."""
        return getattr(self, '_name', 'Unnamed')
    
    @name.setter
    def name(self, value: str):
        """Setter para nome do módulo."""
        self._name = value

    @property
    def triggers(self) -> List[str]:
        """Lista de palavras-chave que ativam este módulo."""
        return getattr(self, '_triggers', [])
    
    @triggers.setter
    def triggers(self, value: List[str]):
        """Setter para triggers do módulo."""
        self._triggers = value

    @property
    def dependencies(self) -> List[str]:
        """
        Lista de módulos necessários para este funcionar.
        
        Exemplo: ["brain", "system"]
        
        Sobrescreva se seu módulo depender de outros.
        """
        return self._dependencies

    @property
    def metadata(self) -> Dict[str, str]:
        """
        Metadados do módulo (versão, autor, descrição).
        
        Exemplo:
            {
                "version": "1.0.0",
                "author": "Seu Nome",
                "description": "Descrição curta do módulo"
            }
        
        Sobrescreva para fornecer informações.
        """
        return {
            "version": "1.0.0",
            "author": "Unknown",
            "description": "Módulo sem descrição"
        }

    @abstractmethod
    def process(self, command: str) -> str:
        """
        O método principal que processa o comando do usuário.

        Args:
            command (str): O comando completo do usuário.

        Returns:
            str: Uma resposta em texto para ser falada pelo assistente.
                 Retorna uma string vazia se nenhuma ação for tomada.
        """
        raise NotImplementedError

    def check_dependencies(self) -> bool:
        """
        Verifica se todos os módulos dependentes estão disponíveis.
        
        Returns:
            bool: True se todas as dependências foram satisfeitas, False caso contrário.
        """
        if not self.dependencies:
            return True
        
        # Obter lista de módulos carregados
        module_manager = self.core_context.get("module_manager")
        if not module_manager:
            # Se não há module_manager, verificar diretamente no core_context
            for dep in self.dependencies:
                if dep not in self.core_context or self.core_context[dep] is None:
                    print(f"[{self.name}] Dependência ausente: {dep}")
                    return False
            return True
        
        # Verificar se o ModuleManager tem um método para listar módulos
        if hasattr(module_manager, 'get_loaded_modules'):
            loaded_names = [m.name.lower() for m in module_manager.get_loaded_modules()]
            for dep in self.dependencies:
                if dep.lower() not in loaded_names:
                    print(f"[{self.name}] Dependência ausente: {dep}")
                    return False
        
        return True

    def on_load(self) -> bool:
        """
        Hook chamado quando o módulo é carregado.
        Sobrescreva para inicialização customizada.
        
        Returns:
            bool: True se carregou com sucesso, False caso contrário.
        """
        self._loaded = True
        return True

    def on_unload(self) -> bool:
        """
        Hook chamado quando o módulo é descarregado.
        Sobrescreva para limpeza customizada.
        
        Returns:
            bool: True se descarregou com sucesso, False caso contrário.
        """
        self._loaded = False
        return True

    def is_loaded(self) -> bool:
        """Retorna True se o módulo está carregado."""
        return self._loaded

    def get_info(self) -> Dict[str, Any]:
        """Retorna informações completas do módulo (para debug/admin)."""
        return {
            "name": self.name,
            "triggers": self.triggers,
            "dependencies": self.dependencies,
            "metadata": self.metadata,
            "loaded": self.is_loaded(),
            "dependencies_ok": self.check_dependencies()
        }
