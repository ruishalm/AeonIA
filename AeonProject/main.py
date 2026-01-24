import sys
import os

# Ajusta caminho para encontrar os módulos
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    # Tenta iniciar a Interface Esférica (PyQt6)
    try:
        from PyQt6.QtWidgets import QApplication
        from core.gui_sphere import AeonSphere
        
        print("[BOOT] Iniciando Interface Neural (Esfera)...")
        qt_app = QApplication(sys.argv)
        sphere = AeonSphere()
        sphere.show()
        
        sys.exit(qt_app.exec())

    except Exception as e:
        print(f"\n[ERRO CRÍTICO] Falha ao iniciar Esfera: {e}")
        print("[DICA] Alguma biblioteca pode estar faltando. Tente rodar: python -m pip install -r requirements.txt")
        print("[BOOT] Ativando Protocolo de Segurança (GUI Clássica)...")
        
        from core.gui_app import AeonGUI
        app = AeonGUI()
        app.mainloop()