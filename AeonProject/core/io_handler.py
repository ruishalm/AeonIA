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

# O core_context idealmente teria um logger e a config
# Por agora, vamos usar prints para simplicidade
def log_display(msg):
    print(f"[IO_HANDLER] {msg}")

class IOHandler:
    """
    Gerencia toda a entrada (microfone) e saída (áudio/fala) do assistente.
    """
    def __init__(self, config: dict, installer):
        self.config = config
        self.installer = installer
        self.parar_fala = False
        self.recalibrar_mic_flag = False
        
        # O caminho para a pasta de áudio temporário na nova estrutura
        self.temp_audio_path = os.path.join("AeonProject", "bagagem", "temp")
        os.makedirs(self.temp_audio_path, exist_ok=True)
        
        # Inicializa o Pygame Mixer para tocar áudio
        pygame.mixer.init()

    def _tocar_audio(self, arquivo: str):
        """
        Toca um arquivo de áudio e o apaga em seguida.
        """
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
        threading.Thread(target=self._limpar_seguro, args=(arquivo,)).start()

    def _limpar_seguro(self, arquivo: str):
        """Tenta deletar o arquivo com um pequeno delay."""
        time.sleep(0.5)
        try:
            if os.path.exists(arquivo):
                os.remove(arquivo)
        except Exception as e:
            log_display(f"Falha ao limpar arquivo temporário {arquivo}: {e}")

    def falar(self, texto: str):
        """
        Converte texto em fala usando um sistema de camadas (online > offline neural > fallback).
        """
        if not texto:
            return

        self.parar_fala = False
        clean_text = re.sub(r'[*_#`]', '', texto).replace('\n', ' ').strip()
        
        # Define o caminho completo para o arquivo de áudio temporário
        temp_file = os.path.join(self.temp_audio_path, f"fala_{random.randint(1000, 9999)}.wav")

        # 1. Tenta Online (Edge-TTS)
        try:
            # A API do edge_tts requer um bloco async
            async def save_edge_tts():
                comunicador = edge_tts.Communicate(clean_text, self.config.get("VOICE", "pt-BR-AntonioNeural"))
                await comunicador.save(temp_file)
            
            asyncio.run(save_edge_tts())
            self._tocar_audio(temp_file)
            return
        except Exception as e:
            log_display(f"Falha no Edge-TTS (online), tentando Piper. Erro: {e}")

        # 2. Tenta Offline Neural (Piper)
        if self.installer.verificar_piper():
            log_display("Usando Piper (Offline)...")
            try:
                # O comando do Piper precisa de aspas para lidar com espaços nos caminhos
                cmd = f'echo {clean_text} | "{self.installer.piper_exe}" --model "{self.installer.voice_model}" --output_file "{temp_file}"'
                subprocess.run(cmd, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                self._tocar_audio(temp_file)
                return
            except Exception as e:
                log_display(f"Falha no Piper, tentando fallback robótico. Erro: {e}")

        # 3. Fallback Robótico (pyttsx3)
        try:
            log_display("Usando voz de emergência (pyttsx3)...")
            engine = pyttsx3.init()
            engine.say(clean_text)
            engine.runAndWait()
            engine.stop()
        except Exception as e:
            log_display(f"Falha total no sistema de áudio: {e}")

    def calar_boca(self):
        """
        Interrompe imediatamente qualquer áudio que esteja sendo reproduzido.
        """
        self.parar_fala = True
        log_display("Comando de silêncio recebido.")
        try:
            if pygame.mixer.get_init() and pygame.mixer.music.get_busy():
                pygame.mixer.music.stop()
        except Exception as e:
            log_display(f"Erro ao tentar parar a música: {e}")

    def recalibrar_mic(self):
        """Sinaliza para o loop de voz para recalibrar o microfone."""
        log_display("Sinal de recalibração recebido.")
        self.recalibrar_mic_flag = True

