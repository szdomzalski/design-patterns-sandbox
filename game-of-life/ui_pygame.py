import pygame
import numpy as np
from game_controller import GameController
from event_handling import EventType
from ui import UI, UIBuilder, UIColor, UIElement, UIWindow
from typing import Any, Optional

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
        self.attach(GameController())

    def draw(self, window: PygameUIWindow, **kwargs: Any) -> None:
        screen = window.get_surface()
        pygame.draw.rect(screen, UIColor.GREEN.value, (self.x, self.y, self.width, self.height))
        font = pygame.font.Font(None, 36)
        text = font.render(self.label, True, UIColor.BLACK.value)
        text_rect = text.get_rect(center=(self.x + self.width // 2, self.y + self.height // 2))
        screen.blit(text, text_rect)

    def is_clicked(self, click_x: int, click_y: int) -> bool:
        return self.x <= click_x <= self.x + self.width and self.y <= click_y <= self.y + self.height

    def on_click(self) -> None:
        self.publish(self.event)


class PygameUI(UI):
    def __init__(self, screen: PygameUIWindow, grid: PygameUIGrid, buttons: list[PygameUIButton]) -> None:
        super().__init__()
        self.screen = screen
        self.screen.setup()
        self.grid = grid
        self.buttons = buttons

    def render(self, board_state: np.ndarray) -> None:
        self.screen.clear()
        self.grid.draw(self.screen, board_state=board_state)
        self._draw_buttons()

        pygame.display.flip()

    def close(self) -> None:
        pygame.quit()

    def run(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.publish(EventType.UI_QUIT)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self._process_click(event)

    def _draw_buttons(self) -> None:
        for button in self.buttons:
             button.draw(self.screen)

    def _process_click(self, event: pygame.event.Event) -> None:
        for button in self.buttons:
            if button.is_clicked(event.pos[0], event.pos[1]):
                button.on_click()


class PygameUIBuilder(UIBuilder):
    def __init__(self) -> None:
        self.screen: Optional[PygameUIWindow] = None
        self.grid: Optional[PygameUIGrid] = None
        self.buttons: list[PygameUIButton] = []

    def build_window(self, width: int, height: int) -> None:
        self.screen = PygameUIWindow(width, height)

    def build_grid(self, n_cells_x: int, n_cells_y: int, cell_width: int, cell_height: int) -> None:
        self.grid = PygameUIGrid(n_cells_x, n_cells_y, cell_width, cell_height)

    def build_button(self, label: str, width: int, height: int, x: int, y: int, event: EventType) -> None:
        self.buttons.append(PygameUIButton(label, width, height, x, y, event))

    def get_ui(self) -> PygameUI:
        return PygameUI(self.screen, self.grid, self.buttons)
