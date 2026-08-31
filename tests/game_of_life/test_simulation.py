import numpy as np
import pytest

from game_of_life.simulation import InvalidBoardError, Simulation, SimulationFactory


class InvertingRuleset:
    """Return the opposite value for every board cell."""

    def next_generation(self, state: np.ndarray) -> np.ndarray:
        return 1 - state


def test_simulation_owns_normalized_mutable_board() -> None:
    source = np.array([[0.0, 1.0]])
    simulation = Simulation(source, InvertingRuleset())
    source[0, 0] = 1.0

    assert simulation.board.dtype == np.uint8
    np.testing.assert_array_equal(simulation.board, np.array([[0, 1]], dtype=np.uint8))

    simulation.board[0, 0] = 1
    np.testing.assert_array_equal(simulation.board, np.array([[1, 1]], dtype=np.uint8))


def test_step_uses_ruleset_to_replace_board() -> None:
    simulation = Simulation(np.array([[0, 1]], dtype=int), InvertingRuleset())

    simulation.step()

    np.testing.assert_array_equal(simulation.board, np.array([[1, 0]], dtype=np.uint8))


def test_random_factory_is_reproducible_for_same_seed() -> None:
    first = SimulationFactory.create_random(
        cells_x=10,
        cells_y=8,
        alive_probability=0.2,
        random_seed=42,
        ruleset=InvertingRuleset(),
    )
    second = SimulationFactory.create_random(
        cells_x=10,
        cells_y=8,
        alive_probability=0.2,
        random_seed=42,
        ruleset=InvertingRuleset(),
    )

    assert first.board is not second.board
    np.testing.assert_array_equal(first.board, second.board)


@pytest.mark.parametrize(("board", "message"), [
    (np.array([0, 1]), "two-dimensional"),
    (np.empty((0, 2), dtype=int), "must not be empty"),
    (np.array([[0, 2]]), "either 0 or 1"),
])
def test_rejects_invalid_initial_board(board: np.ndarray, message: str) -> None:
    with pytest.raises(InvalidBoardError, match=message):
        Simulation(board, InvertingRuleset())