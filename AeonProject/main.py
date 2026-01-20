import customtkinter as ctk
import threading
import speech_recognition as sr
import time
import os
import json
import re

# Importando os novos componentes da arquitetura
from core.brain import Brain
from core.io_handler import IOHandler
from core.module_manager import ModuleManager
from core.config_manager import ConfigManager
from core.status_manager import StatusManager

# A classe Installer do aeon.py original, adaptada para o novo contexto
# Em uma refatoração completa, isso também poderia ser seu próprio arquivo em core/
class InstallMgr:
    def __init__(self, config_manager):
        self.config_manager = config_manager
        # O ideal seria que os caminhos do Piper viessem do config_manager
        self.piper_dir = os.path.join("AeonProject", "piper_tts")
        self.piper_exe = os.path.join(self.piper_dir, "piper", "piper.exe")
        self.voice_model = os.path.join(self.piper_dir, "pt_BR-faber-medium.onnx")

    def verificar_ollama(self):
        # Esta é uma simplificação. A lógica real está no aeon.py
        return True 

    def verificar_piper(self):
        return os.path.exists(self.piper_exe) and os.path.exists(self.voice_model)


# --- INTERFACE GRÁFICA (Adaptada do aeon.py) ---

class AeonGUI(ctk.CTk):
    def __init__(self, module_manager, io_handler, status_manager):
        super().__init__()
        
        self.module_manager = module_manager
        self.io_handler = io_handler
        self.status_manager = status_manager
        self.core_context = module_manager.core_context

        self.title("Aeon Modular")
        self.geometry("500x700")
        ctk.set_appearance_mode("Dark")
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # --- STATUS BAR COM LEDs ---
        self.status_frame = ctk.CTkFrame(self, fg_color="#080808", height=50, corner_radius=0)
        self.status_frame.grid(row=0, column=0, sticky="ew")
        
        # Modo DIRETO/CHAMAR
        mode_label = ctk.CTkLabel(self.status_frame, text="Modo:", font=("Arial", 10, "bold"))
        mode_label.pack(side="left", padx=10, pady=5)
        
        self.mode_button = ctk.CTkButton(
            self.status_frame, text="DIRETO", width=60, fg_color="#00cc00", 
            font=("Arial", 10, "bold"), command=self.toggle_mode
        )
        self.mode_button.pack(side="left", padx=2)
        
        # LEDs de Status
        led_label = ctk.CTkLabel(self.status_frame, text="Status:", font=("Arial", 10, "bold"))
        led_label.pack(side="left", padx=(20, 10), pady=5)
        
        self.led_cloud = self._criar_led("CLOUD")
        self.led_local = self._criar_led("LOCAL")
        self.led_hybrid = self._criar_led("HYBRID")
        
        # Registrar callback para atualizar status
        self.status_manager.on_status_change = self.update_leds

        # --- CHAT BOX ---
        self.chat_box = ctk.CTkTextbox(self, font=("Consolas", 11), state="disabled")
        self.chat_box.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        
        self.chat_box.tag_config("user", foreground="cyan")
        self.chat_box.tag_config("bot", foreground="white")
        self.chat_box.tag_config("sys", foreground="yellow")
        self.chat_box.tag_config("err", foreground="red")
        self.chat_box.tag_config("code_label", foreground="#888888", font=("Arial", 9))
        self.chat_box.tag_config("code", foreground="#00ff00", font=("Courier", 10))

        # --- INPUT FRAME ---
        input_frame = ctk.CTkFrame(self, fg_color="#111111", corner_radius=10)
        input_frame.grid(row=2, column=0, padx=5, pady=(0, 5), sticky="ew")

        self.input_entry = ctk.CTkEntry(input_frame, placeholder_text="Digite um comando...", font=("Arial", 11))
        self.input_entry.pack(side="left", fill="x", expand=True, padx=5, pady=5)
        self.input_entry.bind("<Return>", self.on_send)

        ctk.CTkButton(input_frame, text="OK", width=40, fg_color="#b30000", font=("Arial", 10), command=self.on_send).pack(side="right", padx=2)
        ctk.CTkButton(input_frame, text="XIU", width=40, fg_color="#ff5555", hover_color="#990000", font=("Arial", 10), command=self.mute).pack(side="right", padx=2)

        # Inicia o loop de escuta em uma thread separada
        threading.Thread(target=self.loop_voz, daemon=True).start()
        threading.Thread(target=self.boot, daemon=True).start()

    def _criar_led(self, label: str):
        """Cria um indicador LED na status bar."""
        frame = ctk.CTkFrame(self.status_frame, fg_color="transparent")
        frame.pack(side="left", padx=10)
        
        lbl = ctk.CTkLabel(frame, text=label, font=("Arial", 9, "bold"), text_color="#777777")
        lbl.pack()
        
        canvas = ctk.CTkCanvas(frame, width=15, height=15, bg="#080808", highlightthickness=0)
        canvas.pack()
        
        led = canvas.create_oval(3, 3, 13, 13, fill="#1a1a1a", outline="")
        return (canvas, led)

    def update_leds(self):
        """Atualiza o estado dos LEDs baseado no status do sistema."""
        led_status = self.status_manager.get_led_status()
        
        colors = {
            "on_cloud": "#0088ff",
            "on_local": "#ffaa00",
            "on_hybrid": "#00ff00",
            "off": "#1a1a1a"
        }
        
        # Cloud
        cloud_color = colors["on_cloud"] if led_status["cloud"] == "on" else colors["off"]
        self.led_cloud[0].itemconfig(self.led_cloud[1], fill=cloud_color)
        
        # Local
        local_color = colors["on_local"] if led_status["local"] == "on" else colors["off"]
        self.led_local[0].itemconfig(self.led_local[1], fill=local_color)
        
        # Hybrid
        hybrid_color = colors["on_hybrid"] if led_status["hybrid"] == "on" else colors["off"]
        self.led_hybrid[0].itemconfig(self.led_hybrid[1], fill=hybrid_color)

    def toggle_mode(self):
        """Alterna entre DIRETO e CHAMAR."""
        new_mode = self.status_manager.toggle_mode()
        color = "#e6b800" if new_mode == "CHAMAR" else "#00cc00"
        self.mode_button.configure(fg_color=color, text=new_mode)
        self.chat_display(f"Modo: {new_mode}", "SISTEMA", "sys")

    def mute(self):
        """Silencia o assistente."""
        self.io_handler.parar_fala = True
        self.chat_display(">> SILÊNCIO.", "SISTEMA", "err")

    def boot(self):
        """Inicialização do sistema."""
        time.sleep(1)
        self.chat_display("Aeon Modular Online.", "SISTEMA", "sys")
        self.update_leds()

    def on_send(self, event=None):
        text = self.input_entry.get()
        if not text:
            return
        self.input_entry.delete(0, "end")
        self.chat_display(text, "VOCÊ", "user")
        
        # Roteia o comando através do ModuleManager
        threading.Thread(target=self.process_command_thread, args=(text,)).start()

    def process_command_thread(self, command):
        """Processa um comando verificando triggers em modo CHAMAR."""
        status_manager = self.status_manager
        
        # Em modo CHAMAR, verifica se tem trigger
        if status_manager.is_chamar_mode():
            if not status_manager.has_trigger(command):
                return  # Ignora comandos sem trigger em modo CHAMAR
        
        response = self.module_manager.route_command(command)
        if response:
            self.chat_display(response, "AEON", "bot")
            self.io_handler.falar(response)

    def chat_display(self, msg, sender, tag="bot"):
        """
        Exibe mensagem no chat.
        Se conter blocos de código (```), renderiza formatado.
        """
        self.chat_box.configure(state="normal")
        
        # Parsear msg procurando blocos de código
        self._render_message(msg, sender, tag)
        
        self.chat_box.configure(state="disabled")
        self.chat_box.see("end")

    def _render_message(self, msg: str, sender: str, tag: str):
        """
        Renderiza mensagem, detectando e formatando blocos de código.
        
        Procura por: ` ``` [language] ... ``` `
        """
        # Inserir cabeçalho
        self.chat_box.insert("end", f"[{sender}]: ", tag)
        
        # Procurar por blocos de código (```...```)
        pattern = r"```(\w*)\n(.*?)\n```"
        
        # Split da mensagem em partes (código e texto)
        parts = re.split(pattern, msg, flags=re.DOTALL)
        
        # Se não achou blocos de código, apenas insere texto normal
        if len(parts) == 1:
            self.chat_box.insert("end", msg + "\n\n", tag)
            return
        
        # Processar partes (alternando entre texto e código)
        for i, part in enumerate(parts):
            if i == 0:  # Texto antes do primeiro bloco
                if part.strip():
                    self.chat_box.insert("end", part + "\n\n", tag)
            elif i % 3 == 1:  # Language identifier
                continue
            elif i % 3 == 2:  # Código
                language = parts[i-1] if i >= 1 else "python"
                # Inserir rótulo de linguagem
                self.chat_box.insert("end", f"┌─ {language} ─────\n", "code_label")
                # Inserir código
                self.chat_box.insert("end", part + "\n", "code")
                # Fechar bloco
                self.chat_box.insert("end", "└─────────────\n\n", "code_label")
            else:  # Texto após código
                if part.strip():
                    self.chat_box.insert("end", part + "\n\n", tag)

    def loop_voz(self):
        recognizer = sr.Recognizer()
        recognizer.pause_threshold = 0.8
        
        with sr.Microphone() as source:
            self.chat_display("Microfone calibrando, aguarde...", "SISTEMA", "sys")
            recognizer.adjust_for_ambient_noise(source, duration=2)
            self.chat_display("Microfone pronto.", "SISTEMA", "sys")
            
            while True:
                try:
                    audio = recognizer.listen(source, timeout=5, phrase_time_limit=15)
                    command = recognizer.recognize_google(audio, language="pt-BR")
                    
                    self.chat_display(command, "VOCÊ (Voz)", "user")
                    # Roteia o comando de voz
                    self.process_command_thread(command)

                except sr.UnknownValueError:
                    continue # Ignora se não entendeu nada
                except sr.WaitTimeoutError:
                    continue # Ignora se não houve fala
                except Exception as e:
                    print(f"[VOICE_LOOP] Erro: {e}")
                    time.sleep(1)


