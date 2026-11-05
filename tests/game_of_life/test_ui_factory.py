import pytest

from game_of_life.ui_factory import UIBuilderFactory, UIBuilderFactoryError
from game_of_life.ui_pygame import PygameUIBuilder
from game_of_life.ui_tkinter import TkinterUIBuilder


def test_factory_creates_pygame_builder() -> None:
    assert isinstance(UIBuilderFactory.create('pygame'), PygameUIBuilder)


def test_factory_creates_tkinter_builder() -> None:
    assert isinstance(UIBuilderFactory.create('tkinter'), TkinterUIBuilder)


def test_factory_rejects_unknown_engine() -> None:
    with pytest.raises(UIBuilderFactoryError, match="Unknown UI engine: 'unknown'"):
        UIBuilderFactory.create('unknown')