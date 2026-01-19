import warnings
warnings.filterwarnings("ignore")
import customtkinter as ctk
import threading
import time
import datetime
import sys
import os
import re
import json
import asyncio
import subprocess
from io import BytesIO
from PIL import Image, ImageGrab
import psutil
import random
import webbrowser
import base64

# ==============================================================================
#                       BOOTSTRAP
# ==============================================================================
def check_deps():
    DEPS = {
        "pygame": "pygame", "edge-tts": "edge_tts", "GPUtil": "GPUtil", 
        "ollama": "ollama", "packaging": "packaging", "Pillow": "PIL", 
        "SpeechRecognition": "speech_recognition", "pyautogui": "pyautogui", 
        "pyaudio": "pyaudio", "psutil": "psutil", "groq": "groq",
        "requests": "requests", "beautifulsoup4": "bs4", "googlesearch-python": "googlesearch",
        "feedparser": "feedparser", "PyGetWindow": "pygetwindow"
    }
    miss = [pip for pip, mod in DEPS.items() if import_safe(mod) is None]
    if miss:
        print(f">> [BOOT] Instalando: {miss}")
        try: subprocess.check_call([sys.executable, "-m", "pip", "install"] + miss)
        except: pass

def import_safe(name):
    try: return __import__(name)
    except ImportError: return None

check_deps()

import pygame
import edge_tts
import GPUtil
import ollama
import pyautogui
import speech_recognition as sr
import psutil
from groq import Groq
import requests
from bs4 import BeautifulSoup
from googlesearch import search
import feedparser
import pygetwindow as gw

# ==============================================================================
#                               CONFIGURAÇÕES
# ==============================================================================

XGROQ_KEY = [no_key]

CFG = {
    "mem": "memoria_aeon.json",
    "sys": "aeon_system.json",
    "aud": "temp_audio.mp3",
    "model_txt_cloud": "llama3-70b-8192",
    "model_vis_cloud": "llama-3.2-11b-vision-preview", # Único ativo atualmente
    "model_txt_local": "llama3.2",
    "model_vis_local": "moondream"
}

C = {
    "bg": "#050505", 
    "panel_log": "#000000", 
    "panel_chat": "#101010",
    "log_text": "#004400", 
    "user": "#00ffff", 
    "bot": "#ffffff", 
    "sys": "#ffff00", 
    "err": "#ff5555", 
    "border": "#b30000",
    "led_off": "#1a1a1a",
    "led_cloud": "#0088ff", 
    "led_local": "#ffaa00", 
    "led_hybrid": "#00ff00"
}

TRIGGERS = ["aeon", "aion", "iron", "filho", "assistente", "computador"]
APP_REF = None
PARAR_FALA = False
RECALIBRAR_MIC = False
CONVERSATION_MODE = False
LAST_ACTIVITY_TIME = None
DITADO_MODE = False

# ==============================================================================
#                     GESTOR DE INSTALAÇÃO & LIMPEZA
# ==============================================================================

