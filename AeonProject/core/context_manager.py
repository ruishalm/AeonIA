import json
import os
import time
from datetime import datetime

class ContextManager:
    """
    O 'Quadro Branco' do Aeon.
    Permite que módulos compartilhem dados entre si sem acoplamento.
    Exemplo: Visão salva 'erro_lido', Dev lê 'erro_lido'.
    """
    def __init__(self):
        self.data = {}
        self.metadata = {} # Para guardar timestamps (TTL)

    def set(self, key: str, value, ttl: int = None):
        """
        Salva um dado no contexto.
        Args:
            key: Nome da chave (ex: 'clipboard_content')
            value: O valor (pode ser qualquer objeto)
            ttl: (Opcional) Tempo de vida em segundos. Se passar, o dado expira.
        """
        self.data[key] = value
        self.metadata[key] = {
            "created_at": time.time(),
            "ttl": ttl
        }
        # Log simples para debug (pode ser removido em produção)
        print(f"[CONTEXT] '{key}' atualizado.")

    def get(self, key: str):
        """
        Recupera um dado. Retorna None se não existir ou tiver expirado.
        """
        if key not in self.data:
            return None
        
        # Checagem de Expiração (TTL)
        meta = self.metadata.get(key)
        if meta and meta["ttl"]:
            if time.time() - meta["created_at"] > meta["ttl"]:
                print(f"[CONTEXT] '{key}' expirou e foi removido.")
                del self.data[key]
                del self.metadata[key]
                return None
        
        return self.data[key]

    def get_all(self):
        """Retorna todo o contexto atual (útil para debug)."""
        # Limpa expirados antes de retornar
        keys = list(self.data.keys())
        for k in keys:
            self.get(k) 
        return self.data

    def save_snapshot(self, path="bagagem/memory_dump.json"):
        """Salva o estado atual em JSON para persistência entre reboots."""
        try:
            # Filtra apenas dados serializáveis (strings, dicts, lists)
            serializable_data = {k: v for k, v in self.data.items() if isinstance(v, (str, int, float, bool, list, dict))}
            
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "w", encoding="utf-8") as f:
                json.dump(serializable_data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"[CONTEXT] Erro ao salvar snapshot: {e}")
            return False

    def load_snapshot(self, path="bagagem/memory_dump.json"):
        """Carrega estado anterior do JSON."""
        if not os.path.exists(path):
            return False
        try:
            with open(path, "r", encoding="utf-8") as f:
                loaded = json.load(f)
                self.data.update(loaded)
            return True
        except Exception as e:
            print(f"[CONTEXT] Erro ao carregar snapshot: {e}")
            return False