if __name__ == "__main__":
    # 1. Inicializa o Gerenciador de Configuração
    print("Inicializando o Gerenciador de Configuração...")
    config_manager = ConfigManager()
    
    # 2. Inicializa o Status Manager (modo, LEDs, triggers)
    print("Inicializando Status Manager...")
    status_manager = StatusManager()
    
    # 3. Inicializa os componentes do Core
    print("Inicializando componentes do Core...")
    # Passamos o config_manager para os componentes que precisam de acesso direto a dados
    installer = InstallMgr(config_manager)
    brain = Brain(config=config_manager.system_data, installer=installer)
    io_handler = IOHandler(config=config_manager.system_data, installer=installer)
    
    # Atualizar status inicial do Brain
    status_manager.update_cloud_status(brain.online)
    status_manager.update_local_status(brain.local_ready)
    
    # 4. Cria o Contexto do Core
    core_context = {
        "config_manager": config_manager,
        "brain": brain,
        "io_handler": io_handler,
        "installer": installer,
        "status_manager": status_manager
    }
    
    # 5. Inicializa e carrega o Gerenciador de Módulos
    print("Carregando módulos de habilidade...")
    module_manager = ModuleManager(core_context)
    module_manager.load_modules()
    core_context["module_manager"] = module_manager
    
    # 6. Inicializa a Interface Gráfica
    print("Iniciando Interface Gráfica...")
    app = AeonGUI(module_manager=module_manager, io_handler=io_handler, status_manager=status_manager)
    
    # 7. Inicia o loop principal da aplicação
    app.mainloop()
