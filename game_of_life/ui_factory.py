from importlib import import_module
from typing import cast

from .config_loader import ConfigError
from .ui import UIBuilder


class UIBuilderFactoryError(ConfigError):
    """Report an unknown UI engine name."""


class UIBuilderFactory:
    """Create UI builders registered under configuration-friendly names."""

    # Store import targets instead of concrete classes so an engine's optional
    # dependencies are required only when configuration selects that engine.
    _builders: dict[str, tuple[str, str]] = {  # noqa: RUF012
        'pygame': ('.ui_pygame', 'PygameUIBuilder'),
        'tkinter': ('.ui_tkinter', 'TkinterUIBuilder'),
    }

    @classmethod
    def create(cls, engine: str) -> UIBuilder:
        """Create the builder registered for the configured UI engine."""
        try:
            module_name, builder_name = cls._builders[engine]
        except KeyError as error:
            raise UIBuilderFactoryError(f"Unknown UI engine: {engine!r}") from error
        try:
            # Resolve the selected adapter here rather than at module import time.
            module = import_module(module_name, package=__package__)
        except ImportError as error:
            raise UIBuilderFactoryError(
                f"UI engine {engine!r} is unavailable: {error}") from error
        # getattr() returns Any for a dynamic name; cast restores the registry's
        # UIBuilder type for static analysis without changing the runtime object.
        builder_type = cast(type[UIBuilder], getattr(module, builder_name))
        return builder_type()