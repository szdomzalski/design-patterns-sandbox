import numpy as np

from .game_logic import GameOfLifeRuleset


class InvalidBoardError(ValueError):
    """Report a board that cannot represent a Game of Life simulation."""


class Simulation:
    """Own the current board and advance it with an injected ruleset strategy."""

    def __init__(self, board: np.ndarray, ruleset: GameOfLifeRuleset) -> None:
        """Initialize the simulation with a validated defensive board copy.

        :param board: A non-empty two-dimensional array containing only zeroes and ones.
        :param ruleset: The strategy used to calculate each generation.
        """
        self.board = self._validated_initial_board(board)
        self._ruleset = ruleset

    def step(self) -> None:
        """Trust the ruleset to calculate and return a valid new generation."""
        self.board = self._ruleset.next_generation(self.board)

    @staticmethod
    def _validated_initial_board(board: np.ndarray) -> np.ndarray:
        """Validate and normalize an owned copy of the initial board."""
        if not isinstance(board, np.ndarray):
            raise InvalidBoardError("board must be a NumPy array")
        if board.ndim != 2:
            raise InvalidBoardError("board must be two-dimensional")
        if board.size == 0:
            raise InvalidBoardError("board must not be empty")
        if not np.isin(board, (0, 1)).all():
            raise InvalidBoardError("board values must be either 0 or 1")
        return board.astype(np.uint8, copy=True)