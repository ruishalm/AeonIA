# 🧪 GUIA DE TESTES: Sistema Plug & Play

## 1. TESTE BÁSICO: Carregamento de Módulos

```bash
# No terminal, dentro de d:\Dev\Aeon

$ python -c "
from core.module_manager import ModuleManager
from core.brain import Brain

core_context = {'brain': Brain(...)}
manager = ModuleManager(core_context)
manager.load_modules()
print('✓ Módulos carregados com sucesso!')
"
```

**Esperado:**
- Sem erros
- Lista de módulos carregados
- DevFactory entre eles

---

## 2. TESTE: Listar Módulos com Verbose

```python
# test_modules.py

from core.module_manager import ModuleManager
from core.brain import Brain
from core.io_handler import IOHandler
from core.config_manager import ConfigManager

# Setup (simples)
config_manager = ConfigManager()
brain = Brain(config={"GROQ_KEY": "..."}, installer=None)
io_handler = IOHandler(config={}, installer=None)

core_context = {
    'brain': brain,
    'io_handler': io_handler,
    'config_manager': config_manager
}

# Testar
manager = ModuleManager(core_context)
manager.load_modules()
manager.list_modules(verbose=True)

# Ver info específica
dev_factory_info = manager.get_module_info("DevFactory")
print("\nInfo do DevFactory:")
print(dev_factory_info)
```

**Esperado:**
```
============================================================
MÓDULOS CARREGADOS (X)
============================================================

1. DevFactory
   Triggers: crie um site, crie um script, crie um projeto, ...
   Versão: 1.0.0
   Autor: Aeon DevFactory
   Descrição: Gera projetos de software completos usando IA
   Dependências: brain
   Status: ✓ OK

... (outros módulos)
```

---

## 3. TESTE: Validação de Dependências

```python
# test_dependencies.py

class TesteModule(AeonModule):
    @property
    def dependencies(self):
        return ["brain", "modulo_que_nao_existe"]  # ← Vai falhar!
    
    @property
    def name(self):
        return "TesteMod"
    
    @property
    def triggers(self):
        return ["teste"]
    
    def process(self, command):
        return "ok"

# Testar
module = TesteModule(core_context)
if module.check_dependencies():
    print("✓ Dependências OK")
else:
    print("✗ Dependência ausente!")  # ← Vai vir aqui
```

**Esperado:**
```
[TesteMod] Dependência ausente: modulo_que_nao_existe
✗ Dependência ausente!
```

---

## 4. TESTE: Hooks on_load / on_unload

```python
# test_hooks.py

class HookTestModule(AeonModule):
    @property
    def name(self):
        return "HookTest"
    
    @property
    def triggers(self):
        return ["teste"]
    
    def on_load(self):
        print("✓ on_load() chamado!")
        return True
    
    def on_unload(self):
        print("✓ on_unload() chamado!")
        return True
    
    def process(self, command):
        return "ok"

# Testar
module = HookTestModule(core_context)
print("Status antes:", module.is_loaded())  # False

module.on_load()
print("Status depois:", module.is_loaded())   # True

module.on_unload()
print("Status após unload:", module.is_loaded())  # False
```

**Esperado:**
```
Status antes: False
✓ on_load() chamado!
Status depois: True
✓ on_unload() chamado!
Status após unload: False
```

---

## 5. TESTE: DevFactory - Criar Site

```python
# test_devfactory.py

# Setup completo
config_manager = ConfigManager()
brain = Brain(config={"GROQ_KEY": "seu_groq_key_aqui"}, installer=None)
io_handler = IOHandler(config={}, installer=None)

core_context = {
    'brain': brain,
    'io_handler': io_handler,
    'config_manager': config_manager
}

# Carregar DevFactory
manager = ModuleManager(core_context)
manager.load_modules()

# Obter DevFactory
dev_factory = manager.get_module_info("DevFactory")
if dev_factory:
    print(f"✓ DevFactory encontrado")
    print(f"  Triggers: {dev_factory['triggers']}")

# Usar DevFactory
command = "crie um site simples com HTML e CSS"
response = manager.route_command(command)
print(f"Resposta: {response}")

# Aguardar um pouco (thread está rodando)
import time
time.sleep(5)

# Verificar se projeto foi criado
import os
workspace = os.path.join("AeonProject", "workspace")
projects = os.listdir(workspace)
print(f"\nProjetos em workspace: {projects}")
```

**Esperado:**
```
✓ DevFactory encontrado
  Triggers: ['crie um site', 'crie um script', ...]
Resposta: Criando site... Aguarde (pode levar até 1 minuto).

(Após ~30-60s, VS Code abre)

Projetos em workspace: ['site_20260119_120000', ...]
```

---

## 6. TESTE: DevFactory - Verificar Arquivos

```python
# test_devfactory_files.py

import os
import json

workspace = os.path.join("AeonProject", "workspace")

# Verificar projects.json
projects_log = os.path.join(workspace, "projects.json")
if os.path.exists(projects_log):
    with open(projects_log, 'r') as f:
        projects = json.load(f)
    
    print(f"✓ Projetos criados: {len(projects)}")
    for proj in projects:
        print(f"\n  - {proj['name']}")
        print(f"    Tipo: {proj['type']}")
        print(f"    Criado em: {proj['created_at']}")
        print(f"    Arquivos: {proj['files']}")
        
        # Verificar se arquivos existem
        for file in proj['files']:
            filepath = os.path.join(proj['path'], file)
            if os.path.exists(filepath):
                size = os.path.getsize(filepath)
                print(f"    ✓ {file} ({size} bytes)")
            else:
                print(f"    ✗ {file} (NÃO ENCONTRADO)")
```

