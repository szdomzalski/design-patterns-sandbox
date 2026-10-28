import json
from pathlib import Path

import pytest

from game_of_life.config_loader import (
    ApplicationConfig,
    ButtonSpec,
    ConfigError,
    ConfigLoaderFactory,
    ConfigLoaderFactoryError,
    GridSpec,
    SimulationSpec,
    SliderSpec,
    UIConfig,
    WindowSpec,
    XMLConfigLoader,
)
from game_of_life.event_handling import EventType


CONFIG_DIR = Path(__file__).parents[2] / "game_of_life" / "config"


def expected_config() -> ApplicationConfig:
    """Return the UI represented by every example configuration format."""
    return ApplicationConfig(
        simulation=SimulationSpec(
            cells_x=40,
            cells_y=30,
            alive_probability=0.2,
            random_seed=42,
            updates_per_second=10,
            ruleset="classic",
        ),
        ui=UIConfig(
            window=WindowSpec(800, 800),
            grid=GridSpec(800, 600),
            buttons=(
                ButtonSpec("Stop", 200, 50, 180, 640, EventType.UI_STOP),
                ButtonSpec("Start", 200, 50, 420, 640, EventType.UI_START),
            ),
            sliders=(
                SliderSpec(150, 740, 500, 20, 1.0, 50.0, 10.0, EventType.SPEED_CHANGE),
            ),
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
        "simulation": {
            "cells_x": 10,
            "cells_y": 10,
            "alive_probability": 0.2,
            "random_seed": 42,
            "updates_per_second": 10,
            "ruleset": "classic",
        },
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


def test_rejects_invalid_simulation_settings() -> None:
    with pytest.raises(ConfigError, match="alive_probability must be between 0 and 1"):
        SimulationSpec(
            cells_x=40,
            cells_y=30,
            alive_probability=1.1,
            random_seed=42,
            updates_per_second=10,
            ruleset="classic",
        )


def test_rejects_non_integer_simulation_speed() -> None:
    with pytest.raises(ConfigError, match="updates_per_second must be a positive integer"):
        SimulationSpec(
            cells_x=40,
            cells_y=30,
            alive_probability=0.2,
            random_seed=42,
            updates_per_second=10.5,
            ruleset="classic",
        )


def test_speed_slider_initial_value_comes_from_simulation(tmp_path: Path) -> None:
    config_data = json.loads((CONFIG_DIR / "ui_config.json").read_text())
    config_data['simulation']['updates_per_second'] = 20
    # A configured value is deliberately ignored only for SPEED_CHANGE.
    config_data['sliders'][0]['initial_value'] = 5
    config_path = tmp_path / "configured_speed.json"
    config_path.write_text(json.dumps(config_data))

    config = ConfigLoaderFactory.create(str(config_path)).get_config()

    assert config.ui.sliders[0].initial_value == 20


def test_xml_preserves_optional_slider_initial_value_before_speed_override(tmp_path: Path) -> None:
    xml = (CONFIG_DIR / "ui_config.xml").read_text().replace(
        'event="SPEED_CHANGE"',
        'initial_value="5.0" event="SPEED_CHANGE"',
    )
    config_path = tmp_path / "configured_speed.xml"
    config_path.write_text(xml)
    loader = XMLConfigLoader(str(config_path))

    parsed_mapping = loader._read_mapping()
    config = loader.get_config()

    # XML parsing preserves the optional slider value of 5.0. The complete
    # application adapter then replaces it with simulation speed (10) because
    # this particular slider publishes SPEED_CHANGE.
    assert parsed_mapping['sliders'][0]['initial_value'] == 5.0
    assert config.ui.sliders[0].initial_value == config.simulation.updates_per_second


def test_rejects_board_dimensions_incompatible_with_grid() -> None:
    with pytest.raises(ConfigError, match="divisible by board dimensions"):
        ApplicationConfig(
            simulation=SimulationSpec(
                cells_x=6,
                cells_y=8,
                alive_probability=0.2,
                random_seed=42,
                updates_per_second=10,
                ruleset="classic",
            ),
            ui=UIConfig(window=WindowSpec(100, 100), grid=GridSpec(100, 80)),
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