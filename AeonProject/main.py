import customtkinter as ctk
import threading
import time
import datetime
import sys
import os
import re
import json
import psutil
from core.module_manager import ModuleManager
from core.config_manager import ConfigManager
from core.brain import Brain
from core.io_handler import IOHandler
from core.status_manager import StatusManager

# ==============================================================================
#                           CONFIGURAÇÕES DE TEMA (CYBERPUNK)
# ==============================================================================
C = {
    "bg": "#0d1117",           # Fundo Geral (Dark GitHub)
    "panel_bg": "#161b22",     # Fundo dos Painéis
    "accent_primary": "#58a6ff", # Azul Neon (Aeon)
    "accent_secondary": "#238636", # Verde Matrix (Sistema)
    "accent_alert": "#da3633",   # Vermelho Erro
    "text_main": "#c9d1d9",    # Texto Claro
    "text_dim": "#8b949e",     # Texto Escuro (Logs/Metadados)
    "code_bg": "#000000",      # Fundo do Code Block
    "user_bubble": "#1f6feb",  # Balão do Usuário
    "bot_bubble": "#21262d"    # Balão do Bot
}

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("dark-blue")

# ==============================================================================
#                           INTERFACE V80 (DASHBOARD)
# ==============================================================================

class AeonGUI(ctk.CTk):
    def __init__(self, module_manager=None, io_handler=None, status_manager=None, config_manager=None):
        super().__init__()
        
        self.module_manager = module_manager
        self.io_handler = io_handler
        self.status_manager = status_manager
        self.config_manager = config_manager
        
        # Configurações da Janela
        self.title("AEON V80 // MODULAR SYSTEM")
        self.geometry("1400x800")
        self.configure(fg_color=C["bg"])
        self.minsize(1200, 700)

        # Layout Principal: Grid 1x3 (Esquerda | Meio | Direita)
        self.grid_columnconfigure(0, weight=1, minsize=280) # System Deck
        self.grid_columnconfigure(1, weight=3, minsize=600) # Comm Hub (Chat)
        self.grid_columnconfigure(2, weight=1, minsize=320) # Workspace
        self.grid_rowconfigure(0, weight=1)

        self.setup_left_panel()
        self.setup_center_panel()
        self.setup_right_panel()

        # Inicia Threads de Monitoramento
        self.running = True
        threading.Thread(target=self.loop_vitals, daemon=True).start()
        threading.Thread(target=self.loop_voice, daemon=True).start()
        
        # Mensagem de Boas Vindas + Carrega Histórico
        self.add_message("Sistema Online. Módulos carregados.", "SISTEMA")
        
        # Carrega histórico anterior se existir
        if self.config_manager:
            history = self.config_manager.get_history()
            if history:
                self.add_message(f"📚 Histórico carregado: {len(history)} conversas anteriores", "SISTEMA")
                # Mostra últimas 3 conversas
                for conv in history[-3:]:
                    self.add_message(conv.get("user", "?"), "VOCÊ")
                    self.add_message(conv.get("aeon", ""), "AEON")


    # ==========================================================================
    # PAINEL ESQUERDO: SYSTEM DECK (Monitoramento & Módulos)
    # ==========================================================================
    def setup_left_panel(self):
        self.frame_left = ctk.CTkFrame(self, fg_color=C["panel_bg"], corner_radius=0)
        self.frame_left.grid(row=0, column=0, sticky="nsew", padx=(0,1), pady=0)
        
        # Título
        ctk.CTkLabel(self.frame_left, text="SYSTEM VITALS", font=("Consolas", 14, "bold"), text_color=C["text_dim"]).pack(pady=(20, 10), padx=20, anchor="w")

        # CPU Monitor
        self.lbl_cpu = ctk.CTkLabel(self.frame_left, text="CPU: 0%", font=("Consolas", 12), text_color=C["text_main"])
        self.lbl_cpu.pack(padx=20, anchor="w")
        self.bar_cpu = ctk.CTkProgressBar(self.frame_left, progress_color=C["accent_secondary"])
        self.bar_cpu.pack(padx=20, pady=(0, 15), fill="x")
        self.bar_cpu.set(0)

        # RAM Monitor
        self.lbl_ram = ctk.CTkLabel(self.frame_left, text="RAM: 0%", font=("Consolas", 12), text_color=C["text_main"])
        self.lbl_ram.pack(padx=20, anchor="w")
        self.bar_ram = ctk.CTkProgressBar(self.frame_left, progress_color=C["accent_primary"])
        self.bar_ram.pack(padx=20, pady=(0, 20), fill="x")
        self.bar_ram.set(0)

        # Separator
        ctk.CTkFrame(self.frame_left, height=2, fg_color="#30363d").pack(fill="x", padx=20, pady=10)

        # Módulos Ativos
        ctk.CTkLabel(self.frame_left, text="ACTIVE MODULES", font=("Consolas", 14, "bold"), text_color=C["text_dim"]).pack(pady=10, padx=20, anchor="w")
        
        self.scroll_modules = ctk.CTkScrollableFrame(self.frame_left, fg_color="transparent")
        self.scroll_modules.pack(fill="both", expand=True, padx=10, pady=10)

        # Carrega módulos do ModuleManager
        if self.module_manager:
            for module in self.module_manager.module_map.values():
                self.add_module_status(module.name, True)
        else:
            # Simulação
            self.add_module_status("Core Brain", True)
            self.add_module_status("DevFactory", True)

    def add_module_status(self, name, active):
        row = ctk.CTkFrame(self.scroll_modules, fg_color="transparent")
        row.pack(fill="x", pady=2)
        
        color = C["accent_secondary"] if active else C["accent_alert"]
        status_text = "ONLINE" if active else "OFFLINE"
        
        # LED Status
        canvas = ctk.CTkCanvas(row, width=10, height=10, bg=C["panel_bg"], highlightthickness=0)
        canvas.pack(side="left", padx=(5,10))
        canvas.create_oval(1, 1, 9, 9, fill=color, outline="")
        
        ctk.CTkLabel(row, text=name, font=("Consolas", 12), text_color=C["text_main"]).pack(side="left")
        ctk.CTkLabel(row, text=status_text, font=("Consolas", 10), text_color=C["text_dim"]).pack(side="right", padx=5)

    # ==========================================================================
    # PAINEL CENTRAL: COMMUNICATION HUB (Chat Inteligente)
    # ==========================================================================
    def setup_center_panel(self):
        self.frame_center = ctk.CTkFrame(self, fg_color=C["bg"], corner_radius=0)
        self.frame_center.grid(row=0, column=1, sticky="nsew")
        self.frame_center.grid_rowconfigure(1, weight=1)
        self.frame_center.grid_columnconfigure(0, weight=1)

        # ===== STATUS BAR COM LEDs =====
        self.status_bar = ctk.CTkFrame(self.frame_center, fg_color=C["panel_bg"], height=40)
        self.status_bar.grid(row=0, column=0, sticky="ew", padx=0, pady=0)
        
        ctk.CTkLabel(self.status_bar, text="STATUS", font=("Consolas", 10, "bold"), text_color=C["text_dim"]).pack(side="left", padx=10)
        
        # LEDs
        self.leds = {}
        for name in ["CLOUD", "LOCAL", "HYBRID"]:
            led_frame = ctk.CTkFrame(self.status_bar, fg_color="transparent")
            led_frame.pack(side="left", padx=8)
            
            canvas = ctk.CTkCanvas(led_frame, width=12, height=12, bg=C["panel_bg"], highlightthickness=0)
            canvas.pack(side="left", padx=(0,5))
            led_id = canvas.create_oval(1, 1, 11, 11, fill="#1a1a1a", outline="")
            self.leds[name] = (canvas, led_id)
            
            ctk.CTkLabel(led_frame, text=name, font=("Consolas", 9), text_color=C["text_dim"]).pack(side="left")

        # Área de Chat (Scrollable)
        self.chat_feed = ctk.CTkScrollableFrame(self.frame_center, fg_color="transparent")
        self.chat_feed.grid(row=1, column=0, sticky="nsew", padx=20, pady=20)

        # Área de Input
        self.input_container = ctk.CTkFrame(self.frame_center, fg_color=C["panel_bg"], height=60)
        self.input_container.grid(row=2, column=0, sticky="ew", padx=20, pady=(0, 20))
        
        self.entry_msg = ctk.CTkEntry(
            self.input_container, 
            placeholder_text="Digite um comando ou trigger...",
            font=("Consolas", 14),
            border_width=0,
            fg_color="transparent",
            text_color=C["text_main"]
        )
        self.entry_msg.pack(side="left", fill="both", expand=True, padx=15, pady=10)
        self.entry_msg.bind("<Return>", self.send_message_event)

        self.btn_mic = ctk.CTkButton(
            self.input_container, 
            text="🎤 MIC", 
            width=70, 
            fg_color=C["accent_primary"], 
            font=("Consolas", 12, "bold"),
            command=self.toggle_mic
        )
        self.btn_mic.pack(side="right", padx=10)
        
        # Atualiza LEDs iniciais
        self.update_leds()

    def add_message(self, text, sender="VOCÊ"):
        """
        O CORAÇÃO DA NOVA GUI.
        Renderiza mensagens detectando blocos de código (```).
        """
        # Container da mensagem
        msg_frame = ctk.CTkFrame(self.chat_feed, fg_color="transparent")
        msg_frame.pack(fill="x", pady=5)

        # Define alinhamento e cor
        if sender == "VOCÊ":
            align = "e" # East (Direita)
            bubble_color = C["user_bubble"]
            text_color = "white"
            anchor = "e"
        else: # AEON ou SISTEMA
            align = "w" # West (Esquerda)
            bubble_color = C["bot_bubble"]
            text_color = C["text_main"]
            anchor = "w"

        # Label do Remetente
        ctk.CTkLabel(msg_frame, text=sender, font=("Consolas", 10, "bold"), text_color=C["text_dim"]).pack(anchor=align, padx=5)

        # PARSER DE CÓDIGO (SPLIT POR ```)
        parts = text.split("```")
        
        for i, part in enumerate(parts):
            if not part.strip(): continue # Pula partes vazias

            if i % 2 == 0: 
                # ÍNDICE PAR = TEXTO NORMAL
                lbl = ctk.CTkLabel(
                    msg_frame, 
                    text=part.strip(), 
                    fg_color=bubble_color, 
                    corner_radius=12,
                    font=("Roboto", 14),
                    text_color=text_color,
                    wraplength=500,
                    justify="left"
                )
                lbl.pack(anchor=align, pady=2, padx=5, ipady=5, ipadx=10)
            
            else:
                # ÍNDICE ÍMPAR = BLOCO DE CÓDIGO
                # Remove primeira linha se for o nome da linguagem (ex: python)
                lines = part.strip().split('\n')
                if len(lines) > 0 and len(lines[0]) < 15 and " " not in lines[0]:
                    code_content = "\n".join(lines[1:])
                else:
                    code_content = part.strip()

                code_box = ctk.CTkTextbox(
                    msg_frame,
                    font=("Consolas", 13),
                    fg_color=C["code_bg"],
                    text_color="#3fb950", # Verde Hacker
                    border_color="#30363d",
                    border_width=1,
                    width=520,
                    height=min(len(code_content.split('\n')) * 20 + 20, 300), # Altura dinâmica
                    wrap="none"
                )
                code_box.insert("0.0", code_content)
                code_box.configure(state="disabled") # Read-only
                code_box.pack(anchor=align, pady=5, padx=5)

        # Scroll automático para o fim
        self.after(100, self.scroll_to_bottom)

    def scroll_to_bottom(self):
        try:
            self.chat_feed._parent_canvas.yview_moveto(1.0)
        except:
            pass

    def send_message_event(self, event=None):
        txt = self.entry_msg.get()
        if txt:
            self.add_message(txt, "VOCÊ")
            self.entry_msg.delete(0, "end")
            # Processa comando nos módulos
            if self.module_manager:
                threading.Thread(target=self.process_command, args=(txt,), daemon=True).start()

    def process_command(self, command):
        """Processa comando e retorna resposta, salvando no histórico"""
        try:
            # Tenta rotear para um módulo
            resposta = self.module_manager.route_command(command)
            if resposta:
                resposta_str = str(resposta)
                self.add_message(resposta_str, "AEON")
                # Salva no histórico
                if self.config_manager:
                    self.config_manager.add_to_history(command, resposta_str)
            else:
                # Se nenhum módulo respondeu, usa o Brain com contexto completo
                if self.module_manager.core_context.get("brain"):
                    brain = self.module_manager.core_context["brain"]
                    
                    # Constrói contexto: últimas 5 conversas
                    historico_txt = "HISTÓRICO DA CONVERSA:\n"
                    if self.config_manager:
                        hist = self.config_manager.get_history()
                        if hist:
                            # Últimas 5 conversas
                            for i, conv in enumerate(hist[-5:], 1):
                                user_msg = conv.get('user', '?')
                                aeon_msg = conv.get('aeon', '?')
                                historico_txt += f"{i}. Usuário: {user_msg}\n   Aeon: {aeon_msg}\n"
                        else:
                            historico_txt += "(Nenhuma conversa anterior)"
                    else:
                        historico_txt += "(Sem histórico disponível)"
                    
                    resposta = brain.pensar(command, historico_txt)
                    self.add_message(resposta, "AEON")
                    self.update_leds()
                    
                    # Salva no histórico
                    if self.config_manager:
                        self.config_manager.add_to_history(command, resposta)
        except Exception as e:
            self.add_message(f"Erro: {e}", "SISTEMA")

    def update_leds(self):
        """Atualiza status dos LEDs baseado na conexão"""
        try:
            brain = self.module_manager.core_context.get("brain")
            if not brain:
                return
            
            # Desliga todos
            for name, (canvas, led_id) in self.leds.items():
                canvas.itemconfig(led_id, fill="#1a1a1a")
            
            # Cloud
            if brain.online:
                self.leds["CLOUD"][0].itemconfig(self.leds["CLOUD"][1], fill=C["accent_primary"])
            
            # Local
            if brain.local_ready:
                self.leds["LOCAL"][0].itemconfig(self.leds["LOCAL"][1], fill=C["accent_secondary"])
            
            # Hybrid (ambos ativos)
            if brain.online and brain.local_ready:
                self.leds["HYBRID"][0].itemconfig(self.leds["HYBRID"][1], fill="#3fb950")
        except:
            pass

    def toggle_mic(self):
        self.btn_mic.configure(text="⏹️ STOP" if self.btn_mic.cget("text") == "🎤 MIC" else "🎤 MIC")

    # ==========================================================================
    # PAINEL DIREITO: WORKSPACE (Arquivos e Logs)
    # ==========================================================================
    def setup_right_panel(self):
        self.frame_right = ctk.CTkFrame(self, fg_color=C["panel_bg"], corner_radius=0)
        self.frame_right.grid(row=0, column=2, sticky="nsew", padx=(1,0), pady=0)

        # Tabs
        self.tabs = ctk.CTkTabview(self.frame_right, fg_color="transparent")
        self.tabs.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.tabs.add("WORKSPACE")
        self.tabs.add("LOGS")
        self.tabs.add("INFO")

        # Aba Workspace (Lista de Módulos)
        self.file_list = ctk.CTkTextbox(self.tabs.tab("WORKSPACE"), font=("Consolas", 12))
        self.file_list.pack(fill="both", expand=True)
        if self.module_manager:
            info = f"Módulos Carregados: {len(self.module_manager.module_map)}\n"
            info += f"Triggers: {len(self.module_manager.trigger_map)}\n\n"
            for name, module in self.module_manager.module_map.items():
                info += f"▸ {name} ({len(module.triggers)} triggers)\n"
            self.file_list.insert("end", info)
        else:
            self.file_list.insert("end", "> Aguardando módulos...\n")
        self.file_list.configure(state="disabled")

        # Aba Logs
        self.log_box = ctk.CTkTextbox(self.tabs.tab("LOGS"), font=("Consolas", 10), text_color=C["text_dim"])
        self.log_box.pack(fill="both", expand=True)
        self.log_box.insert("end", "[SYSTEM]: GUI V80 Dashboard Initialized.\n")

        # Aba Info
        self.info_box = ctk.CTkTextbox(self.tabs.tab("INFO"), font=("Consolas", 11), text_color=C["text_main"])
        self.info_box.pack(fill="both", expand=True)
        self.info_box.insert("end", "AEON V80 - Modular System\n\n" +
            "▸ Arquitetura: Plugin-based\n" +
            "▸ Módulos: Carregamento dinâmico\n" +
            "▸ Focus System: Roteamento exclusivo\n" +
            "▸ GUI: Dashboard 3-colunas Cyberpunk\n\n" +
            "Triggers disponíveis são roteados automaticamente.\n")
        self.info_box.configure(state="disabled")

    # ==========================================================================
    # LOOPS E UTILITÁRIOS
    # ==========================================================================
    def loop_vitals(self):
        while self.running:
            try:
                cpu = psutil.cpu_percent(interval=1)
                ram = psutil.virtual_memory().percent
                
                # Atualiza na Thread principal
                self.after(0, self.update_vitals, cpu, ram)
            except: 
                pass

    def update_vitals(self, cpu, ram):
        self.bar_cpu.set(cpu / 100)
        self.lbl_cpu.configure(text=f"CPU: {cpu:.0f}%")
        
        self.bar_ram.set(ram / 100)
        self.lbl_ram.configure(text=f"RAM: {ram:.0f}%")

        # Muda cor se estiver alto
        color_cpu = C["accent_alert"] if cpu > 80 else C["accent_secondary"]
        self.bar_cpu.configure(progress_color=color_cpu)

    def loop_voice(self):
        """Loop para processar entrada de voz"""
        while self.running:
            time.sleep(0.5)
            # Aqui entra a lógica do IOHandler para captar voz


