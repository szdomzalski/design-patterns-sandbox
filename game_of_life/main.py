import argparse
import os

from .config_loader import ConfigError, ConfigLoaderFactory
from .event_handling import Clock, SystemClock, Ticker
from .game_controller import GameController
from .game_logic import RulesetFactory, RulesetFactoryError
from .simulation import SimulationFactory
from .ui import UIBuilder, UIDirector
from .ui_pygame import PygameUIBuilder


DEFAULT_CONFIG_PATH = os.path.join(
    os.path.dirname(__file__), 'config', 'ui_config.json')


def compose_game(config_path: str, ui_builder: UIBuilder, clock: Clock) -> GameController:
    """Compose a game controller from configuration and injected adapters.

    :param config_path: Path to any configuration format supported by the loader factory.
    :param ui_builder: Builder for the concrete UI adapter.
    :param clock: Monotonic simulation clock implementation.
    :return: A fully wired controller that has not started its run loop.
    """
    config_loader = ConfigLoaderFactory.create(config_path)
    application_config = config_loader.get_config()
    simulation_config = application_config.simulation
    ruleset = RulesetFactory.create(simulation_config.ruleset)

    ui = UIDirector(ui_builder).construct_ui(
        application_config.ui,
        simulation_config.cells_x,
        simulation_config.cells_y,
    )
    simulation = SimulationFactory.create_random(
        cells_x=simulation_config.cells_x,
        cells_y=simulation_config.cells_y,
        alive_probability=simulation_config.alive_probability,
        random_seed=simulation_config.random_seed,
        ruleset=ruleset,
    )
    ticker = Ticker(
        interval_sec=1.0 / simulation_config.updates_per_second,
        clock=clock,
    )
    game = GameController(simulation, ui, ticker)

    ui.attach(game)
    ui.attach(ticker)
    return game


def main() -> None:
    """Compose the application and run its controller loop."""
    # Parse command-line arguments for config path
    parser = argparse.ArgumentParser(description="Game of Life Application")
    parser.add_argument('--config', type=str, default=None,
                        help='Path to configuration file (default: bundled config/ui_config.json)')
    args = parser.parse_args()

    # Factory selection keeps the composition root independent of JSON, TOML,
    # YAML, and XML parsing details. The loader returns validated typed specs.
    config_path = args.config if args.config else DEFAULT_CONFIG_PATH
    try:
        game = compose_game(config_path, PygameUIBuilder(), SystemClock())
    except (ConfigError, RulesetFactoryError) as e:
        print(f"Error: {e}")
        exit(1)

    game.run()


if __name__ == "__main__":
    main()
