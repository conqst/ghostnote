import os
import json
import base64
import hashlib

# Path to the config file stored in user's AppData directory
CONFIG_PATH = os.path.join(
    os.getenv('LOCALAPPDATA', os.getenv('APPDATA', os.path.expanduser('~'))),
    "GhostNote",
    "config.json"
)

def create_default_config() -> dict:
    """
    Creates a default configuration file with initial password and hotkeys.
    """
    default_password = "1234"
    salt_bytes = os.urandom(16)
    salt_b64 = base64.b64encode(salt_bytes).decode('utf-8')
    password_hash = hashlib.sha256((default_password + salt_b64).encode('utf-8')).hexdigest()
    config = {
        "password_hash": password_hash,
        "salt": salt_b64,
        "gui_hotkey": "<ctrl>+<alt>+g",
        "keylogger_hotkey": "<ctrl>+<alt>+k"
    }
    os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
    with open(CONFIG_PATH, 'w') as f:
        json.dump(config, f, indent=4)
    return config

def load_config() -> dict:
    """
    Loads configuration from disk.
    """
    with open(CONFIG_PATH, 'r') as f:
        return json.load(f)

def save_config(config: dict):
    """
    Saves the configuration to disk.
    """
    with open(CONFIG_PATH, 'w') as f:
        json.dump(config, f, indent=4)
