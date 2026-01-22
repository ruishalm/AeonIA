import shutil
import os
import sys
from pathlib import Path

def limpar_lixo():
    base = Path(os.getcwd())
    print(f"🧹 INICIANDO LIMPEZA EM: {base}")

    # 1. Matar Cache (Obrigatório para ler seu código novo)
    caches = list(base.rglob("__pycache__"))
    for cache in caches:
        try:
            shutil.rmtree(cache)
            print(f"   [DELETADO] Cache velho: {cache.name}")
        except: pass

    # 2. Matar a Pasta Fantasma (Boneca Russa)
    pasta_fantasma = base / "AeonProject"
    if pasta_fantasma.exists() and pasta_fantasma.is_dir():
        try:
            shutil.rmtree(pasta_fantasma)
            print(f"   [DELETADO] Pasta fantasma 'AeonProject' (Lixo)")
        except Exception as e:
            print(f"   [ERRO] Não consegui apagar a pasta fantasma: {e}")

    print("✅ Limpeza concluída. O Python agora é OBRIGADO a ler o código novo.")
    print("-" * 50)

def rodar_aeon():
    print("🚀 Iniciando Aeon...")
    # Importa e roda o main diretamente para garantir o mesmo processo
    try:
        import main
        app = main.AeonGUI()
        app.mainloop()
    except Exception as e:
        print(f"❌ ERRO FATAL AO INICIAR: {e}")
        input("Pressione Enter para ver o erro...")

if __name__ == "__main__":
    limpar_lixo()
    rodar_aeon()