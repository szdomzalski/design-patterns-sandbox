from typing import Any

import numpy as np

from game_of_life.event_handling import Event, EventPublisher, EventType, TickSource
from game_of_life.game_controller import GameController
from game_of_life.ui import UI


class IncrementingRuleset:
    def __init__(self) -> None:
        self.calls = 0

    def next_generation(self, state: np.ndarray) -> np.ndarray:
        self.calls += 1
        return state + 1


class NullUI(UI):
    """Satisfy the UI interface without performing input or rendering work."""

    def render(self, board_state: Any) -> None:
        """Ignore rendering requests."""
        pass

    def process_events(self) -> None:
        """Process no input events."""
        pass

    def finish_frame(self) -> None:
        """Apply no frame-rate limit."""
        pass

    def close(self) -> None:
        """Release no resources."""
        pass


class FakeTicker(TickSource):
    """Return a predetermined sequence of tick decisions to controller tests."""

    def __init__(self, ticks: list[bool] | None = None) -> None:
        """Initialize the sequence of values returned by poll()."""
        self.ticks = iter(ticks or [])
        self.poll_count = 0

    def poll(self) -> bool:
        """Return the next tick decision, defaulting to no tick."""
        self.poll_count += 1
        return next(self.ticks, False)


def create_controller(
        board_state: np.ndarray,
        ruleset: IncrementingRuleset | None = None,
        ui: UI | None = None,
        ticker: TickSource | None = None) -> GameController:
    """Build a controller with inert test doubles for omitted collaborators."""
    return GameController(
        board_state,
        ruleset or IncrementingRuleset(),
        ui or NullUI(),
        ticker or FakeTicker(),
    )


def test_controller_only_advances_while_running() -> None:
    initial_board = np.zeros((2, 2), dtype=int)
    ruleset = IncrementingRuleset()
    controller = create_controller(initial_board, ruleset)
    publisher = EventPublisher()
    publisher.attach(controller)

    controller.tick()
    np.testing.assert_array_equal(controller.board_state, initial_board)
    assert ruleset.calls == 0

    publisher.publish(EventType.UI_START)
    controller.tick()
    np.testing.assert_array_equal(controller.board_state, np.ones((2, 2), dtype=int))
    assert ruleset.calls == 1

    publisher.publish(EventType.UI_STOP)
    controller.tick()
    np.testing.assert_array_equal(controller.board_state, np.ones((2, 2), dtype=int))
    assert ruleset.calls == 1


def test_controllers_have_independent_state() -> None:
    first = create_controller(np.zeros((1, 1), dtype=int))
    second = create_controller(np.full((1, 1), 10, dtype=int))

    first.notify(Event(EventType.UI_START))
    first.tick()

    assert first is not second
    np.testing.assert_array_equal(first.board_state, np.ones((1, 1), dtype=int))
    np.testing.assert_array_equal(second.board_state, np.full((1, 1), 10, dtype=int))


def test_repeated_start_and_stop_follow_state_action_matrix() -> None:
    ruleset = IncrementingRuleset()
    controller = create_controller(np.zeros((1, 1), dtype=int), ruleset)

    # The initial state is stopped. Stopping again is a no-op, and a tick
    # must not calculate a new generation.
    controller.stop()
    controller.tick()
    assert ruleset.calls == 0

    # Starting an already running game is a no-op. The following tick still
    # calculates exactly one generation rather than applying the action twice.
    controller.start()
    controller.start()
    controller.tick()
    assert ruleset.calls == 1

    # Stopping an already stopped game is also a no-op. A later tick leaves
    # the generation count unchanged.
    controller.stop()
    controller.stop()
    controller.tick()
    assert ruleset.calls == 1


def test_quit_stops_application_loop() -> None:
    controller = create_controller(np.zeros((1, 1), dtype=int))
    controller.running = True

    controller.quit()

    assert controller.running is False


class QuittingUI(NullUI):
    """Record UI lifecycle calls and request quit after a chosen frame count."""

    def __init__(self, quit_after_runs: int = 1) -> None:
        """Configure the event-processing call on which the UI requests quit."""
        super().__init__()
        self.quit_callback = lambda: None
        self.quit_after_runs = quit_after_runs
        self.run_count = 0
        self.render_count = 0
        self.finished_frame_count = 0
        self.closed = False

    def render(self, board_state: Any) -> None:
        """Record that a frame was rendered."""
        self.render_count += 1

    def process_events(self) -> None:
        """Record event processing and request quit at the configured count."""
        self.run_count += 1
        if self.run_count >= self.quit_after_runs:
            self.quit_callback()

    def finish_frame(self) -> None:
        """Record completion of a UI frame."""
        self.finished_frame_count += 1

    def close(self) -> None:
        """Record that the UI was closed."""
        self.closed = True


def test_run_processes_quit_without_waiting_for_simulation_tick() -> None:
    """A UI quit event exits before simulation polling or frame completion."""
    ui = QuittingUI()
    ticker = FakeTicker()
    controller = create_controller(np.zeros((1, 1), dtype=int), ui=ui, ticker=ticker)
    ui.quit_callback = controller.quit

    controller.run()

    assert ui.run_count == 1
    assert ticker.poll_count == 0
    assert ui.finished_frame_count == 0
    assert ui.closed is True


def test_run_advances_once_when_ticker_reports_tick() -> None:
    """One due simulation tick advances one generation during a UI frame."""
    ui = QuittingUI(quit_after_runs=2)
    ticker = FakeTicker([True])
    ruleset = IncrementingRuleset()
    controller = create_controller(np.zeros((1, 1), dtype=int), ruleset, ui, ticker)
    ui.quit_callback = controller.quit
    controller.start()

    controller.run()

    assert ruleset.calls == 1
    assert ui.render_count == 2
    assert ui.finished_frame_count == 1
    assert ticker.poll_count == 1