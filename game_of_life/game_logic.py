"""Implement Game of Life rulesets and ruleset selection."""

from abc import ABC, abstractmethod

import numpy as np
from scipy.signal import convolve2d


class GameOfLifeRuleset(ABC):
    """Define the interface for calculating Game of Life generations.

    Concrete rulesets implement :meth:`next_generation`.
    """

    @abstractmethod
    def next_generation(self, state: np.ndarray) -> np.ndarray:
        """Calculate the next generation of the game state.

        Args:
            state: The current game state as a two-dimensional NumPy array.

        Returns:
            The next generation as a two-dimensional NumPy array.
        """


class LifeLikeRuleset(GameOfLifeRuleset):
    """Calculate generations from configurable birth and survival counts."""

    birth_counts: tuple[int, ...] = ()
    survival_counts: tuple[int, ...] = ()

    def next_generation(self, state: np.ndarray) -> np.ndarray:
        """Calculate a generation using configured birth and survival counts.

        Args:
            state: The current game state as a two-dimensional NumPy array.

        Returns:
            The next generation as a two-dimensional NumPy array.
        """
        kernel = np.array([[1, 1, 1],
                           [1, 0, 1],
                           [1, 1, 1]])
        neighbors = convolve2d(state, kernel, mode='same', boundary='fill', fillvalue=0)
        birth = (state == 0) & np.isin(neighbors, self.birth_counts)
        survive = (state == 1) & np.isin(neighbors, self.survival_counts)
        return np.where(birth | survive, 1, 0)


class ClassicGameOfLife(LifeLikeRuleset):
    """Implement Conway's original rules for cell survival and birth."""

    birth_counts = (3,)
    survival_counts = (2, 3)


class HighLife(LifeLikeRuleset):
    """Implement the HighLife ruleset (B36/S23), known for its replicator pattern."""

    birth_counts = (3, 6)
    survival_counts = (2, 3)


class DayAndNight(LifeLikeRuleset):
    """Implement the Day & Night ruleset (B3678/S34678), symmetric under inversion."""

    birth_counts = (3, 6, 7, 8)
    survival_counts = (3, 4, 6, 7, 8)


class RulesetFactoryError(ValueError):
    """Report an unknown Game of Life ruleset name."""


class RulesetFactory:
    """Create ruleset strategies registered under configuration-friendly names."""

    _rulesets: dict[str, type[GameOfLifeRuleset]] = {  # noqa: RUF012
        'classic': ClassicGameOfLife,
        'highlife': HighLife,
        'day_and_night': DayAndNight,
    }

    @classmethod
    def create(cls, name: str) -> GameOfLifeRuleset:
        """Create the ruleset registered under the supplied name.

        Args:
            name: Configuration-friendly ruleset name.

        Returns:
            A new instance of the registered ruleset.
        """
        try:
            ruleset_type = cls._rulesets[name]
        except KeyError as error:
            raise RulesetFactoryError(f"Unknown ruleset: {name!r}") from error
        return ruleset_type()
