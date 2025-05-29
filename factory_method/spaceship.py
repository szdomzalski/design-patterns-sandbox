from abc import ABC
from dataclasses import dataclass
from enum import Enum


@dataclass
class Position:
    x: float
    y: float

    def __str__(self) -> str:
        return f"Position(x={self.x:.2f}, y={self.y:.2f})"


@dataclass
class Size:
    width: float
    height: float

    def __str__(self) -> str:
        return f"Size(width={self.width:.2f}, height={self.height:.2f})"


@dataclass
class Velocity:
    velocity_x: float
    velocity_y: float

    def __str__(self) -> str:
        return f"Velocity(velocity_x={self.velocity_x:.2f}, velocity_y={self.velocity_y:.2f})"


class SpaceshipType(Enum):
    MILLENNIUM_FALCON = "Millennium Falcon"
    UNSC_INFINITY = "UNSC Infinity"
    USS_ENTERPRISE = "USS Enterprise"
    SERENITY = "Serenity"


class SpaceshipContext:
    def __init__(self, position: Position, size: Size, display_name: str, velocity: Velocity) -> None:
        """
        Initialize the SpaceshipContext class.
        :param position: The position of the spaceship.
        :param size: The size of the spaceship.
        :param display_name: The display name of the spaceship.
        :param velocity: The velocity of the spaceship.
        :return: None
        """
        self.position = position
        self.size = size
        self.display_name = display_name
        self.velocity = velocity


class Spaceship(ABC):
    def __init__(self, ctx: SpaceshipContext) -> None:
        """
        Initialize the Spaceship class.
        :param ctx: The context containing position, size, display name, and velocity.
        :return: None
        """
        self.position = ctx.position  # Position of the spaceship
        self.velocity = ctx.velocity
        self.size = ctx.size
        self.name = ctx.display_name  # Display name of the spaceship


class MilleniumFalcon(Spaceship):
    pass


class UNSCInfinity(Spaceship):
    pass


class USSEnterprise(Spaceship):
    pass


class Serenity(Spaceship):
    pass


__SPACESHIP_FACTORY_DICT = {
    SpaceshipType.MILLENNIUM_FALCON: MilleniumFalcon,
    SpaceshipType.UNSC_INFINITY: UNSCInfinity,
    SpaceshipType.USS_ENTERPRISE: USSEnterprise,
    SpaceshipType.SERENITY: Serenity,
}


class SpaceshipFactory:
    def create_spaceship(self, spaceship_type: SpaceshipType, ctx: SpaceshipContext) -> Spaceship:
        """
        Create a spaceship based on the spaceship_type parameter.
        :param spaceship_type: The type of spaceship to create.
        :param ctx: The context containing position, size, display name, and velocity.
        :return: An instance of the specified spaceship type.
        """
        return __SPACESHIP_FACTORY_DICT[spaceship_type](ctx)


if __name__ == "__main__":
    # Example usage
    ctx = SpaceshipContext(
        position=Position(100.0, 200.0),
        size=Size(50.0, 20.0),
        display_name="Millennium Falcon Mark II",
        velocity=Velocity(10.0, 5.0)
    )

    factory = SpaceshipFactory()
    spaceship = factory.create_spaceship(SpaceshipType.MILLENNIUM_FALCON, ctx)
    print(f"Created spaceship: {spaceship.name} ({type(spaceship).__name__} class) at {spaceship.position} with "
          f"size {spaceship.size}")
