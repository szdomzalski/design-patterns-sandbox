from .config_loader import ConfigError
from .ui import UIBuilder
from .ui_pygame import PygameUIBuilder


class UIBuilderFactoryError(ConfigError):
    """Report an unknown UI engine name."""


class UIBuilderFactory:
    """Create UI builders registered under configuration-friendly names."""

    _builders: dict[str, type[UIBuilder]] = {  # noqa: RUF012
        'pygame': PygameUIBuilder,
    }

    @classmethod
    def create(cls, engine: str) -> UIBuilder:
        """Create the builder registered for the configured UI engine."""
        try:
            builder_type = cls._builders[engine]
        except KeyError as error:
            raise UIBuilderFactoryError(f"Unknown UI engine: {engine!r}") from error
        return builder_type()