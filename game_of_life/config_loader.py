from abc import ABC, abstractmethod
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from typing import Any, Type
import json
import os
import tomllib
import xml.etree.ElementTree as ET

import yaml

from .event_handling import EventType


ALLOWED_BUTTON_EVENTS = frozenset({
    EventType.UI_QUIT,
    EventType.UI_STOP,
    EventType.UI_START,
})


class ConfigError(Exception):
    """Report invalid or unreadable application configuration."""


def _require_positive_int(value: int, field_name: str) -> None:
    """Require a non-Boolean integer greater than zero for a named field."""
    if not isinstance(value, int) or isinstance(value, bool) or value <= 0:
        raise ConfigError(f"{field_name} must be a positive integer")


def _require_non_negative_int(value: int, field_name: str) -> None:
    """Require a non-Boolean integer greater than or equal to zero for a named field."""
    if not isinstance(value, int) or isinstance(value, bool) or value < 0:
        raise ConfigError(f"{field_name} must be a non-negative integer")


def _require_number(value: float, field_name: str) -> None:
    """Require a non-Boolean integer or floating-point value for a named field."""
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        raise ConfigError(f"{field_name} must be a number")


@dataclass(frozen=True)
class SimulationSpec:
    """Describe initial board generation, update speed, and ruleset selection."""

    cells_x: int
    cells_y: int
    alive_probability: float
    random_seed: int
    updates_per_second: int
    ruleset: str

    def __post_init__(self) -> None:
        """Validate all simulation startup settings after field assignment."""
        _require_positive_int(self.cells_x, "simulation.cells_x")
        _require_positive_int(self.cells_y, "simulation.cells_y")
        _require_number(self.alive_probability, "simulation.alive_probability")
        if not 0.0 <= self.alive_probability <= 1.0:
            raise ConfigError("simulation.alive_probability must be between 0 and 1")
        _require_non_negative_int(self.random_seed, "simulation.random_seed")
        _require_positive_int(self.updates_per_second, "simulation.updates_per_second")
        if not isinstance(self.ruleset, str) or not self.ruleset.strip():
            raise ConfigError("simulation.ruleset must be a non-empty string")


@dataclass(frozen=True)
class WindowSpec:
    """Describe the dimensions of the application window."""

    width: int
    height: int

    def __post_init__(self) -> None:
        """Validate dimensions immediately after dataclass initialization."""
        # A dataclass-generated __init__ calls __post_init__ automatically
        # after assigning fields. Raising here prevents an invalid frozen spec
        # from ever being returned to the caller.
        _require_positive_int(self.width, "window.width")
        _require_positive_int(self.height, "window.height")


@dataclass(frozen=True)
class GridSpec:
    """Describe the pixel dimensions of the simulation grid."""

    width: int
    height: int

    def __post_init__(self) -> None:
        """Validate grid dimensions after dataclass field assignment."""
        _require_positive_int(self.width, "grid.width")
        _require_positive_int(self.height, "grid.height")

    def cell_size(self, n_cells_x: int, n_cells_y: int) -> tuple[int, int]:
        """Return exact cell dimensions for the requested board shape."""
        _require_positive_int(n_cells_x, "n_cells_x")
        _require_positive_int(n_cells_y, "n_cells_y")
        if self.width % n_cells_x != 0 or self.height % n_cells_y != 0:
            raise ConfigError("grid dimensions must be divisible by board dimensions")
        return self.width // n_cells_x, self.height // n_cells_y


@dataclass(frozen=True)
class ButtonSpec:
    """Describe a button and the application event it publishes."""

    label: str
    width: int
    height: int
    x: int
    y: int
    event: EventType

    def __post_init__(self) -> None:
        """Validate button content, geometry, and event after initialization."""
        if not isinstance(self.label, str) or not self.label.strip():
            raise ConfigError("button.label must be a non-empty string")
        _require_positive_int(self.width, "button.width")
        _require_positive_int(self.height, "button.height")
        _require_non_negative_int(self.x, "button.x")
        _require_non_negative_int(self.y, "button.y")
        if self.event not in ALLOWED_BUTTON_EVENTS:
            raise ConfigError("button.event must be a UI action event")