# ==============================================================================
#                               MAIN
# ==============================================================================

if __name__ == "__main__":
    try:
        # 1. Configurações Iniciais
        print("Inicializando o Gerenciador de Configuração...")
        config_manager = ConfigManager()
        
        # 2. Status Manager
        print("Inicializando Status Manager...")
        status_manager = StatusManager()
        
        # 3. Componentes do Core
        print("Inicializando componentes do Core...")
        config = {
            "GROQ_KEY": "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",
            "model_txt_cloud": "llama-3.3-70b-versatile",
            "model_vis_cloud": "llama-3.2-11b-vision-preview",
            "model_txt_local": "llama3.2",
            "model_vis_local": "moondream"
        }
        installer = None
        brain = Brain(config=config, installer=installer)
        io_handler = IOHandler(config=config, installer=installer)
        
        # 4. Contexto do Core
        core_context = {
            "config_manager": config_manager,
            "brain": brain,
            "io_handler": io_handler,
            "installer": installer,
            "status_manager": status_manager
        }
        
        # 5. ModuleManager
        print("Carregando módulos de habilidade...")
        module_manager = ModuleManager(core_context)
        module_manager.load_modules()
        core_context["module_manager"] = module_manager
        
        # 6. GUI
        print("Iniciando Interface Gráfica...")
        app = AeonGUI(module_manager=module_manager, io_handler=io_handler, status_manager=status_manager, config_manager=config_manager)
        app.mainloop()
        
    except Exception as e:
        print(f"Erro ao inicializar Aeon: {e}")
        import traceback
        traceback.print_exc()
