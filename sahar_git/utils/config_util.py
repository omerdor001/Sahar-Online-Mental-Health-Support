import logging
import json
import os


class ConfigUtil:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance

    def init(
        self,
        config_path="config.json",
    ):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        parent_dir = os.path.dirname(current_dir)  # Go up one directory level
        relative_path = os.path.join(parent_dir, "config.json")

        self._config_path = relative_path
        self._config_data = None
        self.load_config()

    def load_config(self):
        try:
            with open(self._config_path, "r") as config_file:
                self._config_data = json.load(config_file)
        except FileNotFoundError as e:
            logging.error(f"Config file '{self._config_path}' not found. {e}")
            self._config_data = {}

    def get_config_attribute(self, attributeName):
        attribute = self._config_data.get(attributeName)
        return attribute

    def set_config_path(self, config_path):
        self._config_path = config_path