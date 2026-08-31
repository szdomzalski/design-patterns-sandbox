import numpy as np

from game_of_life.event_handling import EventPublisher, EventType
from game_of_life.game_controller import GameController


class IncrementingRuleset:
    def __init__(self) -> None:
        self.calls = 0

    def next_generation(self, state: np.ndarray) -> np.ndarray:
        self.calls += 1
        return state + 1


def test_controller_only_advances_while_running() -> None:
    controller = GameController()
    initial_board = np.zeros((2, 2), dtype=int)
    ruleset = IncrementingRuleset()
    publisher = EventPublisher()
    controller.set_board_state(initial_board)
    controller.assign_game_logic(ruleset)
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