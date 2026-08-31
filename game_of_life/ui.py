from abc import ABC, abstractmethod
from enum import Enum
from typing import Any
from .config_loader import UIConfig
from .event_handling import EventPublisher, EventType


class UIColor(Enum):
    '''
    Enum representing UI color constants as RGB tuples.
    '''
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    GRAY = (128, 128, 128)
    GREEN = (0, 255, 0)
    LIGHT_GRAY = (211, 211, 211)


class UIWindow(ABC):
    '''
    Abstract base class for UI windows.
    '''
    @abstractmethod
    def setup(self) -> None:
        '''
        Set up the UI window.
        :return: None
        '''
        pass

    @abstractmethod
    def clear(self) -> None:
        '''
        Clear the UI window.
        :return: None
        '''
        pass


class UIElement(EventPublisher, ABC):
    '''
    Abstract base class for UI elements.
    '''
    @abstractmethod
    def draw(self, window: UIWindow, **kwargs: Any) -> None:
        '''
        Draw the UI element on the screen.
        :param window: The window to draw on.
        :param kwargs: Additional keyword arguments required for dynamic drawing.
        :return: None
        '''
        pass


class UI(EventPublisher, ABC):
    '''
    Abstract base class for UI objects. Defines the interface for updating and drawing UI elements.
    '''
    @abstractmethod
    def render(self, board_state: Any) -> None:
        '''
        Redraw the UI according to the passed game state.
        :param board_state: The current game state to render.
        :return: None
        '''
        pass

    @abstractmethod
    def run(self) -> None:
        '''
        Run the main event loop for the UI.
        :return: None
        '''
        pass

    @abstractmethod
    def close(self) -> None:
        '''
        Close the UI window.
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
    def build_button(self, label: str, width: int, height: int, x: int, y: int, event: EventType) -> None:
        '''
        Build a button component for the UI.
        :param label: The label text for the button.
        :param width: The width of the button.
        :param height: The height of the button.
        :param x: The x-coordinate of the button.
        :param y: The y-coordinate of the button.
        :param event: The event type associated with the button.
        :return: None
        '''
        pass

    @abstractmethod
    def build_slider(self, x: int, y: int, width: int, height: int, min_value: float,
                    max_value: float, initial_value: float, event: EventType) -> None:
        '''
        Build a slider component for the UI.
        :param x: The x-coordinate of the slider.
        :param y: The y-coordinate of the slider.
        :param width: The width of the slider.
        :param height: The height of the slider.
        :param min_value: The minimum value of the slider.
        :param max_value: The maximum value of the slider.
        :param initial_value: The initial value of the slider.
        :param event: The event type associated with the slider.
        :return: None
        '''
        pass

    @abstractmethod
    def get_ui(self) -> UI:
        '''
        Return the constructed UI object.
        :return: An instance of UI.
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

    def construct_ui(self, config: UIConfig, n_cells_x: int, n_cells_y: int) -> UI:
        '''
        Construct the UI by issuing build commands to the builder based on the provided configuration and cell counts.
        :param config: A UIConfig instance containing UI configuration parameters.
        :param n_cells_x: Number of cells in the x direction.
        :param n_cells_y: Number of cells in the y direction.
        :return: The constructed UI.
        '''
        self._builder.build_window(config.width, config.height)
        cell_width = config.grid_width // n_cells_x
        cell_height = config.grid_height // n_cells_y
        self._builder.build_grid(n_cells_x, n_cells_y, cell_width, cell_height)
        for button in config.buttons:
            self._builder.build_button(*button)
        for slider in config.sliders:
            self._builder.build_slider(*slider)
        return self._builder.get_ui()
