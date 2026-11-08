"""Implement the Game of Life UI with Pygame."""

from typing import Any

import numpy as np
import pygame

from .event_handling import Event, EventSubscriber, EventType
from .ui import UI, UIBuilder, UIBuilderError, UIButton, UIColor, UIElement, UIWindow

UI_FRAME_RATE = 60


class PygameUIWindow(UIWindow):
    """Manage the Pygame display surface."""

    def __init__(self, width: int, height: int) -> None:
        """Store the dimensions used to create the display.

        Args:
            width: Display width in pixels.
            height: Display height in pixels.

        Returns:
            None.
        """
        self.width = width
        self.height = height
        self.screen: pygame.Surface | None = None

    def setup(self) -> None:
        """Initialize Pygame and create the display surface.

        Args:
            None.

        Returns:
            None.
        """
        pygame.init()
        self.screen = pygame.display.set_mode((self.width, self.height))

    def clear(self) -> None:
        """Fill the display with the configured background color.

        Args:
            None.

        Returns:
            None.
        """
        self.screen.fill(UIColor.WHITE.value)

    def get_surface(self) -> pygame.Surface:
        """Return the display surface.

        Args:
            None.

        Returns:
            The Pygame display surface.
        """
        return self.screen


class PygameUIGrid(UIElement):
    """Draw the simulation board as a grid of Pygame rectangles."""

    def __init__(self, n_cells_x: int, n_cells_y: int, cell_width: int, cell_height: int) -> None:
        """Store board dimensions and cell pixel dimensions.

        Args:
            n_cells_x: Number of cells along the board's x-axis.
            n_cells_y: Number of cells along the board's y-axis.
            cell_width: Width of each cell in pixels.
            cell_height: Height of each cell in pixels.

        Returns:
            None.
        """
        super().__init__()
        self.n_cells_x = n_cells_x
        self.n_cells_y = n_cells_y
        self.cell_width = cell_width
        self.cell_height = cell_height

    def draw(self, window: PygameUIWindow, **kwargs: Any) -> None:
        """Draw the board cells on a Pygame window.

        Args:
            window: Window providing the display surface.
            **kwargs: Optional ``board_state`` array to draw.

        Returns:
            None.
        """
        board_state = kwargs.get('board_state', np.zeros((self.n_cells_x, self.n_cells_y)))
        for (x, y), value in np.ndenumerate(board_state):
            cell = pygame.Rect(x * self.cell_width, y * self.cell_height, self.cell_width, self.cell_height)
            # In case of "living" cells, fill the cell with black, otherwise only draw the border (gray)
            pygame.draw.rect(window.get_surface(), UIColor.BLACK.value if value else UIColor.GRAY.value, cell,
                             width=1 - min(value, 1))


