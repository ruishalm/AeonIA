# QUICK REFERENCE: Funções do V71 Mapeadas no Projeto Modular

## 📋 TABELA RÁPIDA

| Função V71 | Localização Modular | Tipo | Status |
|-----------|-------------------|------|--------|
| `check_deps()` | ❌ Removida | Init | Depreciada |
| `InstallMgr` | `main.py` + `modules/controle/` | Core | ✅ |
| `Brain` | `core/brain.py` | Core | ✅ |
| `SysMgr` | `core/config_manager.py` | Core | ✅ |
| `carregar_memoria()` | `ConfigManager.get_memory()` | Core | ✅ |
| `salvar_memoria()` | `ConfigManager._save_json()` | Core | ✅ |
| `adicionar_memoria()` | `ConfigManager.add_to_memory()` | Core | ✅ |
| `_edge_tts_save()` | `IOHandler.falar()` | Core | ✅ |
| `falar()` | `IOHandler.falar()` | Core | ✅ |
| `calar_boca()` | `IOHandler.calar_boca()` + Botão GUI | Core | ✅ |
| `limpar_arquivo_seguro()` | `IOHandler._limpar_seguro()` | Core | ✅ |
| `indexar_programas()` | `SistemaModule.indexar_programas()` | Módulo | ✅ |
| `processar_comando()` | `ModuleManager.route_command()` | Core | ✅ |
| "abre"/"iniciar" | `SistemaModule.process()` | Módulo | ✅ |
| "alarme"/"timer" | `RotinasModule.processar_alarme()` | Módulo | ✅ |
| "criar rotina" | `RotinasModule.process()` | Módulo | ✅ |
| "executar rotina" | `RotinasModule.executar_rotina()` | Módulo | ✅ |
| "tela"/"veja" | `VisionModule.process()` | Módulo | ✅ |
| "sair" | `SistemaModule.process()` | Módulo | ✅ |
| "conectar"/"online" | `ControleModule.process()` | Módulo | ✅ |
| "instalar offline" | `ControleModule.instalar_offline()` | Módulo | ✅ |
| "instalar pacote" | `SistemaModule.instalar_pacote()` | Módulo | ✅ |
| "calibrar microfone" | `ControleModule.process()` | Módulo | ✅ |
| `AeonGUI.__init__()` | `main.py - AeonGUI.__init__()` | GUI | ✅ |
| `chat_display()` | `AeonGUI.chat_display()` | GUI | ✅ |
| `log_display()` | Integrado em `chat_display()` | GUI | ✅ |
| `update_leds()` | `AeonGUI.update_leds()` | GUI | ✅ |
| `toggle_mode()` | `StatusManager.toggle_mode()` + `AeonGUI` | GUI | ✅ |
| `loop_voz()` | `AeonGUI.loop_voz()` | GUI | ✅ |
| `loop_alarm()` | `RotinasModule._monitor_alarm()` | Módulo | ✅ |
| `boot()` | `AeonGUI.boot()` | GUI | ✅ |
| `on_send()` | `AeonGUI.on_send()` | GUI | ✅ |
| TRIGGERS (lista) | `StatusManager.triggers` | Core | ✅ |
| LEDs (Cloud/Local/Hybrid) | `StatusManager.get_led_status()` | Core | ✅ |
| Modo CHAMAR/DIRETO | `StatusManager.operation_mode` | Core | ✅ |

---

## 🔍 PROCURANDO UMA FUNÇÃO?

### Se você quer modificar...

**Reconhecimento de voz:**
→ `AeonGUI.loop_voz()` em `main.py`

**Síntese de voz (TTS):**
→ `IOHandler.falar()` em `core/io_handler.py`

**Inteligência/Respostas:**
→ `Brain.pensar()` em `core/brain.py`

**Análise de imagens:**
→ `Brain.ver()` em `core/brain.py`

**Memória/Histórico:**
→ `ConfigManager` em `core/config_manager.py`

**Abertura de programas:**
→ `SistemaModule.process()` em `modules/sistema/sys_mod.py`

**Alarmes/Timers:**
→ `RotinasModule.processar_alarme()` em `modules/rotinas/rotinas_mod.py`

**LEDs/Status:**
→ `StatusManager` em `core/status_manager.py`

**Interface gráfica:**
→ `AeonGUI` em `main.py`

**Roteamento de comandos:**
→ `ModuleManager.route_command()` em `core/module_manager.py`

---

## 📝 COMO ADICIONAR UMA NOVA FUNCIONALIDADE?

### 1. **Se é uma funcionalidade CORE (cérebro, áudio, config):**
   → Modifique o arquivo em `core/`

### 2. **Se é uma funcionalidade ESPECIALIZADA (novo comando):**
   → Crie um novo módulo em `modules/`
   ```python
   from modules.base_module import AeonModule
   
   class MeuModulo(AeonModule):
       def __init__(self, core_context):
           super().__init__(core_context)
           self.name = "Meu Módulo"
           self.triggers = ["meu", "comando", "chave"]
       
       def process(self, command: str) -> str:
           if "meu" in command:
               return "Executei meu comando!"
           return ""
   ```

### 3. **O ModuleManager carregará automaticamente:**
   - Escaneia `modules/`
   - Encontra `*_mod.py`
   - Registra triggers

---

## 🧪 TESTANDO ALTERAÇÕES

### Test 1: Reconhecimento de voz
```
$ python main.py
(Fale um comando com o microfone)
```

### Test 2: Modo CHAMAR/DIRETO
```
Clique no botão "DIRETO" para alternar para "CHAMAR"
Agora tente falar algo SEM o trigger "aeon"
(Deve ser ignorado)
```

### Test 3: Alarme
```
"alarme em 10 segundos teste"
(Aguarde 10 segundos)
(Deve falar: "Atenção! teste")
```

### Test 4: Screenshot
```
"tire uma foto da tela"
(GUI deve analisar e descrever)
```

---

## 🐛 DEBUGGING

### Ver logs do Brain:
Modificar `core/brain.py` linha 8:
```python
def log_display(msg):
    print(f"[BRAIN] {msg}")  # Já mostra tudo
```

### Ver logs de todos os componentes:
Os componentes já printam com seus prefixos:
- `[BRAIN]` - Brain
- `[IO_HANDLER]` - IOHandler
- `[MOD_MANAGER]` - ModuleManager
- `[SISTEMA]` - SistemaModule

### Desabilitar um módulo temporariamente:
Renomear arquivo `*_mod.py` para `*_mod.py.bak`
O ModuleManager ignorará na próxima inicialização.

---

## ⚡ PERFORMANCE NOTES

- **Inicialização:** ~2-3 segundos (reconhecimento de voz init)
- **Resposta Brain (Cloud):** ~0.5-1s (Groq API)
- **Resposta Brain (Local):** ~1-3s (Ollama)
- **Síntese de voz:** ~0.1-0.5s (Edge-TTS) | ~0.5-1s (Piper)
- **Análise de imagem:** ~1-2s (Cloud) | ~2-5s (Local)

---

## 🔑 PALAVRAS-CHAVE IMPORTANTES

- **TRIGGERS:** Palavras que ativam um módulo
- **CORE_CONTEXT:** Dicionário com todos os componentes
- **AeonModule:** Classe base para módulos
- **ModuleManager:** Orquestrador de módulos
- **StatusManager:** Gerenciador de estado e LEDs
