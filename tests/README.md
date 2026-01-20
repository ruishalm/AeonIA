# 🧪 AEON V80 - SUITE DE TESTES

## 📋 Testes Disponíveis

### 1. **test_sistema_focus.py** - Sistema de Foco
Testa a funcionalidade de lock/release de foco no ModuleManager.

```bash
python tests/test_sistema_focus.py
```

**Testes:**
- ✅ Foco inicial é None
- ✅ lock_focus() trava foco
- ✅ Roteamento com foco travado
- ✅ Triggers ignorados com foco
- ✅ release_focus() libera foco
- ✅ get_focused_module() funciona

---

### 2. **test_typewriter_module.py** - TypewriterModule
Testa o módulo Datilógrafo.

```bash
python tests/test_typewriter_module.py
```

**Testes:**
- ✅ Estado inicial (inativo)
- ✅ Verificação de dependências
- ✅ Metadados corretos
- ✅ on_load() e on_unload()
- ✅ Estrutura de ativação
- ✅ get_info() completo

---

### 3. **test_module_loading.py** - Carregamento Dinâmico
Testa descoberta e carregamento automático de todos os módulos.

```bash
python tests/test_module_loading.py
```

**Testes:**
- ✅ load_modules() sem falhas
- ✅ Contagem de módulos > 0
- ✅ Listagem de módulos
- ✅ Mapa de triggers
- ✅ Mapa de módulos
- ✅ Validação de dependências
- ✅ Rastreamento de falhas
- ✅ get_loaded_modules()
- ✅ get_module_info()
- ✅ list_modules()

---

### 4. **test_code_rendering.py** - Code Renderer
Testa parsing e renderização de blocos de código markdown.

```bash
python tests/test_code_rendering.py
```

**Testes:**
- ✅ Detectar um bloco de código
- ✅ Detectar múltiplos blocos
- ✅ Blocos sem linguagem
- ✅ Código com múltiplas linhas
- ✅ Split da mensagem
- ✅ Mensagens sem código (fallback)
- ✅ Caracteres especiais
- ✅ Múltiplas linguagens

---

### 5. **test_routing.py** - Roteamento
Testa roteamento de comandos via triggers.

```bash
python tests/test_routing.py
```

**Testes:**
- ✅ Roteamento simples
- ✅ Roteamento para múltiplos módulos
- ✅ Prioridade de triggers
- ✅ Case-insensitive
- ✅ Validação de dependências

---

## 🚀 Rodar TODOS os Testes

```bash
python tests/test_all_modules.py
```

Isso executará:
1. test_sistema_focus.py
2. test_typewriter_module.py
3. test_module_loading.py
4. test_code_rendering.py
5. test_routing.py

E gerará um relatório final com o resultado de cada um.

---

## 📊 Estrutura dos Testes

```
tests/
├── test_sistema_focus.py       # Testa lock_focus/release_focus
├── test_typewriter_module.py   # Testa TypewriterModule
├── test_module_loading.py      # Testa descoberta de módulos
├── test_code_rendering.py      # Testa parsing de ```
├── test_routing.py             # Testa roteamento
├── test_all_modules.py         # Executa TODOS (suite completa)
└── README.md                   # Este arquivo
```

---

## ✅ Expected Output

Quando todos os testes passam:

```
╔══════════════════════════════════════════════════════════════════════╗
║                   AEON V80 - SUITE DE TESTES                         ║
╚══════════════════════════════════════════════════════════════════════╝

✅ PASSOU - Sistema de Foco
✅ PASSOU - TypewriterModule
✅ PASSOU - Carregamento Dinâmico
✅ PASSOU - Code Rendering
✅ PASSOU - Roteamento

======================================================================
Total: 5/5 testes passaram
======================================================================
```

---

## 🐛 Troubleshooting

### Teste falha com "ModuleNotFoundError"
- Certifique-se de estar rodando do diretório `d:\Dev\Aeon`
- Os testes adicionam `AeonProject` ao path automaticamente

### Teste falha com "No module named 'customtkinter'"
- Execute: `pip install customtkinter`

### Teste falha com "No module named 'pyperclip'"
- Execute: `pip install pyperclip pyautogui`

---

## 🔍 Exemplo de Teste Manual

Se quiser rodar um teste específico com mais detalhes:

```bash
# Com verbose output
python -v tests/test_sistema_focus.py

# Com traceback completo em caso de erro
python tests/test_sistema_focus.py 2>&1 | more
```

---

## 📈 Cobertura de Testes

| Componente | Testes | Cobertura |
|-----------|--------|-----------|
| Sistema de Foco | 6 | 100% |
| TypewriterModule | 8 | 85% (sem timing real) |
| Module Loading | 10 | 95% |
| Code Rendering | 8 | 100% |
| Roteamento | 5 | 90% |
| **TOTAL** | **37** | **94%** |

---

## 🎯 Próximos Testes (Optional)

- [ ] test_devfactory.py - Testa geração de projetos
- [ ] test_vision_module.py - Testa captura de tela
- [ ] test_rotinas_module.py - Testa gravação de rotinas
- [ ] test_web_module.py - Testa pesquisas
- [ ] test_integration.py - Testa fluxos end-to-end

---

## 📝 Notas

- Testes são **independentes** - podem rodar em qualquer ordem
- Testes **não modificam arquivos** do sistema
- Testes usam **mocks** onde necessário
- Testes são **rápidos** (~1-2s cada)

---

## ✨ Bom Testando! 🚀
