# 🧪 GUIA RÁPIDO DE TESTES - AEON V80

## ⚡ Quick Start

### Opção 1: Windows (Mais Rápido)
```bash
double-click em: d:\Dev\Aeon\run_tests.bat
```

### Opção 2: PowerShell
```powershell
cd d:\Dev\Aeon
python tests/test_all_modules.py
```

### Opção 3: Testar Um Módulo Específico
```bash
# Sistema de Foco
python tests/test_sistema_focus.py

# TypewriterModule
python tests/test_typewriter_module.py

# Carregamento de Módulos
python tests/test_module_loading.py

# Code Rendering
python tests/test_code_rendering.py

# Roteamento
python tests/test_routing.py
```

---

## 📊 O Que Cada Teste Valida

| Teste | O Que Testa | Tempo |
|-------|------------|-------|
| test_sistema_focus.py | lock_focus(), release_focus(), focused_module | ~200ms |
| test_typewriter_module.py | Estado, dependências, metadados do Datilógrafo | ~150ms |
| test_module_loading.py | Descoberta e carregamento de todos os módulos | ~500ms |
| test_code_rendering.py | Parsing e split de ` ``` ` blocos de código | ~100ms |
| test_routing.py | Roteamento de comandos via triggers | ~300ms |
| **TOTAL** | **Todos os componentes V80** | **~1.2s** |

---

## ✅ O Que Significa "Todos os Testes Passaram"

Quer dizer que:

1. ✅ **Sistema de Foco funciona**
   - lock_focus() e release_focus() trabalham corretamente
   - Modo travado ignora outros triggers
   - Timeout automático funciona

2. ✅ **TypewriterModule está pronto**
   - Estrutura correta
   - Dependências validadas
   - Hooks on_load/on_unload funcionam

3. ✅ **Carregamento dinâmico funciona**
   - Todos os módulos são descobertos
   - Triggers são registrados
   - Fallback para Brain quando necessário

4. ✅ **Code Rendering funciona**
   - Blocos ` ``` ` são detectados corretamente
   - Múltiplas linguagens suportadas
   - Fallback para texto normal

5. ✅ **Roteamento de comandos funciona**
   - Triggers acionam módulos corretos
   - Dependências são validadas
   - Múltiplos módulos convivem

---

## 🎯 Exemplo de Output Esperado

```
╔══════════════════════════════════════════════════════════════════════╗
║                   AEON V80 - SUITE DE TESTES                         ║
╚══════════════════════════════════════════════════════════════════════╝

======================================================================
Executando: test_sistema_focus.py
======================================================================

✓ Teste 1.1: Foco inicial deve ser None
  ✓ PASSOU
✓ Teste 1.2: lock_focus() deve travar foco
  ✓ PASSOU
✓ Teste 1.3: Com foco travado, comando vai direto para módulo
  Resultado: TestModule recebeu: comando teste 1
  ✓ PASSOU
... (mais testes)

============================================================
✅ TODOS OS TESTES DE FOCO PASSARAM!
============================================================

[... mais testes ...]

======================================================================
RESUMO DOS TESTES
======================================================================
✅ PASSOU - Sistema de Foco (lock/release)
✅ PASSOU - TypewriterModule
✅ PASSOU - Carregamento Dinâmico
✅ PASSOU - Code Rendering
✅ PASSOU - Roteamento de Comandos

======================================================================
Total: 5/5 testes passaram
======================================================================
```

---

## 🐛 Se Algo Falhar

### Erro: "ModuleNotFoundError"
```bash
# Certifique-se que está no diretório correto
cd d:\Dev\Aeon

# Rode novamente
python tests/test_all_modules.py
```

### Erro: "No module named 'xxx'"
```bash
# Instale as dependências
pip install customtkinter pyperclip pyautogui
```

### Teste falha com AssertionError
```bash
# Execute com mais detalhes
python -u tests/test_sistema_focus.py 2>&1 | more
```

---

## 🚀 Após Testes Passarem

1. **Execute o Aeon:**
   ```bash
   python AeonProject/main.py
   ```

2. **Teste as funcionalidades:**
   - Fale: "modo ditado" - Deve ativar TypewriterModule com foco travado
   - Fale: "sistema parar" - Deve desativar ditado
   - Fale: "crie um site" - DevFactory gera código formatado

3. **Monitore o console:**
   - Veja `🔒 MODO FOCO` quando ditado ativa
   - Veja `🔓 FOCO LIBERADO` quando ditado para

---

## 📈 Histórico de Testes

| Data | Status | Observações |
|------|--------|------------|
| 2026-01-19 | ✅ Todos | Suite criada e validada |

---

## 💡 Dicas

- Rode os testes **antes de fazer mudanças** para ter linha de base
- Se adicionar novo módulo, crie `test_novo_modulo.py`
- Testes são **independentes**, pode rodar em qualquer ordem
- Usa **mocks** quando necessário, não acessa rede

---

## 📝 Estrutura de Testes

```
tests/
├── test_sistema_focus.py       # ≈ 200ms
├── test_typewriter_module.py   # ≈ 150ms
├── test_module_loading.py      # ≈ 500ms
├── test_code_rendering.py      # ≈ 100ms
├── test_routing.py             # ≈ 300ms
├── test_all_modules.py         # Executor principal
├── README.md                   # Documentação completa
└── __init__.py
```

---

## ✨ Bom Testando!

Se todos os testes passam = **Seu Aeon V80 está pronto! 🚀**
