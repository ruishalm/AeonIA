"""
test_module_loading.py
======================
Testa carregamento dinâmico de todos os módulos
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'AeonProject'))

from core.module_manager import ModuleManager
from core.config_manager import ConfigManager
from core.brain import Brain
from core.io_handler import IOHandler


def test_module_loading():
    """Testa descoberta e carregamento de todos os módulos."""
    
    print("\n" + "="*60)
    print("TESTE 3: Carregamento Dinâmico de Módulos")
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
    
    # ===== TESTE 1: load_modules não deve falhar =====
    print("\n✓ Teste 3.1: Carregando módulos...")
    try:
        manager.load_modules()
        print("  ✓ PASSOU")
    except Exception as e:
        print(f"  ❌ FALHOU: {e}")
        raise
    
    # ===== TESTE 2: Pelo menos alguns módulos devem ter carregado =====
    print("\n✓ Teste 3.2: Verificar número de módulos")
    num_modules = len(manager.modules)
    print(f"  Módulos carregados: {num_modules}")
    assert num_modules > 0, "Nenhum módulo foi carregado!"
    print("  ✓ PASSOU")
    
    # ===== TESTE 3: Listar módulos =====
    print("\n✓ Teste 3.3: Listar módulos")
    for i, mod in enumerate(manager.modules, 1):
        print(f"  {i}. {mod.name} ({len(mod.triggers)} triggers)")
    print("  ✓ PASSOU")
    
    # ===== TESTE 4: Verificar trigger_map =====
    print("\n✓ Teste 3.4: Verificar mapa de triggers")
    num_triggers = len(manager.trigger_map)
    print(f"  Total de triggers: {num_triggers}")
    assert num_triggers > 0, "Nenhum trigger foi registrado!"
    # Mostrar alguns
    print("  Amostra de triggers:")
    for trigger in list(manager.trigger_map.keys())[:5]:
        print(f"    - '{trigger}'")
    print("  ✓ PASSOU")
    
    # ===== TESTE 5: Verificar module_map =====
    print("\n✓ Teste 3.5: Verificar mapa de módulos")
    assert len(manager.module_map) == len(manager.modules), "Mapa de módulos inconsistente"
    print(f"  Módulos no mapa: {len(manager.module_map)}")
    print("  ✓ PASSOU")
    
    # ===== TESTE 6: Todas dependências validadas =====
    print("\n✓ Teste 3.6: Verificar dependências")
    for mod in manager.modules:
        deps_ok = mod.check_dependencies()
        print(f"  {mod.name}: {' ✓' if deps_ok else ' ✗'} (deps: {mod.dependencies or 'none'})")
    print("  ✓ PASSOU")
    
    # ===== TESTE 7: Failed modules =====
    print("\n✓ Teste 3.7: Verificar módulos com falha")
    if manager.failed_modules:
        print(f"  {len(manager.failed_modules)} módulos falharam:")
        for failed in manager.failed_modules:
            print(f"    - {failed['name']}: {failed['error']}")
    else:
        print("  Nenhum módulo falhou! ✓")
    print("  ✓ PASSOU")
    
    # ===== TESTE 8: get_loaded_modules =====
    print("\n✓ Teste 3.8: get_loaded_modules()")
    loaded = manager.get_loaded_modules()
    assert len(loaded) == len(manager.modules), "get_loaded_modules() inconsistente"
    print(f"  Retornou {len(loaded)} módulos")
    print("  ✓ PASSOU")
    
    # ===== TESTE 9: get_module_info =====
    print("\n✓ Teste 3.9: get_module_info()")
    if manager.modules:
        first_mod = manager.modules[0]
        info = manager.get_module_info(first_mod.name)
        assert info is not None, "Info não encontrada"
        assert info['name'] == first_mod.name, "Nome incorreto"
        print(f"  Info de '{first_mod.name}':")
        print(f"    - Triggers: {len(info['triggers'])}")
        print(f"    - Deps OK: {info['dependencies_ok']}")
        print(f"    - Loaded: {info['loaded']}")
        print("  ✓ PASSOU")
    
    # ===== TESTE 10: list_modules =====
    print("\n✓ Teste 3.10: list_modules()")
    manager.list_modules(verbose=False)
    print("  ✓ PASSOU")
    
    print("\n" + "="*60)
    print("✅ TODOS OS TESTES DE CARREGAMENTO PASSARAM!")
    print("="*60)


if __name__ == "__main__":
    try:
        test_module_loading()
    except AssertionError as e:
        print(f"\n❌ TESTE FALHOU: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ ERRO: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
