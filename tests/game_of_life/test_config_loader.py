import json
from pathlib import Path

import pytest

from game_of_life.config_loader import (
    ButtonSpec,
    ConfigError,
    ConfigLoaderFactory,
    ConfigLoaderFactoryError,
    GridSpec,
    SliderSpec,
    UIConfig,
    WindowSpec,
)
from game_of_life.event_handling import EventType


CONFIG_DIR = Path(__file__).parents[2] / "game_of_life" / "config"


def expected_config() -> UIConfig:
    """Return the UI represented by every example configuration format."""
    return UIConfig(
        window=WindowSpec(800, 800),
        grid=GridSpec(800, 600),
        buttons=(
            ButtonSpec("Stop", 200, 50, 180, 640, EventType.UI_STOP),
            ButtonSpec("Start", 200, 50, 420, 640, EventType.UI_START),
        ),
        sliders=(
            SliderSpec(150, 740, 500, 20, 1.0, 50.0, 10.0, EventType.SPEED_CHANGE),
        ),
    )


@pytest.mark.parametrize("file_name", [
    "ui_config.json",
    "ui_config.toml",
    "ui_config.yaml",
    "ui_config.xml",
])
def test_loaders_produce_equivalent_ui_configuration(file_name: str) -> None:
    loader = ConfigLoaderFactory.create(str(CONFIG_DIR / file_name))

    config = loader.get_config()

    assert config == expected_config()


def test_yml_extension_uses_yaml_loader(tmp_path: Path) -> None:
    config_path = tmp_path / "ui_config.yml"
    config_path.write_text((CONFIG_DIR / "ui_config.yaml").read_text())

    assert ConfigLoaderFactory.create(str(config_path)).get_config() == expected_config()


@pytest.mark.parametrize(("extension", "content"), [
    (".json", "{"),
    (".toml", "window = ["),
    (".yaml", "window: ["),
    (".xml", "<ui>"),
])
def test_loaders_report_malformed_sources(extension: str, content: str, tmp_path: Path) -> None:
    config_path = tmp_path / f"invalid{extension}"
    config_path.write_text(content)

    with pytest.raises(ConfigError, match="Invalid configuration"):
        ConfigLoaderFactory.create(str(config_path)).get_config()


def test_rejects_unknown_event_name(tmp_path: Path) -> None:
    config_path = tmp_path / "invalid.json"
    config_path.write_text(json.dumps({
        "window": {"width": 100, "height": 100},
        "grid": {"width": 100, "height": 80},
        "buttons": [{
            "label": "Start",
            "width": 50,
            "height": 20,
            "x": 0,
            "y": 80,
            "event": "NOT_AN_EVENT",
        }],
    }))

    with pytest.raises(ConfigError, match="Unknown event type"):
        ConfigLoaderFactory.create(str(config_path)).get_config()


def test_rejects_invalid_slider_range() -> None:
    with pytest.raises(ConfigError, match="min_value must be less"):
        SliderSpec(
            x=0,
            y=0,
            width=100,
            height=20,
            min_value=10.0,
            max_value=1.0,
            initial_value=5.0,
            event=EventType.SPEED_CHANGE,
        )


def test_rejects_control_outside_window() -> None:
    with pytest.raises(ConfigError, match="controls must fit"):
        UIConfig(
            window=WindowSpec(100, 100),
            grid=GridSpec(100, 80),
            # The button starts at x=75 and is 50 px wide, so its right edge
            # is x=125, beyond the 100 px window width.
            buttons=(ButtonSpec(
                label="Start",
                width=50,
                height=20,
                x=75,
                y=80,
                event=EventType.UI_START,
            ),),
        )


def test_rejects_unsupported_config_format() -> None:
    with pytest.raises(ConfigLoaderFactoryError, match="Unsupported or missing config file extension"):
        ConfigLoaderFactory.create("ui_config.ini")