import pygame
import numpy as np
from ui import UI, UIBuilder, UIColor, UIElement, UIWindow
from typing import Optional

# https://www.pygame.org/docs/ref/event.html#module-pygame.event

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
        self.n_cells_x = n_cells_x
        self.n_cells_y = n_cells_y
        self.cell_width = cell_width
        self.cell_height = cell_height

    def draw(self, window: PygameUIWindow) -> None:
        for y in range(0, self.n_cells_y * self.cell_height, self.cell_height):
            for x in range(0, self.n_cells_x * self.cell_width, self.cell_width):
                cell = pygame.Rect(x, y, self.cell_width, self.cell_height)
                pygame.draw.rect(window.get_surface(), UIColor.GRAY.value, cell, 1)


class PygameUIButton(UIElement):
    def __init__(self, name: str, label: str, width: int, height: int, x: int, y: int) -> None:
        self.name = name
        self.label = label
        self.width = width
        self.height = height
        self.x = x
        self.y = y

    def draw(self, window: PygameUIWindow) -> None:
        screen = window.get_surface()
        pygame.draw.rect(screen, UIColor.GREEN.value, (self.x, self.y, self.width, self.height))
        font = pygame.font.Font(None, 36)
        text = font.render(self.label, True, UIColor.BLACK.value)
        text_rect = text.get_rect(center=(self.x + self.width // 2, self.y + self.height // 2))
        screen.blit(text, text_rect)


class PygameUI(UI):
    def __init__(self, screen: PygameUIWindow, grid: PygameUIGrid, buttons: list[PygameUIButton]) -> None:
        self.screen = screen
        self.screen.setup()
        self.grid = grid
        self.buttons = buttons

    def render(self, board_state: np.ndarray) -> None:
        self.screen.clear()
        self.grid.draw(self.screen)
        self._draw_buttons()

        self._draw_cells(board_state)
        pygame.display.flip()

    def run(self) -> None:
        pass

    def _draw_cells(self, board_state: np.ndarray) -> None:
        for y in range(self.grid.n_cells_y):
            for x in range(self.grid.n_cells_x):
                cell = pygame.Rect(x * self.grid.cell_width, y * self.grid.cell_height, self.grid.cell_width,
                                   self.grid.cell_height)
                if board_state[x, y] == 1:
                    pygame.draw.rect(self.screen.get_surface(), UIColor.BLACK.value, cell)

    def _draw_buttons(self) -> None:
        for button in self.buttons:
             button.draw(self.screen)


class PygameUIBuilder(UIBuilder):
    def __init__(self) -> None:
        self.screen: Optional[PygameUIWindow] = None
        self.grid: Optional[PygameUIGrid] = None
        self.buttons: list[PygameUIButton] = []

    def build_window(self, width: int, height: int) -> None:
        self.screen = PygameUIWindow(width, height)

    def build_grid(self, n_cells_x: int, n_cells_y: int, cell_width: int, cell_height: int) -> None:
        self.grid = PygameUIGrid(n_cells_x, n_cells_y, cell_width, cell_height)

    def build_button(self, name: str, label: str, width: int, height: int, x: int, y: int) -> None:
        self.buttons.append(PygameUIButton(name, label, width, height, x, y))

    def get_ui(self) -> PygameUI:
        return PygameUI(self.screen, self.grid, self.buttons)
