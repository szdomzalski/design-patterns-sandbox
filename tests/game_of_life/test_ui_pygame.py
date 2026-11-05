import pytest

from game_of_life.event_handling import Event, EventSubscriber, EventType
from game_of_life.ui import UIBuilderError
from game_of_life.ui_pygame import (
    PygameUIButton,
    PygameUI,
    PygameUIBuilder,
    PygameUIGrid,
    PygameUISlider,
    PygameUIWindow,
)


class RecordingSubscriber(EventSubscriber):
    def __init__(self) -> None:
        self.events: list[Event] = []

    def notify(self, event: Event) -> None:
        self.events.append(event)


class WindowWithoutDisplay(PygameUIWindow):
    def __init__(self) -> None:
        super().__init__(width=1, height=1)

    def setup(self) -> None:
        pass


def create_ui(
        buttons: list[PygameUIButton] | None = None,
        sliders: list[PygameUISlider] | None = None) -> PygameUI:
    return PygameUI(
        WindowWithoutDisplay(),
        PygameUIGrid(n_cells_x=1, n_cells_y=1, cell_width=1, cell_height=1),
        buttons or [],
        sliders or [],
    )


def test_button_has_no_hidden_application_subscriber() -> None:
    button = PygameUIButton("Start", 100, 20, 0, 0, EventType.UI_START)

    assert button.subscribers == []


def test_ui_forwards_events_from_its_controls() -> None:
    button = PygameUIButton("Start", 100, 20, 0, 0, EventType.UI_START)
    ui = create_ui(buttons=[button])
    subscriber = RecordingSubscriber()
    ui.attach(subscriber)

    button.on_click()

    assert subscriber.events == [Event(EventType.UI_START)]


def test_slider_publishes_its_updated_value() -> None:
    # Starting at (0, 0) simplifies the position calculation. A 100 px slider
    # with its 20 px handle has 80 px of horizontal travel.
    slider = PygameUISlider(
        x=0,
        y=0,
        width=100,
        height=20,
        # The value range is 1..11, so its midpoint is 6; start at the minimum.
        min_value=1.0,
        max_value=11.0,
        initial_value=1.0,
        event=EventType.SPEED_CHANGE,
    )
    subscriber = RecordingSubscriber()
    ui = create_ui(sliders=[slider])
    ui.attach(subscriber)

    slider.start_dragging()
    # x=40 is halfway through the 80 px travel, so the slider must publish 6.
    slider.update_drag(40)

    assert subscriber.events == [Event(EventType.SPEED_CHANGE, 6.0)]


def test_builder_rejects_components_built_before_required_parts() -> None:
    builder = PygameUIBuilder()

    with pytest.raises(UIBuilderError, match="build the window"):
        builder.build_grid(n_cells_x=1, n_cells_y=1, cell_width=10, cell_height=10)

    builder.build_window(width=100, height=100)
    with pytest.raises(UIBuilderError, match="build the grid"):
        builder.build_button("Start", 50, 20, 0, 80, EventType.UI_START)


def test_builder_rejects_incomplete_product() -> None:
    builder = PygameUIBuilder()

    with pytest.raises(UIBuilderError, match="build the window"):
        builder.get_ui()

    builder.build_window(width=100, height=100)
    with pytest.raises(UIBuilderError, match="build the grid"):
        builder.get_ui()


def test_builder_creates_independent_products(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(PygameUIWindow, "setup", lambda window: None)
    builder = PygameUIBuilder()

    builder.build_window(width=100, height=100)
    builder.build_grid(n_cells_x=10, n_cells_y=10, cell_width=10, cell_height=10)
    builder.build_button("Start", 50, 20, 0, 80, EventType.UI_START)
    first_ui = builder.get_ui()

    builder.build_window(width=200, height=200)
    builder.build_grid(n_cells_x=10, n_cells_y=10, cell_width=20, cell_height=20)
    second_ui = builder.get_ui()

    assert first_ui is not second_ui
    assert (first_ui.screen.width, first_ui.screen.height) == (100, 100)
    assert (second_ui.screen.width, second_ui.screen.height) == (200, 200)
    assert len(first_ui.buttons) == 1
    assert second_ui.buttons == []