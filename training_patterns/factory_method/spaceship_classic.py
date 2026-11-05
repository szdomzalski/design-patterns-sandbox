from abc import ABC, abstractmethod
from dataclasses import dataclass


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


class SpaceshipFactory(ABC):
    @abstractmethod
    def create_spaceship(self, ctx: SpaceshipContext) -> Spaceship:
        """
        Abstract method to create a spaceship based on the provided context.
        :param ctx: The context containing position, size, display name, and velocity.
        :return: An instance of a spaceship.
        """
        pass


class MilleniumFalconFactory(SpaceshipFactory):
    def create_spaceship(self, ctx: SpaceshipContext) -> Spaceship:
        """
        Create a Millennium Falcon spaceship based on the provided context.
        :param ctx: The context containing position, size, display name, and velocity.
        :return: An instance of the Millennium Falcon spaceship.
        """
        return MilleniumFalcon(ctx)

class UNSCInfinityFactory(SpaceshipFactory):
    def create_spaceship(self, ctx: SpaceshipContext) -> Spaceship:
        """
        Create a UNSC Infinity spaceship based on the provided context.
        :param ctx: The context containing position, size, display name, and velocity.
        :return: An instance of the UNSC Infinity spaceship.
        """
        return UNSCInfinity(ctx)

class USSEnterpriseFactory(SpaceshipFactory):
    def create_spaceship(self, ctx: SpaceshipContext) -> Spaceship:
        """
        Create a USS Enterprise spaceship based on the provided context.
        :param ctx: The context containing position, size, display name, and velocity.
        :return: An instance of the USS Enterprise spaceship.
        """
        return USSEnterprise(ctx)


class SerenityFactory(SpaceshipFactory):
    def create_spaceship(self, ctx: SpaceshipContext) -> Spaceship:
        """
        Create a Serenity spaceship based on the provided context.
        :param ctx: The context containing position, size, display name, and velocity.
        :return: An instance of the Serenity spaceship.
        """
        return Serenity(ctx)


if __name__ == "__main__":
    # Example usage
    position = Position(100.0, 200.0)
    size = Size(50.0, 20.0)
    velocity = Velocity(10.0, 5.0)
    ctx = SpaceshipContext(position, size, "Millennium Falcon Mark III", velocity)

    factory = MilleniumFalconFactory()
    spaceship = factory.create_spaceship(ctx)

    print(f"Created spaceship: {spaceship.name} (class {type(spaceship).__name__})")
    print(f"Position: {spaceship.position}")
    print(f"Size: {spaceship.size}")
    print(f"Velocity: {spaceship.velocity}")
