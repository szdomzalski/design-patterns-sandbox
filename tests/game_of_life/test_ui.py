from typing import Any

import pytest

from game_of_life.config_loader import ButtonSpec, ConfigError, GridSpec, SliderSpec, UIConfig, WindowSpec
from game_of_life.event_handling import EventType
from game_of_life.ui import UI, UIBuilder, UIDirector


class NullUI(UI):
    """Provide an inert product for recording builder calls."""

    def render(self, board_state: Any) -> None:
        pass

    def process_events(self) -> None:
        pass

    def finish_frame(self) -> None:
        pass

    def close(self) -> None:
        pass


class RecordingBuilder(UIBuilder):
    """Record the named values passed from the director to the builder."""

    def __init__(self) -> None:
        self.calls: list[tuple[Any, ...]] = []
        self.ui = NullUI()

    def build_window(self, width: int, height: int) -> None:
        self.calls.append(("window", width, height))

    def build_grid(self, n_cells_x: int, n_cells_y: int, cell_width: int, cell_height: int) -> None:
        self.calls.append(("grid", n_cells_x, n_cells_y, cell_width, cell_height))

    def build_button(self, label: str, width: int, height: int, x: int, y: int, event: EventType) -> None:
        self.calls.append(("button", label, width, height, x, y, event))

    def build_slider(
            self,
            x: int,
            y: int,
            width: int,
            height: int,
            min_value: float,
            max_value: float,
            initial_value: float,
            event: EventType) -> None:
        self.calls.append(("slider", x, y, width, height, min_value, max_value, initial_value, event))

    def get_ui(self) -> UI:
        self.calls.append(("get_ui",))
        return self.ui


def test_director_builds_ui_from_typed_specs() -> None:
    config = UIConfig(
        window=WindowSpec(100, 120),
        grid=GridSpec(100, 80),
        buttons=(ButtonSpec("Start", 40, 20, 0, 80, EventType.UI_START),),
        sliders=(SliderSpec(0, 100, 100, 20, 1.0, 10.0, 5.0, EventType.SPEED_CHANGE),),
    )
    builder = RecordingBuilder()

    result = UIDirector(builder).construct_ui(config, n_cells_x=10, n_cells_y=8)

    assert result is builder.ui
    assert builder.calls == [
        ("window", 100, 120),
        ("grid", 10, 8, 10, 10),
        ("button", "Start", 40, 20, 0, 80, EventType.UI_START),
        ("slider", 0, 100, 100, 20, 1.0, 10.0, 5.0, EventType.SPEED_CHANGE),
        ("get_ui",),
    ]


def test_director_rejects_grid_that_cannot_form_equal_cells() -> None:
    config = UIConfig(window=WindowSpec(100, 100), grid=GridSpec(100, 80))

    with pytest.raises(ConfigError, match="divisible by board dimensions"):
        # A 100 px grid cannot be split into 6 equal integer-width cells
        # because 100 is not divisible by 6. The height, 80 / 8, is valid.
        UIDirector(RecordingBuilder()).construct_ui(config, n_cells_x=6, n_cells_y=8)