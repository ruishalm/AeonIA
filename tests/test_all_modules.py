"""
test_all_modules.py
===================
Suite de testes para todos os módulos principais
Execute este arquivo para rodar TODOS os testes
"""

import sys
import os
import subprocess

# Adicionar AeonProject ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'AeonProject'))


def run_test(test_file):
    """Executa um arquivo de teste."""
    test_path = os.path.join(os.path.dirname(__file__), test_file)
    print(f"\n{'='*70}")
    print(f"Executando: {test_file}")
    print(f"{'='*70}")
    
    result = subprocess.run([sys.executable, test_path], capture_output=False)
    return result.returncode == 0


def main():
    """Executa todos os testes."""
    
    print("""
    ╔══════════════════════════════════════════════════════════════════════╗
    ║                   AEON V80 - SUITE DE TESTES                         ║
    ╚══════════════════════════════════════════════════════════════════════╝
    """)
    
    tests = [
        ("test_sistema_focus.py", "Sistema de Foco (lock/release)"),
        ("test_typewriter_module.py", "TypewriterModule"),
        ("test_module_loading.py", "Carregamento Dinâmico"),
        ("test_code_rendering.py", "Code Rendering"),
    ]
    
    results = {}
    
    for test_file, description in tests:
        print(f"\n[TEST] {description}")
        try:
            success = run_test(test_file)
            results[description] = "✅ PASSOU" if success else "❌ FALHOU"
        except Exception as e:
            print(f"Erro ao executar {test_file}: {e}")
            results[description] = "❌ ERRO"
    
    # Resumo final
    print("\n\n" + "="*70)
    print("RESUMO DOS TESTES")
    print("="*70)
    
    passed = sum(1 for r in results.values() if "PASSOU" in r)
    total = len(results)
    
    for test_name, result in results.items():
        print(f"{result} - {test_name}")
    
    print(f"\n{'='*70}")
    print(f"Total: {passed}/{total} testes passaram")
    print(f"{'='*70}")
    
    # Retornar 0 se todos passaram, 1 caso contrário
    return 0 if passed == total else 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
