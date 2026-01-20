import json
import os

class ConfigManager:
    """
    Gerencia o carregamento e salvamento de todos os arquivos de configuração
    e dados persistentes do Aeon, como sistema, tarefas e memória.
    """
    def __init__(self, storage_path="AeonProject/bagagem"):
        self.storage_path = storage_path
        os.makedirs(self.storage_path, exist_ok=True)
        
        self.sys_path = os.path.join(self.storage_path, "system.json")
        self.tasks_path = os.path.join(self.storage_path, "tasks.json")
        self.mem_path = os.path.join(self.storage_path, "memoria.json")
        self.history_path = os.path.join(self.storage_path, "historico.json")

        self.system_data = self._load_json(self.sys_path, default={"apps": {}, "routines": {}, "triggers": [], "themes": {}})
        self.tasks = self._load_json(self.tasks_path, default=[])
        self.memory = self._load_json(self.mem_path, default=[])
        self.history = self._load_json(self.history_path, default={"conversations": [], "last_context": ""})

    def _load_json(self, file_path, default=None):
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                try:
                    return json.load(f)
                except json.JSONDecodeError:
                    return default if default is not None else {}
        return default if default is not None else {}

    def _save_json(self, file_path, data):
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)

    # --- Métodos do Sistema ---
    def get_system_data(self, key, default=None):
        return self.system_data.get(key, default)

    def set_system_data(self, key, value):
        self.system_data[key] = value
        self._save_json(self.sys_path, self.system_data)

    # --- Métodos de Tarefas (TaskManager) ---
    def get_tasks(self):
        return self.tasks

    def add_task(self, task_data):
        self.tasks.append(task_data)
        self._save_json(self.tasks_path, self.tasks)

    def save_tasks(self):
        self._save_json(self.tasks_path, self.tasks)

    # --- Métodos de Memória (Conversa) ---
    def get_memory(self):
        return self.memory
    
    def add_to_memory(self, user_input, aeon_response, timestamp):
        self.memory.append({"user": user_input, "aeon": aeon_response, "time": str(timestamp)})
        # Salva apenas as últimas 20 interações
        self._save_json(self.mem_path, self.memory[-20:])

    # --- Métodos de Histórico (Contexto Persistente) ---
    def get_history(self):
        """Retorna o histórico completo de conversas"""
        return self.history.get("conversations", [])
    
    def add_to_history(self, user_input, aeon_response):
        """Adiciona uma interação ao histórico"""
        import datetime
        interaction = {
            "timestamp": datetime.datetime.now().isoformat(),
            "user": user_input,
            "aeon": aeon_response
        }
        self.history["conversations"].append(interaction)
        # Mantém apenas as últimas 50 conversas
        if len(self.history["conversations"]) > 50:
            self.history["conversations"] = self.history["conversations"][-50:]
        self._save_json(self.history_path, self.history)
    
    def get_last_context(self):
        """Retorna o último contexto salvo"""
        return self.history.get("last_context", "")
    
    def save_context(self, context):
        """Salva contexto atual para próximas sessões"""
        self.history["last_context"] = context
        self._save_json(self.history_path, self.history)

