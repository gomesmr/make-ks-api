import json
import os

from src.constants import CONFIG_DIR, PATH_PREFIX_CONFIG


def get_path_prefix():
    """Obtém o prefixo de path configurado ou detecta automaticamente"""
    try:
        with open(PATH_PREFIX_CONFIG, 'r') as f:
            config = json.load(f)
            return config.get('prefix', '')
    except (FileNotFoundError, json.JSONDecodeError):
        home = os.path.expanduser("~")
        common_patterns = ['stk-dev', 'projects', 'workspace', 'dev', 'code']
        for pattern in common_patterns:
            potential_prefix = os.path.join(home, pattern)
            if os.path.isdir(potential_prefix):
                return potential_prefix + os.sep
        return ''


def set_path_prefix(prefix):
    """Define o prefixo de path a ser removido"""
    with open(PATH_PREFIX_CONFIG, 'w') as f:
        json.dump({'prefix': prefix}, f, indent=2)
    print(f"✅ Prefixo de path configurado: {prefix}")


def save_config(config_name, config_data):
    config_path = os.path.join(CONFIG_DIR, f"{config_name}.json")
    try:
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config_data, f, indent=2)
        print(f"✅ Configuração '{config_name}' salva com sucesso!")
        print(f"📁 Local: {config_path}")
        return True
    except Exception as e:
        print(f"❌ Erro ao salvar configuração: {e}")
        return False


def load_config(config_name):
    config_path = os.path.join(CONFIG_DIR, f"{config_name}.json")
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"❌ Configuração '{config_name}' não encontrada.")
        return None
    except Exception as e:
        print(f"❌ Erro ao carregar configuração: {e}")
        return None


def list_configs():
    configs = [f.replace('.json', '') for f in os.listdir(CONFIG_DIR) if
               f.endswith('.json') and f != 'path_prefix.json']
    return configs


def delete_config(config_name):
    config_path = os.path.join(CONFIG_DIR, f"{config_name}.json")
    try:
        os.remove(config_path)
        print(f"✅ Configuração '{config_name}' removida.")
        return True
    except FileNotFoundError:
        print(f"❌ Configuração '{config_name}' não encontrada.")
        return False
    except Exception as e:
        print(f"❌ Erro ao remover configuração: {e}")
        return False
