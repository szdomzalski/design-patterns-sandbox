from abc import ABC, abstractmethod
import numpy as np
from scipy.signal import convolve2d


class GameOfLifeRuleset(ABC):
    '''
    Abstract base class for Game of Life rulesets.
    This class defines the interface for calculating the next generation of the game state.
    Concrete rulesets should inherit from this class and implement the next_generation method.
    '''
    @abstractmethod
    def next_generation(self, state: np.ndarray) -> np.ndarray:
        '''
        Calculate the next generation of the game state.
        :param state: Current game state as a 2D numpy array.
        :return: Next generation as a 2D numpy array.
        '''
        pass


class ClassicGameOfLife(GameOfLifeRuleset):
    '''
    Classic Game of Life ruleset implementation.
    Implements Conway's original rules for cell survival and birth.
    '''
    def next_generation(self, state: np.ndarray) -> np.ndarray:
        '''
        Calculate the next generation of the game state using Conway's rules.
        :param state: Current game state as a 2D numpy array.
        :return: Next generation as a 2D numpy array.
        '''
        kernel = np.array([[1, 1, 1],
                          [1, 0, 1],
                          [1, 1, 1]])
        neighbors = convolve2d(state, kernel, mode='same', boundary='fill', fillvalue=0)
        birth = (state == 0) & (neighbors == 3)
        survive = (state == 1) & ((neighbors == 2) | (neighbors == 3))
        return np.where(birth | survive, 1, 0)


class RulesetFactoryError(ValueError):
    """Report an unknown Game of Life ruleset name."""


class RulesetFactory:
    """Create ruleset strategies registered under configuration-friendly names."""

    _rulesets: dict[str, type[GameOfLifeRuleset]] = {
        'classic': ClassicGameOfLife,
    }

    @classmethod
    def create(cls, name: str) -> GameOfLifeRuleset:
        """Create the ruleset registered under the supplied name."""
        try:
            ruleset_type = cls._rulesets[name]
        except KeyError as error:
            raise RulesetFactoryError(f"Unknown ruleset: {name!r}") from error
        return ruleset_type()