@dataclass(frozen=True)
class SliderSpec:
    """Describe a bounded slider and the event carrying its current value."""

    x: int
    y: int
    width: int
    height: int
    min_value: float
    max_value: float
    initial_value: float
    event: EventType

    def __post_init__(self) -> None:
        """Validate slider geometry, value range, and event after initialization."""
        _require_non_negative_int(self.x, "slider.x")
        _require_non_negative_int(self.y, "slider.y")
        _require_positive_int(self.width, "slider.width")
        _require_positive_int(self.height, "slider.height")
        if self.min_value >= self.max_value:
            raise ConfigError("slider.min_value must be less than slider.max_value")
        if not self.min_value <= self.initial_value <= self.max_value:
            raise ConfigError("slider.initial_value must be within the configured range")
        if self.event is not EventType.SPEED_CHANGE:
            raise ConfigError("slider.event must be SPEED_CHANGE")


@dataclass(frozen=True)
class UIConfig:
    """Collect validated immutable specifications for constructing a UI."""

    window: WindowSpec
    grid: GridSpec
    buttons: tuple[ButtonSpec, ...] = ()
    sliders: tuple[SliderSpec, ...] = ()

    def __post_init__(self) -> None:
        """Validate relationships between the window, grid, and controls."""
        if self.grid.width > self.window.width or self.grid.height > self.window.height:
            raise ConfigError("grid dimensions must fit inside the window")
        for control in (*self.buttons, *self.sliders):
            if control.x + control.width > self.window.width or control.y + control.height > self.window.height:
                raise ConfigError("UI controls must fit inside the window")


@dataclass(frozen=True)
class ApplicationConfig:
    """Collect simulation and UI specifications for application composition."""

    simulation: SimulationSpec
    ui: UIConfig

    def __post_init__(self) -> None:
        """Validate relationships between simulation and UI settings."""
        self.ui.grid.cell_size(self.simulation.cells_x, self.simulation.cells_y)


class ApplicationConfigAdapter:
    """Adapt a format-independent mapping to validated application settings."""

    @staticmethod
    def from_mapping(data: Mapping[str, Any]) -> ApplicationConfig:
        """Convert parsed configuration data to validated application settings."""
        if not isinstance(data, Mapping):
            raise ConfigError("configuration root must be a mapping")
        simulation = data['simulation']
        simulation_spec = SimulationSpec(
            cells_x=simulation['cells_x'],
            cells_y=simulation['cells_y'],
            alive_probability=simulation['alive_probability'],
            random_seed=simulation['random_seed'],
            updates_per_second=simulation['updates_per_second'],
            ruleset=simulation['ruleset'],
        )
        window = data['window']
        grid = data['grid']
        buttons = tuple(
            ButtonSpec(
                label=button['label'],
                width=button['width'],
                height=button['height'],
                x=button['x'],
                y=button['y'],
                event=ApplicationConfigAdapter._event_type(button['event']),
            )
            for button in data.get('buttons', [])
        )
        sliders = tuple(
            ApplicationConfigAdapter._slider_spec(slider, simulation_spec)
            for slider in data.get('sliders', [])
        )
        return ApplicationConfig(
            simulation=simulation_spec,
            ui=UIConfig(
                window=WindowSpec(width=window['width'], height=window['height']),
                grid=GridSpec(width=grid['width'], height=grid['height']),
                buttons=buttons,
                sliders=sliders,
            ),
        )

    @staticmethod
    def _slider_spec(slider: Mapping[str, Any], simulation: SimulationSpec) -> SliderSpec:
        """Adapt a slider while deriving only simulation-speed initialization."""
        event = ApplicationConfigAdapter._event_type(slider['event'])
        if event is EventType.SPEED_CHANGE:
            # Simulation speed is the single source of truth for speed controls.
            initial_value = simulation.updates_per_second
        else:
            # Other slider types own their initial value in UI configuration.
            initial_value = slider['initial_value']

        return SliderSpec(
            x=slider['x'],
            y=slider['y'],
            width=slider['width'],
            height=slider['height'],
            min_value=slider['min_value'],
            max_value=slider['max_value'],
            initial_value=initial_value,
            event=event,
        )

    @staticmethod
    def _event_type(event_name: str) -> EventType:
        """Convert a serialized event name to its EventType member."""
        try:
            return EventType[event_name]
        except (KeyError, TypeError) as error:
            raise ConfigError(f"Unknown event type: {event_name!r}") from error


class ConfigLoader(ABC):
    """Load one configuration syntax and adapt it to application settings."""

    def __init__(self, path: str) -> None:
        self._path = path

    def get_config(self) -> ApplicationConfig:
        """Read, parse, and adapt the configured source file."""
        try:
            return ApplicationConfigAdapter.from_mapping(self._read_mapping())
        except ConfigError:
            raise
        except (OSError, ET.ParseError, yaml.YAMLError, KeyError, TypeError, ValueError) as error:
            raise ConfigError(f"Invalid configuration in '{self._path}': {error}") from error

    @abstractmethod
    def _read_mapping(self) -> Mapping[str, Any]:
        """Parse the source format into the shared mapping representation."""
        pass


