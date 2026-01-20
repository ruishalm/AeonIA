# 🔌 SISTEMA PLUG & PLAY MELHORADO

## 📋 O QUE FOI IMPLEMENTADO

### 1. **Extended AeonModule** (`modules/base_module.py`)

#### Novos Atributos:
```python
dependencies     # Lista de módulos necessários
metadata         # Versão, autor, descrição
_loaded          # Flag de status
```

#### Novos Métodos:
```python
dependencies()           # Property: retorna lista de dependências
metadata()              # Property: versão, autor, descrição
check_dependencies()    # Valida dependências antes de executar
on_load()              # Hook: executado quando carrega
on_unload()            # Hook: executado quando descarrega
is_loaded()            # Retorna status
get_info()             # Info completa (para debug/admin)
```

#### Exemplo de Uso:
```python
class MeuModulo(AeonModule):
    @property
    def dependencies(self) -> List[str]:
        return ["brain", "io_handler"]  # Módulos necessários
    
    @property
    def metadata(self) -> Dict[str, str]:
        return {
            "version": "1.0.0",
            "author": "Seu Nome",
            "description": "Descrição do módulo"
        }
    
    def on_load(self) -> bool:
        # Inicialização customizada
        print("Módulo carregando!")
        return True
```

---

### 2. **Improved ModuleManager** (`core/module_manager.py`)

#### Novos Recursos:
```python
load_modules()              # Agora com validação de dependências
get_loaded_modules()        # Retorna lista de módulos carregados
get_module_info(name)       # Info completa de um módulo
list_modules(verbose=False) # Lista formatada de módulos
failed_modules              # Armazena módulos que falharam
module_map                  # Busca rápida por nome
```

#### Workflow Melhorado:
1. **Descoberta** → Encontra todos os `*_mod.py`
2. **Instanciação** → Cria instâncias com `core_context`
3. **Validação de Deps** → Checa se dependências existem
4. **on_load() Hook** → Executa inicialização customizada
5. **Registro** → Mapeia triggers
6. **Relatório** → Lista sucessos/falhas

#### Exemplo:
```python
manager.load_modules()      # Carrega tudo com validação
manager.list_modules(verbose=True)  # Mostra status detalhado
info = manager.get_module_info("dev_factory")  # Info de um módulo
```

---

### 3. **DevFactory Module** (`modules/dev/dev_mod.py`)

#### O que faz:
Cria **projetos completos** automaticamente!

#### Triggers:
- "crie um site"
- "crie um script"
- "crie um projeto"
- "gere um código"
- "construa um app"
- "crie uma calculadora"

#### Workflow:
```
Usuário: "Crie um site de portfólio"
    ↓
DevFactory extrai tipo ("site") + requisitos ("de portfólio")
    ↓
Brain gera código JSON:
{
  "index.html": "...HTML...",
  "style.css": "...CSS...",
  "script.js": "...JavaScript..."
}
    ↓
DevFactory cria arquivos em /workspace/site_20260119_120000/
    ↓
Abre automáticamente no VS Code
    ↓
Usuário vê código pronto para usar!
```

#### Tipos Suportados:
- **site** → HTML/CSS/JavaScript
- **script** → Python
- **calculator** → Calculadora completa
- **api** → Flask/FastAPI
- **app** → Aplicação completa

#### Histórico:
Salva tudo em `workspace/projects.json`:
```json
{
  "name": "site_20260119_120000",
  "type": "site",
  "created_at": "2026-01-19T12:00:00",
  "requirements": "de portfólio",
  "path": "/AeonProject/workspace/site_20260119_120000",
  "files": ["index.html", "style.css", "script.js"]
}
```

---

## 🚀 COMO USAR

### 1. **Criar um Novo Módulo**

```python
# modules/meu_modulo/meu_mod.py

from modules.base_module import AeonModule
from typing import List, Dict, Any

class MeuModulo(AeonModule):
    @property
    def name(self) -> str:
        return "Meu Módulo"
    
    @property
    def triggers(self) -> List[str]:
        return ["meu comando", "faça algo"]
    
    @property
    def dependencies(self) -> List[str]:
        # Declarar dependências aqui
        return ["brain"]  # Preciso do Brain
    
    @property
    def metadata(self) -> Dict[str, str]:
        return {
            "version": "1.0.0",
            "author": "Seu Nome",
            "description": "Descrição curta"
        }
    
    def on_load(self) -> bool:
        # Executado quando o módulo carrega
        print(f"[{self.name}] Inicializando...")
        return True  # True = sucesso, False = falha
    
    def process(self, command: str) -> str:
        # Lógica principal
        if "meu comando" in command.lower():
            return "Executei meu comando!"
        return ""  # Retornar vazio = não processou
```

### 2. **O ModuleManager Carrega Automaticamente**

Ao iniciar `main.py`:
```python
manager = ModuleManager(core_context)
manager.load_modules()  # Varrer modules/ e carregar tudo
manager.list_modules(verbose=True)  # Ver o que carregou
```

