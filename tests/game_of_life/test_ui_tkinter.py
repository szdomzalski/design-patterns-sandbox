import pytest

from game_of_life.event_handling import Event, EventSubscriber, EventType
from game_of_life.ui import UIBuilderError
from game_of_life.ui_tkinter import (
    TkinterUIButton,
    TkinterUI,
    TkinterUIBuilder,
    TkinterUIGrid,
    TkinterUISlider,
    TkinterUIWindow,
)


class RecordingSubscriber(EventSubscriber):
    def __init__(self) -> None:
        self.events: list[Event] = []

    def notify(self, event: Event) -> None:
        self.events.append(event)


def disable_window_setup(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(TkinterUIWindow, "setup", lambda window: None)
    monkeypatch.setattr(TkinterUIWindow, "set_close_handler", lambda window, handler: None)
    monkeypatch.setattr(TkinterUIButton, "mount", lambda button, window: None)
    monkeypatch.setattr(TkinterUISlider, "mount", lambda slider, window: None)


def test_ui_forwards_events_from_its_controls(monkeypatch: pytest.MonkeyPatch) -> None:
    disable_window_setup(monkeypatch)
    button = TkinterUIButton("Start", 100, 20, 0, 0, EventType.UI_START)
    ui = TkinterUI(
        TkinterUIWindow(100, 100),
        TkinterUIGrid(n_cells_x=1, n_cells_y=1, cell_width=1, cell_height=1),
        [button],
    )
    subscriber = RecordingSubscriber()
    ui.attach(subscriber)

    button.on_click()

    assert subscriber.events == [Event(EventType.UI_START)]


def test_slider_publishes_changed_value() -> None:
    slider = TkinterUISlider(
        x=0,
        y=0,
        width=100,
        height=20,
        min_value=1.0,
        max_value=11.0,
        initial_value=1.0,
        event=EventType.SPEED_CHANGE,
    )
    subscriber = RecordingSubscriber()
    slider.attach(subscriber)

    slider.on_change("6.0")

    assert subscriber.events == [Event(EventType.SPEED_CHANGE, 6.0)]


def test_builder_rejects_components_built_before_required_parts() -> None:
    builder = TkinterUIBuilder()

    with pytest.raises(UIBuilderError, match="build the window"):
        builder.build_grid(n_cells_x=1, n_cells_y=1, cell_width=10, cell_height=10)

    builder.build_window(width=100, height=100)
    with pytest.raises(UIBuilderError, match="build the grid"):
        builder.build_button("Start", 50, 20, 0, 80, EventType.UI_START)


def test_builder_creates_independent_products(monkeypatch: pytest.MonkeyPatch) -> None:
    disable_window_setup(monkeypatch)
    builder = TkinterUIBuilder()

    builder.build_window(width=100, height=100)
    builder.build_grid(n_cells_x=10, n_cells_y=10, cell_width=10, cell_height=10)
    first_ui = builder.get_ui()

    builder.build_window(width=200, height=200)
    builder.build_grid(n_cells_x=10, n_cells_y=10, cell_width=20, cell_height=20)
    second_ui = builder.get_ui()

    assert first_ui is not second_ui
    assert (first_ui.screen.width, first_ui.screen.height) == (100, 100)
    assert (second_ui.screen.width, second_ui.screen.height) == (200, 200)