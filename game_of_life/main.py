import argparse
import os
import numpy as np

from .config_loader import ConfigError, ConfigLoaderFactory
from .event_handling import SystemClock, Ticker
from .game_controller import GameController
from .game_logic import ClassicGameOfLife
from .simulation import Simulation
from .ui import UIDirector
from .ui_pygame import PygameUIBuilder


def main() -> None:
    """Compose the application and run its controller loop."""
    # Set a constant random seed for reproducibility
    np.random.seed(42)

    # Parse command-line arguments for config path
    parser = argparse.ArgumentParser(description="Game of Life Application")
    parser.add_argument('--config', type=str, default=None,
                        help='Path to configuration file (default: bundled config/ui_config.json)')
    args = parser.parse_args()

    CONFIG_PATH = args.config if args.config else os.path.join(
        os.path.dirname(__file__), 'config', 'ui_config.json')
    try:
        config_loader = ConfigLoaderFactory.create(CONFIG_PATH)
        ui_config = config_loader.get_config()
    except ConfigError as e:
        print(f"Error: {e}")
        exit(1)

    # For now, keep cell count fixed (can be made dynamic later)
    n_cells_x, n_cells_y = 40, 30

    builder = PygameUIBuilder()
    director = UIDirector(builder)
    ui = director.construct_ui(ui_config, n_cells_x, n_cells_y)

    initial_board_state = np.random.choice([0, 1], size=(n_cells_x, n_cells_y), p=[0.8, 0.2])
    simulation = Simulation(initial_board_state, ClassicGameOfLife())
    # This clock schedules board generations. Pygame owns a separate clock
    # that limits UI input/render frames without changing simulation speed.
    ticker = Ticker(interval_sec=0.1, clock=SystemClock())
    game = GameController(simulation, ui, ticker)

    ui.attach(game)
    ui.attach(ticker)

    game.run()


if __name__ == "__main__":
    main()
