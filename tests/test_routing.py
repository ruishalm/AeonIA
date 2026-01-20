"""
test_routing.py
===============
Testa roteamento de comandos via triggers
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'AeonProject'))

from core.module_manager import ModuleManager
from core.config_manager import ConfigManager
from core.brain import Brain
from core.io_handler import IOHandler
from modules.base_module import AeonModule
from typing import List, Dict


class MockSystemModule(AeonModule):
    """Mock do SistemaModule para testes."""
    
    def __init__(self, core_context):
        super().__init__(core_context)
        self.name = "SistemaTest"
        self.triggers = ["minimize", "maximizar", "fechar"]
        self.processed = []
    
    @property
    def dependencies(self) -> List[str]:
        return []
    
    @property
    def metadata(self) -> Dict[str, str]:
        return {"version": "1.0.0", "author": "test", "description": "Test"}
    
    def process(self, command: str) -> str:
        self.processed.append(command)
        return f"SistemaTest: {command}"


class MockRotinasModule(AeonModule):
    """Mock do RotinasModule para testes."""
    
    def __init__(self, core_context):
        super().__init__(core_context)
        self.name = "RotinasTest"
        self.triggers = ["rotina", "alarme", "lembrete"]
        self.processed = []
    
    @property
    def dependencies(self) -> List[str]:
        return []
    
    @property
    def metadata(self) -> Dict[str, str]:
        return {"version": "1.0.0", "author": "test", "description": "Test"}
    
    def process(self, command: str) -> str:
        self.processed.append(command)
        return f"RotinasTest: {command}"


def test_routing():
    """Testa roteamento de comandos."""
    
    print("\n" + "="*60)
    print("TESTE 5: Roteamento de Comandos")
    print("="*60)
    
    # Setup
    config = ConfigManager()
    brain = Brain(config=config.system_data, installer=None)
    io_handler = IOHandler(config=config.system_data, installer=None)
    
    core_context = {
        "config_manager": config,
        "brain": brain,
        "io_handler": io_handler
    }
    
    manager = ModuleManager(core_context)
    
    # Criar módulos de teste
    sistema = MockSystemModule(core_context)
    rotinas = MockRotinasModule(core_context)
    
    # Registrar manualmente (simulando load_modules)
    manager.modules = [sistema, rotinas]
    manager.module_map["sistematest"] = sistema
    manager.module_map["rotinastest"] = rotinas
    
    # Registrar triggers
    for trigger in sistema.triggers:
        manager.trigger_map[trigger] = sistema
    for trigger in rotinas.triggers:
        manager.trigger_map[trigger] = rotinas
    
    # ===== TESTE 1: Roteamento simples =====
    print("\n✓ Teste 5.1: Roteamento simples (trigger em SistemaModule)")
    result = manager.route_command("minimize a janela")
    assert "SistemaTest" in result, f"Deveria rotear para SistemaTest, mas: {result}"
    assert "minimize a janela" in sistema.processed, "Comando não foi registrado"
    print(f"  Resultado: {result}")
    print("  ✓ PASSOU")
    
    # ===== TESTE 2: Roteamento para outro módulo =====
    print("\n✓ Teste 5.2: Roteamento para RotinasModule")
    result = manager.route_command("criar rotina especial")
    assert "RotinasTest" in result, f"Deveria rotear para RotinasTest, mas: {result}"
    assert "criar rotina especial" in rotinas.processed, "Comando não foi registrado"
    print(f"  Resultado: {result}")
    print("  ✓ PASSOU")
    
    # ===== TESTE 3: Trigger com overlap =====
    print("\n✓ Teste 5.3: Prioridade - primeiro trigger found")
    # Se ambos tivessem "teste", qual seria acionado depende da ordem
    result = manager.route_command("alarme as 10 da manhã")
    assert "RotinasTest" in result, "Deveria rotear para RotinasTest"
    print(f"  Resultado: {result}")
    print("  ✓ PASSOU")
    
    # ===== TESTE 4: Trigger case-insensitive =====
    print("\n✓ Teste 5.4: Triggers são case-insensitive")
    result = manager.route_command("MINIMIZE a janela")
    assert "SistemaTest" in result, "Deveria encontrar 'minimize' em maiúscula"
    print("  ✓ PASSOU")
    
    # ===== TESTE 5: Dependências validadas =====
    print("\n✓ Teste 5.5: Dependências validadas antes de rotear")
    # Neste caso, ambos não têm dependências, então deveria funcionar
    assert sistema.check_dependencies(), "Sistema deveria ter deps OK"
    assert rotinas.check_dependencies(), "Rotinas deveria ter deps OK"
    print("  ✓ PASSOU")
    
    print("\n" + "="*60)
    print("✅ TODOS OS TESTES DE ROTEAMENTO PASSARAM!")
    print("="*60)


if __name__ == "__main__":
    try:
        test_routing()
    except AssertionError as e:
        print(f"\n❌ TESTE FALHOU: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ ERRO: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
