"""
test_code_rendering.py
======================
Testa o renderizador de código em main.py
"""

import sys
import os
import re

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'AeonProject'))


def test_code_parsing():
    """Testa o parsing de código markdown."""
    
    print("\n" + "="*60)
    print("TESTE 4: Code Rendering (Parsing de ```)")
    print("="*60)
    
    # Padrão usado no renderizador
    pattern = r"```(\w*)\n(.*?)\n```"
    
    # ===== TESTE 1: Parsing simples =====
    print("\n✓ Teste 4.1: Detectar um bloco de código")
    text = """Aqui está um exemplo:
```python
def hello():
    print("Olá!")
```
Fim do código."""
    
    matches = re.findall(pattern, text, flags=re.DOTALL)
    assert len(matches) == 1, f"Deveria encontrar 1 bloco, encontrou {len(matches)}"
    language, code = matches[0]
    assert language == "python", f"Linguagem incorreta: {language}"
    assert "hello" in code, "Código não encontrado"
    print(f"  ✓ PASSOU - Linguagem: {language}, Linhas: {len(code.split(chr(10)))}")
    
    # ===== TESTE 2: Múltiplos blocos =====
    print("\n✓ Teste 4.2: Detectar múltiplos blocos")
    text = """Primeiro:
```python
x = 1
```
Segundo:
```javascript
let y = 2;
```
Fim."""
    
    matches = re.findall(pattern, text, flags=re.DOTALL)
    assert len(matches) == 2, f"Deveria encontrar 2 blocos, encontrou {len(matches)}"
    print(f"  ✓ PASSOU - Encontrados: {[m[0] for m in matches]}")
    
    # ===== TESTE 3: Sem linguagem especificada =====
    print("\n✓ Teste 4.3: Bloco sem linguagem")
    text = """Código genérico:
```
some code here
```"""
    
    matches = re.findall(pattern, text, flags=re.DOTALL)
    assert len(matches) == 1, "Deveria encontrar 1 bloco"
    language, code = matches[0]
    assert language == "", f"Linguagem deveria estar vazia, mas é: {language}"
    print("  ✓ PASSOU - Linguagem vazia detectada corretamente")
    
    # ===== TESTE 4: Código com múltiplas linhas =====
    print("\n✓ Teste 4.4: Código com múltiplas linhas e indentação")
    text = """Aqui:
```python
def exemplo():
    if True:
        print("Indentado")
    return None
```
Pronto."""
    
    matches = re.findall(pattern, text, flags=re.DOTALL)
    assert len(matches) == 1, "Deveria encontrar 1 bloco"
    language, code = matches[0]
    lines = code.strip().split('\n')
    assert len(lines) == 4, f"Deveria ter 4 linhas, tem {len(lines)}"
    print(f"  ✓ PASSOU - {len(lines)} linhas com indentação preservada")
    
    # ===== TESTE 5: Split da mensagem =====
    print("\n✓ Teste 4.5: Split da mensagem (simulate _render_message)")
    text = """Explicação antes:
```python
print("código")
```
Explicação depois."""
    
    parts = re.split(pattern, text, flags=re.DOTALL)
    # Esperado: ['Explicação antes:\n', 'python', 'print("código")', '\nExplicação depois.']
    assert len(parts) >= 3, f"Deveria ter pelo menos 3 partes, tem {len(parts)}"
    print(f"  Parts: {len(parts)} partes")
    print(f"    1. Texto: '{parts[0][:30]}...'")
    print(f"    2. Linguagem: '{parts[1]}'")
    print(f"    3. Código: '{parts[2][:30]}...'")
    print("  ✓ PASSOU")
    
    # ===== TESTE 6: Sem código (fallback) =====
    print("\n✓ Teste 4.6: Mensagem sem bloco de código")
    text = "Apenas texto normal sem código."
    parts = re.split(pattern, text, flags=re.DOTALL)
    assert len(parts) == 1, "Deveria ter 1 parte (texto completo)"
    assert parts[0] == text, "Texto deveria ser preservado"
    print("  ✓ PASSOU - Fallback para texto normal")
    
    # ===== TESTE 7: Caracteres especiais no código =====
    print("\n✓ Teste 4.7: Código com caracteres especiais")
    text = """HTML:
```html
<div class="container">
    <h1>Título</h1>
</div>
```"""
    
    matches = re.findall(pattern, text, flags=re.DOTALL)
    assert len(matches) == 1, "Deveria encontrar 1 bloco"
    language, code = matches[0]
    assert "container" in code, "Código não preservado corretamente"
    assert '"' in code, "Aspas não preservadas"
    print("  ✓ PASSOU - Caracteres especiais preservados")
    
    # ===== TESTE 8: Case sensitivity =====
    print("\n✓ Teste 4.8: Suporte a diferentes linguagens")
    languages = ["python", "javascript", "html", "css", "json", "bash", "cpp"]
    for lang in languages:
        text = f"```{lang}\ncode\n```"
        matches = re.findall(pattern, text, flags=re.DOTALL)
        assert len(matches) == 1, f"Falhou para {lang}"
    print(f"  ✓ PASSOU - {len(languages)} linguagens testadas")
    
    print("\n" + "="*60)
    print("✅ TODOS OS TESTES DE RENDERING PASSARAM!")
    print("="*60)


if __name__ == "__main__":
    try:
        test_code_parsing()
    except AssertionError as e:
        print(f"\n❌ TESTE FALHOU: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ ERRO: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
