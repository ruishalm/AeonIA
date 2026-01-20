import os
import datetime
from io import BytesIO
from typing import List, Dict
from PIL import ImageGrab

# Importa a classe base para garantir a conformidade da interface
from modules.base_module import AeonModule

class VisionModule(AeonModule):
    """
    Módulo responsável por capturar a tela e analisá-la.
    """
    def __init__(self, core_context):
        super().__init__(core_context)
        self.name = "Visão"
        self.triggers = ["tela", "veja", "analise a tela", "o que você vê"]
        
        # Define o caminho para salvar os snapshots dentro da estrutura do módulo
        self.snapshots_path = os.path.join("AeonProject", "modules", "visao", "snapshots")
        os.makedirs(self.snapshots_path, exist_ok=True)

    @property
    def dependencies(self) -> List[str]:
        """Visão depende de brain (LLM) para análise de imagens."""
        return ["brain"]

    @property
    def metadata(self) -> Dict[str, str]:
        """Metadados do módulo."""
        return {
            "version": "2.0.0",
            "author": "Aeon Core",
            "description": "Captura e analisa screenshots da tela usando IA"
        }

    def on_load(self) -> bool:
        """Inicializa o módulo - cria diretório de snapshots."""
        try:
            os.makedirs(self.snapshots_path, exist_ok=True)
            return True
        except Exception as e:
            print(f"[VisionModule] Erro ao carregar: {e}")
            return False

    def on_unload(self) -> bool:
        """Limpa recursos ao descarregar."""
        return True

    def process(self, command: str) -> str:
        """
        Captura a tela, salva um snapshot, envia para o cérebro analisar e retorna a descrição.
        """
        try:
            # Acessa os componentes do core através do core_context
            brain = self.core_context.get("brain")
            if not brain:
                return "O componente 'brain' não está disponível."

            # 1. Captura a tela
            screenshot = ImageGrab.grab()
            
            # 2. Salva o snapshot com um timestamp
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            snapshot_file = os.path.join(self.snapshots_path, f"snapshot_{timestamp}.png")
            screenshot.save(snapshot_file, "PNG")
            
            # 3. Prepara a imagem para análise (em memória)
            img_byte_arr = BytesIO()
            screenshot.save(img_byte_arr, format='PNG')
            img_bytes = img_byte_arr.getvalue()
            
            # 4. Envia para o cérebro e obtém a descrição
            self.core_context["io_handler"].falar("Analisando o que estou vendo...")
            description = brain.ver(img_bytes)
            
            # 5. Retorna a descrição para ser falada
            return description

        except Exception as e:
            error_message = f"Ocorreu um erro no módulo de visão: {e}"
            print(error_message) # Idealmente, usar um logger do core_context
            return error_message
