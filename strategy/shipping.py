from abc import ABC, abstractmethod


class Carrier(ABC):
    '''
    Abstract base class for shipping carriers.
    This class defines the interface for shipping carriers, which includes a method to calculate shipping cost.
    '''
    @abstractmethod
    def calculate_shipping_cost(self, weight: float) -> float:
        """
        Calculate the shipping cost based on the weight of the package.
        :param weight: Weight of the package in pounds.
        :return: Shipping cost as a float.
        """
        pass

    def __str__(self) -> str:
        '''
        Return the name of the carrier.
        :return: Name of the carrier as a string.
        '''
        return self.__class__.__name__[:-7]  # Remove 'Carrier' suffix for cleaner output


class FedExCarrier(Carrier):
    '''
    Concrete implementation of the Carrier interface for FedEx.
    '''
    def calculate_shipping_cost(self, weight: float) -> float:
        """
        Calculate the shipping cost for FedEx.
        :param weight: Weight of the package in pounds.
        :return: Shipping cost as a float.
        """
        return weight * 2.5


class UPSCarrier(Carrier):
    '''
    Concrete implementation of the Carrier interface for UPS.
    '''
    def calculate_shipping_cost(self, weight: float) -> float:
        """
        Calculate the shipping cost for UPS.
        :param weight: Weight of the package in pounds.
        :return: Shipping cost as a float.
        """
        return weight * 3


class DHLCarrier(Carrier):
    '''
    Concrete implementation of the Carrier interface for DHL.
    '''
    def calculate_shipping_cost(self, weight: float) -> float:
        """
        Calculate the shipping cost for DHL.
        :param weight: Weight of the package in pounds.
        :return: Shipping cost as a float.
        """
        return weight * 4


class AmazonDeliveryCarrier(Carrier):
    '''
    Concrete implementation of the Carrier interface for Amazon Delivery.
    '''
    def calculate_shipping_cost(self, weight: float) -> float:
        """
        Calculate the shipping cost for Amazon Delivery.
        :param weight: Weight of the package in pounds.
        :return: Shipping cost as a float.
        """
        return weight * 3.25


class ShippingCostCalculator:
    '''
    Class to calculate shipping costs using a specific carrier.
    This class uses the Strategy pattern to allow different carriers to be used interchangeably.
    '''
    def __init__(self, carrier: Carrier) -> None:
        """
        Initializes the ShippingCostCalculator with a specific carrier.
        :param carrier: An instance of a class that implements the Carrier interface.
        """
        self.carrier = carrier

    def calculate(self, weight: float) -> float:
        '''
        Calculate the shipping cost using the specified carrier.
        :param weight: Weight of the package in pounds.
        :return: Shipping cost as a float.
        '''
        return self.carrier.calculate_shipping_cost(weight)


SHIPPING_CARRIERS = {
    1: FedExCarrier(),
    2: UPSCarrier(),
    3: DHLCarrier(),
    4: AmazonDeliveryCarrier()
}


if __name__ == "__main__":
    print("Welcome to the Shipping Cost Calculator!")
    print("Select a carrier for shipping:")
    print("1. FedEx")
    print("2. UPS")
    print("3. DHL")
    print("4. Amazon Delivery")

    choice = int(input("Enter the number corresponding to your choice: "))
    weight = float(input("Enter the weight of the package (in pounds): "))

    carrier = SHIPPING_CARRIERS[choice]
    calculator = ShippingCostCalculator(carrier)

    shipping_cost = calculator.calculate(weight)
    print(f"The shipping cost for {carrier} is ${shipping_cost:.2f}")