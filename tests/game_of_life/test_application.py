from pathlib import Path
from typing import Any

import numpy as np
import pygame
import pytest

from game_of_life.event_handling import Clock, EventType
from game_of_life.game_logic import ClassicGameOfLife
from game_of_life.main import compose_game
from game_of_life.ui import UI, UIBuilder
from game_of_life.ui_pygame import PygameUIBuilder


CONFIG_PATH = Path(__file__).parents[2] / "game_of_life" / "config" / "ui_config.json"


class FakeClock(Clock):
    """Provide manually advanced simulation time to the composed ticker."""

    def __init__(self) -> None:
        self.current_time = 0.0

    def now(self) -> float:
        return self.current_time

    def advance(self, seconds: float) -> None:
        self.current_time += seconds


class ScriptedUI(UI):
    """Drive start, speed, and quit events while recording rendered boards."""

    def __init__(self, clock: FakeClock) -> None:
        super().__init__()
        self.clock = clock
        self.frame = 0
        self.rendered_boards: list[np.ndarray] = []
        self.closed = False

    def render(self, board_state: Any) -> None:
        self.rendered_boards.append(board_state.copy())

    def process_events(self) -> None:
        self.frame += 1
        # Frame 1 starts the game and raises speed from the configured 10 UPS
        # to 20 UPS. Frame 2 has no events, so its due tick advances the board.
        if self.frame == 1:
            self.publish(EventType.UI_START)
            self.publish(EventType.SPEED_CHANGE, 20)
        # Frame 3 quits before ticker polling or rendering another frame.
        elif self.frame == 3:
            self.publish(EventType.UI_QUIT)

    def finish_frame(self) -> None:
        # At 20 updates per second, advancing 0.05 seconds makes one tick due
        # on the next frame without sleeping in the test.
        self.clock.advance(0.05)

    def close(self) -> None:
        self.closed = True


class HeadlessUIBuilder(UIBuilder):
    """Accept the real UI recipe while returning a scripted test adapter."""

    def __init__(self, ui: ScriptedUI) -> None:
        self.ui = ui
        self.window_size: tuple[int, int] | None = None
        self.grid_shape: tuple[int, int] | None = None

    def build_window(self, width: int, height: int) -> None:
        self.window_size = (width, height)

    def build_grid(self, n_cells_x: int, n_cells_y: int, cell_width: int, cell_height: int) -> None:
        self.grid_shape = (n_cells_x, n_cells_y)

    def build_button(self, label: str, width: int, height: int, x: int, y: int, event: EventType) -> None:
        # Controls are accepted from the real recipe, but input is driven by
        # ScriptedUI so this builder does not need concrete control objects.
        pass

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
        pass

    def get_ui(self) -> UI:
        return self.ui


def test_composed_application_runs_one_configured_generation_headlessly() -> None:
    clock = FakeClock()
    ui = ScriptedUI(clock)
    builder = HeadlessUIBuilder(ui)
    game = compose_game(str(CONFIG_PATH), builder, clock)

    game.run()

    # These values prove the real config loader and UI director participated
    # in composition rather than the test constructing the model directly.
    assert builder.window_size == (800, 800)
    assert builder.grid_shape == (40, 30)

    # Render 0 is the initial display. Render 1 follows frame 1 before enough
    # time has elapsed; render 2 follows frame 2 and contains one generation.
    assert len(ui.rendered_boards) == 3
    np.testing.assert_array_equal(ui.rendered_boards[0], ui.rendered_boards[1])
    expected_generation = ClassicGameOfLife().next_generation(ui.rendered_boards[1])
    np.testing.assert_array_equal(ui.rendered_boards[2], expected_generation)
    assert ui.closed is True
