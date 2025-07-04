import numpy as np
from game_logic import ClassicGameOfLife
from ui_director import UIDirector
from ui_pygame_builder import PygameUIBuilder
import pygame
import os
import argparse
from config_loader import ConfigLoaderFactory, ConfigLoaderFactoryError

# Set a constant random seed for reproducibility
np.random.seed(42)

# Parse command-line arguments for config path
parser = argparse.ArgumentParser(description="Game of Life Application")
parser.add_argument('--config', type=str, default=None, help='Path to configuration file (default: ./ui_config.json)')
args = parser.parse_args()

CONFIG_PATH = args.config if args.config else os.path.join(os.path.dirname(__file__), 'ui_config.json')
try:
    config_loader = ConfigLoaderFactory.create(CONFIG_PATH)
except ConfigLoaderFactoryError as e:
    print(f"Error: {e}")
    exit(1)
ui_config = config_loader.get_config()

# For now, keep cell count fixed (can be made dynamic later)
n_cells_x, n_cells_y = 40, 30

builder = PygameUIBuilder()
director = UIDirector(builder)
ui = director.construct_ui(ui_config, n_cells_x, n_cells_y)

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

