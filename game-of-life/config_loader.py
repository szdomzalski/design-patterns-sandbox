from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Tuple, Type
import json
import os

from event_handling import EventType


@dataclass
class UIConfig:
    width: int
    height: int
    grid_width: int
    grid_height: int
    buttons: List[Tuple[str, int, int, int, int]]


class ConfigLoader(ABC):
    @abstractmethod
    def get_config(self) -> UIConfig:
        pass


class JSONConfigLoader(ConfigLoader):
    def __init__(self, path: str):
        self._path = path

    def get_config(self) -> UIConfig:
        with open(self._path, 'r') as f:
            data = json.load(f)
        window = data['window']
        grid = data['grid']
        buttons: List[Tuple[str, str, int, int, int, int, EventType]] = []
        for btn in data.get('buttons', []):
            buttons.append((btn['label'], btn['width'], btn['height'], btn['x'], btn['y'], EventType[btn['event']]))
        return UIConfig(
            width=window['width'],
            height=window['height'],
            grid_width=grid['width'],
            grid_height=grid['height'],
            buttons=buttons
        )


class ConfigLoaderFactoryError(Exception):
    pass


class ConfigLoaderFactory:
    _loaders = {
        '.json': JSONConfigLoader,
        # '.yaml': YAMLConfigLoader,  # To be implemented
        # '.xml': XMLConfigLoader,    # To be implemented
    }

    @staticmethod
    def create(path: str) -> ConfigLoader:
        _, ext = os.path.splitext(path)
        ext = ext.lower()
        if not ext or ext not in ConfigLoaderFactory._loaders:
            raise ConfigLoaderFactoryError(f"Unsupported or missing config file extension: '{ext}'")
        loader_cls: Type[ConfigLoader] = ConfigLoaderFactory._loaders[ext]
        return loader_cls(path)
