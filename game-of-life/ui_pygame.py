import pygame
import numpy as np
from ui import UIBuilder, UI, UIColor
from typing import Optional, Dict, Tuple


class PygameUI(UI):
    def __init__(self, screen: pygame.Surface, grid_params: tuple,
                 buttons: Dict[str, Tuple[str, int, int, int, int]]) -> None:
        self.screen: pygame.Surface = screen
        self.grid_params: tuple = grid_params
        self.buttons: Dict[str, Tuple[str, int, int, int, int]] = buttons  # Dict[name, (label, width, height, x, y)]

    def render(self, board_state: np.ndarray) -> None:
        self.screen.fill(UIColor.WHITE.value)
        self._draw_grid()
        self._draw_cells(board_state)
        self._draw_buttons()
        pygame.display.flip()

    def _draw_grid(self) -> None:
        n_cells_x, n_cells_y, cell_width, cell_height = self.grid_params
        for y in range(0, n_cells_y * cell_height, cell_height):
            for x in range(0, n_cells_x * cell_width, cell_width):
                cell = pygame.Rect(x, y, cell_width, cell_height)
                pygame.draw.rect(self.screen, UIColor.GRAY.value, cell, 1)

    def _draw_cells(self, board_state: np.ndarray) -> None:
        n_cells_x, n_cells_y, cell_width, cell_height = self.grid_params
        for y in range(n_cells_y):
            for x in range(n_cells_x):
                cell = pygame.Rect(x * cell_width, y * cell_height, cell_width, cell_height)
                if board_state[x, y] == 1:
                    pygame.draw.rect(self.screen, UIColor.BLACK.value, cell)

    def _draw_buttons(self) -> None:
        for name in self.buttons:
            self._draw_button(name)

    def _draw_button(self, name: str) -> None:
        btn_label, b_width, b_height, b_x, b_y = self.buttons[name]
        pygame.draw.rect(self.screen, UIColor.GREEN.value, (b_x, b_y, b_width, b_height))
        font = pygame.font.Font(None, 36)
        text = font.render(btn_label, True, UIColor.BLACK.value)
        text_rect = text.get_rect(center=(b_x + b_width // 2, b_y + b_height // 2))
        self.screen.blit(text, text_rect)


class PygameUIBuilder(UIBuilder):
    def __init__(self) -> None:
        self.screen: Optional[pygame.Surface] = None
        self.grid_params: Optional[tuple] = None
        self.buttons: Dict[str, Tuple[str, int, int, int, int]] = {}

    def build_window(self, width: int, height: int) -> None:
        pygame.init()
        self.screen = pygame.display.set_mode((width, height))

    def build_grid(self, n_cells_x: int, n_cells_y: int, cell_width: int, cell_height: int) -> None:
        self.grid_params = (n_cells_x, n_cells_y, cell_width, cell_height)

    def build_button(self, name: str, label: str, width: int, height: int, x: int, y: int) -> None:
        self.buttons[name] = (label, width, height, x, y)

    def get_ui(self) -> PygameUI:
        return PygameUI(self.screen, self.grid_params, self.buttons)