class PygameUIButton(UIButton):
    """Draw a button and publish its configured event when clicked."""

    def __init__(self, label: str, width: int, height: int, x: int, y: int, event: EventType) -> None:
        """Store the button's label, geometry, and event.

        Args:
            label: Text displayed on the button.
            width: Button width in pixels.
            height: Button height in pixels.
            x: Button's horizontal position in pixels.
            y: Button's vertical position in pixels.
            event: Event published when the button is clicked.

        Returns:
            None.
        """
        super().__init__(event)
        self.label = label
        self.width = width
        self.height = height
        self.x = x
        self.y = y

    def draw(self, window: PygameUIWindow, **kwargs: Any) -> None:
        """Draw the button on a Pygame window.

        Args:
            window: Window providing the display surface.
            **kwargs: Unused drawing options.

        Returns:
            None.
        """
        screen = window.get_surface()
        pygame.draw.rect(screen, UIColor.LIGHT_GRAY.value, (self.x, self.y, self.width, self.height))
        font = pygame.font.Font(None, 36)
        text = font.render(self.label, True, UIColor.BLACK.value)
        text_rect = text.get_rect(center=(self.x + self.width // 2, self.y + self.height // 2))
        screen.blit(text, text_rect)

    def is_clicked(self, click_x: int, click_y: int) -> bool:
        """Check whether a point lies within the button bounds.

        Args:
            click_x: Horizontal coordinate of the click.
            click_y: Vertical coordinate of the click.

        Returns:
            Whether the point is inside the button.
        """
        return self.x <= click_x <= self.x + self.width and self.y <= click_y <= self.y + self.height


class PygameUISlider(UIElement):
    """Draw and handle a draggable numeric slider."""

    def __init__(self, x: int, y: int, width: int, height: int,
                 min_value: float, max_value: float,
                 initial_value: float, event: EventType) -> None:
        """Initialize slider geometry, range, value, and event.

        Args:
            x: Slider's horizontal position in pixels.
            y: Slider's vertical position in pixels.
            width: Slider width in pixels.
            height: Slider height in pixels.
            min_value: Minimum selectable value.
            max_value: Maximum selectable value.
            initial_value: Initial slider value.
            event: Event published when the value changes.

        Returns:
            None.
        """
        super().__init__()
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.min_value = min_value
        self.max_value = max_value
        self.value = initial_value
        self.event = event
        self.is_dragging = False

        # Calculate the initial handle position
        self.handle_width = 20
        self.handle_height = height + 10
        self._update_handle_position()

    def _update_handle_position(self) -> None:
        """Update the handle's horizontal position from the current value.

        Args:
            None.

        Returns:
            None.
        """
        value_range = self.max_value - self.min_value
        value_ratio = (self.value - self.min_value) / value_range
        self.handle_x = self.x + int(value_ratio * (self.width - self.handle_width))

    def draw(self, window: PygameUIWindow, **kwargs: Any) -> None:
        """Draw the slider track, handle, and current value.

        Args:
            window: Window providing the display surface.
            **kwargs: Unused drawing options.

        Returns:
            None.
        """
        screen = window.get_surface()

        # Draw the slider track
        track_rect = pygame.Rect(self.x, self.y + (self.height // 2) - 2, self.width, 4)
        pygame.draw.rect(screen, UIColor.GRAY.value, track_rect)

        # Draw the handle
        handle_rect = pygame.Rect(
            self.handle_x,
            self.y - (self.handle_height - self.height) // 2,
            self.handle_width,
            self.handle_height
        )
        pygame.draw.rect(screen, UIColor.LIGHT_GRAY.value, handle_rect)
        pygame.draw.rect(screen, UIColor.BLACK.value, handle_rect, 1)  # Border

        # Draw the value text
        font = pygame.font.Font(None, 24)
        value_text = font.render(f"{self.value:.1f}", True, UIColor.BLACK.value)
        text_rect = value_text.get_rect(midtop=(self.x + self.width // 2, self.y + self.height + 5))
        screen.blit(value_text, text_rect)

    def is_clicked(self, click_x: int, click_y: int) -> bool:
        """Check whether a point lies within the slider handle.

        Args:
            click_x: Horizontal coordinate of the click.
            click_y: Vertical coordinate of the click.

        Returns:
            Whether the point is inside the handle.
        """
        return (self.handle_x <= click_x <= self.handle_x + self.handle_width and
                self.y - (self.handle_height - self.height) // 2 <= click_y <=
                self.y + self.height + (self.handle_height - self.height) // 2)

    def start_dragging(self) -> None:
        """Mark the slider handle as being dragged.

        Args:
            None.

        Returns:
            None.
        """
        self.is_dragging = True

    def stop_dragging(self) -> None:
        """Mark the slider handle as no longer being dragged.

        Args:
            None.

        Returns:
            None.
        """
        self.is_dragging = False

    def update_drag(self, mouse_x: int) -> None:
        """Update and publish the slider value during an active drag.

        Args:
            mouse_x: Current horizontal mouse coordinate.

        Returns:
            None.
        """
        if not self.is_dragging:
            return

        # Clamp mouse_x to the slider's bounds
        mouse_x = max(self.x, min(mouse_x, self.x + self.width - self.handle_width))

        # Calculate the new value based on position
        position_ratio = (mouse_x - self.x) / (self.width - self.handle_width)
        new_value = self.min_value + position_ratio * (self.max_value - self.min_value)

        # Update the value and handle position
        if new_value != self.value:
            self.value = new_value
            self.handle_x = mouse_x
            self.publish(self.event, self.value)


class PygameUI(UI, EventSubscriber):
    """Implement UI input, rendering, and frame pacing with Pygame."""

    def __init__(self, screen: PygameUIWindow, grid: PygameUIGrid,
                 buttons: list[PygameUIButton], sliders: list[PygameUISlider] | None = None) -> None:
        """Initialize the window, controls, event wiring, and frame clock.

        Args:
            screen: Window wrapper used to display the game.
            grid: Renderer for the simulation board.
            buttons: Buttons included in the UI.
            sliders: Optional sliders included in the UI.

        Returns:
            None.
        """
        super().__init__()
        self.screen = screen
        self.screen.setup()
        self.grid = grid
        self.buttons = buttons
        self.sliders = sliders or []
        # This clock only caps UI frames. Simulation generations are scheduled
        # separately by Ticker using its injected monotonic Clock.
        self.frame_clock = pygame.time.Clock()
        for element in [*self.buttons, *self.sliders]:
            element: UIElement
            element.attach(self)

    def notify(self, event: Event) -> None:
        """Forward child control events to subscribers of the complete UI.

        Args:
            event: The child control event to forward.

        Returns:
            None.
        """
        self.publish(event.event_type, event.payload)

    def render(self, board_state: np.ndarray) -> None:
        """Draw the board and controls, then present the frame.

        Args:
            board_state: Current simulation board.

        Returns:
            None.
        """
        self.screen.clear()
        self.grid.draw(self.screen, board_state=board_state)
        self._draw_buttons()
        self._draw_sliders()
        pygame.display.flip()

    def close(self) -> None:
        """Shut down Pygame resources.

        Args:
            None.

        Returns:
            None.
        """
        pygame.quit()

    def process_events(self) -> None:
        """Translate pending Pygame input into application events.

        Args:
            None.

        Returns:
            None.
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.publish(EventType.UI_QUIT)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self._process_click(event)
            elif event.type == pygame.MOUSEBUTTONUP:
                self._process_mouse_up()
            elif event.type == pygame.MOUSEMOTION:
                self._process_mouse_motion(event)

    def finish_frame(self) -> None:
        """Limit UI processing to the configured frame rate.

        Args:
            None.

        Returns:
            None.
        """
        self.frame_clock.tick(UI_FRAME_RATE)

    def _draw_buttons(self) -> None:
        """Draw each configured button.

        Args:
            None.

        Returns:
            None.
        """
        for button in self.buttons:
             button.draw(self.screen)

    def _draw_sliders(self) -> None:
        """Draw each configured slider.

        Args:
            None.

        Returns:
            None.
        """
        for slider in self.sliders:
            slider.draw(self.screen)

    def _process_click(self, event: pygame.event.Event) -> None:
        """Dispatch a mouse click to a button or slider.

        Args:
            event: Pygame mouse-button-down event.

        Returns:
            None.
        """
        # Handle button clicks
        for button in self.buttons:
            if button.is_clicked(event.pos[0], event.pos[1]):
                button.on_click()
                return

        # Handle slider clicks
        for slider in self.sliders:
            if slider.is_clicked(event.pos[0], event.pos[1]):
                slider.start_dragging()
                return

    def _process_mouse_up(self) -> None:
        """Stop dragging all configured sliders.

        Args:
            None.

        Returns:
            None.
        """
        # Stop dragging any active sliders
        for slider in self.sliders:
            slider.stop_dragging()

    def _process_mouse_motion(self, event: pygame.event.Event) -> None:
        """Update sliders in response to mouse movement.

        Args:
            event: Pygame mouse-motion event.

        Returns:
            None.
        """
        # Update any active slider drags
        for slider in self.sliders:
            slider.update_drag(event.pos[0])


class PygameUIBuilder(UIBuilder):
    """Build complete Pygame UIs while enforcing component construction order."""

    def __init__(self) -> None:
        """Initialize an empty builder.

        Args:
            None.

        Returns:
            None.
        """
        self._reset()

    def _reset(self) -> None:
        """Clear builder state so it can construct another UI.

        Args:
            None.

        Returns:
            None.
        """
        self.screen: PygameUIWindow | None = None
        self.grid: PygameUIGrid | None = None
        self.buttons: list[PygameUIButton] = []
        self.sliders: list[PygameUISlider] = []

    def build_window(self, width: int, height: int) -> None:
        """Start building a UI by creating its window.

        Args:
            width: Window width in pixels.
            height: Window height in pixels.

        Returns:
            None.
        """
        if self.screen is not None:
            raise UIBuilderError("window has already been built for the current UI")
        self.screen = PygameUIWindow(width, height)

    def build_grid(self, n_cells_x: int, n_cells_y: int, cell_width: int, cell_height: int) -> None:
        """Build the grid after creating the window.

        Args:
            n_cells_x: Number of cells along the board's x-axis.
            n_cells_y: Number of cells along the board's y-axis.
            cell_width: Width of each cell in pixels.
            cell_height: Height of each cell in pixels.

        Returns:
            None.
        """
        self._require_window()
        if self.grid is not None:
            raise UIBuilderError("grid has already been built for the current UI")
        self.grid = PygameUIGrid(n_cells_x, n_cells_y, cell_width, cell_height)

    def build_button(self, label: str, width: int, height: int, x: int, y: int, event: EventType) -> None:
        """Add a button to the current UI product.

        Args:
            label: Text displayed on the button.
            width: Button width in pixels.
            height: Button height in pixels.
            x: Button's horizontal position in pixels.
            y: Button's vertical position in pixels.
            event: Event published when the button is clicked.

        Returns:
            None.
        """
        self._require_grid()
        self.buttons.append(PygameUIButton(label, width, height, x, y, event))

    def build_slider(self, x: int, y: int, width: int, height: int, min_value: float,
                    max_value: float, initial_value: float, event: EventType) -> None:
        """Add a slider to the current UI product.

        Args:
            x: Slider's horizontal position in pixels.
            y: Slider's vertical position in pixels.
            width: Slider width in pixels.
            height: Slider height in pixels.
            min_value: Minimum selectable value.
            max_value: Maximum selectable value.
            initial_value: Initial slider value.
            event: Event published when the value changes.

        Returns:
            None.
        """
        self._require_grid()
        self.sliders.append(PygameUISlider(x, y, width, height, min_value, max_value, initial_value, event))

    def get_ui(self) -> PygameUI:
        """Return the completed UI and reset the builder.

        Args:
            None.

        Returns:
            The completed Pygame UI.
        """
        screen = self._require_window()
        grid = self._require_grid()
        ui = PygameUI(screen, grid, self.buttons, self.sliders)
        self._reset()
        return ui

    def _require_window(self) -> PygameUIWindow:
        """Return the current window or reject an out-of-order operation.

        Args:
            None.

        Returns:
            The window built for the current UI product.
        """
        if self.screen is None:
            raise UIBuilderError("build the window before other UI components")
        return self.screen

    def _require_grid(self) -> PygameUIGrid:
        """Return the current grid or reject an incomplete product.

        Args:
            None.

        Returns:
            The grid built for the current UI product.
        """
        self._require_window()
        if self.grid is None:
            raise UIBuilderError("build the grid before controls or product retrieval")
        return self.grid
