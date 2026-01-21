import os
import re
import asyncio
import subprocess
import random
import threading
import time
import pygame
import edge_tts
import pyttsx3

def log_display(msg):
    print(f"[IO_HANDLER] {msg}")

class IOHandler:
    """
    Gerencia áudio com proteção de threads (Lock).
    """
    def __init__(self, config: dict, installer=None):
        self.config = config if config else {}
        self.installer = installer
        self.parar_fala = False
        self.audio_lock = threading.Lock() # <--- A PROTEÇÃO V80
        
        self.temp_audio_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "bagagem", "temp")
        os.makedirs(self.temp_audio_path, exist_ok=True)
        
        try: pygame.mixer.init()
        except: pass

    def _tocar_audio(self, arquivo: str):
        with self.audio_lock: # Só um por vez
            try:
                if pygame.mixer.music.get_busy():
                    pygame.mixer.music.stop()
                pygame.mixer.music.load(arquivo)
                pygame.mixer.music.play()
            except Exception as e:
                log_display(f"Erro audio: {e}")
                return

        while pygame.mixer.music.get_busy():
            if self.parar_fala:
                pygame.mixer.music.stop()
                break
            time.sleep(0.1)
        
        threading.Thread(target=self._limpar_seguro, args=(arquivo,), daemon=True).start()

    def _limpar_seguro(self, arquivo: str):
        time.sleep(0.5)
        try:
            if os.path.exists(arquivo): os.remove(arquivo)
        except: pass

    def falar(self, texto: str):
        if not texto: return
        self.parar_fala = False
        clean_text = re.sub(r'[*_#`]', '', texto).replace('\n', ' ').strip()
        temp_file = os.path.join(self.temp_audio_path, f"fala_{random.randint(1000, 9999)}.wav")

        try:
            async def save_edge_tts():
                voz = self.config.get("VOICE", "pt-BR-AntonioNeural")
                com = edge_tts.Communicate(clean_text, voz)
                await com.save(temp_file)
            asyncio.run(save_edge_tts())
            self._tocar_audio(temp_file)
            return
        except: pass

        if self.installer and self.installer.verificar_piper():
            try:
                cmd = f'echo {clean_text} | "{self.installer.piper_exe}" --model "{self.installer.voice_model}" --output_file "{temp_file}"'
                subprocess.run(cmd, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                self._tocar_audio(temp_file)
                return
            except: pass

        try:
            with self.audio_lock:
                engine = pyttsx3.init()
                engine.say(clean_text)
                engine.runAndWait()
                engine.stop()
        except: pass

    def calar_boca(self):
        self.parar_fala = True
        try:
            with self.audio_lock:
                if pygame.mixer.get_init(): pygame.mixer.music.stop()
        except: pass