class InstallMgr:
    def limpar_lixo(self):
        """O Gari: Remove arquivos de áudio órfãos."""
        count = 0
        for f in os.listdir("."):
            if f.startswith("fala_") and f.endswith(".mp3"):
                try: os.remove(f); count += 1
                except: pass
        if count > 0: print(f">> [GARI] Removidos {count} arquivos de áudio temporários.")

    def verificar_ollama(self):
        try:
            subprocess.run(["ollama", "--version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
            return True
        except: return False

    def instalar_ollama(self):
        if APP_REF: APP_REF.chat_display("Tentando instalar Ollama...", "SISTEMA", "sys")
        try:
            subprocess.run(["winget", "install", "Ollama.Ollama"], check=True)
            return True
        except:
            webbrowser.open("https://ollama.com/download")
            return False

    def baixar_modelos(self):
        if APP_REF: APP_REF.chat_display("Baixando Llama 3.2...", "SISTEMA", "sys")
        os.system(f"start cmd /k ollama pull {CFG['model_txt_local']}")
        os.system(f"start cmd /k ollama pull {CFG['model_vis_local']}")

INSTALLER = InstallMgr()

# ==============================================================================
#                     CÉREBRO HÍBRIDO
# ==============================================================================

class Brain:
    def __init__(self):
        self.client = None
        self.local_ready = False
        self.online = True
        
        if GROQ_KEY:
            try: 
                self.client = Groq(api_key=GROQ_KEY)
                self.client.models.list()
            except Exception as e: 
                print(f">> Erro Chave Groq: {e}")
                self.online = False
            
        self.local_ready = INSTALLER.verificar_ollama()

    def reconectar(self):
        if not self.client: return "Sem chave API."
        try:
            self.client.models.list()
            self.online = True
            if APP_REF: APP_REF.update_leds()
            return "Conexão Nuvem OK."
        except Exception as e: return f"Falha: {e}"

    def pensar(self, prompt, historico_txt):
        if self.client and self.online:
            try:
                if APP_REF: APP_REF.log_display("Groq Cloud (Llama 3.3)...")
                comp = self.client.chat.completions.create(
                    model=CFG["model_txt_cloud"],
                    messages=[
                        {"role": "system", "content": f"Data: {datetime.datetime.now()}. Responda curto (PT-BR)."},
                        {"role": "user", "content": f"Contexto:\n{historico_txt}\n\nUsuário: {prompt}"}
                    ],
                    temperature=0.6, max_tokens=300
                )
                return comp.choices[0].message.content
            except Exception as e:
                if APP_REF: 
                    APP_REF.log_display(f"ERRO GROQ: {e}")
                    APP_REF.chat_display(f"FALHA ONLINE: {str(e)[:40]}...", "SISTEMA", "err")
                self.online = False
                if APP_REF: APP_REF.update_leds()

        if self.local_ready:
            if APP_REF: APP_REF.log_display("Ollama Local...")
            try:
                r = ollama.chat(model=CFG["model_txt_local"], messages=[
                    {'role':'system','content':"Seja curto."},
                    {'role':'user','content':prompt}
                ])
                return r['message']['content']
            except: pass
        
        return "Estou sem cérebro. Diga 'instalar offline'."

    def ver(self, raw_image_bytes):
        try:
            pil_img = Image.open(BytesIO(raw_image_bytes))
            pil_img.thumbnail((1024, 1024))
            buf = BytesIO()
            pil_img.save(buf, format="JPEG", quality=70)
            optimized_bytes = buf.getvalue()
        except: optimized_bytes = raw_image_bytes

        if self.client and self.online:
            try:
                if APP_REF: APP_REF.log_display("Groq Vision (11B)...")
                b64 = base64.b64encode(optimized_bytes).decode('utf-8')
                comp = self.client.chat.completions.create(
                    model=CFG["model_vis_cloud"],
                    messages=[{"role": "user", "content": [
                        {"type": "text", "text": "Descreva em PT-BR."},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64}"}}
                    ]}], temperature=0.1, max_tokens=300
                )
                return comp.choices[0].message.content
            except Exception as e: 
                if APP_REF: APP_REF.log_display(f"Erro Vision Cloud: {e}")
            
        if self.local_ready:
            try:
                if APP_REF: APP_REF.log_display("Moondream Local...")
                res = ollama.chat(model=CFG["model_vis_local"], messages=[{'role':'user','content':'Describe','images':[raw_image_bytes]}])
                return self.pensar(f"Traduza: {res['message']['content']}", "")
            except Exception as e:
                if APP_REF: APP_REF.log_display(f"Erro Vision Local: {e}")
            
        return "Não consegui ver nada."

CEREBRO = Brain()

# ==============================================================================
#                     SISTEMA & MEMÓRIA
# ==============================================================================

class SysMgr:
    def __init__(self): self.data = self.load()
    def load(self): return json.load(open(CFG["sys"], encoding='utf-8')) if os.path.exists(CFG["sys"]) else {"apps": {}}
    def save(self): json.dump(self.data, open(CFG["sys"], 'w', encoding='utf-8'), indent=4)
    def get_apps(self): return self.data.get("apps", {})
    def set_apps(self, apps): self.data["apps"] = apps; self.save()

SISTEMA = SysMgr()

def carregar_memoria():
    if not os.path.exists(CFG["mem"]): return []
    try:
        d = json.load(open(CFG["mem"], encoding='utf-8'))
        return [i for i in d if isinstance(i, dict) and 'user' in i]
    except: return []

def salvar_memoria(hist):
    try: json.dump(hist[-20:], open(CFG["mem"], 'w', encoding='utf-8'), indent=4)
    except: pass

def adicionar_memoria(u, a):
    global MEMORIA_RAM
    MEMORIA_RAM.append({"user": u, "aeon": a, "time": str(datetime.datetime.now())})
    salvar_memoria(MEMORIA_RAM)

MEMORIA_RAM = carregar_memoria()

# ==============================================================================
#                          LÓGICA DE ÁUDIO (CLEANUP FIX)
# ==============================================================================

async def _edge_tts_save(texto, arquivo):
    communicate = edge_tts.Communicate(texto, "pt-BR-AntonioNeural")
    await communicate.save(arquivo)

def falar(texto):
    global PARAR_FALA
    if not texto: return
    PARAR_FALA = False
    if APP_REF: APP_REF.chat_display(texto, "AEON", "bot")
    
    clean = re.sub(r'[*_#`]', '', texto).replace('\n', ' ').strip()
    f_tmp = f"fala_{random.randint(1000,9999)}.mp3"

    try:
        asyncio.run(_edge_tts_save(clean, f_tmp))
        
        pygame.mixer.music.load(f_tmp)
        pygame.mixer.music.play()
        
        while pygame.mixer.music.get_busy():
            if PARAR_FALA:
                pygame.mixer.music.stop()
                break
            time.sleep(0.1)
        
    except Exception as e: 
        if APP_REF: APP_REF.log_display(f"Audio Error: {e}")
    
    # Tentativa agressiva de limpeza
    threading.Thread(target=limpar_arquivo_seguro, args=(f_tmp,)).start()

def limpar_arquivo_seguro(arquivo):
    """Tenta deletar o arquivo com delay para o Windows liberar o lock."""
    time.sleep(0.5) # Dá um tempo pro Windows
    try:
        if os.path.exists(arquivo): os.remove(arquivo)
    except: pass # Se falhar, o Gari limpa no próximo boot

def calar_boca():
    global PARAR_FALA
    PARAR_FALA = True
    print(">> SILÊNCIO!")
    if APP_REF: APP_REF.chat_display(">> SILÊNCIO.", "SISTEMA", "err")
    try:
        if pygame.mixer.get_init(): pygame.mixer.music.stop()
    except: pass

# ==============================================================================
#                          CORE
# ==============================================================================

def indexar_programas():
    if APP_REF: APP_REF.log_display("Indexando...")
    apps = {"calc": "calc", "notepad": "notepad", "cmd": "start cmd", "explorer": "explorer"}
    for r, d, f in os.walk(os.environ["ProgramData"] + r"\Microsoft\Windows\Start Menu\Programs"):
        for file in f:
            if file.endswith(".lnk"): apps[file.lower().replace(".lnk","")] = os.path.join(r, file)
    SISTEMA.set_apps(apps)
    return apps

def processar_comando(texto):
    if not texto: return
    cmd = texto.lower()
    global RECALIBRAR_MIC
    
    if "sair" in cmd: falar("Até logo."); os._exit(0)
    
    if "conectar" in cmd or "online" in cmd:
        msg = CEREBRO.reconectar()
        falar(msg); return

    if "sistema recalibrar" in cmd or "ajustar áudio" in cmd:
        falar("Entendido. Silêncio por 3 segundos.")
        time.sleep(3)
        RECALIBRAR_MIC = True
        return

    if "instalar" in cmd and "offline" in cmd:
        falar("Iniciando instalação local.")
        if not INSTALLER.verificar_ollama():
            if INSTALLER.instalar_ollama(): falar("Instalando motor...")
            else: falar("Abri o site. Instale e reinicie.")
            return
        INSTALLER.baixar_modelos()
        falar("Baixando. Aguarde.")
        CEREBRO.local_ready = True
        if APP_REF: APP_REF.update_leds()
        return

    if "instalar" in cmd and "pacote" in cmd:
        pkg = cmd.replace("instalar","").replace("pacote","").strip()
        falar(f"Baixando {pkg}...")
        try: subprocess.check_call([sys.executable, "-m", "pip", "install", pkg]); falar("Pronto.")
        except: falar("Erro.")
        return

    # Lógica de Lembretes e Alarmes
    lembrete_triggers = ["alarme", "timer", "lembrete", "me lembre de"]
    if any(t in cmd for t in lembrete_triggers):
        nums = {"um":1,"dois":2,"tres":3,"quatro":4,"cinco":5,"dez":10,"vinte":20,"trinta":30,"meia":30}
        for k,v in nums.items(): cmd = cmd.replace(k, str(v))
        
        match = re.search(r'(\d+)\s*(segundo|minuto|hora)', cmd)
        if match:
            q, u = int(match.group(1)), match.group(2)
            dt = datetime.timedelta(seconds=q) if "seg" in u else datetime.timedelta(minutes=q) if "min" in u else datetime.timedelta(hours=q)
            
            # Extrai a mensagem do lembrete
            mensagem = re.sub(r'em\s*(\d+)\s*(segundo|minuto|hora)s?', '', cmd)
            for t in lembrete_triggers: mensagem = mensagem.replace(t, '')
            mensagem = mensagem.strip()
            if not mensagem: mensagem = "Seu tempo acabou!"
            
            if APP_REF: APP_REF.adicionar_alarme(dt, mensagem)
            falar(f"Ok, lembrete definido para daqui a {q} {u}s.")
        else: 
            falar("Não consegui entender o tempo para o lembrete.")
        return

    apps = SISTEMA.get_apps()
    for n, p in apps.items():
        if n in cmd and ("abre" in cmd or "iniciar" in cmd):
            falar(f"Abrindo {n}...")
            try: os.startfile(p)
            except: os.system(p)
            return

    # Nova lógica de busca na web
    search_triggers = ["pesquise por", "procure por", "o que é", "quem é", "quem foi"]
    for trigger in search_triggers:
        if cmd.startswith(trigger):
            query = cmd.replace(trigger, "").strip()
            falar(f"Pesquisando sobre {query}...")
            contexto_web = web_search(query)
            if "Ocorreu um erro" in contexto_web or "Não encontrei" in contexto_web:
                falar(contexto_web)
            else:
                prompt_final = f"Com base no seguinte texto, responda de forma concisa à pergunta: '{query}'\n\nTexto: {contexto_web}"
                resposta = CEREBRO.pensar(prompt_final, "")
                adicionar_memoria(query, resposta)
                falar(resposta)
            return

    # Lógica de Clima
    clima_triggers = ["como está o tempo", "previsão do tempo"]
    for trigger in clima_triggers:
        if trigger in cmd:
            cidade = cmd.replace(trigger, "").replace("em", "").strip()
            falar("Verificando...")
            resultado_clima = obter_clima(cidade)
            falar(resultado_clima)
            return

    # Lógica de Notícias
    noticias_triggers = ["quais as notícias", "me dê as manchetes", "manchetes de hoje"]
    for trigger in noticias_triggers:
        if trigger in cmd:
            falar("Buscando as últimas notícias...")
            resultado_noticias = obter_noticias()
            falar(resultado_noticias)
            return

    # Lógica de Controle de Janelas
    acoes_janela = {
        "minimize": "minimize", "minimizar": "minimize",
        "maximize": "maximize", "maximizar": "maximize",
        "restore": "restore", "restaurar": "restore",
        "close": "close", "feche": "close", "fechar": "close",
        "activate": "activate", "alterne para": "activate", "foco em": "activate"
    }
    for palavra, acao in acoes_janela.items():
        if palavra in cmd:
            partes = cmd.split(palavra)
            titulo = partes[1].strip() if len(partes) > 1 and partes[1].strip() else None
            
            # Evita confundir com "fechar o programa"
            if acao == 'close' and not titulo and 'janela' not in cmd:
                continue

            resultado = controlar_janela(acao, titulo)
            falar(resultado)
            return

    # Lógica de Resumo de URL
    if "http:" in cmd or "www." in cmd:
        url = re.search(r'(https?://[^\s]+)', cmd).group(0)
        if url:
            falar(f"Analisando o conteúdo de {url.split('//')[1].split('/')[0]}...")
            contexto_web = web_search(url)
            if "Ocorreu um erro" in contexto_web or "Não encontrei" in contexto_web:
                falar(contexto_web)
            else:
                prompt_final = f"Resuma o seguinte texto de forma concisa:\n\n{contexto_web}"
                resposta = CEREBRO.pensar(prompt_final, "")
                falar(resposta)
            return

    # Lógica de Rolagem
    if "role para cima" in cmd:
        pyautogui.scroll(300)
        return
    if "role para baixo" in cmd:
        pyautogui.scroll(-300)
        return

    if "tela" in cmd or "veja" in cmd:
        img = ImageGrab.grab(); buf = BytesIO(); img.save(buf, format="PNG")
        falar("Analisando...")
        falar(CEREBRO.ver(buf.getvalue()))
        return

    hist = ""
    for i in MEMORIA_RAM[-2:]: 
        hist += f"User: {i.get('user','')} | AI: {i.get('aeon','')}\n"
    
    resp = CEREBRO.pensar(texto, hist)
    adicionar_memoria(texto, resp)
    falar(resp)

# ==============================================================================
#                          FERRAMENTAS (TOOLS)
# ==============================================================================

def web_search(query):
    if APP_REF: APP_REF.log_display(f"Processando Web: {query[:50]}")
    try:
        if query.startswith("http"):
            url = query
        else:
            urls = list(search(query, num_results=1, lang="pt"))
            if not urls: return "Não encontrei resultados para essa busca."
            url = urls[0]
        
        if APP_REF: APP_REF.log_display(f"Analisando URL: {url}")
        
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        response = requests.get(url, headers=headers, timeout=5)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        for tag in ['nav', 'footer', 'aside', 'script', 'style']:
            for s in soup(tag):
                s.decompose()
        
        text_content = ' '.join(p.get_text() for p in soup.find_all('p'))
        return text_content[:4000] # Limita o tamanho para não sobrecarregar a IA
        
    except Exception as e:
        if APP_REF: APP_REF.log_display(f"Erro na busca/URL: {e}")
        return f"Ocorreu um erro ao processar a requisição web: {e}"

def obter_clima(cidade=''):
    try:
        if not cidade: # Tenta autodetectar a cidade
            ip_info = requests.get('https://ipinfo.io/json').json()
            cidade = ip_info.get('city', 'Sao Paulo')
        
        url = f"https://wttr.in/{cidade.replace(' ', '+')}?format=j1"
        data = requests.get(url).json()
        
        condicao_atual = data['current_condition'][0]
        temp = condicao_atual['temp_C']
        sensacao = condicao_atual['FeelsLikeC']
        descricao = condicao_atual['lang_pt'][0]['value']
        
        return f"O tempo em {data['nearest_area'][0]['areaName'][0]['value']} agora é: {descricao}, com temperatura de {temp} graus e sensação térmica de {sensacao} graus."
        
    except Exception as e:
        if APP_REF: APP_REF.log_display(f"Erro no clima: {e}")
        return "Não consegui verificar o tempo."

def obter_noticias():
    try:
        url_rss = "https://g1.globo.com/rss/g1/"
        if APP_REF: APP_REF.log_display(f"Buscando notícias: {url_rss}")
        feed = feedparser.parse(url_rss)
        manchetes = [entry.title for entry in feed.entries[:3]]
        if not manchetes:
            return "Não consegui obter as manchetes."
        
        resposta = "As principais manchetes do G1 são: "
        resposta += "; ".join(manchetes)
        return resposta

    except Exception as e:
        if APP_REF: APP_REF.log_display(f"Erro nas notícias: {e}")
        return "Tive um problema ao buscar as notícias."

def controlar_janela(acao, titulo_alvo=None):
    try:
        if titulo_alvo:
            # Tenta encontrar a janela que contém o título
            alvos = gw.getWindowsWithTitle(titulo_alvo)
            if not alvos:
                return f"Não encontrei nenhuma janela com o título '{titulo_alvo}'."
            win = alvos[0]
        else:
            # Pega a janela ativa
            win = gw.getActiveWindow()
            if not win:
                return "Não há uma janela ativa no momento."

        if acao == 'minimize': win.minimize()
        elif acao == 'maximize': win.maximize()
        elif acao == 'restore': win.restore()
        elif acao == 'close': win.close()
        elif acao == 'activate': win.activate()
        else: return f"Ação '{acao}' desconhecida."
        
        return f"Janela '{win.title[:20]}...' {acao}."

    except Exception as e:
        if APP_REF: APP_REF.log_display(f"Erro de janela: {e}")
        return "Ocorreu um erro ao tentar controlar a janela."

# ==============================================================================
#                          INTERFACE GRÁFICA (V71)
# ==============================================================================

class PrintRedirector:
    def __init__(self, app): self.app = app
    def write(self, msg): 
        if msg.strip() and self.app: self.app.log_display(msg.strip())
    def flush(self): pass

class AeonGUI(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Inicialização única do Pygame
        pygame.init()
        pygame.mixer.init()
        
        self.title("AEON V71 - CLEANER")
        self.geometry("450x650")
        self.configure(fg_color=C["bg"])
        ctk.set_appearance_mode("Dark")
        
        self.grid_columnconfigure(0, weight=1); self.grid_columnconfigure(1, weight=4)
        self.grid_rowconfigure(1, weight=1)

        # STATUS BAR
        self.status_frame = ctk.CTkFrame(self, fg_color="#080808", height=40, corner_radius=0)
        self.status_frame.grid(row=0, column=0, columnspan=2, sticky="ew")
        
        def criar_led(texto, coluna):
            frame = ctk.CTkFrame(self.status_frame, fg_color="transparent")
            frame.pack(side="left", padx=15, pady=5)
            lbl = ctk.CTkLabel(frame, text=texto, font=("Arial", 10, "bold"), text_color="#777777")
            lbl.pack()
            cv = ctk.CTkCanvas(frame, width=15, height=15, bg="#080808", highlightthickness=0)
            cv.pack()
            c = cv.create_oval(3, 3, 13, 13, fill=C["led_off"], outline="")
            return cv, c

        self.cv_cloud, self.id_cloud = criar_led("CLOUD", 0)
        self.cv_local, self.id_local = criar_led("LOCAL", 1)
        self.cv_hybrid, self.id_hybrid = criar_led("HYBRID", 2)

        # LOGS
        self.log_box = ctk.CTkTextbox(self, font=("Consolas", 9), fg_color=C["panel_log"], text_color=C["log_text"])
        self.log_box.grid(row=1, column=0, sticky="nsew", padx=(5,2), pady=5)
        self.log_box.configure(state="disabled")

        # CHAT
        self.chat_box = ctk.CTkTextbox(self, font=("Consolas", 12), fg_color=C["panel_chat"], text_color=C["bot"])
        self.chat_box.grid(row=1, column=1, sticky="nsew", padx=(2,5), pady=5)
        self.chat_box.configure(state="disabled")
        
        self.tk_chat = self.chat_box._textbox
        self.tk_chat.tag_config("user", foreground=C["user"]); self.tk_chat.tag_config("bot", foreground=C["bot"])
        self.tk_chat.tag_config("sys", foreground=C["sys"]); self.tk_chat.tag_config("err", foreground=C["err"])

        sys.stdout = PrintRedirector(self)

        # INPUTS
        f = ctk.CTkFrame(self, fg_color="#111111", corner_radius=10)
        f.grid(row=2, column=0, columnspan=2, padx=5, pady=(0, 5), sticky="ew")

        self.inp = ctk.CTkEntry(f, placeholder_text="Cmd...", font=("Arial", 12), fg_color="black", border_color=C["border"])
        self.inp.pack(side="left", fill="x", expand=True, padx=5, pady=5)
        self.inp.bind("<Return>", self.on_send)

        self.btn_mode = ctk.CTkButton(f, text="DIRETO", width=60, fg_color="#00cc00", font=("Arial", 10), command=self.toggle_mode)
        self.btn_mode.pack(side="left", padx=2)

        ctk.CTkButton(f, text="XIU", width=40, fg_color=C["err"], hover_color="#990000", font=("Arial", 10), command=calar_boca).pack(side="right", padx=5)
        ctk.CTkButton(f, text="OK", width=40, fg_color=C["border"], font=("Arial", 10), command=self.on_send).pack(side="right", padx=2)

        self.mode_call = False
        self.alarms = []
        threading.Thread(target=self.boot, daemon=True).start()

    def boot(self):
        print(">> Boot V71...")
        INSTALLER.limpar_lixo() # O GARI ENTRA EM AÇÃO
        if not SISTEMA.get_apps(): indexar_programas()
        self.update_leds()
        self.chat_display("Aeon Online.", "SISTEMA", "sys")
        threading.Thread(target=self.loop_voz, daemon=True).start()
        threading.Thread(target=self.loop_alarm, daemon=True).start()

    def update_leds(self):
        off = C["led_off"]
        self.cv_cloud.itemconfig(self.id_cloud, fill=off)
        self.cv_local.itemconfig(self.id_local, fill=off)
        self.cv_hybrid.itemconfig(self.id_hybrid, fill=off)
        
        has_cloud = CEREBRO.client is not None and CEREBRO.online
        has_local = CEREBRO.local_ready
        
        if has_cloud: self.cv_cloud.itemconfig(self.id_cloud, fill=C["led_cloud"])
        if has_local: self.cv_local.itemconfig(self.id_local, fill=C["led_local"])
        if has_cloud and has_local: self.cv_hybrid.itemconfig(self.id_hybrid, fill=C["led_hybrid"])

    def log_display(self, msg):
        self.log_box.configure(state="normal")
        self.log_box.insert("end", f"> {msg}\n")
        self.log_box.configure(state="disabled"); self.log_box.see("end")

    def chat_display(self, msg, sender, tag="bot"):
        self.chat_box.configure(state="normal")
        pre = f"[{sender}]: " if sender != "LOG" else ""
        self.tk_chat.insert("end", f"\n{pre}{msg}\n", tag)
        self.chat_box.configure(state="disabled"); self.chat_box.see("end")

    def on_send(self, e=None):
        txt = self.inp.get()
        if not txt: return
        self.inp.delete(0, "end")
        self.chat_display(txt, "VOCÊ", "user")
        threading.Thread(target=processar_comando, args=(txt,)).start()

    def toggle_mode(self):
        self.mode_call = not self.mode_call
        c, t = ("#e6b800", "CHAMAR") if self.mode_call else ("#00cc00", "DIRETO")
        self.btn_mode.configure(fg_color=c, text=t)
        self.log_display(f"Modo de escuta: {'CHAMAR' if self.mode_call else 'DIRETO'}")

    def adicionar_alarme(self, delta, msg):
        self.alarms.append({"t": datetime.datetime.now() + delta, "msg": msg})


    def loop_alarm(self):
        while True:
            now = datetime.datetime.now()
            for a in self.alarms[:]:
                if now >= a['t']:
                    pyautogui.press("playpause"); falar(f"Atenção: {a['msg']}")
                    time.sleep(1); pyautogui.press("playpause"); self.alarms.remove(a)
            time.sleep(1)

    def loop_voz(self):
        global RECALIBRAR_MIC, CONVERSATION_MODE, LAST_ACTIVITY_TIME, DITADO_MODE
        rec = sr.Recognizer(); rec.pause_threshold = 0.8
        
        with sr.Microphone() as source:
            self.log_display("Calibrando mic...")
            rec.adjust_for_ambient_noise(source, duration=2)
            self.log_display("Microfone OK.")
            
            while True:
                time.sleep(0.1) # Pequena pausa para não sobrecarregar
                
                # Lógica do Modo Ditado
                if DITADO_MODE:
                    try:
                        self.log_display("Ouvindo ditado...")
                        audio = rec.listen(source, timeout=None, phrase_time_limit=30)
                        texto_ditado = rec.recognize_google(audio, language="pt-BR")
                        
                        if "encerrar ditado" in texto_ditado.lower():
                            DITADO_MODE = False
                            falar("Modo ditado encerrado.")
                            # Limpa o comando para não digitar "encerrar ditado"
                            texto_final = texto_ditado.lower().replace("encerrar ditado", "")
                            pyautogui.write(texto_final)
                        else:
                            pyautogui.write(texto_ditado + " ")

                    except sr.UnknownValueError:
                        self.log_display("Não entendi o ditado.")
                    except sr.WaitTimeoutError:
                        pass
                    continue # Volta para o início do loop de ditado

                if RECALIBRAR_MIC:
                    self.log_display("Recalibrando...")
                    rec.adjust_for_ambient_noise(source, duration=2)
                    self.log_display("Mic OK."); falar("Pronto.")
                    RECALIBRAR_MIC = False

                try:
                    # Modo CHAMAR (precisa de palavra de ativação)
                    if self.mode_call:
                        # Verifica inatividade no modo de conversação
                        if CONVERSATION_MODE and (time.time() - LAST_ACTIVITY_TIME > 20):
                            falar("Inatividade. Retornando ao modo de espera.")
                            CONVERSATION_MODE = False
                            self.log_display("Modo de espera (timeout).")

                        listen_timeout = 5 if CONVERSATION_MODE else None
                        audio = rec.listen(source, timeout=listen_timeout, phrase_time_limit=15)
                        cmd = rec.recognize_google(audio, language="pt-BR").lower()
                        
                        if CONVERSATION_MODE:
                            LAST_ACTIVITY_TIME = time.time()
                            self.chat_display(cmd, "VOCÊ (Voz)", "user")
                            if "dispensar" in cmd:
                                falar("Entendido."); CONVERSATION_MODE = False
                                self.log_display("Modo de espera (dispensado).")
                            else:
                                threading.Thread(target=processar_comando, args=(cmd,)).start()
                        else: # Esperando palavra de ativação
                            if any(t in cmd for t in TRIGGERS):
                                CONVERSATION_MODE = True
                                LAST_ACTIVITY_TIME = time.time()
                                self.log_display("Modo de conversação ativado.")
                                falar("Sim?")
                                for t in TRIGGERS: cmd = cmd.replace(t, "").strip()
                                if cmd:
                                    self.chat_display(cmd, "VOCÊ (Voz)", "user")
                                    threading.Thread(target=processar_comando, args=(cmd,)).start()
                    
                    # Modo DIRETO (sempre ouvindo)
                    else:
                        CONVERSATION_MODE = False # Garante que está desativado
                        audio = rec.listen(source, timeout=5, phrase_time_limit=10)
                        cmd = rec.recognize_google(audio, language="pt-BR").lower()
                        if cmd:
                            self.chat_display(cmd, "VOCÊ (Voz)", "user")
                            threading.Thread(target=processar_comando, args=(cmd,)).start()

                except sr.UnknownValueError:
                    if not self.mode_call: self.log_display("...")
                except sr.WaitTimeoutError:
                    pass
                except Exception as e:
                    self.log_display(f"Erro no loop de voz: {e}")
                    time.sleep(1)

if __name__ == "__main__":
    app = AeonGUI()
    APP_REF = app
    app.mainloop()