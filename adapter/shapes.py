from abc import ABC, abstractmethod


class Shape(ABC):
    '''
    Abstract base class for shapes.
    This class defines the interface for shapes, which includes methods to calculate area and perimeter.
    Concrete shape classes should implement these methods.
    '''

    @abstractmethod
    def area(self) -> float:
        '''
        Calculate and return the area of the shape.
        :return: The area of the shape as a float.
        '''
        pass

    @abstractmethod
    def perimeter(self) -> float:
        '''
        Calculate and return the perimeter of the shape.
        :return: The perimeter of the shape as a float.
        '''
        pass


class LegacyRectangle(Shape):
    def __init__(self, x: float, y: float, width: float, height: float) -> None:
        '''
        Initializes a LegacyRectangle instance.
        :param x: The x-coordinate of the rectangle's top-left corner.
        :param y: The y-coordinate of the rectangle's top-left corner.
        :param width: The width of the rectangle.
        :param height: The height of the rectangle.
        '''
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    def area(self) -> float:
        '''
        Calculate and return the area of the rectangle.
        :return: The area of the rectangle as a float.
        '''
        return self.width * self.height

    def perimeter(self) -> float:
        '''
        Calculate and return the perimeter of the rectangle.
        :return: The perimeter of the rectangle as a float.
        '''
        return 2 * (self.width + self.height)


class NewerShape(Shape):
    @abstractmethod
    def diagonal(self) -> float:
        '''
        Calculate and return the diagonal length of the shape.
        :return: The diagonal length of the shape as a float.
        '''
        pass


class NewerRectangle(NewerShape):
    def __init__(self, x1: float, y1: float, x2: float, y2: float) -> None:
        '''
        Initializes a NewerRectangle instance.
        :param x1: The x-coordinate of the rectangle's top-left corner.
        :param y1: The y-coordinate of the rectangle's top-left corner.
        :param x2: The x-coordinate of the rectangle's bottom-right corner.
        :param y2: The y-coordinate of the rectangle's bottom-right corner.
        '''
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2

    def area(self) -> float:
        '''
        Calculate and return the area of the rectangle.
        :return: The area of the rectangle as a float.
        '''
        width = self.x2 - self.x1
        height = self.y2 - self.y1
        return width * height

    def perimeter(self) -> float:
        '''
        Calculate and return the perimeter of the rectangle.
        :return: The perimeter of the rectangle as a float.
        '''
        width = self.x2 - self.x1
        height = self.y2 - self.y1
        return 2 * (width + height)

    def diagonal(self) -> float:
        '''
        Calculate and return the diagonal length of the rectangle.
        :return: The diagonal length of the rectangle as a float.
        '''
        width = self.x2 - self.x1
        height = self.y2 - self.y1
        return (width ** 2 + height ** 2) ** 0.5


class RectangleAdapter(NewerShape):
    '''
    Adapter class to convert LegacyRectangle to NewerShape interface.
    This class allows LegacyRectangle instances to be used where NewerShape is expected.
    '''

    def __init__(self, legacy_rectangle: LegacyRectangle) -> None:
        '''
        Initializes the adapter with a LegacyRectangle instance.
        :param legacy_rectangle: An instance of LegacyRectangle.
        '''
        self.legacy_rectangle = legacy_rectangle

    def area(self) -> float:
        '''
        Calculate and return the area of the rectangle using the legacy rectangle's area method.
        :return: The area of the rectangle as a float.
        '''
        return self.legacy_rectangle.area()

    def perimeter(self) -> float:
        '''
        Calculate and return the perimeter of the rectangle using the legacy rectangle's perimeter method.
        :return: The perimeter of the rectangle as a float.
        '''
        return self.legacy_rectangle.perimeter()

    def diagonal(self) -> float:
        '''
        Calculate and return the diagonal length of the rectangle.
        This method calculates the diagonal using the legacy rectangle's width and height.
        :return: The diagonal length of the rectangle as a float.
        '''
        width = self.legacy_rectangle.width
        height = self.legacy_rectangle.height
        return (width ** 2 + height ** 2) ** 0.5

    @property
    def x2(self) -> float:
        '''
        Calculate and return the x-coordinate of the rectangle's bottom-right corner.
        :return: The x-coordinate of the rectangle's bottom-right corner as a float.
        '''
        return self.legacy_rectangle.x + self.legacy_rectangle.width

    @property
    def y2(self) -> float:
        '''
        Calculate and return the y-coordinate of the rectangle's bottom-right corner.
        :return: The y-coordinate of the rectangle's bottom-right corner as a float.
        '''
        return self.legacy_rectangle.y + self.legacy_rectangle.height


if __name__ == "__main__":
    # Example usage
    legacy_rect = LegacyRectangle(0, 0, 5, 10)
    print(f"Legacy Rectangle Area: {legacy_rect.area()}")
    print(f"Legacy Rectangle Perimeter: {legacy_rect.perimeter()}")

    newer_rect = NewerRectangle(0, 0, 5, 10)
    print(f"Newer Rectangle Area: {newer_rect.area()}")
    print(f"Newer Rectangle Perimeter: {newer_rect.perimeter()}")

    # Test scenario of conversion
    # Let's assume we have a function which uses newer rectangle but we have a legacy rectangle instance.
    def test(shape_with_diagonal: NewerShape) -> None:
        '''
        Test function that requires a shape with a diagonal method.
        :param shape_with_diagonal: An instance of NewerShape.
        :return: None
        '''
        print(f"Area: {shape_with_diagonal.area()}")
        print(f"Perimeter: {shape_with_diagonal.perimeter()}")
        print(f"Diagonal: {shape_with_diagonal.diagonal()}")

    # 1. Create a legacy rectangle
    legacy_rect = LegacyRectangle(0, 0, 3, 4)
    # 2. Convert it to a NewerShape using the adapter
    adapted_rect = RectangleAdapter(legacy_rect)
    # 3. Use the adapted rectangle in the test function
    test(adapted_rect)
    # 4. Check the adapted rectangle's properties
    print(f'Adapted Rectangle 2nd Point: ({adapted_rect.x2}, {adapted_rect.y2})')

    # Compare with a newer rectangle
    newer_rect = NewerRectangle(0, 0, 3, 4)
    test(newer_rect)

    print(f'Newer Rectangle 2nd Point: ({newer_rect.x2}, {newer_rect.y2})')


