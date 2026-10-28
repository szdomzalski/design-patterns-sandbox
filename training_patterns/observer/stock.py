from __future__ import annotations
from abc import ABC, abstractmethod


class Observer(ABC):
    '''
    Observer is an abstract base class that defines the interface for all observers.
    Observers must implement the update method to receive updates from the subject.
    '''
    @abstractmethod
    def update(self, stock_data: Stock) -> None:
        ''' Update method that will be called by the subject when there are changes in the stock data. '''
        pass


class PriceDisplay(Observer):
    '''
    PriceDisplay is an observer that displays the current stock price.
    It implements the update method to receive updates from the Stock subject.
    '''
    def update(self, stock_data: Stock) -> None:
        ''' Update method that prints the current stock price. '''
        print(f"Current price of {stock_data.symbol}: ${stock_data.price:.2f}")


class ChangeDisplay(Observer):
    '''
    ChangeDisplay is an observer that displays the change in stock price.
    It implements the update method to receive updates from the Stock subject.
    '''
    def update(self, stock_data: Stock) -> None:
        ''' Update method that prints the change in stock price. '''
        if len(stock_data.price_history) < 2:
            print(f"No previous price data for {stock_data.symbol}.")
            return
        previous_price = stock_data.price_history[-2]
        change = stock_data.price - previous_price
        change_percentage = (change / previous_price) * 100
        print(f"Change in {stock_data.symbol}: ${change:.2f} "
              f"({change_percentage:.2f}%) from previous price.")


class Stock:
    '''
    Stock is a subject that holds information about a stock's symbol and price.
    It maintains a list of observers that can be notified of price changes.
    Observers can subscribe to receive updates when the stock price changes.
    '''
    def __init__(self, symbol: str, price: float) -> None:
        '''
        Initialize the stock with a symbol and an initial price.
        Also initializes an empty list of observers.
        '''
        self.symbol = symbol
        self.price = price
        self.price_history = [price]
        self.observers: list[Observer] = []

    def notify_observers(self) -> None:
        '''
        Notify all observers about the stock price change.
        '''
        for observer in self.observers:
            observer.update(self)

    def set_price(self, price: float) -> None:
        '''
        Set the stock price and notify all observers of the change.
        '''
        self.price = price
        self.price_history.append(price)
        self.notify_observers()

    def attach(self, observer: Observer) -> None:
        '''
        Attach an observer to the stock so it can receive updates.
        '''
        self.observers.append(observer)

    def detach(self, observer: Observer) -> None:
        '''
        Detach an observer from the stock so it no longer receives updates.
        '''
        self.observers.remove(observer)


if __name__ == "__main__":
    # Example usage
    stock = Stock("AAPL", 150.00)
    price_display = PriceDisplay()
    change_display = ChangeDisplay()

    stock.attach(price_display)
    stock.attach(change_display)

    stock.set_price(155.00)  # This will notify observers
    stock.set_price(152.50)  # This will notify observers again
