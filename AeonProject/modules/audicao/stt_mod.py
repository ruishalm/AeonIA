import threading
import speech_recognition as sr
from modules.base_module import AeonModule

class STTModule(AeonModule):
    def __init__(self, core_context):
        super().__init__(core_context)
        self.name = "Audicao"
        self.triggers = ["ativar escuta", "ouvir", "parar escuta"]
        self.dependencies = ["gui", "io_handler"]
        
        self.recognizer = sr.Recognizer()
        self.listening = False
        self.thread = None

    def process(self, command: str) -> str:
        if "ativar" in command or "ouvir" in command:
            if not self.listening:
                self.listening = True
                self.thread = threading.Thread(target=self._listen_loop, daemon=True)
                self.thread.start()
                return "Microfone ativado. Pode falar."
            return "Já estou ouvindo."
        
        if "parar" in command:
            self.listening = False
            return "Microfone desativado."
        
        return ""

    def _listen_loop(self):
        """Loop infinito que ouve, transcreve e injeta no sistema."""
        gui = self.core_context.get("gui")
        mm = self.core_context.get("module_manager")
        
        with sr.Microphone() as source:
            # Calibragem rápida de ruído
            if gui: gui.add_message("Calibrando ruído...", "AUDIÇÃO")
            self.recognizer.adjust_for_ambient_noise(source, duration=1)
            
            while self.listening:
                try:
                    # Ouve (bloqueante por padrão, mas estamos em thread)
                    print("[AUDIÇÃO] Ouvindo...")
                    audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=10)
                    
                    # Transcreve (Google é rápido e grátis para online)
                    # Se quiser offline, pode mudar para: self.recognizer.recognize_whisper(audio)
                    texto = self.recognizer.recognize_google(audio, language="pt-BR")
                    
                    if texto:
                        print(f"[AUDIÇÃO] Ouvi: {texto}")
                        # MAGIA: Manda o texto para a GUI como se você tivesse digitado
                        # Isso ativa o Cérebro, salva no histórico e ativa módulos!
                        if gui:
                            # Usa o método after para thread-safety na GUI
                            gui.after(0, lambda t=texto: gui.entry_msg.insert(0, t))
                            gui.after(100, lambda: gui.send_message_event())
                            
                except sr.WaitTimeoutError:
                    pass # Ninguém falou nada
                except sr.UnknownValueError:
                    pass # Ruído não identificado
                except Exception as e:
                    print(f"[AUDIÇÃO] Erro: {e}")
                    # Se cair a internet, tenta offline (lógica futura)