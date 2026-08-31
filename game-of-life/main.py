import argparse
import os
import numpy as np

from config_loader import ConfigLoaderFactory, ConfigLoaderFactoryError
from event_handling import Timer
from game_controller import GameController
from game_logic import ClassicGameOfLife
from ui import UIDirector
from ui_pygame import PygameUIBuilder


def main() -> None:
    # Set a constant random seed for reproducibility
    np.random.seed(42)

    # Parse command-line arguments for config path
    parser = argparse.ArgumentParser(description="Game of Life Application")
    parser.add_argument('--config', type=str, default=None,
                        help='Path to configuration file (default: ./ui_config.json)')
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

    game = GameController()
    builder = PygameUIBuilder()
    director = UIDirector(builder)
    ui = director.construct_ui(ui_config, n_cells_x, n_cells_y)
    ui.attach(game)

    initial_board_state = np.random.choice([0, 1], size=(n_cells_x, n_cells_y), p=[0.8, 0.2])
    game_logic = ClassicGameOfLife()

    game.set_board_state(initial_board_state)
    game.assign_ui(ui)
    game.assign_game_logic(game_logic)

    # Initialize timer with 10 updates per second (0.1s interval)
    timer = Timer(interval_sec=0.1, step_sec=0.01)
    timer.attach(game)

    # Configure speed control with the speed control publisher from UI
    timer.configure_speed_control(ui.get_speed_control())

    with timer:
        game.run()


if __name__ == "__main__":
    main()
