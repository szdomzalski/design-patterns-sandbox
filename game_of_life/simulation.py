"""Own and advance Game of Life boards."""

import numpy as np

from .game_logic import GameOfLifeRuleset


class InvalidBoardError(ValueError):
    """Report a board that cannot represent a Game of Life simulation."""


class Simulation:
    """Own the current board and advance it with an injected ruleset strategy."""

    def __init__(self, board: np.ndarray, ruleset: GameOfLifeRuleset) -> None:
        """Initialize the simulation with a validated defensive board copy.

        Args:
            board: A non-empty two-dimensional array containing only zeroes and ones.
            ruleset: The strategy used to calculate each generation.

        Returns:
            None.
        """
        self.board = self._validated_initial_board(board)
        self._ruleset = ruleset

    def step(self) -> None:
        """Advance the board by one generation using the configured ruleset.

        Args:
            None.

        Returns:
            None.
        """
        self.board = self._ruleset.next_generation(self.board)

    @staticmethod
    def _validated_initial_board(board: np.ndarray) -> np.ndarray:
        """Validate and normalize a defensive copy of the initial board.

        Args:
            board: Board to validate.

        Returns:
            Owned two-dimensional board normalized to unsigned 8-bit integers.
        """
        if not isinstance(board, np.ndarray):
            raise InvalidBoardError("board must be a NumPy array")
        if board.ndim != 2:
            raise InvalidBoardError("board must be two-dimensional")
        if board.size == 0:
            raise InvalidBoardError("board must not be empty")
        if not np.isin(board, (0, 1)).all():
            raise InvalidBoardError("board values must be either 0 or 1")
        return board.astype(np.uint8, copy=True)


class SimulationFactory:
    """Create simulations whose initial boards are generated from settings."""

    @staticmethod
    def create_random(
            cells_x: int,
            cells_y: int,
            alive_probability: float,
            random_seed: int,
            ruleset: GameOfLifeRuleset) -> Simulation:
        """Create a simulation with a reproducible random initial board.

        Args:
            cells_x: Number of cells along the board's x-axis.
            cells_y: Number of cells along the board's y-axis.
            alive_probability: Probability that an initial cell is alive.
            random_seed: Seed for the local random number generator.
            ruleset: Strategy used to advance the generated board.

        Returns:
            Simulation initialized with the generated board.
        """
        random_generator = np.random.default_rng(random_seed)
        board = random_generator.choice(
            [0, 1],
            size=(cells_x, cells_y),
            p=[1.0 - alive_probability, alive_probability],
        )
        return Simulation(board, ruleset)