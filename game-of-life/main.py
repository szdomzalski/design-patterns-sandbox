import numpy as np
from game_logic import ClassicGameOfLife
from ui import UIDirector
from ui_pygame import PygameUIBuilder
import pygame
import os
import argparse
from config_loader import ConfigLoaderFactory, ConfigLoaderFactoryError
from event_handling import TimerEventPublisher
from game_controller import GameController

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

board_state = np.random.choice([0, 1], size=(n_cells_x, n_cells_y), p=[0.8, 0.2])
game_logic = ClassicGameOfLife()

controller = GameController(game_logic, board_state)
timer = TimerEventPublisher(interval_sec=0.1, step_sec=0.01)
timer.attach(controller)

with timer:
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                for name, (label, b_width, b_height, b_x, b_y) in ui.buttons.items():
                    if b_x <= event.pos[0] <= b_x + b_width and b_y <= event.pos[1] <= b_y + b_height:
                        if name == "stop":
                            timer.stop()
                        # Add more button actions here
                        break
                # Only handle button clicks, do not break for non-button clicks
        if controller.update_needed:
            ui.render(controller.get_state())
            controller.update_needed = False
pygame.quit()

