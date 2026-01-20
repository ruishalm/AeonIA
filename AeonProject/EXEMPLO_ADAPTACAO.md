# EXEMPLO: Como Adaptar um Módulo Existente para o Novo Sistema

Este arquivo mostra como adaptar um módulo para usar:
- Dependências
- Metadados
- Hooks de ciclo de vida

## ANTES (Simples)

```python
from modules.base_module import AeonModule

class VisaoModule(AeonModule):
    def __init__(self, core_context):
        super().__init__(core_context)
        self.name = "Visão"
        self.triggers = ["tela", "veja", "analise a tela"]
    
    @property
    def name(self) -> str:
        return self._name
    
    @property
    def triggers(self) -> list:
        return self._triggers
    
    def process(self, command: str) -> str:
        return "Analisando a tela..."
```

## DEPOIS (Melhorado com Plug & Play)

```python
from modules.base_module import AeonModule
from typing import List, Dict, Any

class VisionModule(AeonModule):
    """
    Módulo de Visão - Captura e análise de tela.
    
    Dependências:
    - brain: Para análise de imagens via LLM
    
    Exemplo:
    >>> "Aeon, analise a tela"
    "Estou vendo um terminal Python com..."
    """
    
    def __init__(self, core_context: Dict[str, Any]):
        super().__init__(core_context)
        self._name = "Visão"
        self._triggers = ["tela", "veja", "analise a tela", "o que você vê"]
        self._dependencies = ["brain"]  # ← Dependências declaradas!
        self.snapshot_count = 0

    @property
    def name(self) -> str:
        return self._name

    @property
    def triggers(self) -> List[str]:
        return self._triggers

    @property
    def dependencies(self) -> List[str]:
        """Este módulo precisa do Brain para análise de imagens."""
        return self._dependencies

    @property
    def metadata(self) -> Dict[str, str]:
        """Metadados do módulo."""
        return {
            "version": "2.0.0",
            "author": "Aeon Team",
            "description": "Captura e analisa screenshots da tela"
        }

    def on_load(self) -> bool:
        """
        Hook: Chamado quando o módulo é carregado.
        Aqui você faz inicialização customizada.
        """
        print(f"[{self.name}] Inicializando... Criando diretório de snapshots")
        
        try:
            import os
            snapshots_dir = os.path.join("AeonProject", "modules", "visao", "snapshots")
            os.makedirs(snapshots_dir, exist_ok=True)
            self.snapshot_count = len(os.listdir(snapshots_dir))
            print(f"[{self.name}] ✓ Pronto! {self.snapshot_count} snapshots existentes")
            return True
        except Exception as e:
            print(f"[{self.name}] ✗ Erro: {e}")
            return False

    def on_unload(self) -> bool:
        """
        Hook: Chamado quando o módulo é descarregado.
        Aqui você faz limpeza (fechar arquivos, etc).
        """
        print(f"[{self.name}] Descarregando...")
        # Aqui você poderia fazer limpeza se necessário
        return True

    def process(self, command: str) -> str:
        """Processa comandos de visão."""
        try:
            from PIL import ImageGrab
            from io import BytesIO
            
            # Verificar se Brain está disponível (dependência)
            brain = self.core_context.get("brain")
            if not brain:
                return "Brain não disponível para análise de imagens"
            
            # Capturar tela
            screenshot = ImageGrab.grab()
            img_byte_arr = BytesIO()
            screenshot.save(img_byte_arr, format='PNG')
            img_bytes = img_byte_arr.getvalue()
            
            # Usar Brain para análise
            analysis = brain.ver(img_bytes)
            
            self.snapshot_count += 1
            return analysis
        
        except Exception as e:
            return f"Erro ao analisar tela: {e}"
```

---

## O QUE MUDOU?

| Aspecto | Antes | Depois |
|--------|-------|--------|
| Dependências | Nenhuma | `dependencies` explícitas |
| Metadados | Nenhum | `version`, `author`, `description` |
| Inicialização | Inline | `on_load()` hook |
| Limpeza | Nenhuma | `on_unload()` hook |
| Debug | Difícil | `get_info()` retorna tudo |
| Type Hints | Nenhum | Completo com `typing` |

---

## BENEFÍCIOS

✅ **Segurança** - Dependências validadas antes de executar
✅ **Rastreabilidade** - Metadados identificam versão/autor
✅ **Escalabilidade** - Hooks permitem lógica complexa
✅ **Debug** - `get_info()` mostra status completo
✅ **Extensibilidade** - Fácil adicionar novos módulos

---

## MIGRAÇÃO EM 5 PASSOS

Para adaptar um módulo existente:

### 1. Adicionar Dependências
```python
@property
def dependencies(self) -> List[str]:
    return ["brain", "io_handler"]
```

### 2. Adicionar Metadados
```python
@property
def metadata(self) -> Dict[str, str]:
    return {
        "version": "2.0.0",
        "author": "Seu Nome",
        "description": "O que faz"
    }
```

### 3. Adicionar on_load()
```python
def on_load(self) -> bool:
    # Inicializar recursos
    return True  # ou False se falhar
```

### 4. Adicionar on_unload()
```python
def on_unload(self) -> bool:
    # Limpar recursos
    return True
```

### 5. Adicionar Type Hints
```python
from typing import List, Dict, Any

def process(self, command: str) -> str:
    # Com type hints!
```

---

## TESTE PARA VERIFICAR

```python
# main.py ou terminal

from core.module_manager import ModuleManager
from core.brain import Brain

# Setup
core_context = {"brain": Brain(...), ...}
manager = ModuleManager(core_context)
manager.load_modules()

# Listar módulos com metadados
manager.list_modules(verbose=True)

# Obter info de um módulo
info = manager.get_module_info("Visão")
print(info)
# Output:
# {
#     'name': 'Visão',
#     'triggers': ['tela', 'veja', ...],
#     'dependencies': ['brain'],
#     'metadata': {'version': '2.0.0', ...},
#     'loaded': True,
#     'dependencies_ok': True
# }
```

---

## PRÓXIMAS ATUALIZAÇÕES

Considere adaptar estes módulos:
- [ ] SistemaModule - Adicionar dependências
- [ ] RotinasModule - Adicionar metadados
- [ ] ControleModule - Adicionar hooks
- [ ] Todos os outros - Follow same pattern
