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
        # Dependências opcionais não precisam estar listadas aqui se tratamos no código
        self.dependencies = ["brain", "context"]

    @property
    def metadata(self) -> dict:
        return {
            "version": "1.1.0",
            "author": "Aeon Core",
            "description": "Captura e analisa o conteúdo da tela."
        }

    def check_dependencies(self):
        # Verifica se as libs externas estão instaladas
        if not VISAO_AVAILABLE:
            print("[VISAO] Erro: 'pyautogui' não instalado. Rode: pip install pyautogui")
            # Retorna True para não bloquear o módulo de carregar, 
            # mas ele vai avisar ao usuário se for chamado.
            return True 
        return super().check_dependencies()

    def process(self, command: str) -> str:
        brain = self.core_context.get("brain")
        ctx = self.core_context.get("context")

        if not VISAO_AVAILABLE:
            return "Minha visão está desativada. Instale a biblioteca 'pyautogui' para corrigir."

        if not brain:
            return "Cérebro não encontrado."

        try:
            # 1. Captura a tela
            screenshot = pyautogui.screenshot()
            
            # 2. Converte para bytes
            img_byte_arr = BytesIO()
            screenshot.save(img_byte_arr, format='PNG')
            img_bytes = img_byte_arr.getvalue()

            # 3. Envia para o Cérebro (Vision Model)
            analise = brain.ver(img_bytes)

            # 4. SALVA NO CONTEXTO
            if ctx:
                ctx.set("vision_last_result", analise, ttl=600)
                print(f"[VISAO] Contexto salvo: {analise[:50]}...")

            return f"Analisei sua tela: {analise}"

        except Exception as e:
            return f"Erro ao processar visão: {str(e)}"