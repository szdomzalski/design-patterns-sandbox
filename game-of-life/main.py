import numpy as np
from game_logic import ClassicGameOfLife
from ui_director import UIDirector
from ui_pygame_builder import PygameUIBuilder
import pygame

# Set a constant random seed for reproducibility
np.random.seed(42)

# UI config
grid_width, grid_height = 800, 600
n_cells_x, n_cells_y = 40, 30
cell_width = grid_width // n_cells_x
cell_height = grid_height // n_cells_y
button_width, button_height = 200, 50
button_x, button_y = (grid_width - button_width) // 2, grid_height - button_height - 10

config = {
    'width': grid_width,
    'height': grid_height,
    'n_cells_x': n_cells_x,
    'n_cells_y': n_cells_y,
    'cell_width': cell_width,
    'cell_height': cell_height,
    'buttons': [
        ("next", "Next Generation", button_width, button_height, button_x, button_y),
        # Add more buttons as needed: (name, label, width, height, x, y)
    ]
}

builder = PygameUIBuilder()
director = UIDirector(builder)
ui = director.construct_ui(config)

game_state = np.random.choice([0, 1], size=(n_cells_x, n_cells_y), p=[0.8, 0.2])
game_logic = ClassicGameOfLife()

running = True
while running:
    ui.update(game_state)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            for name, (label, b_width, b_height, b_x, b_y) in ui.buttons.items():
                if b_x <= event.pos[0] <= b_x + b_width and b_y <= event.pos[1] <= b_y + b_height:
                    if name == "next":
                        game_state = game_logic.next_generation(game_state)
                    # Add more button actions here
                    break
            else:
                n_cells_x, n_cells_y, cell_width, cell_height = ui.grid_params
                x, y = event.pos[0] // cell_width, event.pos[1] // cell_height
                game_state[x, y] = not game_state[x, y]
pygame.quit()

