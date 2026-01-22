import sys
import os
import importlib.util
import time

# Cores para o terminal
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
RESET = "\033[0m"

def status(msg, ok=True, warning=False):
    if warning:
        print(f"{YELLOW}[!] {msg}{RESET}")
    elif ok:
        print(f"{GREEN}[OK] {msg}{RESET}")
    else:
        print(f"{RED}[ERRO] {msg}{RESET}")

print(f"\n{GREEN}=== DIAGNÓSTICO DE SISTEMA AEON (V80) ==={RESET}")
print(f"Hardware Detectado: Python {sys.version.split()[0]} em {sys.platform}\n")

# 1. VERIFICAÇÃO DE BIBLIOTECAS
print("--- 1. Dependências ---")
libs = [
    "customtkinter", "pygame", "edge_tts", "groq", "ollama", 
    "psutil", "pyautogui", "pyttsx3", "speech_recognition", "pyaudio"
]
missing = []

for lib in libs:
    import_name = lib
    if lib == "speech_recognition": import_name = "speech_recognition"
    
    if importlib.util.find_spec(import_name):
        status(f"Biblioteca '{lib}' encontrada.")
    else:
        status(f"Biblioteca '{lib}' AUSENTE.", ok=False)
        missing.append(lib)

if missing:
    print(f"\n{RED}FALTA INSTALAR:{RESET} pip install {' '.join(missing)}")
else:
    print("Todas as dependências estão ok.\n")

# 2. VERIFICAÇÃO DE I.A. LOCAL (OLLAMA)
print("--- 2. Inteligência Local (Ollama) ---")
try:
    import requests
    resp = requests.get("http://localhost:11434", timeout=2)
    if resp.status_code == 200:
        status("Serviço Ollama está rodando.")
        import ollama
        try:
            models = [m['name'] for m in ollama.list()['models']]
            print(f"   Modelos encontrados: {', '.join(models)}")
        except:
            status("Ollama rodando, mas não consegui listar modelos.", warning=True)
    else:
        status(f"Ollama respondeu com erro: {resp.status_code}", warning=True)
except Exception as e:
    status("Ollama NÃO detectado. Verifique se o app está aberto.", ok=False)
print("")

# 3. VERIFICAÇÃO DE ÁUDIO
print("--- 3. Drivers de Áudio ---")
try:
    import pygame
    pygame.mixer.init()
    status("Mixer de Áudio (Pygame) inicializado.")
    pygame.mixer.quit()
except Exception as e:
    status(f"Falha no driver de áudio: {e}", ok=False)

print(f"\n{GREEN}=== FIM DO DIAGNÓSTICO ==={RESET}")