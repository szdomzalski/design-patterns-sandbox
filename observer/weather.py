from __future__ import annotations
from abc import ABC, abstractmethod
import random


class Observer(ABC):
    '''
    Observer is an abstract base class that defines the interface for all observers.
    Observers must implement the update method to receive updates from the subject.
    '''
    @abstractmethod
    def update(self, weather_data: WeatherData) -> None:
        ''' Update method that will be called by the subject when there are changes in the weather data. '''
        pass


class CurrentConditionsDisplay(Observer):
    '''
    CurrentConditionsDisplay is an observer that displays the current weather conditions.
    It implements the update method to receive updates from the WeatherData subject.
    '''
    def update(self, weather_data: WeatherData) -> None:
        ''' Update method that prints the current weather conditions. '''
        print(f"Current conditions: {weather_data.temperature}°C, "
              f"{weather_data.humidity}% humidity, "
              f"{weather_data.pressure} hPa pressure.")


class StatisticsDisplay(Observer):
    '''
    StatisticsDisplay is an observer that displays statistical information about the weather.
    It implements the update method to receive updates from the WeatherData subject.
    '''
    def update(self, weather_data: WeatherData) -> None:
        ''' Update method that prints statistical information about the weather. '''
        # For simplicity, I just print the current data as statistics.
        print(f"Statistics: {weather_data.temperature}°C, "
              f"{weather_data.humidity}% humidity, "
              f"{weather_data.pressure} hPa pressure.")


class ForecastDisplay(Observer):
    '''
    ForecastDisplay is an observer that provides a weather forecast based on the current data.
    It implements the update method to receive updates from the WeatherData subject.
    '''
    def update(self, weather_data: WeatherData) -> None:
        ''' Update method that prints a simple weather forecast. '''
        # For simplicity, I just print a mock forecast.
        temp_bias = random.uniform(-2, 2)
        humidity_bias = random.uniform(-5, 5)
        pressure_bias = random.uniform(-1, 1)
        forecast_temp = weather_data.temperature + temp_bias
        forecast_humidity = weather_data.humidity + humidity_bias
        forecast_pressure = weather_data.pressure + pressure_bias
        print(f"Forecast: The weather will be around {forecast_temp:.1f}°C, "
              f"{forecast_humidity:.1f}% humidity, "
              f"{forecast_pressure:.1f} hPa pressure.")


class WeatherData:
    '''
    WeatherData is the subject that holds weather measurements and notifies observers
    when measurements change.
    '''
    def __init__(self, temperature: float, humidity: float, pressure: float) -> None:
        ''' Initialize the WeatherData with initial measurements. '''
        self.temperature = temperature
        self.humidity = humidity
        self.pressure = pressure
        self.observers: list[Observer] = []

    def __str__(self) -> str:
        ''' Return a string representation of the WeatherData object. '''
        return f"WeatherData(temperature={self.temperature}, humidity={self.humidity}, pressure={self.pressure})"

    def set_measurements(self, temperature: float, humidity: float, pressure: float) -> None:
        '''
        Set new measurements and notify observers of the change.
        '''
        self.temperature = temperature
        self.humidity = humidity
        self.pressure = pressure
        self.notify_observers()

    def attach(self, observer: Observer) -> None:
        '''
        Attach an observer to the WeatherData subject.
        If the observer is not already attached, it will be added to the list of observers.
        '''
        if observer not in self.observers:
            self.observers.append(observer)

    def detach(self, observer: Observer) -> None:
        '''
        Detach an observer from the WeatherData subject.
        If the observer is attached, it will be removed from the list of observers.
        '''
        try:
            self.observers.remove(observer)
        except ValueError:
            print(f"Observer {observer} not found in the list of observers.")

    def notify_observers(self) -> None:
        '''
        Notify all attached observers about the change in weather data.
        Each observer's update method will be called with the current weather data.
        '''
        for observer in self.observers:
            observer.update(self)


if __name__ == "__main__":
    # Example usage of the WeatherData subject and its observers.
    weather_data = WeatherData(25.0, 65.0, 1013.0)

    current_display = CurrentConditionsDisplay()
    statistics_display = StatisticsDisplay()
    forecast_display = ForecastDisplay()

    weather_data.attach(current_display)
    weather_data.attach(statistics_display)
    weather_data.attach(forecast_display)

    # Simulate a change in weather data.
    weather_data.set_measurements(26.5, 70.0, 1012.5)
    weather_data.set_measurements(24.0, 60.0, 1014.0)

    # Detach the current display and simulate another change.
    weather_data.detach(current_display)
    weather_data.set_measurements(22.0, 55.0, 1015.0)
