import numpy as np
import pytest

from game_of_life.game_logic import (
    ClassicGameOfLife,
    DayAndNight,
    HighLife,
    RulesetFactory,
    RulesetFactoryError,
)


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


def test_highlife_births_cell_with_six_neighbors() -> None:
    board = np.array([
        [1, 1, 1],
        [1, 0, 1],
        [1, 0, 0],
    ])

    assert HighLife().next_generation(board)[1, 1] == 1


def test_day_and_night_births_cell_with_seven_neighbors() -> None:
    board = np.array([
        [1, 1, 1],
        [1, 0, 1],
        [1, 1, 0],
    ])

    assert DayAndNight().next_generation(board)[1, 1] == 1


def test_day_and_night_cell_survives_with_four_neighbors() -> None:
    board = np.array([
        [1, 1, 0],
        [1, 1, 0],
        [1, 0, 0],
    ])

    assert DayAndNight().next_generation(board)[1, 1] == 1


@pytest.mark.parametrize(
    ('name', 'ruleset_type'),
    [
        ('classic', ClassicGameOfLife),
        ('highlife', HighLife),
        ('day_and_night', DayAndNight),
    ],
)
def test_ruleset_factory_creates_registered_strategy(
        name: str,
        ruleset_type: type[ClassicGameOfLife | HighLife | DayAndNight]) -> None:
    assert isinstance(RulesetFactory.create(name), ruleset_type)


def test_ruleset_factory_rejects_unknown_strategy() -> None:
    with pytest.raises(RulesetFactoryError, match="Unknown ruleset"):
        RulesetFactory.create('unknown')