from io import BytesIO
from modules.base_module import AeonModule

# SAFE IMPORT: Impede que o sistema crashe se faltar a lib
try:
    import pyautogui
    VISAO_AVAILABLE = True
except ImportError:
    VISAO_AVAILABLE = False

class VisaoModule(AeonModule):
    def __init__(self, core_context):
        super().__init__(core_context)
        self.name = "Visao"
        self.triggers = ["veja isso", "leia a tela", "o que está na tela", "analise a imagem"]
        self.dependencies = ["brain", "context"]

    def check_dependencies(self):
        # Verifica se as libs externas estão instaladas
        if not VISAO_AVAILABLE:
            print("[VISAO] Erro: 'pyautogui' não instalado. Rode: pip install pyautogui")
            return False
        return super().check_dependencies()

    def process(self, command: str) -> str:
        brain = self.core_context.get("brain")
        ctx = self.core_context.get("context")

        if not brain:
            return "Erro: Cérebro não encontrado."

        if not VISAO_AVAILABLE:
            return "Erro: Módulo de visão requer 'pyautogui' instalado."

        try:
            # 1. Captura a tela
            screenshot = pyautogui.screenshot()
            
            # 2. Converte para bytes
            img_byte_arr = BytesIO()
            screenshot.save(img_byte_arr, format='PNG')
            img_bytes = img_byte_arr.getvalue()

            # 3. Envia para o Cérebro (Vision Model)
            analise = brain.ver(img_bytes)

            # 4. SALVA NO CONTEXTO (O Pulo do Gato)
            if ctx:
                ctx.set("vision_last_result", analise, ttl=600) # Lembra por 10 minutos
                print(f"[VISAO] Contexto salvo: {analise[:50]}...")

            return f"Analisei sua tela: {analise}"

        except Exception as e:
            return f"Erro ao processar visão: {str(e)}"