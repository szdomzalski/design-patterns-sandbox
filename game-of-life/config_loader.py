from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Tuple
import json


@dataclass
class UIConfig:
    width: int
    height: int
    grid_width: int
    grid_height: int
    buttons: List[Tuple[str, str, int, int, int, int]]


class ConfigLoader(ABC):
    def __init__(self, path: str):
        self._path = path

    @abstractmethod
    def get_config(self) -> UIConfig:
        """
        Return the UIConfig instance loaded from the config file.
        """
        pass

class JSONConfigLoader(ConfigLoader):
    def get_config(self) -> UIConfig:
        with open(self._path, 'r') as f:
            data = json.load(f)
        window = data['window']
        grid = data['grid']
        buttons: List[Tuple[str, str, int, int, int, int]] = []
        for btn in data.get('buttons', []):
            buttons.append((btn['name'], btn['label'], btn['width'], btn['height'], btn['x'], btn['y']))
        return UIConfig(
            width=window['width'],
            height=window['height'],
            grid_width=grid['width'],
            grid_height=grid['height'],
            buttons=buttons
        )
