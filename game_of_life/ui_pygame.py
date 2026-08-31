import pygame
import numpy as np
from typing import Any, Optional

from .event_handling import Event, EventSubscriber, EventType
from .ui import UI, UIBuilder, UIColor, UIElement, UIWindow

UI_FRAME_RATE = 60


class PygameUIWindow(UIWindow):
    def __init__(self, width: int, height: int) -> None:
        self.width = width
        self.height = height
        self.screen: Optional[pygame.Surface] = None

    def setup(self) -> None:
        pygame.init()
        self.screen = pygame.display.set_mode((self.width, self.height))

    def clear(self) -> None:
        self.screen.fill(UIColor.WHITE.value)

    def get_surface(self) -> pygame.Surface:
        return self.screen


class PygameUIGrid(UIElement):
    def __init__(self, n_cells_x: int, n_cells_y: int, cell_width: int, cell_height: int) -> None:
        super().__init__()
        self.n_cells_x = n_cells_x
        self.n_cells_y = n_cells_y
        self.cell_width = cell_width
        self.cell_height = cell_height

    def draw(self, window: PygameUIWindow, **kwargs: Any) -> None:
        board_state = kwargs.get('board_state', np.zeros((self.n_cells_x, self.n_cells_y)))
        for (x, y), value in np.ndenumerate(board_state):
            cell = pygame.Rect(x * self.cell_width, y * self.cell_height, self.cell_width, self.cell_height)
            # In case of "living" cells, fill the cell with black, otherwise only draw the border (gray)
            pygame.draw.rect(window.get_surface(), UIColor.BLACK.value if value else UIColor.GRAY.value, cell,
                             width=1 - min(value, 1))


class PygameUIButton(UIElement):
    def __init__(self, label: str, width: int, height: int, x: int, y: int, event: EventType) -> None:
        super().__init__()
        self.label = label
        self.width = width
        self.height = height
        self.x = x
        self.y = y
        self.event = event

    def draw(self, window: PygameUIWindow, **kwargs: Any) -> None:
        screen = window.get_surface()
        pygame.draw.rect(screen, UIColor.LIGHT_GRAY.value, (self.x, self.y, self.width, self.height))
        font = pygame.font.Font(None, 36)
        text = font.render(self.label, True, UIColor.BLACK.value)
        text_rect = text.get_rect(center=(self.x + self.width // 2, self.y + self.height // 2))
        screen.blit(text, text_rect)

    def is_clicked(self, click_x: int, click_y: int) -> bool:
        return self.x <= click_x <= self.x + self.width and self.y <= click_y <= self.y + self.height

    def on_click(self) -> None:
        self.publish(self.event)


class PygameUISlider(UIElement):
    def __init__(self, x: int, y: int, width: int, height: int,
                 min_value: float, max_value: float,
                 initial_value: float, event: EventType) -> None:
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
        """Updates the handle's x position based on the current value"""
        value_range = self.max_value - self.min_value
        value_ratio = (self.value - self.min_value) / value_range
        self.handle_x = self.x + int(value_ratio * (self.width - self.handle_width))

    def draw(self, window: PygameUIWindow, **kwargs: Any) -> None:
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
        """Check if the slider handle was clicked"""
        return (self.handle_x <= click_x <= self.handle_x + self.handle_width and
                self.y - (self.handle_height - self.height) // 2 <= click_y <=
                self.y + self.height + (self.handle_height - self.height) // 2)

    def start_dragging(self) -> None:
        """Start dragging the slider handle"""
        self.is_dragging = True

    def stop_dragging(self) -> None:
        """Stop dragging the slider handle"""
        self.is_dragging = False

    def update_drag(self, mouse_x: int) -> None:
        """Update the slider value based on the current mouse position"""
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
                 buttons: list[PygameUIButton], sliders: list[PygameUISlider] = None) -> None:
        """Initialize the window, controls, and Pygame frame clock."""
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
            element.attach(self)

    def notify(self, event: Event) -> None:
        '''
        Forward events from child controls to subscribers of the complete UI.
        :param event: The child control event to forward.
        :return: None
        '''
        self.publish(event.event_type, event.payload)

    def render(self, board_state: np.ndarray) -> None:
        """Draw the current board and controls, then present the frame."""
        self.screen.clear()
        self.grid.draw(self.screen, board_state=board_state)
        self._draw_buttons()
        self._draw_sliders()
        pygame.display.flip()

    def close(self) -> None:
        """Shut down Pygame resources."""
        pygame.quit()

    def process_events(self) -> None:
        """Translate pending Pygame input into application events."""
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
        """Delay if necessary to keep UI processing at or below its frame rate."""
        self.frame_clock.tick(UI_FRAME_RATE)

    def _draw_buttons(self) -> None:
        for button in self.buttons:
             button.draw(self.screen)

    def _draw_sliders(self) -> None:
        for slider in self.sliders:
            slider.draw(self.screen)

    def _process_click(self, event: pygame.event.Event) -> None:
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
        # Stop dragging any active sliders
        for slider in self.sliders:
            slider.stop_dragging()

    def _process_mouse_motion(self, event: pygame.event.Event) -> None:
        # Update any active slider drags
        for slider in self.sliders:
            slider.update_drag(event.pos[0])


class PygameUIBuilder(UIBuilder):
    def __init__(self) -> None:
        self.screen: Optional[PygameUIWindow] = None
        self.grid: Optional[PygameUIGrid] = None
        self.buttons: list[PygameUIButton] = []
        self.sliders: list[PygameUISlider] = []

    def build_window(self, width: int, height: int) -> None:
        self.screen = PygameUIWindow(width, height)

    def build_grid(self, n_cells_x: int, n_cells_y: int, cell_width: int, cell_height: int) -> None:
        self.grid = PygameUIGrid(n_cells_x, n_cells_y, cell_width, cell_height)

    def build_button(self, label: str, width: int, height: int, x: int, y: int, event: EventType) -> None:
        self.buttons.append(PygameUIButton(label, width, height, x, y, event))

    def build_slider(self, x: int, y: int, width: int, height: int, min_value: float,
                    max_value: float, initial_value: float, event: EventType) -> None:
        self.sliders.append(PygameUISlider(x, y, width, height, min_value, max_value, initial_value, event))

    def get_ui(self) -> PygameUI:
        return PygameUI(self.screen, self.grid, self.buttons, self.sliders)
