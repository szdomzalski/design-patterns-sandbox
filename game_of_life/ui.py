"""Define UI interfaces, builder contracts, and UI construction direction."""

from abc import ABC, abstractmethod
from enum import Enum
from typing import Any

from .config_loader import UIConfig
from .event_handling import EventPublisher, EventType


class UIColor(Enum):
    """Define UI colors as RGB tuples."""

    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    GRAY = (128, 128, 128)
    GREEN = (0, 255, 0)
    LIGHT_GRAY = (211, 211, 211)


class UIWindow(ABC):
    """Define the interface for UI windows."""

    @abstractmethod
    def setup(self) -> None:
        """Set up the UI window.

        Args:
            None.

        Returns:
            None.
        """

    @abstractmethod
    def clear(self) -> None:
        """Clear or prepare the UI window for drawing.

        Args:
            None.

        Returns:
            None.
        """


class UIElement(EventPublisher, ABC):
    """Define the interface for drawable UI elements."""

    @abstractmethod
    def draw(self, window: UIWindow, **kwargs: Any) -> None:
        """Draw the UI element on the screen.

        Args:
            window: The window to draw on.
            **kwargs: Additional arguments required for dynamic drawing.

        Returns:
            None.
        """


class UI(EventPublisher, ABC):
    """Define input, rendering, frame pacing, and shutdown operations for a UI."""

    @abstractmethod
    def render(self, board_state: Any) -> None:
        """Redraw the UI according to the current game state.

        Args:
            board_state: The current game state to render.

        Returns:
            None.
        """

    @abstractmethod
    def process_events(self) -> None:
        """Process pending input events for the current UI frame.

        Args:
            None.

        Returns:
            None.
        """

    @abstractmethod
    def finish_frame(self) -> None:
        """Complete the current UI frame and apply its frame-rate limit.

        Args:
            None.

        Returns:
            None.
        """

    @abstractmethod
    def close(self) -> None:
        """Close the UI and release its resources.

        Args:
            None.

        Returns:
            None.
        """


class UIBuilderError(RuntimeError):
    """Report invalid UI builder operation order or incomplete products."""


class UIBuilder(ABC):
    """Define the interface for building UI objects in a prescribed sequence."""

    @abstractmethod
    def build_window(self, width: int, height: int) -> None:
        """Build the main UI window.

        Args:
            width: The window width in pixels.
            height: The window height in pixels.

        Returns:
            None.
        """

    @abstractmethod
    def build_grid(self, n_cells_x: int, n_cells_y: int, cell_width: int, cell_height: int) -> None:
        """Build the UI grid.

        Args:
            n_cells_x: Number of cells along the x-axis.
            n_cells_y: Number of cells along the y-axis.
            cell_width: Width of each cell in pixels.
            cell_height: Height of each cell in pixels.

        Returns:
            None.
        """

    @abstractmethod
    def build_button(self, label: str, width: int, height: int, x: int, y: int, event: EventType) -> None:
        """Build a button that publishes an event.

        Args:
            label: The button label.
            width: The button width in pixels.
            height: The button height in pixels.
            x: The button's horizontal position in pixels.
            y: The button's vertical position in pixels.
            event: The event published when the button is activated.

        Returns:
            None.
        """

    @abstractmethod
    def build_slider(self, x: int, y: int, width: int, height: int, min_value: float,
                    max_value: float, initial_value: float, event: EventType) -> None:
        """Build a slider that publishes its selected value.

        Args:
            x: The slider's horizontal position in pixels.
            y: The slider's vertical position in pixels.
            width: The slider width in pixels.
            height: The slider height in pixels.
            min_value: The minimum selectable value.
            max_value: The maximum selectable value.
            initial_value: The slider's initial value.
            event: The event published when the value changes.

        Returns:
            None.
        """

    @abstractmethod
    def get_ui(self) -> UI:
        """Return the completed UI and prepare the builder for another product.

        Args:
            None.

        Returns:
            The UI built by this builder.
        """


class UIDirector:
    """Direct a builder through the steps required to construct a UI."""

    def __init__(self, builder: UIBuilder) -> None:
        """Initialize the director with a UI builder.

        Args:
            builder: The builder used to construct the UI.

        Returns:
            None.
        """
        self._builder = builder

    def construct_ui(self, config: UIConfig, n_cells_x: int, n_cells_y: int) -> UI:
        """Build the configured UI for a board of the requested dimensions.

        Args:
            config: The configuration describing the window and controls.
            n_cells_x: Number of cells along the x-axis.
            n_cells_y: Number of cells along the y-axis.

        Returns:
            The constructed UI.
        """
        cell_width, cell_height = config.grid.cell_size(n_cells_x, n_cells_y)
        self._builder.build_window(config.window.width, config.window.height)
        self._builder.build_grid(n_cells_x, n_cells_y, cell_width, cell_height)
        for button in config.buttons:
            self._builder.build_button(
                button.label,
                button.width,
                button.height,
                button.x,
                button.y,
                button.event,
            )
        for slider in config.sliders:
            self._builder.build_slider(
                slider.x,
                slider.y,
                slider.width,
                slider.height,
                slider.min_value,
                slider.max_value,
                slider.initial_value,
                slider.event,
            )
        return self._builder.get_ui()