**Esperado:**
```
✓ Projetos criados: 1

  - site_20260119_120000
    Tipo: site
    Criado em: 2026-01-19T12:00:00.000000
    Arquivos: ['index.html', 'style.css', 'script.js']
    ✓ index.html (2500 bytes)
    ✓ style.css (1200 bytes)
    ✓ script.js (3400 bytes)
```

---

## 7. TESTE: Roteamento com Fallback

```python
# test_routing.py

# Setup
manager = ModuleManager(core_context)
manager.load_modules()

# Teste 1: Comando que aciona DevFactory
response = manager.route_command("crie um site")
print(f"Teste 1 (DevFactory): {response}")

# Teste 2: Comando que aciona outro módulo
response = manager.route_command("analise a tela")
print(f"Teste 2 (Visão): {response}")

# Teste 3: Comando genérico (fallback para Brain)
response = manager.route_command("qual é a capital da França?")
print(f"Teste 3 (Brain): {response}")
```

**Esperado:**
```
Teste 1 (DevFactory): Criando site... Aguarde...
Teste 2 (Visão): [análise de tela]
Teste 3 (Brain): Paris é a capital da França
```

---

## 8. TESTE: Verificar Relatório de Falhas

```python
# test_failures.py

manager = ModuleManager(core_context)
manager.load_modules()

print(f"Módulos com sucesso: {len(manager.modules)}")
print(f"Módulos falhados: {len(manager.failed_modules)}")

if manager.failed_modules:
    print("\nMódulos com falha:")
    for failed in manager.failed_modules:
        print(f"  - {failed['name']}: {failed['error']}")
```

**Esperado (sem falhas):**
```
Módulos com sucesso: 10
Módulos falhados: 0
```

**Ou (com falha simulada):**
```
Módulos com sucesso: 9
Módulos falhados: 1

Módulos com falha:
  - MeuModuloErrado: Unmet dependencies
```

---

## 9. TESTE: Workflow Completo (Integração)

```python
# test_integration.py
# Este é o teste "end-to-end" mais realista

from main import setup_aeon  # Assumindo que main.py tem setup_aeon()

# 1. Inicializar tudo
gui, manager = setup_aeon()

# 2. Simular comando do usuário
commands = [
    "crie um site de portfólio",
    "crie um script python que sorted listas",
    "crie uma calculadora"
]

for cmd in commands:
    print(f"\nComando: {cmd}")
    response = manager.route_command(cmd)
    print(f"Resposta: {response}")
    
    # Aguardar um pouco
    import time
    time.sleep(2)

# 3. Verificar resultados
import os
workspace = os.path.join("AeonProject", "workspace")
created = os.listdir(workspace)
print(f"\nProjetos criados: {len(created) - 1}")  # -1 para projects.json
```

---

## 🎯 CHECKLIST DE TESTES

- [ ] **Carregamento Básico** - Módulos carregam sem erro
- [ ] **Validação de Deps** - Dependências são validadas
- [ ] **Hooks** - on_load() e on_unload() são chamados
- [ ] **DevFactory Site** - Cria site HTML/CSS/JS
- [ ] **DevFactory Script** - Cria script Python
- [ ] **DevFactory Calculator** - Cria calculadora
- [ ] **Arquivos Criados** - Todos os arquivos existem e têm conteúdo
- [ ] **VS Code Abre** - VS Code abre automaticamente
- [ ] **Histórico** - projects.json é populado corretamente
- [ ] **Roteamento** - Comandos vão para módulos corretos
- [ ] **Fallback** - Brain recebe comandos genéricos
- [ ] **Relatório** - Erros são rastreados e reportados

---

## 🐛 DEBUGGING

Se algo falhar, verifique:

1. **Import Error?**
   ```
   Adicionar print() no início de cada arquivo para rastrear import
   ```

2. **Dependência faltando?**
   ```python
   manager.get_module_info("DevFactory")['dependencies_ok']
   # Deve ser True
   ```

3. **DevFactory não cria arquivos?**
   ```
   Verificar se Brain está retornando JSON válido
   Adicionar try/except em _extract_json()
   ```

4. **VS Code não abre?**
   ```
   1. Verificar se VS Code está instalado
   2. Executar: code --version (no terminal)
   3. Se falhar, comentar linha de subprocess.Popen
   ```

5. **Módulo falhando em on_load()?**
   ```
   Adicionar debug prints em on_load()
   Verificar se recursos necessários existem
   ```

---

## 📝 EXEMPLO DE RESULTADO ESPERADO

Após executar testes, você deve ter:

```
AeonProject/
├── modules/
│   ├── dev/
│   │   ├── dev_mod.py         ✓ DevFactory
│   │   └── __init__.py
│   ├── ...outros módulos...
│
├── workspace/
│   ├── projects.json
│   ├── site_20260119_120000/
│   │   ├── index.html
│   │   ├── style.css
│   │   └── script.js
│   ├── script_20260119_120100/
│   │   └── main.py
│   └── ... (mais projetos criados)
│
└── ... (resto da estrutura)
```

E você deve ter visto:
- ✓ Módulos carregados
- ✓ DevFactory entre eles
- ✓ Projetos criados em tempo real
- ✓ VS Code abrir automaticamente
- ✓ Arquivos com código real (não vazio)

---

## ✅ TUDO PRONTO!

Se todos os testes passarem, você tem um sistema Plug & Play totalmente funcional!
