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
    Gerencia toda a entrada (microfone) e saída (áudio/fala) do assistente.
    Versão Thread-Safe com Lock.
    """
    def __init__(self, config: dict, installer=None):
        self.config = config if config else {}
        self.installer = installer
        self.parar_fala = False
        self.recalibrar_mic_flag = False
        self.audio_lock = threading.Lock() # <--- CORREÇÃO: Segurança de Thread
        
        self.temp_audio_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "bagagem", "temp")
        os.makedirs(self.temp_audio_path, exist_ok=True)
        
        try:
            pygame.mixer.init()
        except Exception as e:
            log_display(f"Aviso: Não foi possível iniciar mixer de áudio: {e}")

    def _tocar_audio(self, arquivo: str):
        """Toca um arquivo de áudio de forma segura."""
        # Usa o Lock para garantir que só um áudio carregue por vez
        with self.audio_lock:
            try:
                # Se já estiver tocando, para o anterior
                if pygame.mixer.music.get_busy():
                    pygame.mixer.music.stop()
                
                pygame.mixer.music.load(arquivo)
                pygame.mixer.music.play()
            except Exception as e:
                log_display(f"Erro ao tocar áudio: {e}")
                return

        # Loop de espera (fora do lock para não travar o sistema, mas verificando flags)
        while pygame.mixer.music.get_busy():
            if self.parar_fala:
                pygame.mixer.music.stop()
                break
            time.sleep(0.1)
        
        threading.Thread(target=self._limpar_seguro, args=(arquivo,), daemon=True).start()

    def _limpar_seguro(self, arquivo: str):
        """Tenta deletar o arquivo com um pequeno delay."""
        time.sleep(0.5)
        try:
            if os.path.exists(arquivo):
                os.remove(arquivo)
        except Exception as e:
            pass

    def falar(self, texto: str):
        if not texto: return

        self.parar_fala = False
        clean_text = re.sub(r'[*_#`]', '', texto).replace('\n', ' ').strip()
        temp_file = os.path.join(self.temp_audio_path, f"fala_{random.randint(1000, 9999)}.wav")

        # 1. Tenta Online (Edge-TTS)
        try:
            async def save_edge_tts():
                voz = self.config.get("VOICE", "pt-BR-AntonioNeural")
                comunicador = edge_tts.Communicate(clean_text, voz)
                await comunicador.save(temp_file)
            
            asyncio.run(save_edge_tts())
            self._tocar_audio(temp_file)
            return
        except Exception as e:
            log_display(f"Falha no Edge-TTS, tentando fallback. Erro: {e}")

        # 2. Tenta Offline Neural (Piper)
        if self.installer and self.installer.verificar_piper():
            try:
                cmd = f'echo {clean_text} | "{self.installer.piper_exe}" --model "{self.installer.voice_model}" --output_file "{temp_file}"'
                subprocess.run(cmd, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                self._tocar_audio(temp_file)
                return
            except: pass

        # 3. Fallback Robótico (pyttsx3)
        try:
            with self.audio_lock: # Protege também o pyttsx3
                engine = pyttsx3.init()
                engine.say(clean_text)
                engine.runAndWait()
                engine.stop()
        except Exception as e:
            log_display(f"Falha total no áudio: {e}")

    def calar_boca(self):
        self.parar_fala = True
        try:
            with self.audio_lock:
                if pygame.mixer.get_init():
                    pygame.mixer.music.stop()
        except: pass

    def recalibrar_mic(self):
        self.recalibrar_mic_flag = True