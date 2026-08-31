import numpy as np
import pytest

from game_of_life.game_logic import ClassicGameOfLife, RulesetFactory, RulesetFactoryError


def test_block_is_still_life() -> None:
    board = np.array([
        [0, 0, 0, 0],
        [0, 1, 1, 0],
        [0, 1, 1, 0],
        [0, 0, 0, 0],
    ])

    next_board = ClassicGameOfLife().next_generation(board)

    np.testing.assert_array_equal(next_board, board)


def test_blinker_oscillates() -> None:
    board = np.array([
        [0, 0, 0, 0, 0],
        [0, 0, 1, 0, 0],
        [0, 0, 1, 0, 0],
        [0, 0, 1, 0, 0],
        [0, 0, 0, 0, 0],
    ])
    expected = np.array([
        [0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0],
        [0, 1, 1, 1, 0],
        [0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0],
    ])

    next_board = ClassicGameOfLife().next_generation(board)

    np.testing.assert_array_equal(next_board, expected)


def test_cells_outside_board_are_dead() -> None:
    board = np.array([
        [1, 0, 0],
        [1, 0, 0],
        [1, 0, 0],
    ])
    expected = np.array([
        [0, 0, 0],
        [1, 1, 0],
        [0, 0, 0],
    ])

    next_board = ClassicGameOfLife().next_generation(board)

    np.testing.assert_array_equal(next_board, expected)


def test_ruleset_factory_creates_registered_strategy() -> None:
    assert isinstance(RulesetFactory.create('classic'), ClassicGameOfLife)


def test_ruleset_factory_rejects_unknown_strategy() -> None:
    with pytest.raises(RulesetFactoryError, match="Unknown ruleset"):
        RulesetFactory.create('unknown')