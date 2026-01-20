import subprocess
import webbrowser
import threading
from typing import List, Dict
from modules.base_module import AeonModule

class ControleModule(AeonModule):
    """
    Módulo para controlar o próprio Aeon:
    - Conectar/reconectar ao serviço de nuvem
    - Instalar modelos offline (Ollama)
    - Recalibrar microfone
    """
    def __init__(self, core_context):
        super().__init__(core_context)
        self.name = "Controle"
        self.triggers = [
            "conectar", "online", "reconectar",
            "instalar offline", "baixar modelos", "instalar ollama",
            "calibrar microfone", "ajustar áudio", "recalibrar"
        ]

    @property
    def dependencies(self) -> List[str]:
        """Controle depende de brain e io_handler."""
        return ["brain", "io_handler"]

    @property
    def metadata(self) -> Dict[str, str]:
        """Metadados do módulo."""
        return {
            "version": "2.0.0",
            "author": "Aeon Core",
            "description": "Controla conexão com nuvem, instalação offline e calibração de áudio"
        }

    def on_load(self) -> bool:
        """Inicializa o módulo - valida dependências."""
        brain = self.core_context.get("brain")
        io_handler = self.core_context.get("io_handler")
        if not brain or not io_handler:
            print("[ControleModule] Erro: dependências não encontradas")
            return False
        return True

    def on_unload(self) -> bool:
        """Limpa recursos ao descarregar."""
        return True

    def process(self, command: str) -> str:
        # Reconectar ao serviço de nuvem
        if "conectar" in command or "online" in command or "reconectar" in command:
            brain = self.core_context.get("brain")
            status_manager = self.core_context.get("status_manager")
            if brain:
                msg = brain.reconectar()
                if status_manager and brain.client and brain.online:
                    status_manager.update_cloud_status(True)
                return msg
            return "Cérebro não encontrado."

        # Instalar Ollama e baixar modelos
        if "instalar offline" in command or "baixar modelos" in command or "instalar ollama" in command:
            return self.instalar_offline()

        # Recalibrar microfone
        if "calibrar microfone" in command or "ajustar áudio" in command or "recalibrar" in command:
            io_handler = self.core_context.get("io_handler")
            if io_handler:
                msg = "Entendido. Silêncio por 3 segundos para recalibração."
                io_handler.recalibrar_mic()
                return msg
            return "IO Handler não encontrado."

        return ""

    def instalar_offline(self) -> str:
        """Instala Ollama e baixa modelos de forma offline em thread separada."""
        installer = self.core_context.get("installer")
        brain = self.core_context.get("brain")
        io_handler = self.core_context.get("io_handler")
        status_manager = self.core_context.get("status_manager")

        def install_thread():
            if not installer.verificar_ollama():
                if io_handler:
                    io_handler.falar("Ollama não encontrado. Tentando instalar...")
                
                try:
                    subprocess.run(["winget", "install", "Ollama.Ollama"], check=True)
                    if io_handler:
                        io_handler.falar("Ollama instalado com sucesso.")
                except Exception:
                    if io_handler:
                        io_handler.falar("Erro ao instalar Ollama. Abri o site de downloads.")
                    webbrowser.open("https://ollama.com/download")
                    return

            # Baixar modelos
            if io_handler:
                io_handler.falar("Baixando modelos de IA. Pode demorar alguns minutos...")
            
            subprocess.Popen("ollama pull llama3.2")
            subprocess.Popen("ollama pull moondream")

            # Atualizar status
            brain.local_ready = True
            if status_manager:
                status_manager.update_local_status(True)
            
            if io_handler:
                io_handler.falar("Modelos baixados! Agora estou funcionando offline.")

        threading.Thread(target=install_thread, daemon=True).start()
        return "Iniciando instalação offline. Pode levar alguns minutos..."
