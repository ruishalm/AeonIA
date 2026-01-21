import ollama
from groq import Groq
import base64
from PIL import Image
from io import BytesIO
import datetime

def log_display(msg):
    print(f"[BRAIN] {msg}")

class Brain:
    """
    O cérebro do Aeon. Gerencia a interação com os modelos de linguagem.
    """
    def __init__(self, config: dict, installer):
        self.config = config
        self.installer = installer
        self.client = None
        self.online = False
        self.local_ready = False
        
        self.groq_api_key = self.config.get("GROQ_KEY")
        
        # Conecta aos serviços no boot
        self.reconectar()
        
        if self.installer:
            self.local_ready = self.installer.verificar_ollama()
        else:
            self.local_ready = False

    def reconectar(self):
        """Tenta (re)conectar ao serviço de nuvem (Groq)."""
        if not self.groq_api_key:
            log_display("Chave da API Groq não encontrada.")
            self.online = False
            return False
        
        try: 
            self.client = Groq(api_key=self.groq_api_key)
            # Teste rápido de conexão
            self.client.models.list()
            self.online = True
            log_display("Conexão com a Nuvem (Groq) estabelecida.")
            return True
        except Exception as e:
            self.online = False
            log_display(f"Falha ao conectar na Nuvem: {e}")
            return False

    def pensar(self, prompt: str, historico_txt: str = "", user_prefs: dict = {}) -> str:
        """
        Processa um prompt com Auto-Healing de conexão.
        """
        # CORREÇÃO: Se estiver marcado como offline, tenta reconectar uma vez antes de desistir
        if not self.online and self.groq_api_key:
            self.reconectar()

        prefs_str = "\n".join([f"- {k}: {v}" for k, v in user_prefs.items()])
        
        system_prompt = f"""Você é Aeon, um assistente focado em respostas precisas.
Data: {datetime.datetime.now().strftime('%d/%m/%Y %H:%M')}
Responda SEMPRE em Português do Brasil, de forma concisa.

CONTEXTO DE CONVERSAS ANTERIORES:
{historico_txt}

Preferências do usuário:
{prefs_str}"""

        # Prioridade 1: Nuvem (Groq)
        if self.client and self.online:
            try:
                log_display("Pensando com Groq Cloud...")
                comp = self.client.chat.completions.create(
                    model=self.config.get("model_txt_cloud", "llama-3.3-70b-versatile"),
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": f"Pergunta atual: {prompt}"}
                    ],
                    temperature=0.6, max_tokens=400
                )
                return comp.choices[0].message.content
            except Exception as e:
                log_display(f"ERRO GROQ (Caindo para local): {e}")
                self.online = False # Marca como offline para forçar reconexão futura

        # Prioridade 2: Local (Ollama)
        if self.local_ready:
            log_display("Pensando com Ollama Local...")
            try:
                r = ollama.chat(
                    model=self.config.get("model_txt_local", "llama3.2"),
                    messages=[
                        {'role': 'system', 'content': "Seja curto e direto em Português do Brasil."},
                        {'role': 'user', 'content': prompt}
                    ]
                )
                return r['message']['content']
            except Exception as e:
                log_display(f"ERRO Ollama: {e}")
        
        return "Desculpe, estou sem conexão e sem um cérebro local funcional."

    def ver(self, raw_image_bytes: bytes) -> str:
        """
        Processa uma imagem.
        """
        if not self.online and self.groq_api_key:
            self.reconectar()

        try:
            pil_img = Image.open(BytesIO(raw_image_bytes))
            pil_img.thumbnail((1024, 1024))
            buf = BytesIO()
            pil_img.save(buf, format="JPEG", quality=70)
            optimized_bytes = buf.getvalue()
        except:
            optimized_bytes = raw_image_bytes

        if self.client and self.online:
            try:
                log_display("Analisando imagem com Groq Vision...")
                b64 = base64.b64encode(optimized_bytes).decode('utf-8')
                comp = self.client.chat.completions.create(
                    model=self.config.get("model_vis_cloud", "llama-3.2-11b-vision-preview"),
                    messages=[{"role": "user", "content": [
                        {"type": "text", "text": "Descreva esta imagem em Português do Brasil de forma concisa."},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64}"}}
                    ]}],
                    temperature=0.1, max_tokens=300
                )
                return comp.choices[0].message.content
            except Exception as e:
                log_display(f"Erro Vision Cloud: {e}")
                self.online = False
        
        if self.local_ready:
            log_display("Analisando imagem com Moondream Local...")
            try:
                res = ollama.chat(
                    model=self.config.get("model_vis_local", "moondream"),
                    messages=[{'role': 'user', 'content': 'Descreva esta imagem.', 'images': [raw_image_bytes]}]
                )
                return self.pensar(f"Traduza: {res['message']['content']}", "")
            except Exception as e:
                log_display(f"Erro Vision Local: {e}")
            
        return "Não consegui analisar a imagem."