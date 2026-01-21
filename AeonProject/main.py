import customtkinter as ctk
import psutil
import threading
import sys
import os

# Ajusta caminho para encontrar os módulos
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.module_manager import ModuleManager
from core.brain import Brain
from core.io_handler import IOHandler
from core.config_manager import ConfigManager
from core.context_manager import ContextManager 

# CONFIGURAÇÕES DE TEMA (CYBERPUNK)
C = {
    "bg": "#0d1117", "panel_bg": "#161b22", "accent_primary": "#58a6ff", 
    "accent_secondary": "#238636", "accent_alert": "#da3633", "text_main": "#c9d1d9", 
    "text_dim": "#8b949e", "code_bg": "#000000", "user_bubble": "#1f6feb", "bot_bubble": "#21262d"
}

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("dark-blue")

class AeonGUI(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # 1. INICIALIZAÇÃO DO CORE
        self.config_manager = ConfigManager()
        cfg = getattr(self.config_manager, 'config', {}) # Proteção contra falha de config
        self.io_handler = IOHandler(cfg, None)
        self.brain = Brain(cfg, None)
        self.context_manager = ContextManager() 
        
        self.core_context = {
            "config_manager": self.config_manager,
            "io_handler": self.io_handler,
            "brain": self.brain,
            "context": self.context_manager,
            "gui": self
        }

        self.module_manager = ModuleManager(self.core_context)
        self.core_context["module_manager"] = self.module_manager
        self.module_manager.load_modules()

        # 2. CONFIGURAÇÃO DA JANELA
        self.title("AEON V80 // MODULAR SYSTEM")
        self.geometry("1200x700")
        self.configure(fg_color=C["bg"])
        self.minsize(1000, 600)

        self.grid_columnconfigure(0, weight=1, minsize=250) 
        self.grid_columnconfigure(1, weight=3, minsize=500) 
        self.grid_columnconfigure(2, weight=1, minsize=300) 
        self.grid_rowconfigure(0, weight=1)

        self.setup_left_panel()
        self.setup_center_panel()
        self.setup_right_panel()

        self.running = True
        threading.Thread(target=self.loop_vitals, daemon=True).start()
        
        self.add_message("Sistema Online. V80 Estabilizada.", "SISTEMA")
        self.update_module_list()

    # --- PAINEL ESQUERDO (LEDS ATIVOS) ---
    def setup_left_panel(self):
        self.frame_left = ctk.CTkFrame(self, fg_color=C["panel_bg"], corner_radius=0)
        self.frame_left.grid(row=0, column=0, sticky="nsew", padx=(0,1), pady=0)
        
        ctk.CTkLabel(self.frame_left, text="SYSTEM STATUS", font=("Consolas", 14, "bold"), text_color=C["text_dim"]).pack(pady=(20, 15), padx=20, anchor="w")

        # Container dos LEDs
        self.status_frame = ctk.CTkFrame(self.frame_left, fg_color="transparent")
        self.status_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        self.led_online = self._create_led(self.status_frame, "NUVEM (GROQ)", C["accent_alert"])
        self.led_online.pack(side="top", fill="x", pady=2)
        
        self.led_local = self._create_led(self.status_frame, "NEURAL (LOCAL)", C["accent_alert"])
        self.led_local.pack(side="top", fill="x", pady=2)

        ctk.CTkFrame(self.frame_left, height=2, fg_color="#30363d").pack(fill="x", padx=20, pady=10)
        
        self.lbl_cpu = ctk.CTkLabel(self.frame_left, text="CPU: 0%", font=("Consolas", 12), text_color=C["text_main"])
        self.lbl_cpu.pack(padx=20, anchor="w")
        self.bar_cpu = ctk.CTkProgressBar(self.frame_left, progress_color=C["accent_secondary"])
        self.bar_cpu.pack(padx=20, pady=(0, 15), fill="x")
        
        self.lbl_ram = ctk.CTkLabel(self.frame_left, text="RAM: 0%", font=("Consolas", 12), text_color=C["text_main"])
        self.lbl_ram.pack(padx=20, anchor="w")
        self.bar_ram = ctk.CTkProgressBar(self.frame_left, progress_color=C["accent_primary"])
        self.bar_ram.pack(padx=20, pady=(0, 20), fill="x")

        ctk.CTkFrame(self.frame_left, height=2, fg_color="#30363d").pack(fill="x", padx=20, pady=10)
        ctk.CTkLabel(self.frame_left, text="ACTIVE MODULES", font=("Consolas", 14, "bold"), text_color=C["text_dim"]).pack(pady=10, padx=20, anchor="w")
        
        self.scroll_modules = ctk.CTkScrollableFrame(self.frame_left, fg_color="transparent")
        self.scroll_modules.pack(fill="both", expand=True, padx=10, pady=10)

    def _create_led(self, parent, text, color):
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        canvas = ctk.CTkCanvas(frame, width=12, height=12, bg=C["panel_bg"], highlightthickness=0)
        canvas.pack(side="left", padx=(0, 10))
        led_id = canvas.create_oval(2, 2, 10, 10, fill=color, outline="")
        label = ctk.CTkLabel(frame, text=text, font=("Consolas", 11, "bold"), text_color=C["text_dim"])
        label.pack(side="left")
        frame.canvas = canvas
        frame.led = led_id
        return frame

    def update_module_list(self):
        for widget in self.scroll_modules.winfo_children():
            widget.destroy()
        try:
            modules = self.module_manager.get_loaded_modules()
            for mod in modules:
                self.add_module_status(mod.name, True)
        except: pass

    def add_module_status(self, name, active):
        row = ctk.CTkFrame(self.scroll_modules, fg_color="transparent")
        row.pack(fill="x", pady=2)
        color = C["accent_secondary"] if active else C["accent_alert"]
        status_text = "ONLINE" if active else "OFFLINE"
        canvas = ctk.CTkCanvas(row, width=10, height=10, bg=C["panel_bg"], highlightthickness=0)
        canvas.pack(side="left", padx=(5,10))
        canvas.create_oval(1, 1, 9, 9, fill=color, outline="")
        ctk.CTkLabel(row, text=name, font=("Consolas", 12), text_color=C["text_main"]).pack(side="left")
        ctk.CTkLabel(row, text=status_text, font=("Consolas", 10), text_color=C["text_dim"]).pack(side="right", padx=5)

    # --- PAINEL CENTRAL ---
    def setup_center_panel(self):
        self.frame_center = ctk.CTkFrame(self, fg_color=C["bg"], corner_radius=0)
        self.frame_center.grid(row=0, column=1, sticky="nsew")
        self.frame_center.grid_rowconfigure(0, weight=1)
        self.frame_center.grid_columnconfigure(0, weight=1)

        self.chat_feed = ctk.CTkScrollableFrame(self.frame_center, fg_color="transparent")
        self.chat_feed.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)

        self.input_container = ctk.CTkFrame(self.frame_center, fg_color=C["panel_bg"], height=60)
        self.input_container.grid(row=1, column=0, sticky="ew", padx=20, pady=(0, 20))
        
        self.entry_msg = ctk.CTkEntry(self.input_container, placeholder_text="Comando...", font=("Consolas", 14), border_width=0, fg_color="transparent", text_color=C["text_main"])
        self.entry_msg.pack(side="left", fill="both", expand=True, padx=15, pady=10)
        self.entry_msg.bind("<Return>", self.send_message_event)

        self.btn_mic = ctk.CTkButton(self.input_container, text="MIC", width=60, fg_color=C["accent_primary"], font=("Consolas", 12, "bold"), command=self.toggle_mic)
        self.btn_mic.pack(side="right", padx=10)

    def add_message(self, text, sender="VOCÊ"):
        msg_frame = ctk.CTkFrame(self.chat_feed, fg_color="transparent")
        msg_frame.pack(fill="x", pady=5)
        align, bubble_color, text_color = ("e", C["user_bubble"], "white") if sender == "VOCÊ" else ("w", C["bot_bubble"], C["text_main"])

        ctk.CTkLabel(msg_frame, text=sender, font=("Consolas", 10, "bold"), text_color=C["text_dim"]).pack(anchor=align, padx=5)

        parts = text.split("```")
        for i, part in enumerate(parts):
            if not part.strip(): continue
            if i % 2 == 0:
                ctk.CTkLabel(msg_frame, text=part.strip(), fg_color=bubble_color, corner_radius=12, font=("Roboto", 14), text_color=text_color, wraplength=450, justify="left").pack(anchor=align, pady=2, padx=5, ipady=5, ipadx=10)
            else:
                code_box = ctk.CTkTextbox(msg_frame, font=("Consolas", 13), fg_color=C["code_bg"], text_color="#3fb950", border_color="#30363d", border_width=1, width=480, height=min(len(part.split('\n')) * 20 + 20, 300), wrap="none")
                code_box.insert("0.0", part.strip())
                code_box.configure(state="disabled")
                code_box.pack(anchor=align, pady=5, padx=5)
        self.after(100, lambda: self.chat_feed._parent_canvas.yview_moveto(1.0))

    def send_message_event(self, event=None):
        txt = self.entry_msg.get()
        if txt:
            self.add_message(txt, "VOCÊ")
            self.entry_msg.delete(0, "end")
            threading.Thread(target=self.process_in_background, args=(txt,), daemon=True).start()

    def process_in_background(self, txt):
        try:
            response = self.module_manager.route_command(txt)
            self.after(0, lambda: self.add_message(response, "AEON"))
            self.after(0, lambda: self.io_handler.falar(response))
        except Exception as e:
            self.after(0, lambda: self.add_message(f"Erro Crítico: {e}", "SISTEMA"))

    def toggle_mic(self):
        # Agora manda o comando para o stt_mod
        threading.Thread(target=self.process_in_background, args=("ativar escuta",), daemon=True).start()
        self.btn_mic.configure(fg_color=C["accent_secondary"])

    # --- PAINEL DIREITO ---
    def setup_right_panel(self):
        self.frame_right = ctk.CTkFrame(self, fg_color=C["panel_bg"], corner_radius=0)
        self.frame_right.grid(row=0, column=2, sticky="nsew", padx=(1,0), pady=0)
        self.tabs = ctk.CTkTabview(self.frame_right, fg_color="transparent")
        self.tabs.pack(fill="both", expand=True, padx=10, pady=10)
        self.tabs.add("WORKSPACE")
        self.tabs.add("LOGS")

    # --- LOOP DE VITAIS ---
    def loop_vitals(self):
        while self.running:
            try:
                cpu = psutil.cpu_percent(interval=1)
                ram = psutil.virtual_memory().percent
                self.after(0, self.update_vitals, cpu, ram)
            except: pass

    def update_vitals(self, cpu, ram):
        self.bar_cpu.set(cpu / 100)
        self.lbl_cpu.configure(text=f"CPU: {cpu}%")
        self.bar_ram.set(ram / 100)
        self.lbl_ram.configure(text=f"RAM: {ram}%")
        
        # Atualiza LEDs
        if hasattr(self, 'brain') and self.brain:
            cor_online = C["accent_primary"] if self.brain.online else C["accent_alert"]
            cor_local = C["accent_secondary"] if self.brain.local_ready else C["accent_alert"]
            self.led_online.canvas.itemconfig(self.led_online.led, fill=cor_online)
            self.led_local.canvas.itemconfig(self.led_local.led, fill=cor_local)

if __name__ == "__main__":
    app = AeonGUI()
    app.mainloop()