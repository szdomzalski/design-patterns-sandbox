from abc import ABC, abstractmethod
from enum import Enum
from typing import Any


class UIColor(Enum):
    '''
    Enum representing UI color constants as RGB tuples.
    '''
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    GRAY = (128, 128, 128)
    GREEN = (0, 255, 0)


class UIObject(ABC):
    '''
    Abstract base class for UI objects. Defines the interface for updating and drawing UI elements.
    '''
    @abstractmethod
    def update(self, game_state: Any) -> None:
        '''
        Redraw the UI according to the passed game state.
        :param game_state: The current game state to render.
        :return: None
        '''
        pass


class UIBuilder(ABC):
    '''
    Abstract base class for building UI objects. Defines the interface for constructing UI components.
    '''
    @abstractmethod
    def build_window(self, width: int, height: int) -> None:
        '''
        Build the main window for the UI.
        :param width: The width of the window.
        :param height: The height of the window.
        :return: None
        '''
        pass

    @abstractmethod
    def build_grid(self, n_cells_x: int, n_cells_y: int, cell_width: int, cell_height: int) -> None:
        '''
        Build the grid component of the UI.
        :param n_cells_x: Number of cells in the x direction.
        :param n_cells_y: Number of cells in the y direction.
        :param cell_width: Width of each cell.
        :param cell_height: Height of each cell.
        :return: None
        '''
        pass

    @abstractmethod
    def build_button(self, name: str, label: str, width: int, height: int, x: int, y: int) -> None:
        '''
        Build a button component for the UI.
        :param name: The unique name of the button.
        :param label: The label text for the button.
        :param width: The width of the button.
        :param height: The height of the button.
        :param x: The x-coordinate of the button.
        :param y: The y-coordinate of the button.
        :return: None
        '''
        pass

    @abstractmethod
    def get_ui(self) -> UIObject:
        '''
        Return the constructed UI object.
        :return: An instance of UIObject.
        '''
        pass


class UIDirector:
    '''
    Director class that defines the order in which to build the UI components and returns the finished UI object.
    '''
    def __init__(self, builder: UIBuilder) -> None:
        '''
        Initialize the UIDirector with a UIBuilder.
        :param builder: An instance of UIBuilder.
        :return: None
        '''
        self._builder = builder

    def construct_ui(self, config: dict) -> UIObject:
        '''
        Construct the UI by issuing build commands to the builder based on the provided configuration.
        :param config: A dictionary containing UI configuration parameters.
        :return: The constructed UIObject.
        '''
        self._builder.build_window(config['width'], config['height'])
        self._builder.build_grid(config['n_cells_x'], config['n_cells_y'], config['cell_width'], config['cell_height'])
        for button in config['buttons']:
            self._builder.build_button(*button)
        return self._builder.get_ui()
