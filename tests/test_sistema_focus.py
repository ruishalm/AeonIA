"""
test_sistema_focus.py
======================
Testa o Sistema de Foco (lock_focus, release_focus, focused_module)
"""

import sys
import os

# Adicionar AeonProject ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'AeonProject'))

from core.module_manager import ModuleManager
from core.config_manager import ConfigManager
from core.brain import Brain
from core.io_handler import IOHandler
from modules.base_module import AeonModule
from typing import List, Dict


class TestModuleFocus(AeonModule):
    """Módulo dummy para testar foco."""
    
    def __init__(self, core_context):
        super().__init__(core_context)
        self.name = "TestModuleFocus"
        self.triggers = ["teste"]
        self.received_commands = []
    
    @property
    def dependencies(self) -> List[str]:
        return []
    
    @property
    def metadata(self) -> Dict[str, str]:
        return {"version": "1.0.0", "author": "test", "description": "Test"}
    
    def process(self, command: str) -> str:
        self.received_commands.append(command)
        return f"TestModule recebeu: {command}"


def test_focus_system():
    """Testa lock_focus, release_focus e roteamento."""
    
    print("\n" + "="*60)
    print("TESTE 1: Sistema de Foco")
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
    test_module = TestModuleFocus(core_context)
    
    # ===== TESTE 1: Foco inicial é None =====
    print("\n✓ Teste 1.1: Foco inicial deve ser None")
    assert manager.focused_module is None, "Foco deveria ser None no início"
    assert not manager.is_focused(), "is_focused() deveria ser False"
    print("  ✓ PASSOU")
    
    # ===== TESTE 2: lock_focus funciona =====
    print("\n✓ Teste 1.2: lock_focus() deve travar foco")
    manager.lock_focus(test_module)
    assert manager.focused_module == test_module, "Foco não foi travado"
    assert manager.is_focused(), "is_focused() deveria ser True"
    print("  ✓ PASSOU")
    
    # ===== TESTE 3: Roteamento com foco travado =====
    print("\n✓ Teste 1.3: Com foco travado, comando vai direto para módulo")
    result = manager.route_command("comando teste 1")
    assert "TestModule recebeu" in result, "Comando não chegou ao módulo"
    assert len(test_module.received_commands) == 1, "Módulo não recebeu comando"
    print(f"  Resultado: {result}")
    print("  ✓ PASSOU")
    
    # ===== TESTE 4: Ignora triggers com foco travado =====
    print("\n✓ Teste 1.4: Triggers devem ser ignorados com foco travado")
    # Mesmo com trigger "teste", deve ir direto para focused_module
    result = manager.route_command("teste xyz abc")
    assert "TestModule recebeu" in result, "Deveria ignorar trigger e enviar direto"
    print(f"  Resultado: {result}")
    print("  ✓ PASSOU")
    
    # ===== TESTE 5: release_focus funciona =====
    print("\n✓ Teste 1.5: release_focus() deve liberar foco")
    manager.release_focus()
    assert manager.focused_module is None, "Foco não foi liberado"
    assert not manager.is_focused(), "is_focused() deveria ser False"
    print("  ✓ PASSOU")
    
    # ===== TESTE 6: get_focused_module =====
    print("\n✓ Teste 1.6: get_focused_module() com e sem foco")
    assert manager.get_focused_module() is None, "Deveria ser None"
    manager.lock_focus(test_module)
    assert manager.get_focused_module() == test_module, "Deveria retornar módulo"
    manager.release_focus()
    print("  ✓ PASSOU")
    
    print("\n" + "="*60)
    print("✅ TODOS OS TESTES DE FOCO PASSARAM!")
    print("="*60)


if __name__ == "__main__":
    try:
        test_focus_system()
    except AssertionError as e:
        print(f"\n❌ TESTE FALHOU: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ ERRO: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