Output:
```
[MOD_MANAGER] Carregando módulos de: AeonProject/modules

[MOD_MANAGER] Importando 'modules.meu_modulo.meu_mod'...
[MOD_MANAGER]   ✓ Classe encontrada: MeuModulo
[MOD_MANAGER]   ✓ Módulo 'Meu Módulo' instanciado
[MOD_MANAGER]   ✓ 'Meu Módulo' carregado com 2 triggers

[MOD_MANAGER] Validando e inicializando módulos...
[MOD_MANAGER]   ✓ 'Meu Módulo' carregado com 2 triggers
[MOD_MANAGER] ============================================================
[MOD_MANAGER] Módulos carregados: 1/1
[MOD_MANAGER] ============================================================

=== MÓDULOS CARREGADOS (1) ===
1. Meu Módulo
   Triggers: meu comando, faça algo
   Versão: 1.0.0
   Autor: Seu Nome
   Descrição: Descrição curta
   Dependências: brain
   Status: ✓ OK
```

### 3. **Usar DevFactory**

```
Usuário: "Aeon, crie um site com seção de contato"

[MOD_MANAGER] Roteando para: 'DevFactory' (trigger: 'crie um site')

Aeon: "Criando site... Aguarde (pode levar até 1 minuto)."

[DevFactory] Gerando código para site...
[DevFactory] Projeto criado em AeonProject/workspace/site_20260119_120000
[DevFactory] Abrindo no VS Code...

Aeon: "Pronto! Projeto 'site_20260119_120000' criado e aberto."

(VS Code abre automaticamente com os arquivos criados!)
```

---

## 🔧 EXTENSIBILIDADE

### Adicionar novo tipo no DevFactory:

```python
# Em DevFactory._build_prompt():
templates = {
    # ... outros tipos ...
    "meu_tipo": """You are a Senior Developer.
    
OUTPUT ONLY VALID JSON:
{{
  "file1.ext": "...code...",
  "file2.ext": "...code..."
}}"""
}
```

### Adicionar novo módulo:

1. Criar pasta: `modules/novo_modulo/`
2. Criar arquivo: `novo_modulo_mod.py` (nome **DEVE** terminar com `_mod.py`)
3. Herdar de `AeonModule`
4. Definir `name`, `triggers`, `process()`
5. **Pronto!** ModuleManager carrega automaticamente na próxima execução

---

## 📊 ARQUITETURA PLUG & PLAY

```
┌─────────────────────────────────────────────────────┐
│              AeonModule (Base Class)                │
│  - name, triggers, dependencies, metadata          │
│  - check_dependencies(), on_load(), on_unload()    │
│  - is_loaded(), get_info()                         │
└─────────────────────┬───────────────────────────────┘
                      │ herda
        ┌─────────────┼─────────────┬─────────────┐
        │             │             │             │
   ┌────▼───┐  ┌─────▼────┐  ┌────▼────┐  ┌────▼────┐
   │ Sistema │  │  Visão   │  │ Rotinas │  │DevFactory│
   └────────┘  └──────────┘  └─────────┘  └──────────┘
        │             │             │             │
        └─────────────┼─────────────┴─────────────┘
                      │
            ┌─────────▼──────────┐
            │ ModuleManager      │
            │ - load_modules()   │
            │ - route_command()  │
            │ - list_modules()   │
            └────────────────────┘
                      │
            ┌─────────▼──────────┐
            │   Trigger Map      │
            │ "trigger" → módulo │
            └────────────────────┘
```

---

## ✅ CHECKLIST: IMPLEMENTAÇÃO

- ✅ `AeonModule` com dependencies, metadata, hooks
- ✅ `ModuleManager` com validação de deps
- ✅ `ModuleManager` com hooks on_load/on_unload
- ✅ `ModuleManager` com list_modules() para debug
- ✅ `DevFactory` com suporte a múltiplos tipos
- ✅ `DevFactory` com histórico de projetos
- ✅ `DevFactory` com integração VS Code
- ✅ Documentação completa

---

## 🎯 PRÓXIMOS PASSOS

1. **Testar DevFactory** - criar alguns projetos de teste
2. **Adicionar más tipos** - React, Vue, Docker, etc
3. **Melhorar JSON parsing** - lidar com respostas malformadas
4. **Adicionar versionamento** - semântico para módulos
5. **Sistema de eventos** - módulos se comunicarem
6. **Cache de módulos** - carregar mais rápido
7. **Admin Panel** - gerenciar módulos via GUI

---

## 📝 NOTAS IMPORTANTES

1. **Nomes de arquivos**: Sempre `*_mod.py` (obrigatório!)
2. **Dependências**: Declarar todas as necessárias
3. **Retorno vazio**: Se `process()` retornar "", cai no Brain
4. **Thread-safe**: DevFactory roda em thread separada
5. **Workspace**: Sempre em `/AeonProject/workspace`
6. **VS Code**: Precisa estar instalado para abrir automaticamente
