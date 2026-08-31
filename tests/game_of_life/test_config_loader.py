from pathlib import Path

import pytest

from game_of_life.config_loader import ConfigLoaderFactory, ConfigLoaderFactoryError
from game_of_life.event_handling import EventType


GAME_OF_LIFE_DIR = Path(__file__).parents[2] / "game_of_life"


def test_loads_existing_json_ui_configuration() -> None:
    loader = ConfigLoaderFactory.create(str(GAME_OF_LIFE_DIR / "ui_config.json"))

    config = loader.get_config()

    assert (config.width, config.height) == (800, 800)
    assert (config.grid_width, config.grid_height) == (800, 600)
    assert [button[0] for button in config.buttons] == ["Stop", "Start"]
    assert [button[-1] for button in config.buttons] == [EventType.UI_STOP, EventType.UI_START]
    assert config.sliders == [
        (150, 740, 500, 20, 1.0, 50.0, 10.0, EventType.SPEED_CHANGE),
    ]


def test_rejects_unsupported_config_format() -> None:
    with pytest.raises(ConfigLoaderFactoryError, match="Unsupported or missing config file extension"):
        ConfigLoaderFactory.create("ui_config.toml")