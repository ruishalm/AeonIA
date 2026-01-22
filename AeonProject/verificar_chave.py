import os
from pathlib import Path
import json
import sys

# Cores para facilitar a leitura
GREEN = "\033[92m"
RED = "\033[91m"
RESET = "\033[0m"

print(f"\n{GREEN}=== INÍCIO DA INVESTIGAÇÃO ==={RESET}")
print(f"Diretório atual: {os.getcwd()}")

# Define os caminhos prováveis
base = Path(os.getcwd())
caminho_correto = base / "bagagem" / "system.json"
caminho_txt = base / "bagagem" / "system.json.txt"
pasta_bagagem = base / "bagagem"

# 1. Verifica se a pasta existe
if not pasta_bagagem.exists():
    print(f"{RED}[X] A pasta 'bagagem' NÃO existe!{RESET}")
    print(f"    Esperado: {pasta_bagagem}")
    sys.exit()
else:
    print(f"{GREEN}[OK] A pasta 'bagagem' existe.{RESET}")

# 2. Verifica se o arquivo existe (e se não é um .txt escondido)
if caminho_correto.exists():
    if caminho_correto.is_dir():
         print(f"{RED}[X] ERRO CRÍTICO: 'system.json' é uma PASTA, não um arquivo!{RESET}")
         print("    Solução: Delete essa pasta e crie um ARQUIVO chamado system.json")
    else:
        print(f"{GREEN}[OK] O arquivo 'system.json' foi encontrado.{RESET}")
        # Tenta ler a chave
        try:
            with open(caminho_correto, 'r', encoding='utf-8') as f:
                dados = json.load(f)
                chave = dados.get("GROQ_KEY", "")
                if chave.startswith("gsk_"):
                    print(f"{GREEN}[SUCESSO] Chave Válida encontrada! (Começa com gsk...){RESET}")
                    print("\nSe o Aeon ainda não conecta, o erro está no 'main.py' ou 'config_manager.py'.")
                else:
                    print(f"{RED}[!] O arquivo existe, mas a chave 'GROQ_KEY' está vazia ou errada.{RESET}")
                    print(f"    Conteúdo lido: {dados}")
        except json.JSONDecodeError:
            print(f"{RED}[X] O arquivo existe, mas o texto dentro dele NÃO é um JSON válido.{RESET}")
            print("    Verifique se não faltam aspas ou chaves { }.")

elif caminho_txt.exists():
    print(f"\n{RED}[ACHEI O CULPADO!] Você criou 'system.json.txt'.{RESET}")
    print("O Windows escondeu a extensão '.txt'.")
    print(f"-> Renomeie o arquivo de 'system.json.txt' para 'system.json'")

else:
    print(f"\n{RED}[X] Arquivo não encontrado!{RESET}")
    print(f"    Procurei por: {caminho_correto}")
    print("    Conteúdo da pasta 'bagagem':")
    try:
        for item in os.listdir(pasta_bagagem):
            print(f"     - {item}")
    except: pass

print(f"\n{GREEN}=== FIM DA INVESTIGAÇÃO ==={RESET}")
input("Pressione ENTER para sair...")