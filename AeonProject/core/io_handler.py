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
    Versão Blindada: Aceita rodar sem Installer.
    """
    def __init__(self, config: dict, installer=None): # <--- Installer agora é opcional
        self.config = config if config else {} # Garante que config não seja None
        self.installer = installer
        self.parar_fala = False
        self.recalibrar_mic_flag = False
        
        # O caminho para a pasta de áudio temporário
        self.temp_audio_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "bagagem", "temp")
        os.makedirs(self.temp_audio_path, exist_ok=True)
        
        # Inicializa o Pygame Mixer para tocar áudio
        try:
            pygame.mixer.init()
        except Exception as e:
            log_display(f"Aviso: Não foi possível iniciar mixer de áudio: {e}")

    def _tocar_audio(self, arquivo: str):
        """Toca um arquivo de áudio e o apaga em seguida."""
        try:
            pygame.mixer.music.load(arquivo)
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                if self.parar_fala:
                    pygame.mixer.music.stop()
                    break
                time.sleep(0.1)
        except Exception as e:
            log_display(f"Erro ao tocar áudio: {e}")
        
        # O Gari: Limpa o arquivo de áudio após o uso
        threading.Thread(target=self._limpar_seguro, args=(arquivo,), daemon=True).start()

    def _limpar_seguro(self, arquivo: str):
        """Tenta deletar o arquivo com um pequeno delay."""
        time.sleep(0.5)
        try:
            if os.path.exists(arquivo):
                os.remove(arquivo)
        except Exception as e:
            pass # Silencia erro de limpeza

    def falar(self, texto: str):
        """
        Converte texto em fala usando um sistema de camadas.
        """
        if not texto:
            return

        self.parar_fala = False
        clean_text = re.sub(r'[*_#`]', '', texto).replace('\n', ' ').strip()
        
        # Define o caminho temporário
        temp_file = os.path.join(self.temp_audio_path, f"fala_{random.randint(1000, 9999)}.wav")

        # 1. Tenta Online (Edge-TTS)
        try:
            # A API do edge_tts requer um bloco async
            async def save_edge_tts():
                voz = self.config.get("VOICE", "pt-BR-AntonioNeural")
                comunicador = edge_tts.Communicate(clean_text, voz)
                await comunicador.save(temp_file)
            
            asyncio.run(save_edge_tts())
            self._tocar_audio(temp_file)
            return
        except Exception as e:
            log_display(f"Falha no Edge-TTS (online), tentando Piper. Erro: {e}")

        # 2. Tenta Offline Neural (Piper) - SOMENTE SE TIVER INSTALLER
        if self.installer and self.installer.verificar_piper():
            log_display("Usando Piper (Offline)...")
            try:
                cmd = f'echo {clean_text} | "{self.installer.piper_exe}" --model "{self.installer.voice_model}" --output_file "{temp_file}"'
                subprocess.run(cmd, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                self._tocar_audio(temp_file)
                return
            except Exception as e:
                log_display(f"Falha no Piper, tentando fallback robótico. Erro: {e}")

        # 3. Fallback Robótico (pyttsx3)
        try:
            # log_display("Usando voz de emergência (pyttsx3)...") # Opcional: Descomentar para debug
            engine = pyttsx3.init()
            engine.say(clean_text)
            engine.runAndWait()
            engine.stop()
        except Exception as e:
            log_display(f"Falha total no sistema de áudio: {e}")

    def calar_boca(self):
        """Interrompe imediatamente qualquer áudio."""
        self.parar_fala = True
        try:
            if pygame.mixer.get_init() and pygame.mixer.music.get_busy():
                pygame.mixer.music.stop()
        except: pass

    def recalibrar_mic(self):
        """Sinaliza para recalibrar o microfone."""
        self.recalibrar_mic_flag = True