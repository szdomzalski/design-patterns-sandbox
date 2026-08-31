import argparse
import os

from .config_loader import ConfigError, ConfigLoaderFactory
from .event_handling import SystemClock, Ticker
from .game_controller import GameController
from .game_logic import RulesetFactory, RulesetFactoryError
from .simulation import SimulationFactory
from .ui import UIDirector
from .ui_pygame import PygameUIBuilder


def main() -> None:
    """Compose the application and run its controller loop."""
    # Parse command-line arguments for config path
    parser = argparse.ArgumentParser(description="Game of Life Application")
    parser.add_argument('--config', type=str, default=None,
                        help='Path to configuration file (default: bundled config/ui_config.json)')
    args = parser.parse_args()

    # Factory selection keeps the composition root independent of JSON, TOML,
    # YAML, and XML parsing details. The loader returns validated typed specs.
    CONFIG_PATH = args.config if args.config else os.path.join(
        os.path.dirname(__file__), 'config', 'ui_config.json')
    try:
        config_loader = ConfigLoaderFactory.create(CONFIG_PATH)
        application_config = config_loader.get_config()
        ruleset = RulesetFactory.create(application_config.simulation.ruleset)
    except (ConfigError, RulesetFactoryError) as e:
        print(f"Error: {e}")
        exit(1)

    simulation_config = application_config.simulation

    # The director translates the UI recipe into calls understood by the
    # concrete Pygame builder.
    builder = PygameUIBuilder()
    director = UIDirector(builder)
    ui = director.construct_ui(
        application_config.ui,
        simulation_config.cells_x,
        simulation_config.cells_y,
    )

    # The simulation factory owns reproducible board generation, while the
    # ruleset factory above selects the configured Strategy implementation.
    simulation = SimulationFactory.create_random(
        cells_x=simulation_config.cells_x,
        cells_y=simulation_config.cells_y,
        alive_probability=simulation_config.alive_probability,
        random_seed=simulation_config.random_seed,
        ruleset=ruleset,
    )
    # This clock schedules board generations. Pygame owns a separate clock
    # that limits UI input/render frames without changing simulation speed.
    ticker = Ticker(
        interval_sec=1.0 / simulation_config.updates_per_second,
        clock=SystemClock(),
    )
    game = GameController(simulation, ui, ticker)

    # Explicit Observer wiring keeps controls, controller, and ticker unaware
    # of each other's concrete implementations.
    ui.attach(game)
    ui.attach(ticker)

    game.run()


if __name__ == "__main__":
    main()
