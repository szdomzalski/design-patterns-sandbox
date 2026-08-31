from typing import Any

import numpy as np

from game_of_life.event_handling import Event, EventPublisher, EventType
from game_of_life.game_controller import GameController
from game_of_life.ui import UI


class IncrementingRuleset:
    def __init__(self) -> None:
        self.calls = 0

    def next_generation(self, state: np.ndarray) -> np.ndarray:
        self.calls += 1
        return state + 1


class NullUI(UI):
    def render(self, board_state: Any) -> None:
        pass

    def run(self) -> None:
        pass

    def close(self) -> None:
        pass


def test_controller_only_advances_while_running() -> None:
    initial_board = np.zeros((2, 2), dtype=int)
    ruleset = IncrementingRuleset()
    controller = GameController(initial_board, ruleset, NullUI())
    publisher = EventPublisher()
    publisher.attach(controller)

    publisher.publish(EventType.TIMER_TICK)
    np.testing.assert_array_equal(controller.board_state, initial_board)
    assert ruleset.calls == 0

    publisher.publish(EventType.UI_START)
    publisher.publish(EventType.TIMER_TICK)
    np.testing.assert_array_equal(controller.board_state, np.ones((2, 2), dtype=int))
    assert ruleset.calls == 1

    publisher.publish(EventType.UI_STOP)
    publisher.publish(EventType.TIMER_TICK)
    np.testing.assert_array_equal(controller.board_state, np.ones((2, 2), dtype=int))
    assert ruleset.calls == 1


def test_controllers_have_independent_state() -> None:
    first = GameController(np.zeros((1, 1), dtype=int), IncrementingRuleset(), NullUI())
    second = GameController(np.full((1, 1), 10, dtype=int), IncrementingRuleset(), NullUI())

    first.notify(Event(EventType.UI_START))
    first.notify(Event(EventType.TIMER_TICK))

    assert first is not second
    np.testing.assert_array_equal(first.board_state, np.ones((1, 1), dtype=int))
    np.testing.assert_array_equal(second.board_state, np.full((1, 1), 10, dtype=int))