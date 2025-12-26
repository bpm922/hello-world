import json
import os
from pathlib import Path
from typing import Dict, Any, Optional
import logging


class Settings:
    def __init__(self):
        self.config_dir = Path(__file__).parent
        self.project_root = self.config_dir.parent
        self.credentials_file = self.config_dir / "credentials.json"
        self.results_dir = self.project_root / "results"
        self.logs_dir = self.project_root / "logs"
        
        self._credentials: Dict[str, Any] = {}
        self._settings: Dict[str, Any] = self._default_settings()
        
        self._ensure_directories()
        self._load_credentials()

    def _default_settings(self) -> Dict[str, Any]:
        return {
            "export": {
                "default_format": "json",
                "auto_export": False,
                "output_directory": str(self.results_dir)
            },
            "search": {
                "timeout": 60,
                "max_concurrent": 5
            },
            "logging": {
                "level": "INFO",
                "file": str(self.logs_dir / "osint_tool.log")
            }
        }

    def _ensure_directories(self):
        self.results_dir.mkdir(exist_ok=True)
        self.logs_dir.mkdir(exist_ok=True)

    def _load_credentials(self):
        if self.credentials_file.exists():
            try:
                with open(self.credentials_file, 'r') as f:
                    self._credentials = json.load(f)
            except Exception as e:
                logging.error(f"Failed to load credentials: {e}")
                self._credentials = {}
        else:
            self._create_default_credentials()

    def _create_default_credentials(self):
        default_creds = {
            "api_keys": {
                "example_api": "your_api_key_here"
            },
            "credentials": {
                "example_service": {
                    "username": "your_username",
                    "password": "your_password"
                }
            }
        }
        try:
            with open(self.credentials_file, 'w') as f:
                json.dump(default_creds, f, indent=4)
            self._credentials = default_creds
        except Exception as e:
            logging.error(f"Failed to create default credentials: {e}")

    def get_credential(self, service: str, key: str) -> Optional[str]:
        return self._credentials.get(service, {}).get(key)

    def set_credential(self, service: str, key: str, value: str):
        if service not in self._credentials:
            self._credentials[service] = {}
        self._credentials[service][key] = value
        self._save_credentials()

    def _save_credentials(self):
        try:
            with open(self.credentials_file, 'w') as f:
                json.dump(self._credentials, f, indent=4)
        except Exception as e:
            logging.error(f"Failed to save credentials: {e}")

    def get_setting(self, *keys: str) -> Any:
        value = self._settings
        for key in keys:
            if isinstance(value, dict):
                value = value.get(key)
            else:
                return None
        return value

    def set_setting(self, value: Any, *keys: str):
        setting = self._settings
        for key in keys[:-1]:
            if key not in setting:
                setting[key] = {}
            setting = setting[key]
        setting[keys[-1]] = value


_settings_instance: Optional[Settings] = None


def get_settings() -> Settings:
    global _settings_instance
    if _settings_instance is None:
        _settings_instance = Settings()
    return _settings_instance