class JSONConfigLoader(ConfigLoader):
    """Adapt a JSON configuration file to UI specifications."""

    def _read_mapping(self) -> Mapping[str, Any]:
        with open(self._path, 'r', encoding='utf-8') as config_file:
            return json.load(config_file)


class YAMLConfigLoader(ConfigLoader):
    """Adapt a YAML configuration file to UI specifications."""

    def _read_mapping(self) -> Mapping[str, Any]:
        with open(self._path, 'r', encoding='utf-8') as config_file:
            return yaml.safe_load(config_file)


class TOMLConfigLoader(ConfigLoader):
    """Adapt a TOML configuration file to UI specifications."""

    def _read_mapping(self) -> Mapping[str, Any]:
        with open(self._path, 'rb') as config_file:
            return tomllib.load(config_file)


class XMLConfigLoader(ConfigLoader):
    """Adapt an XML configuration file to the shared mapping representation."""

    _window_fields: Mapping[str, Callable[[str], Any]] = {
        'width': int,
        'height': int,
    }
    _simulation_fields: Mapping[str, Callable[[str], Any]] = {
        'cells_x': int,
        'cells_y': int,
        'alive_probability': float,
        'random_seed': int,
        'updates_per_second': int,
        'ruleset': str,
    }
    _button_fields: Mapping[str, Callable[[str], Any]] = {
        'label': str,
        'width': int,
        'height': int,
        'x': int,
        'y': int,
        'event': str,
    }
    _slider_fields: Mapping[str, Callable[[str], Any]] = {
        'x': int,
        'y': int,
        'width': int,
        'height': int,
        'min_value': float,
        'max_value': float,
        'event': str,
    }

    def _read_mapping(self) -> Mapping[str, Any]:
        root = ET.parse(self._path).getroot()
        if root.tag != 'application':
            raise ConfigError("XML configuration root must be <application>")

        simulation = self._required_child(root, 'simulation')
        window = self._required_child(root, 'window')
        grid = self._required_child(root, 'grid')
        return {
            'simulation': self._convert_attributes(simulation, self._simulation_fields),
            'window': self._convert_attributes(window, self._window_fields),
            'grid': self._convert_attributes(grid, self._window_fields),
            'buttons': [
                self._convert_attributes(button, self._button_fields)
                for button in root.findall('./buttons/button')
            ],
            'sliders': [
                self._convert_slider_attributes(slider)
                for slider in root.findall('./sliders/slider')
            ],
        }

    @staticmethod
    def _required_child(root: ET.Element, tag: str) -> ET.Element:
        """Return a required direct child or report the missing XML element."""
        element = root.find(tag)
        if element is None:
            raise ConfigError(f"XML configuration requires <{tag}>")
        return element

    @staticmethod
    def _convert_attributes(
            element: ET.Element,
            fields: Mapping[str, Callable[[str], Any]]) -> dict[str, Any]:
        """Convert XML string attributes to the shared mapping value types."""
        try:
            return {name: convert(element.attrib[name]) for name, convert in fields.items()}
        except (KeyError, ValueError) as error:
            raise ConfigError(f"Invalid <{element.tag}> attributes: {error}") from error

    def _convert_slider_attributes(self, element: ET.Element) -> dict[str, Any]:
        """Convert required slider attributes and preserve an optional initial value."""
        slider = self._convert_attributes(element, self._slider_fields)
        if 'initial_value' in element.attrib:
            try:
                slider['initial_value'] = float(element.attrib['initial_value'])
            except ValueError as error:
                raise ConfigError(f"Invalid <{element.tag}> initial_value: {error}") from error
        return slider


class ConfigLoaderFactoryError(ConfigError):
    pass


class ConfigLoaderFactory:
    _loaders = {
        '.json': JSONConfigLoader,
        '.toml': TOMLConfigLoader,
        '.yaml': YAMLConfigLoader,
        '.yml': YAMLConfigLoader,
        '.xml': XMLConfigLoader,
    }

    @staticmethod
    def create(path: str) -> ConfigLoader:
        _, ext = os.path.splitext(path)
        ext = ext.lower()
        if not ext or ext not in ConfigLoaderFactory._loaders:
            raise ConfigLoaderFactoryError(f"Unsupported or missing config file extension: '{ext}'")
        loader_cls: Type[ConfigLoader] = ConfigLoaderFactory._loaders[ext]
        return loader_cls(path)
